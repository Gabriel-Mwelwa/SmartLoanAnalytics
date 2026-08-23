"""Repayment, overdue and penalty management for SmartLoan Analytics."""

from __future__ import annotations

import logging
import sqlite3
from datetime import date

from config import DEFAULT_PENALTY_RATE
from database import get_connection
from modules.authentication import Session
from modules.loan_management import calculate_outstanding_balance
from utils.exceptions import ValidationError
from utils.validation import require_text, validate_positive_amount, validate_reference_number, validate_not_future_date


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
        logging.exception("Unable to write repayment audit event.")


def record_repayment(
    session: Session,
    loan_id: int,
    amount,
    payment_method: str,
    reference_number: str,
    payment_date: date | None = None,
) -> int:
    """Record a repayment and complete a loan when the balance reaches zero."""
    _require_permission(session, "record_repayment")

    payment_amount = validate_positive_amount(amount, "Repayment amount")
    method = require_text(payment_method, "Payment method")
    reference = validate_reference_number(reference_number)
    paid_on = validate_not_future_date(payment_date or date.today(), "Payment date")

    balance_before = calculate_outstanding_balance(loan_id)

    with get_connection() as connection:
        loan = connection.execute(
            "SELECT status FROM loans WHERE loan_id=?",
            (loan_id,),
        ).fetchone()

        if loan is None:
            raise ValidationError("Loan record was not found.")

        if loan["status"] not in {"Disbursed", "Overdue"}:
            raise ValidationError(
                "Repayments can only be recorded for Disbursed or Overdue loans."
            )

        if payment_amount > balance_before + 0.01:
            raise ValidationError(
                f"Repayment cannot exceed outstanding balance of K{balance_before:.2f}."
            )

        try:
            cursor = connection.execute(
                """
                INSERT INTO repayments
                (loan_id, payment_date, amount, payment_method, reference_number)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    loan_id,
                    paid_on.isoformat(),
                    payment_amount,
                    method,
                    reference,
                ),
            )
            repayment_id = cursor.lastrowid
        except sqlite3.IntegrityError as exc:
            raise ValidationError("Reference number already exists.") from exc

    balance_after = calculate_outstanding_balance(loan_id)

    if balance_after <= 0.01:
        with get_connection() as connection:
            connection.execute(
                "UPDATE loans SET status='Completed' WHERE loan_id=?",
                (loan_id,),
            )

    _audit(
        session.user.user_id,
        "REPAYMENT_RECORDED",
        f"Repayment {repayment_id} recorded for loan {loan_id}; amount K{payment_amount:.2f}",
    )
    return repayment_id


def refresh_overdue_loans(reference_date: date | None = None) -> int:
    """Mark disbursed loans overdue when their due date has passed and balance remains."""
    today = reference_date or date.today()
    changed = 0

    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT loan_id
            FROM loans
            WHERE status='Disbursed'
              AND due_date IS NOT NULL
              AND due_date < ?
            """,
            (today.isoformat(),),
        ).fetchall()

    for row in rows:
        if calculate_outstanding_balance(row["loan_id"]) > 0:
            with get_connection() as connection:
                connection.execute(
                    "UPDATE loans SET status='Overdue' WHERE loan_id=?",
                    (row["loan_id"],),
                )
            changed += 1

    return changed


def calculate_overdue_penalty(
    loan_id: int,
    reference_date: date | None = None,
    penalty_rate: float = DEFAULT_PENALTY_RATE,
) -> float:
    """Calculate penalty as percentage of outstanding balance for overdue loans."""
    today = reference_date or date.today()

    with get_connection() as connection:
        loan = connection.execute(
            "SELECT due_date, status FROM loans WHERE loan_id=?",
            (loan_id,),
        ).fetchone()

    if loan is None:
        raise ValidationError("Loan record was not found.")

    if loan["due_date"] is None or date.fromisoformat(loan["due_date"]) >= today:
        return 0.0

    outstanding = calculate_outstanding_balance(loan_id)
    return round(outstanding * (penalty_rate / 100), 2)


def create_penalty_if_needed(
    session: Session,
    loan_id: int,
    reference_date: date | None = None,
) -> float:
    """Create one unpaid penalty record for an overdue loan if needed."""
    _require_permission(session, "manage_loans")

    amount = calculate_overdue_penalty(loan_id, reference_date)
    if amount <= 0:
        return 0.0

    with get_connection() as connection:
        existing = connection.execute(
            """
            SELECT penalty_id
            FROM penalties
            WHERE loan_id=? AND paid=0
            LIMIT 1
            """,
            (loan_id,),
        ).fetchone()

        if existing is None:
            connection.execute(
                """
                INSERT INTO penalties (loan_id, amount, reason, paid)
                VALUES (?, ?, 'Overdue loan penalty', 0)
                """,
                (loan_id, amount),
            )

    _audit(
        session.user.user_id,
        "PENALTY_CREATED",
        f"Penalty K{amount:.2f} created for loan {loan_id}",
    )
    return amount


def list_repayments(loan_id: int | None = None) -> list[dict]:
    conditions = []
    params = []

    if loan_id is not None:
        conditions.append("r.loan_id=?")
        params.append(loan_id)

    where = f"WHERE {' AND '.join(conditions)}" if conditions else ""

    with get_connection() as connection:
        rows = connection.execute(
            f"""
            SELECT
                r.repayment_id,
                r.loan_id,
                r.payment_date,
                r.amount,
                r.payment_method,
                r.reference_number,
                c.customer_code,
                c.full_name AS customer_name
            FROM repayments r
            JOIN loans l ON l.loan_id=r.loan_id
            JOIN customers c ON c.customer_id=l.customer_id
            {where}
            ORDER BY r.repayment_id DESC
            """,
            params,
        ).fetchall()

    return [dict(row) for row in rows]
