"""Customer CRUD, search, sort and filter operations for SmartLoan Analytics."""

from __future__ import annotations

import logging
import sqlite3

from database import get_connection
from models.customer import Customer
from modules.authentication import Session
from utils.exceptions import ValidationError
from utils.validation import (
    require_text,
    validate_customer_code,
    validate_email,
    validate_national_id,
    validate_non_negative_amount,
    validate_phone,
)

ALLOWED_STATUSES = {"Active", "Suspended"}
ALLOWED_EMPLOYMENT = {
    "Employed",
    "Self-Employed",
    "Business Owner",
    "Student",
    "Unemployed",
    "Retired",
    "Other",
}
ALLOWED_SORTS = {
    "Name A-Z": ("full_name", "ASC"),
    "Name Z-A": ("full_name", "DESC"),
    "Customer Code": ("customer_code", "ASC"),
    "Highest Income": ("monthly_income", "DESC"),
    "Lowest Income": ("monthly_income", "ASC"),
    "Newest": ("customer_id", "DESC"),
}


def _require_permission(session: Session, permission: str) -> None:
    if not session.can(permission):
        raise PermissionError(f"Your role does not allow '{permission}' operations.")


def _audit(user_id: int | None, action: str, details: str) -> None:
    try:
        with get_connection() as connection:
            connection.execute(
                "INSERT INTO audit_logs (user_id, action, details) VALUES (?, ?, ?)",
                (user_id, action, details),
            )
    except sqlite3.Error:
        logging.exception("Unable to record customer audit event.")


def _customer_from_row(row: sqlite3.Row) -> Customer:
    return Customer(
        customer_id=row["customer_id"],
        customer_code=row["customer_code"],
        full_name=row["full_name"],
        national_id=row["national_id"],
        phone=row["phone"],
        email=row["email"],
        address=row["address"],
        employment_status=row["employment_status"],
        monthly_income=float(row["monthly_income"]),
        status=row["status"],
    )


def _validate_customer(
    customer_code: str,
    full_name: str,
    national_id: str = "",
    phone: str = "",
    email: str = "",
    address: str = "",
    employment_status: str = "Other",
    monthly_income=0,
    status: str = "Active",
):
    code = validate_customer_code(customer_code)
    name = require_text(full_name, "Full name")
    nid = validate_national_id(national_id)
    clean_phone = validate_phone(phone)
    clean_email = validate_email(email)
    clean_address = (address or "").strip() or None

    employment = require_text(employment_status, "Employment status")
    if employment not in ALLOWED_EMPLOYMENT:
        raise ValidationError("Select a valid employment status.")

    income = validate_non_negative_amount(monthly_income, "Monthly income")

    if status not in ALLOWED_STATUSES:
        raise ValidationError("Customer status must be Active or Suspended.")

    # Domain-specific rules
    if employment in {"Employed", "Self-Employed", "Business Owner"} and income <= 0:
        raise ValidationError(
            "Monthly income must be greater than zero for employed or business customers."
        )

    return (
        code,
        name,
        nid,
        clean_phone,
        clean_email,
        clean_address,
        employment,
        income,
        status,
    )


def add_customer(
    session: Session,
    customer_code: str,
    full_name: str,
    national_id: str = "",
    phone: str = "",
    email: str = "",
    address: str = "",
    employment_status: str = "Other",
    monthly_income=0,
    status: str = "Active",
) -> Customer:
    """Create a validated customer record."""
    _require_permission(session, "create")
    values = _validate_customer(
        customer_code,
        full_name,
        national_id,
        phone,
        email,
        address,
        employment_status,
        monthly_income,
        status,
    )

    try:
        with get_connection() as connection:
            cursor = connection.execute(
                """
                INSERT INTO customers
                (
                    customer_code, full_name, national_id, phone, email,
                    address, employment_status, monthly_income, status
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                values,
            )
            customer_id = cursor.lastrowid
            row = connection.execute(
                "SELECT * FROM customers WHERE customer_id=?",
                (customer_id,),
            ).fetchone()
    except sqlite3.IntegrityError as exc:
        message = str(exc).lower()
        if "customer_code" in message:
            raise ValidationError("Customer code already exists.") from exc
        if "national_id" in message:
            raise ValidationError("National ID already exists.") from exc
        raise ValidationError("Duplicate customer data was detected.") from exc

    customer = _customer_from_row(row)
    _audit(
        session.user.user_id,
        "CUSTOMER_CREATED",
        f"Customer {customer.customer_code} - {customer.full_name} created",
    )
    logging.info("Customer created: %s", customer.customer_code)
    return customer


def update_customer(
    session: Session,
    customer_id: int,
    customer_code: str,
    full_name: str,
    national_id: str = "",
    phone: str = "",
    email: str = "",
    address: str = "",
    employment_status: str = "Other",
    monthly_income=0,
    status: str = "Active",
) -> Customer:
    """Update an existing customer record."""
    _require_permission(session, "update")
    values = _validate_customer(
        customer_code,
        full_name,
        national_id,
        phone,
        email,
        address,
        employment_status,
        monthly_income,
        status,
    )

    with get_connection() as connection:
        exists = connection.execute(
            "SELECT 1 FROM customers WHERE customer_id=?",
            (customer_id,),
        ).fetchone()
        if exists is None:
            raise ValidationError("Customer record was not found.")

        try:
            connection.execute(
                """
                UPDATE customers
                SET customer_code=?, full_name=?, national_id=?, phone=?, email=?,
                    address=?, employment_status=?, monthly_income=?, status=?
                WHERE customer_id=?
                """,
                values + (customer_id,),
            )
        except sqlite3.IntegrityError as exc:
            message = str(exc).lower()
            if "customer_code" in message:
                raise ValidationError(
                    "Another customer already uses this customer code."
                ) from exc
            if "national_id" in message:
                raise ValidationError(
                    "Another customer already uses this National ID."
                ) from exc
            raise ValidationError("Duplicate customer data was detected.") from exc

        row = connection.execute(
            "SELECT * FROM customers WHERE customer_id=?",
            (customer_id,),
        ).fetchone()

    customer = _customer_from_row(row)
    _audit(
        session.user.user_id,
        "CUSTOMER_UPDATED",
        f"Customer {customer.customer_code} updated",
    )
    return customer


def delete_customer(session: Session, customer_id: int) -> None:
    """Delete a customer only when no loan history exists."""
    _require_permission(session, "delete")

    with get_connection() as connection:
        row = connection.execute(
            "SELECT customer_code, full_name FROM customers WHERE customer_id=?",
            (customer_id,),
        ).fetchone()
        if row is None:
            raise ValidationError("Customer record was not found.")

        loan_count = connection.execute(
            "SELECT COUNT(*) FROM loans WHERE customer_id=?",
            (customer_id,),
        ).fetchone()[0]

        if loan_count:
            raise ValidationError(
                "This customer has loan history and cannot be deleted."
            )

        connection.execute(
            "DELETE FROM customers WHERE customer_id=?",
            (customer_id,),
        )

    _audit(
        session.user.user_id,
        "CUSTOMER_DELETED",
        f"Customer {row['customer_code']} - {row['full_name']} deleted",
    )


def get_customer(customer_id: int) -> Customer | None:
    with get_connection() as connection:
        row = connection.execute(
            "SELECT * FROM customers WHERE customer_id=?",
            (customer_id,),
        ).fetchone()
    return _customer_from_row(row) if row else None


def list_customers(
    query: str = "",
    status: str = "All",
    employment_status: str = "All",
    sort_by: str = "Name A-Z",
) -> list[Customer]:
    """Return customers after search, filtering and sorting."""
    column, direction = ALLOWED_SORTS.get(
        sort_by, ALLOWED_SORTS["Name A-Z"]
    )

    conditions = []
    params = []

    if query.strip():
        needle = f"%{query.strip()}%"
        conditions.append(
            """
            (
                customer_code LIKE ?
                OR full_name LIKE ?
                OR national_id LIKE ?
                OR phone LIKE ?
                OR email LIKE ?
            )
            """
        )
        params.extend([needle] * 5)

    if status != "All":
        if status not in ALLOWED_STATUSES:
            raise ValidationError("Invalid customer status filter.")
        conditions.append("status=?")
        params.append(status)

    if employment_status != "All":
        if employment_status not in ALLOWED_EMPLOYMENT:
            raise ValidationError("Invalid employment filter.")
        conditions.append("employment_status=?")
        params.append(employment_status)

    where = f"WHERE {' AND '.join(conditions)}" if conditions else ""

    with get_connection() as connection:
        rows = connection.execute(
            f"""
            SELECT * FROM customers
            {where}
            ORDER BY {column} {direction}, customer_id ASC
            """,
            params,
        ).fetchall()

    return [_customer_from_row(row) for row in rows]
