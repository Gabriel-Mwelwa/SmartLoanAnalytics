from datetime import date, timedelta
import uuid

import pytest

from database import get_connection, initialize_database
from models.user import Administrator, LoanOfficer
from modules.authentication import Session
from modules.customer_management import add_customer, delete_customer
from modules.loan_management import (
    apply_for_loan,
    approve_loan,
    calculate_outstanding_balance,
    disburse_loan,
    get_loan,
    reject_loan,
)
from modules.repayment_management import (
    calculate_overdue_penalty,
    create_penalty_if_needed,
    record_repayment,
    refresh_overdue_loans,
)
from utils.exceptions import ValidationError


def admin_session():
    return Session(
        Administrator(
            user_id=None,
            full_name="Admin",
            username="adminx",
            email="adminx@test.local",
            role="Administrator",
        )
    )


def officer_session():
    return Session(
        LoanOfficer(
            user_id=None,
            full_name="Officer",
            username="officerx",
            email="officerx@test.local",
            role="Loan Officer",
        )
    )


def create_customer():
    return add_customer(
        admin_session(),
        "CUS-" + uuid.uuid4().hex[:8].upper(),
        "Loan Test Customer",
        "",
        "+260971234567",
        "",
        "Ndola",
        "Employed",
        10000,
        "Active",
    )


def test_loan_application_calculates_score():
    customer = create_customer()
    try:
        loan = apply_for_loan(
            officer_session(),
            customer.customer_id,
            5000,
            18,
            12,
            "Business expansion",
        )
        assert loan.status == "Pending"
        assert 0 <= loan.eligibility_score <= 100
    finally:
        with get_connection() as connection:
            connection.execute("DELETE FROM loans WHERE customer_id=?", (customer.customer_id,))
        delete_customer(admin_session(), customer.customer_id)


def test_approve_and_disburse_flow():
    customer = create_customer()
    try:
        loan = apply_for_loan(
            officer_session(),
            customer.customer_id,
            3000,
            12,
            6,
            "School fees",
        )
        approved = approve_loan(admin_session(), loan.loan_id)
        assert approved.status == "Approved"

        disbursed = disburse_loan(
            admin_session(),
            loan.loan_id,
            date.today() - timedelta(days=10),
        )
        assert disbursed.status == "Disbursed"
        assert disbursed.due_date is not None
    finally:
        with get_connection() as connection:
            connection.execute("DELETE FROM loans WHERE customer_id=?", (customer.customer_id,))
        delete_customer(admin_session(), customer.customer_id)


def test_reject_flow():
    customer = create_customer()
    try:
        loan = apply_for_loan(
            officer_session(),
            customer.customer_id,
            2500,
            10,
            6,
            "Emergency",
        )
        rejected = reject_loan(admin_session(), loan.loan_id)
        assert rejected.status == "Rejected"
    finally:
        with get_connection() as connection:
            connection.execute("DELETE FROM loans WHERE customer_id=?", (customer.customer_id,))
        delete_customer(admin_session(), customer.customer_id)


def test_repayment_reduces_balance():
    customer = create_customer()
    try:
        loan = apply_for_loan(
            officer_session(),
            customer.customer_id,
            1200,
            0,
            12,
            "Equipment",
        )
        approve_loan(admin_session(), loan.loan_id)
        disburse_loan(admin_session(), loan.loan_id)

        before = calculate_outstanding_balance(loan.loan_id)
        record_repayment(
            officer_session(),
            loan.loan_id,
            200,
            "Cash",
            "REF-" + uuid.uuid4().hex[:10],
        )
        after = calculate_outstanding_balance(loan.loan_id)
        assert after == before - 200
    finally:
        with get_connection() as connection:
            connection.execute("DELETE FROM repayments WHERE loan_id IN (SELECT loan_id FROM loans WHERE customer_id=?)", (customer.customer_id,))
            connection.execute("DELETE FROM penalties WHERE loan_id IN (SELECT loan_id FROM loans WHERE customer_id=?)", (customer.customer_id,))
            connection.execute("DELETE FROM loans WHERE customer_id=?", (customer.customer_id,))
        delete_customer(admin_session(), customer.customer_id)


def test_overdue_detection_and_penalty():
    customer = create_customer()
    try:
        loan = apply_for_loan(
            officer_session(),
            customer.customer_id,
            1000,
            0,
            1,
            "Short term need",
            application_date=date.today() - timedelta(days=50),
        )
        approve_loan(admin_session(), loan.loan_id, date.today() - timedelta(days=45))
        disburse_loan(admin_session(), loan.loan_id, date.today() - timedelta(days=40))

        changed = refresh_overdue_loans(date.today())
        assert changed >= 1
        assert get_loan(loan.loan_id).status == "Overdue"

        amount = calculate_overdue_penalty(loan.loan_id, date.today())
        assert amount > 0

        created = create_penalty_if_needed(
            officer_session(),
            loan.loan_id,
            date.today(),
        )
        assert created > 0
    finally:
        with get_connection() as connection:
            connection.execute("DELETE FROM repayments WHERE loan_id IN (SELECT loan_id FROM loans WHERE customer_id=?)", (customer.customer_id,))
            connection.execute("DELETE FROM penalties WHERE loan_id IN (SELECT loan_id FROM loans WHERE customer_id=?)", (customer.customer_id,))
            connection.execute("DELETE FROM loans WHERE customer_id=?", (customer.customer_id,))
        delete_customer(admin_session(), customer.customer_id)


def test_cannot_repay_pending_loan():
    customer = create_customer()
    try:
        loan = apply_for_loan(
            officer_session(),
            customer.customer_id,
            2000,
            10,
            12,
            "Pending test",
        )
        with pytest.raises(ValidationError):
            record_repayment(
                officer_session(),
                loan.loan_id,
                100,
                "Cash",
                "REF-" + uuid.uuid4().hex[:10],
            )
    finally:
        with get_connection() as connection:
            connection.execute("DELETE FROM loans WHERE customer_id=?", (customer.customer_id,))
        delete_customer(admin_session(), customer.customer_id)
