"""Reusable validation rules for SmartLoan Analytics."""

from __future__ import annotations

import re
from datetime import date, datetime

from utils.exceptions import ValidationError

EMAIL_PATTERN = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
PHONE_PATTERN = re.compile(r"^\+?[0-9]{9,15}$")
CUSTOMER_CODE_PATTERN = re.compile(r"^[A-Z0-9-]{3,20}$")
NATIONAL_ID_PATTERN = re.compile(r"^[A-Z0-9/-]{5,30}$")
USERNAME_PATTERN = re.compile(r"^[A-Za-z0-9_.-]{3,30}$")


def require_text(value: str, field_name: str) -> str:
    cleaned = (value or "").strip()
    if not cleaned:
        raise ValidationError(f"{field_name} is required.")
    return cleaned


def validate_positive_amount(value, field_name: str = "Amount") -> float:
    try:
        amount = float(value)
    except (TypeError, ValueError) as exc:
        raise ValidationError(f"{field_name} must be a valid number.") from exc

    if amount <= 0:
        raise ValidationError(f"{field_name} must be greater than zero.")
    return round(amount, 2)


def validate_non_negative_amount(value, field_name: str = "Amount") -> float:
    try:
        amount = float(value)
    except (TypeError, ValueError) as exc:
        raise ValidationError(f"{field_name} must be a valid number.") from exc

    if amount < 0:
        raise ValidationError(f"{field_name} cannot be negative.")
    return round(amount, 2)


def validate_date(value: str, field_name: str = "Date") -> str:
    try:
        parsed = datetime.strptime(value, "%Y-%m-%d").date()
    except (TypeError, ValueError) as exc:
        raise ValidationError(
            f"{field_name} must use YYYY-MM-DD format."
        ) from exc
    return parsed.isoformat()


def validate_email(email: str, required: bool = False) -> str | None:
    cleaned = (email or "").strip()

    if not cleaned:
        if required:
            raise ValidationError("Email is required.")
        return None

    if len(cleaned) > 254 or not EMAIL_PATTERN.fullmatch(cleaned):
        raise ValidationError("Enter a valid email address.")

    return cleaned.lower()


def validate_phone(phone: str, required: bool = False) -> str | None:
    cleaned = re.sub(r"[\s-]", "", phone or "")

    if not cleaned:
        if required:
            raise ValidationError("Phone number is required.")
        return None

    if not PHONE_PATTERN.fullmatch(cleaned):
        raise ValidationError(
            "Phone number must contain 9-15 digits and may start with +."
        )

    return cleaned


def validate_customer_code(value: str) -> str:
    cleaned = require_text(value, "Customer code").upper()

    if not CUSTOMER_CODE_PATTERN.fullmatch(cleaned):
        raise ValidationError(
            "Customer code must be 3-20 letters, numbers or hyphens."
        )

    return cleaned


def validate_national_id(value: str) -> str | None:
    cleaned = (value or "").strip().upper()

    if not cleaned:
        return None

    if not NATIONAL_ID_PATTERN.fullmatch(cleaned):
        raise ValidationError(
            "National ID must contain 5-30 letters, numbers, / or -."
        )

    return cleaned


def validate_username(username: str) -> str:
    cleaned = require_text(username, "Username")

    if not USERNAME_PATTERN.fullmatch(cleaned):
        raise ValidationError(
            "Username must be 3-30 characters using letters, numbers, dot, underscore or hyphen."
        )

    return cleaned


def validate_password(password: str) -> str:
    password = require_text(password, "Password")

    if len(password) < 8:
        raise ValidationError("Password must contain at least 8 characters.")
    if not re.search(r"[A-Z]", password):
        raise ValidationError("Password must contain at least one uppercase letter.")
    if not re.search(r"[a-z]", password):
        raise ValidationError("Password must contain at least one lowercase letter.")
    if not re.search(r"\d", password):
        raise ValidationError("Password must contain at least one number.")

    return password


def validate_interest_rate(value) -> float:
    try:
        rate = float(value)
    except (TypeError, ValueError) as exc:
        raise ValidationError("Interest rate must be a valid number.") from exc

    if rate < 0 or rate > 100:
        raise ValidationError("Interest rate must be between 0 and 100 percent.")

    return round(rate, 2)


def validate_loan_term(value, maximum: int = 60) -> int:
    try:
        term = int(value)
    except (TypeError, ValueError) as exc:
        raise ValidationError("Loan term must be a whole number of months.") from exc

    if term < 1 or term > maximum:
        raise ValidationError(
            f"Loan term must be between 1 and {maximum} months."
        )

    return term


def validate_reference_number(value: str) -> str:
    cleaned = require_text(value, "Reference number")

    if len(cleaned) < 4 or len(cleaned) > 50:
        raise ValidationError(
            "Reference number must contain between 4 and 50 characters."
        )

    return cleaned


def validate_not_future_date(value: date, field_name: str = "Date") -> date:
    if value > date.today():
        raise ValidationError(f"{field_name} cannot be in the future.")
    return value
