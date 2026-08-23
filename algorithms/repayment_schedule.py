"""Original Algorithm 2: repayment schedule generation."""

from __future__ import annotations


def calculate_total_payable(
    principal: float,
    annual_interest_rate: float,
    term_months: int,
) -> float:
    """Calculate simple-interest total payable.

    Time complexity: O(1)
    Space complexity: O(1)
    """
    if principal <= 0 or annual_interest_rate < 0 or term_months <= 0:
        raise ValueError("Loan values must be valid and positive.")

    years = term_months / 12
    interest = principal * (annual_interest_rate / 100) * years
    return round(principal + interest, 2)


def calculate_monthly_installment(
    principal: float,
    annual_interest_rate: float,
    term_months: int,
) -> float:
    """Return equal monthly installment using the calculated total payable."""
    total = calculate_total_payable(
        principal,
        annual_interest_rate,
        term_months,
    )
    return round(total / term_months, 2)


def build_repayment_schedule(
    principal: float,
    annual_interest_rate: float,
    term_months: int,
) -> list[dict]:
    """Generate one installment entry for each month of the loan term.

    Let n = term_months.

    Time complexity: O(n)
    Space complexity: O(n), because n schedule rows are returned.
    """
    monthly = calculate_monthly_installment(
        principal,
        annual_interest_rate,
        term_months,
    )
    total = calculate_total_payable(
        principal,
        annual_interest_rate,
        term_months,
    )

    schedule = []
    remaining = total

    for month in range(1, term_months + 1):
        payment = monthly if month < term_months else round(remaining, 2)
        remaining = round(max(0.0, remaining - payment), 2)

        schedule.append(
            {
                "installment_number": month,
                "amount_due": payment,
                "remaining_after_payment": remaining,
            }
        )

    return schedule


def simple_monthly_payment(principal: float, term_months: int) -> float:
    """Backward-compatible Phase 1 equal-principal estimate."""
    if term_months <= 0:
        raise ValueError("Term months must be greater than zero.")
    return round(principal / term_months, 2)
