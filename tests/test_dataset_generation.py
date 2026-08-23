"""Phase 8 dataset-generation tests."""

import csv
import random

from tools.generate_dataset import (
    CUSTOMER_COUNT,
    LOAN_COUNT,
    dataset_summary,
    export_dataset_csv,
    generate_customers,
    generate_loans,
)


def test_generator_record_counts():
    rng = random.Random(2410856)
    customers = generate_customers(rng)
    loans = generate_loans(rng, customers)

    assert len(customers) == CUSTOMER_COUNT == 220
    assert len(loans) == LOAN_COUNT == 650
    assert LOAN_COUNT >= 500


def test_generated_loan_dates_are_consistent():
    rng = random.Random(2410856)
    customers = generate_customers(rng)
    loans = generate_loans(rng, customers)

    for loan in loans:
        if loan["approval_date"]:
            assert loan["approval_date"] >= loan["application_date"]
        if loan["disbursement_date"]:
            assert loan["disbursement_date"] >= loan["approval_date"]
        if loan["due_date"]:
            assert loan["due_date"] > loan["disbursement_date"]


def test_populated_dataset_meets_assignment_requirement():
    summary = dataset_summary()
    assert summary["loans"] >= 500
    assert summary["customers"] >= 100


def test_csv_export_has_500_plus_rows(tmp_path):
    path = export_dataset_csv(tmp_path / "loans.csv")

    with path.open(encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    assert len(rows) >= 500
    assert {
        "loan_id",
        "customer_code",
        "principal",
        "status",
        "eligibility_score",
        "total_repaid",
    }.issubset(rows[0].keys())
