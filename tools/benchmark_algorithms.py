"""Illustrative timing benchmark for SmartLoan algorithms."""

from __future__ import annotations

from random import Random
from time import perf_counter

from algorithms.eligibility_scoring import calculate_eligibility_score
from algorithms.repayment_schedule import build_repayment_schedule
from algorithms.risk_ranking import rank_loans_by_risk


def time_call(function, *args):
    start = perf_counter()
    function(*args)
    return perf_counter() - start


def main():
    rng = Random(42)

    print("SmartLoan algorithm benchmark")
    print("Timings are illustrative; Big O comes from code analysis.")
    print()

    for _ in range(3):
        elapsed = time_call(
            calculate_eligibility_score,
            10000,
            5000,
            12,
            1000,
        )
        print(f"Eligibility O(1): {elapsed:.8f}s")

    print()

    for months in (12, 24, 60):
        elapsed = time_call(
            build_repayment_schedule,
            10000,
            18,
            months,
        )
        print(f"Schedule n={months:>2}: {elapsed:.8f}s")

    print()

    for n in (50, 100, 250):
        records = [
            {
                "loan_id": i,
                "overdue_days": rng.randint(0, 180),
                "outstanding_balance": rng.randint(0, 50000),
                "missed_payment_count": rng.randint(0, 6),
            }
            for i in range(n)
        ]

        elapsed = time_call(rank_loans_by_risk, records)
        print(f"Risk ranking n={n:>3}: {elapsed:.8f}s")


if __name__ == "__main__":
    main()
