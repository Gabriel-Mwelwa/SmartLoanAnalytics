"""Original Algorithm 3: loan risk scoring and ranking."""

from __future__ import annotations


def calculate_risk_score(
    overdue_days: int,
    outstanding_balance: float,
    missed_payment_count: int = 0,
) -> float:
    """Calculate one loan's risk score.

    Time complexity: O(1)
    Space complexity: O(1)
    """
    score = (
        max(0, overdue_days) * 2.0
        + max(0.0, outstanding_balance) / 1000.0
        + max(0, missed_payment_count) * 10.0
    )
    return round(score, 2)


def rank_loans_by_risk(records: list[dict]) -> list[dict]:
    """Rank loans from highest to lowest risk using manual selection sort.

    Each record must contain:
    - overdue_days
    - outstanding_balance
    - missed_payment_count (optional)

    Phase A: calculate one score for each of n records -> O(n)
    Phase B: selection sort the n records -> O(n^2)

    Overall time complexity: O(n^2)
    Space complexity: O(n), because a ranked working list is created.
    """
    ranked = []

    for record in records:
        item = dict(record)
        item["risk_score"] = calculate_risk_score(
            int(item.get("overdue_days", 0)),
            float(item.get("outstanding_balance", 0.0)),
            int(item.get("missed_payment_count", 0)),
        )
        ranked.append(item)

    # Manual selection sort: highest risk first.
    for i in range(len(ranked)):
        highest = i

        for j in range(i + 1, len(ranked)):
            if ranked[j]["risk_score"] > ranked[highest]["risk_score"]:
                highest = j

        ranked[i], ranked[highest] = ranked[highest], ranked[i]

    return ranked


def basic_risk_score(overdue_days: int, outstanding_balance: float) -> float:
    """Backward-compatible Phase 1 wrapper."""
    return calculate_risk_score(
        overdue_days,
        outstanding_balance,
        missed_payment_count=0,
    )
