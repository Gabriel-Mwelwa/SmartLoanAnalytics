"""Original Algorithm 1: loan eligibility scoring."""

from __future__ import annotations


def calculate_eligibility_score(
    monthly_income: float,
    requested_amount: float,
    term_months: int,
    existing_debt: float = 0.0,
) -> float:
    """Return a transparent eligibility score from 0 to 100.

    Steps:
    1. Reject invalid/non-positive inputs with score 0.
    2. Calculate requested-amount-to-income ratio.
    3. Calculate existing-debt-to-income ratio.
    4. Start at 100 and subtract penalties for high ratios and long terms.
    5. Clamp the result between 0 and 100.

    Time complexity: O(1)
    Space complexity: O(1)

    This is an academic rule-based model only, not a real regulated credit score.
    """
    if monthly_income <= 0 or requested_amount <= 0 or term_months <= 0:
        return 0.0

    amount_ratio = requested_amount / monthly_income
    debt_ratio = max(0.0, existing_debt) / monthly_income

    score = 100.0
    score -= min(55.0, amount_ratio * 8.0)
    score -= min(30.0, debt_ratio * 20.0)

    if term_months > 36:
        score -= 10.0
    elif term_months > 24:
        score -= 5.0

    return round(max(0.0, min(100.0, score)), 2)


def calculate_basic_eligibility_score(
    monthly_income: float,
    requested_amount: float,
) -> float:
    """Backward-compatible Phase 1 wrapper."""
    return calculate_eligibility_score(
        monthly_income,
        requested_amount,
        term_months=12,
        existing_debt=0.0,
    )
