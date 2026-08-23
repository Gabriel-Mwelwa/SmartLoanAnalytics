"""Loan application, approval, rejection and disbursement management."""

from __future__ import annotations

import logging
import sqlite3
from datetime import date, timedelta

from algorithms.eligibility_scoring import calculate_eligibility_score
from algorithms.repayment_schedule import calculate_total_payable
from config import DEFAULT_ANNUAL_INTEREST_RATE, MAX_LOAN_TERM_MONTHS, MIN_LOAN_AMOUNT
from database import get_connection
from models.loan import Loan
from modules.authentication import Session
from utils.exceptions import ValidationError
from utils.validation import require_text, validate_positive_amount, validate_interest_rate, validate_loan_term


ALLOWED_STATUSES = {
    "All", "Pending", "Approved", "Rejected", "Disbursed", "Completed", "Overdue"
}


def _require_permission(session: Session, permission: str) -> None:
    if not session.can(permission):
        raise PermissionError(f"Your role does not allow '{permission}' operations.")


def _audit(user_id: int | None, action: str, details: str) -> None:
    try:
        with get_connection() as connection:
            safe_user_id = user_id
            if user_id is not None:
                exists = connection.execute(
                    "SELECT 1 FROM users WHERE user_id=?", (user_id,)
                ).fetchone()
                if exists is None:
                    safe_user_id = None
            connection.execute(
                "INSERT INTO audit_logs (user_id, action, details) VALUES (?, ?, ?)",
                (safe_user_id, action, details),
            )
    except sqlite3.Error:
        logging.exception("Unable to write loan audit event.")


def _loan_from_row(row: sqlite3.Row) -> Loan:
    return Loan(
        loan_id=row["loan_id"],
        customer_id=row["customer_id"],
        principal=float(row["principal"]),
        annual_interest_rate=float(row["annual_interest_rate"]),
        term_months=int(row["term_months"]),
        application_date=row["application_date"],
        approval_date=row["approval_date"],
        disbursement_date=row["disbursement_date"],
        due_date=row["due_date"],
        status=row["status"],
        eligibility_score=row["eligibility_score"],
        purpose=row["purpose"],
    )


def apply_for_loan(
    session: Session,
    customer_id: int,
    principal,
    annual_interest_rate=DEFAULT_ANNUAL_INTEREST_RATE,
    term_months: int = 12,
    purpose: str = "",
    application_date: date | None = None,
) -> Loan:
    """Create a new pending loan application and calculate eligibility score."""
    _require_permission(session, "manage_loans")

    amount = validate_positive_amount(principal, "Loan amount")
    if amount < MIN_LOAN_AMOUNT:
        raise ValidationError(
            f"Loan amount must be at least K{MIN_LOAN_AMOUNT:.2f}."
        )

    rate = validate_interest_rate(annual_interest_rate)
    months = validate_loan_term(term_months, MAX_LOAN_TERM_MONTHS)

    clean_purpose = require_text(purpose, "Loan purpose")
    app_date = application_date or date.today()

    with get_connection() as connection:
        customer = connection.execute(
            """
            SELECT customer_id, customer_code, full_name, monthly_income, status
            FROM customers WHERE customer_id=?
            """,
            (customer_id,),
        ).fetchone()

        if customer is None:
            raise ValidationError("Customer record was not found.")

        if customer["status"] != "Active":
            raise ValidationError("Suspended customers cannot apply for a loan.")

        existing_debt = connection.execute(
            """
            SELECT COALESCE(SUM(
                l.principal - COALESCE((
                    SELECT SUM(r.amount)
                    FROM repayments r
                    WHERE r.loan_id=l.loan_id
                ), 0)
            ), 0)
            FROM loans l
            WHERE l.customer_id=?
              AND l.status IN ('Approved', 'Disbursed', 'Overdue')
            """,
            (customer_id,),
        ).fetchone()[0]

        score = calculate_eligibility_score(
            float(customer["monthly_income"]),
            amount,
            months,
            float(existing_debt or 0),
        )

        cursor = connection.execute(
            """
            INSERT INTO loans
            (
                customer_id, principal, annual_interest_rate, term_months,
                application_date, status, eligibility_score, purpose
            )
            VALUES (?, ?, ?, ?, ?, 'Pending', ?, ?)
            """,
            (
                customer_id,
                amount,
                rate,
                months,
                app_date.isoformat(),
                score,
                clean_purpose,
            ),
        )
        loan_id = cursor.lastrowid
        row = connection.execute(
            "SELECT * FROM loans WHERE loan_id=?",
            (loan_id,),
        ).fetchone()

    _audit(
        session.user.user_id,
        "LOAN_APPLICATION_CREATED",
        f"Loan {loan_id} created for customer {customer_id}; score={score}",
    )
    return _loan_from_row(row)


def approve_loan(session: Session, loan_id: int, approval_date: date | None = None) -> Loan:
    """Approve a pending loan."""
    _require_permission(session, "approve_loans")
    approved_on = approval_date or date.today()

    with get_connection() as connection:
        loan = connection.execute(
            "SELECT * FROM loans WHERE loan_id=?",
            (loan_id,),
        ).fetchone()

        if loan is None:
            raise ValidationError("Loan application was not found.")

        if loan["status"] != "Pending":
            raise ValidationError("Only Pending loans can be approved.")

        connection.execute(
            """
            UPDATE loans
            SET status='Approved', approval_date=?
            WHERE loan_id=?
            """,
            (approved_on.isoformat(), loan_id),
        )

        row = connection.execute(
            "SELECT * FROM loans WHERE loan_id=?",
            (loan_id,),
        ).fetchone()

    _audit(session.user.user_id, "LOAN_APPROVED", f"Loan {loan_id} approved")
    return _loan_from_row(row)


def reject_loan(session: Session, loan_id: int) -> Loan:
    """Reject a pending loan."""
    _require_permission(session, "approve_loans")

    with get_connection() as connection:
        loan = connection.execute(
            "SELECT * FROM loans WHERE loan_id=?",
            (loan_id,),
        ).fetchone()

        if loan is None:
            raise ValidationError("Loan application was not found.")

        if loan["status"] != "Pending":
            raise ValidationError("Only Pending loans can be rejected.")

        connection.execute(
            "UPDATE loans SET status='Rejected' WHERE loan_id=?",
            (loan_id,),
        )

        row = connection.execute(
            "SELECT * FROM loans WHERE loan_id=?",
            (loan_id,),
        ).fetchone()

    _audit(session.user.user_id, "LOAN_REJECTED", f"Loan {loan_id} rejected")
    return _loan_from_row(row)


def disburse_loan(
    session: Session,
    loan_id: int,
    disbursement_date: date | None = None,
) -> Loan:
    """Disburse an approved loan and calculate its due date."""
    _require_permission(session, "approve_loans")
    disbursed_on = disbursement_date or date.today()

    with get_connection() as connection:
        loan = connection.execute(
            "SELECT * FROM loans WHERE loan_id=?",
            (loan_id,),
        ).fetchone()

        if loan is None:
            raise ValidationError("Loan record was not found.")

        if loan["status"] != "Approved":
            raise ValidationError("Only Approved loans can be disbursed.")

        due = disbursed_on + timedelta(days=int(loan["term_months"]) * 30)

        connection.execute(
            """
            UPDATE loans
            SET status='Disbursed',
                disbursement_date=?,
                due_date=?
            WHERE loan_id=?
            """,
            (disbursed_on.isoformat(), due.isoformat(), loan_id),
        )

        row = connection.execute(
            "SELECT * FROM loans WHERE loan_id=?",
            (loan_id,),
        ).fetchone()

    _audit(session.user.user_id, "LOAN_DISBURSED", f"Loan {loan_id} disbursed")
    return _loan_from_row(row)


def get_loan(loan_id: int) -> Loan | None:
    with get_connection() as connection:
        row = connection.execute(
            "SELECT * FROM loans WHERE loan_id=?",
            (loan_id,),
        ).fetchone()
    return _loan_from_row(row) if row else None


def list_loans(status: str = "All", query: str = "") -> list[dict]:
    """Return loan records joined with customer details."""
    conditions = []
    params = []

    if status != "All":
        if status not in ALLOWED_STATUSES:
            raise ValidationError("Invalid loan status filter.")
        conditions.append("l.status=?")
        params.append(status)

    if query.strip():
        needle = f"%{query.strip()}%"
        conditions.append(
            "(c.customer_code LIKE ? OR c.full_name LIKE ? OR CAST(l.loan_id AS TEXT) LIKE ?)"
        )
        params.extend([needle, needle, needle])

    where = f"WHERE {' AND '.join(conditions)}" if conditions else ""

    with get_connection() as connection:
        rows = connection.execute(
            f"""
            SELECT
                l.*,
                c.customer_code,
                c.full_name AS customer_name
            FROM loans l
            JOIN customers c ON c.customer_id=l.customer_id
            {where}
            ORDER BY l.loan_id DESC
            """,
            params,
        ).fetchall()

    return [dict(row) for row in rows]


def calculate_outstanding_balance(loan_id: int) -> float:
    """Return total payable minus repayments."""
    with get_connection() as connection:
        loan = connection.execute(
            """
            SELECT principal, annual_interest_rate, term_months
            FROM loans
            WHERE loan_id=?
            """,
            (loan_id,),
        ).fetchone()

        if loan is None:
            raise ValidationError("Loan record was not found.")

        total_paid = connection.execute(
            "SELECT COALESCE(SUM(amount),0) FROM repayments WHERE loan_id=?",
            (loan_id,),
        ).fetchone()[0]

    total_payable = calculate_total_payable(
        float(loan["principal"]),
        float(loan["annual_interest_rate"]),
        int(loan["term_months"]),
    )
    return round(max(0.0, total_payable - float(total_paid or 0)), 2)
