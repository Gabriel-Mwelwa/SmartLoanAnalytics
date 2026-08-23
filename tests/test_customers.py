import uuid

import pytest

from database import get_connection, initialize_database
from models.user import Administrator, LoanOfficer
from modules.authentication import Session
from modules.customer_management import (
    add_customer,
    delete_customer,
    get_customer,
    list_customers,
    update_customer,
)
from utils.exceptions import ValidationError


def admin_session():
    return Session(
        Administrator(
            user_id=None,
            full_name="Test Admin",
            username="testadmin",
            email="testadmin@test.local",
            role="Administrator",
        )
    )


def officer_session():
    return Session(
        LoanOfficer(
            user_id=None,
            full_name="Loan Officer",
            username="officer",
            email="officer@test.local",
            role="Loan Officer",
        )
    )


def unique_code():
    return "CUS-" + uuid.uuid4().hex[:8].upper()


def test_add_and_get_customer():
    initialize_database()
    code = unique_code()
    customer = add_customer(
        admin_session(),
        code,
        "Chola Chilufya",
        f"NRC/{uuid.uuid4().hex[:10].upper()}",
        "+260971234567",
        "chola@test.local",
        "Ndola",
        "Employed",
        8500,
        "Active",
    )
    loaded = get_customer(customer.customer_id)
    assert loaded is not None
    assert loaded.customer_code == code
    assert loaded.monthly_income == 8500


def test_duplicate_customer_code_rejected():
    code = unique_code()
    session = admin_session()

    first = add_customer(
        session,
        code,
        "Customer One",
        "",
        "",
        "",
        "",
        "Other",
        0,
        "Active",
    )

    try:
        with pytest.raises(ValidationError):
            add_customer(
                session,
                code,
                "Customer Two",
                "",
                "",
                "",
                "",
                "Other",
                0,
                "Active",
            )
    finally:
        delete_customer(session, first.customer_id)


def test_employed_customer_requires_income():
    with pytest.raises(ValidationError):
        add_customer(
            admin_session(),
            unique_code(),
            "Income Test",
            "",
            "",
            "",
            "",
            "Employed",
            0,
            "Active",
        )


def test_update_customer():
    session = admin_session()
    customer = add_customer(
        session,
        unique_code(),
        "Old Name",
        "",
        "",
        "",
        "",
        "Other",
        0,
        "Active",
    )

    updated = update_customer(
        session,
        customer.customer_id,
        customer.customer_code,
        "Updated Name",
        "",
        "",
        "",
        "",
        "Self-Employed",
        5000,
        "Active",
    )

    assert updated.full_name == "Updated Name"
    assert updated.monthly_income == 5000

    delete_customer(session, customer.customer_id)


def test_search_filter_sort():
    session = admin_session()
    code = unique_code()
    customer = add_customer(
        session,
        code,
        "Searchable Customer",
        "",
        "",
        "",
        "",
        "Business Owner",
        12000,
        "Active",
    )

    try:
        results = list_customers(
            query=code,
            status="Active",
            employment_status="Business Owner",
            sort_by="Highest Income",
        )
        assert any(item.customer_id == customer.customer_id for item in results)
    finally:
        delete_customer(session, customer.customer_id)


def test_loan_officer_cannot_delete_customer():
    session = admin_session()
    customer = add_customer(
        session,
        unique_code(),
        "Protected Customer",
        "",
        "",
        "",
        "",
        "Other",
        0,
        "Active",
    )

    try:
        with pytest.raises(PermissionError):
            delete_customer(officer_session(), customer.customer_id)
    finally:
        delete_customer(session, customer.customer_id)
