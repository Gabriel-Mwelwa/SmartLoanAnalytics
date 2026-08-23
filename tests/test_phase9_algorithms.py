"""Formal Phase 9 algorithm tests."""

from algorithms.eligibility_scoring import calculate_eligibility_score
from algorithms.repayment_schedule import (
    build_repayment_schedule,
    calculate_monthly_installment,
    calculate_total_payable,
)
from algorithms.risk_ranking import (
    calculate_risk_score,
    rank_loans_by_risk,
)


def test_eligibility_score_range_and_debt_effect():
    good = calculate_eligibility_score(10000, 5000, 12, 0)
    more_debt = calculate_eligibility_score(10000, 5000, 12, 10000)

    assert 0 <= good <= 100
    assert 0 <= more_debt <= 100
    assert more_debt < good


def test_repayment_schedule_has_one_row_per_month():
    schedule = build_repayment_schedule(12000, 12, 12)

    assert len(schedule) == 12
    assert schedule[0]["installment_number"] == 1
    assert schedule[-1]["installment_number"] == 12
    assert schedule[-1]["remaining_after_payment"] == 0.0


def test_repayment_total_and_installment_are_consistent():
    total = calculate_total_payable(12000, 12, 12)
    monthly = calculate_monthly_installment(12000, 12, 12)

    assert total == 13440.0
    assert monthly == 1120.0


def test_risk_score_increases_with_overdue_days():
    low = calculate_risk_score(5, 1000, 0)
    high = calculate_risk_score(30, 1000, 0)

    assert high > low


def test_manual_risk_ranking_orders_highest_first():
    records = [
        {
            "loan_id": 1,
            "overdue_days": 5,
            "outstanding_balance": 1000,
            "missed_payment_count": 0,
        },
        {
            "loan_id": 2,
            "overdue_days": 30,
            "outstanding_balance": 2000,
            "missed_payment_count": 1,
        },
        {
            "loan_id": 3,
            "overdue_days": 10,
            "outstanding_balance": 5000,
            "missed_payment_count": 0,
        },
    ]

    ranked = rank_loans_by_risk(records)

    assert ranked[0]["loan_id"] == 2
    assert ranked[0]["risk_score"] >= ranked[1]["risk_score"]
    assert ranked[1]["risk_score"] >= ranked[2]["risk_score"]


def test_risk_ranking_empty_input():
    assert rank_loans_by_risk([]) == []
