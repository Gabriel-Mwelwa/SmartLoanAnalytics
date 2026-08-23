from datetime import date, timedelta
import uuid

from database import get_connection
from models.user import Administrator, LoanOfficer
from modules.authentication import Session
from modules.customer_management import add_customer, delete_customer
from modules.loan_management import (
    apply_for_loan,
    approve_loan,
    disburse_loan,
)
from modules.repayment_management import record_repayment, refresh_overdue_loans
from modules.analytics import (
    export_all_charts,
    get_dashboard_kpis,
    get_monthly_application_trend,
    get_overdue_risk_ranking,
    get_recommendations,
    get_status_distribution,
    get_summary_statistics,
    get_top_customers,
)


def admin_session():
    return Session(
        Administrator(
            user_id=None,
            full_name="Analytics Admin",
            username="analyticsadmin",
            email="analyticsadmin@test.local",
            role="Administrator",
        )
    )


def officer_session():
    return Session(
        LoanOfficer(
            user_id=None,
            full_name="Analytics Officer",
            username="analyticsofficer",
            email="analyticsofficer@test.local",
            role="Loan Officer",
        )
    )


def create_customer():
    return add_customer(
        admin_session(),
        "AN-" + uuid.uuid4().hex[:8].upper(),
        "Analytics Customer",
        "",
        "+260971234567",
        "",
        "Lusaka",
        "Employed",
        15000,
        "Active",
    )


def cleanup_customer(customer_id):
    with get_connection() as connection:
        connection.execute(
            "DELETE FROM repayments WHERE loan_id IN (SELECT loan_id FROM loans WHERE customer_id=?)",
            (customer_id,),
        )
        connection.execute(
            "DELETE FROM penalties WHERE loan_id IN (SELECT loan_id FROM loans WHERE customer_id=?)",
            (customer_id,),
        )
        connection.execute("DELETE FROM loans WHERE customer_id=?", (customer_id,))
    delete_customer(admin_session(), customer_id)


def test_kpis_and_rankings_include_created_loan():
    customer = create_customer()
    try:
        loan = apply_for_loan(
            officer_session(),
            customer.customer_id,
            5000,
            18,
            12,
            "Analytics test",
        )
        kpis = get_dashboard_kpis()
        assert kpis["total_loans"] >= 1
        assert any(
            row["customer_code"] == customer.customer_code
            for row in get_top_customers(1000)
        )
        assert any(
            row["status"] == "Pending"
            for row in get_status_distribution()
        )
        assert len(get_monthly_application_trend()) >= 1
    finally:
        cleanup_customer(customer.customer_id)


def test_summary_and_recommendations_available():
    stats = get_summary_statistics()
    assert "average_principal" in stats
    recs = get_recommendations()
    assert len(recs) >= 1


def test_overdue_risk_ranking():
    customer = create_customer()
    try:
        loan = apply_for_loan(
            officer_session(),
            customer.customer_id,
            2000,
            0,
            1,
            "Risk test",
            application_date=date.today() - timedelta(days=60),
        )
        approve_loan(
            admin_session(),
            loan.loan_id,
            date.today() - timedelta(days=55),
        )
        disburse_loan(
            admin_session(),
            loan.loan_id,
            date.today() - timedelta(days=50),
        )
        refresh_overdue_loans(date.today())

        ranking = get_overdue_risk_ranking(100)
        assert any(row["loan_id"] == loan.loan_id for row in ranking)
    finally:
        cleanup_customer(customer.customer_id)


def test_chart_export(tmp_path):
    paths = export_all_charts(tmp_path)
    assert len(paths) == 4
    for path in paths:
        assert path.exists()
        assert path.stat().st_size > 0
