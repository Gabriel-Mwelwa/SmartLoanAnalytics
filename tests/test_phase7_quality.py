"""Phase 7 quality tests."""

import logging
import sqlite3
from datetime import date, timedelta

import pytest

from utils.error_handler import user_friendly_message
from utils.exceptions import ValidationError
from utils.validation import (
    validate_customer_code,
    validate_email,
    validate_interest_rate,
    validate_loan_term,
    validate_password,
    validate_phone,
    validate_reference_number,
    validate_username,
)


def test_valid_advanced_validation_rules():
    assert validate_username("loan.officer") == "loan.officer"
    assert validate_email("USER@example.com") == "user@example.com"
    assert validate_phone("+260 97-1234567") == "+260971234567"
    assert validate_customer_code("cus-001") == "CUS-001"
    assert validate_interest_rate("18") == 18.0
    assert validate_loan_term("12", 60) == 12
    assert validate_reference_number("REF-001") == "REF-001"


@pytest.mark.parametrize(
    "call",
    [
        lambda: validate_username("!"),
        lambda: validate_email("not-an-email"),
        lambda: validate_phone("123"),
        lambda: validate_customer_code("x"),
        lambda: validate_interest_rate(101),
        lambda: validate_loan_term(0, 60),
        lambda: validate_password("weakpass"),
        lambda: validate_reference_number("a"),
    ],
)
def test_invalid_data_rejected(call):
    with pytest.raises(ValidationError):
        call()


def test_database_error_message_hides_sql_detail():
    exc = sqlite3.OperationalError("no such table: secret_internal_table")
    message = user_friendly_message(exc)
    assert "database error" in message.lower()
    assert "secret_internal_table" not in message


def test_validation_error_message_is_preserved():
    exc = ValidationError("Loan term is invalid.")
    assert user_friendly_message(exc) == "Loan term is invalid."
