"""Generate a reproducible 500+ record synthetic loan dataset for SmartLoan Analytics."""

from __future__ import annotations

import csv
import random
from datetime import date, timedelta
from pathlib import Path

from algorithms.eligibility_scoring import calculate_eligibility_score
from algorithms.repayment_schedule import calculate_total_payable
from config import DATA_DIR, DEFAULT_ANNUAL_INTEREST_RATE
from database import get_connection, initialize_database

RANDOM_SEED = 2410856
CUSTOMER_COUNT = 220
LOAN_COUNT = 650

FIRST_NAMES = [
    "Chola", "Sibamba", "Eunice", "Caroline", "Gabriel", "Adrian",
    "Grace", "Brian", "Natasha", "Peter", "Memory", "Kelvin", "Mercy",
    "Ruth", "Joshua", "Thandiwe", "Victor", "Agnes", "James", "Lillian",
]

LAST_NAMES = [
    "Chilufya", "Mumbula", "Kunda", "Musonda", "Mwelwa", "Mumba",
    "Phiri", "Banda", "Mulenga", "Tembo", "Zulu", "Lungu", "Chanda",
    "Mwila", "Kabwe", "Sakala", "Ngoma", "Mbewe", "Mutale", "Nyirenda",
]

EMPLOYMENT = [
    "Employed",
    "Self-Employed",
    "Business Owner",
    "Student",
    "Unemployed",
    "Retired",
    "Other",
]

PURPOSES = [
    "Business expansion",
    "School fees",
    "Medical expenses",
    "House renovation",
    "Farm inputs",
    "Emergency needs",
    "Vehicle repair",
    "Equipment purchase",
    "Working capital",
    "Personal development",
]


def generate_customers(rng: random.Random) -> list[dict]:
    customers = []
    for index in range(1, CUSTOMER_COUNT + 1):
        first = rng.choice(FIRST_NAMES)
        last = rng.choice(LAST_NAMES)
        employment = rng.choice(EMPLOYMENT)

        if employment in {"Employed", "Self-Employed", "Business Owner"}:
            income = rng.randint(2500, 25000)
        elif employment == "Retired":
            income = rng.randint(1200, 8000)
        else:
            income = rng.randint(0, 5000)

        customers.append(
            {
                "customer_code": f"CUS-{index:04d}",
                "full_name": f"{first} {last}",
                "national_id": f"NRC/{100000 + index}/{index % 99 + 1}",
                "phone": f"+26097{index:07d}"[:13],
                "email": f"customer{index:04d}@smartloan.local",
                "address": rng.choice(
                    ["Lusaka", "Ndola", "Kitwe", "Kabwe", "Solwezi", "Chingola"]
                ),
                "employment_status": employment,
                "monthly_income": income,
                "status": "Suspended" if index % 43 == 0 else "Active",
            }
        )

    return customers


def generate_loans(rng: random.Random, customers: list[dict]) -> list[dict]:
    records = []
    today = date.today()
    start = today - timedelta(days=340)

    for index in range(1, LOAN_COUNT + 1):
        customer_id = rng.randint(1, CUSTOMER_COUNT)
        customer = customers[customer_id - 1]

        principal = rng.randrange(500, 30001, 100)
        rate = rng.choice([10.0, 12.0, 15.0, 18.0, 20.0, 24.0])
        term = rng.choice([3, 6, 9, 12, 18, 24, 36])
        application_date = start + timedelta(days=rng.randint(0, 320))

        score = calculate_eligibility_score(
            float(customer["monthly_income"]),
            float(principal),
            term,
            0.0,
        )

        if customer["status"] == "Suspended":
            status = "Rejected"
        elif score >= 60:
            status = rng.choices(
                ["Disbursed", "Completed", "Overdue", "Approved", "Pending"],
                weights=[35, 22, 15, 8, 20],
                k=1,
            )[0]
        else:
            status = rng.choices(
                ["Rejected", "Pending", "Approved"],
                weights=[60, 30, 10],
                k=1,
            )[0]

        approval_date = None
        disbursement_date = None
        due_date = None

        if status in {"Approved", "Disbursed", "Completed", "Overdue"}:
            approval_date = application_date + timedelta(days=rng.randint(1, 7))

        if status in {"Disbursed", "Completed", "Overdue"}:
            disbursement_date = approval_date + timedelta(days=rng.randint(0, 4))
            due_date = disbursement_date + timedelta(days=term * 30)

            if status == "Overdue":
                # Force a logically consistent historical timeline whose due date is before today.
                overdue_days = rng.randint(10, 120)
                due_date = today - timedelta(days=overdue_days)
                disbursement_date = due_date - timedelta(days=term * 30)
                approval_date = disbursement_date - timedelta(days=rng.randint(1, 4))
                application_date = approval_date - timedelta(days=rng.randint(1, 7))

        records.append(
            {
                "customer_id": customer_id,
                "principal": float(principal),
                "annual_interest_rate": rate,
                "term_months": term,
                "application_date": application_date.isoformat(),
                "approval_date": approval_date.isoformat() if approval_date else None,
                "disbursement_date": (
                    disbursement_date.isoformat() if disbursement_date else None
                ),
                "due_date": due_date.isoformat() if due_date else None,
                "status": status,
                "eligibility_score": score,
                "purpose": rng.choice(PURPOSES),
            }
        )

    return records


def reset_generated_data() -> None:
    """Remove synthetic operational data while preserving users."""
    with get_connection() as connection:
        connection.execute("DELETE FROM repayments")
        connection.execute("DELETE FROM penalties")
        connection.execute("DELETE FROM loans")
        connection.execute("DELETE FROM customers")
        connection.execute(
            "DELETE FROM sqlite_sequence WHERE name IN ('customers','loans','repayments','penalties')"
        )


def populate_database(seed: int = RANDOM_SEED) -> dict[str, int]:
    initialize_database()
    rng = random.Random(seed)

    customers = generate_customers(rng)
    loans = generate_loans(rng, customers)

    reset_generated_data()

    with get_connection() as connection:
        connection.executemany(
            """
            INSERT INTO customers
            (
                customer_code, full_name, national_id, phone, email,
                address, employment_status, monthly_income, status
            )
            VALUES
            (
                :customer_code, :full_name, :national_id, :phone, :email,
                :address, :employment_status, :monthly_income, :status
            )
            """,
            customers,
        )

        for record in loans:
            cursor = connection.execute(
                """
                INSERT INTO loans
                (
                    customer_id, principal, annual_interest_rate, term_months,
                    application_date, approval_date, disbursement_date, due_date,
                    status, eligibility_score, purpose
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record["customer_id"],
                    record["principal"],
                    record["annual_interest_rate"],
                    record["term_months"],
                    record["application_date"],
                    record["approval_date"],
                    record["disbursement_date"],
                    record["due_date"],
                    record["status"],
                    record["eligibility_score"],
                    record["purpose"],
                ),
            )

            loan_id = cursor.lastrowid

            if record["status"] in {"Disbursed", "Completed", "Overdue"}:
                total = calculate_total_payable(
                    record["principal"],
                    record["annual_interest_rate"],
                    record["term_months"],
                )

                if record["status"] == "Completed":
                    repayments = rng.randint(2, 6)
                    remaining = total
                    for payment_number in range(1, repayments + 1):
                        amount = round(
                            remaining / (repayments - payment_number + 1),
                            2,
                        )
                        if payment_number == repayments:
                            amount = round(remaining, 2)
                        remaining = round(max(0.0, remaining - amount), 2)
                        pay_date = date.fromisoformat(record["disbursement_date"]) + timedelta(
                            days=payment_number * max(10, record["term_months"] * 30 // repayments)
                        )
                        connection.execute(
                            """
                            INSERT INTO repayments
                            (
                                loan_id, payment_date, amount,
                                payment_method, reference_number
                            )
                            VALUES (?, ?, ?, ?, ?)
                            """,
                            (
                                loan_id,
                                pay_date.isoformat(),
                                amount,
                                rng.choice(["Cash", "Bank Transfer", "Mobile Money"]),
                                f"PAY-{loan_id:04d}-{payment_number:02d}",
                            ),
                        )

                elif record["status"] == "Disbursed":
                    repaid = round(total * rng.uniform(0.05, 0.75), 2)
                    if repaid > 0:
                        connection.execute(
                            """
                            INSERT INTO repayments
                            (
                                loan_id, payment_date, amount,
                                payment_method, reference_number
                            )
                            VALUES (?, ?, ?, ?, ?)
                            """,
                            (
                                loan_id,
                                (
                                    date.fromisoformat(record["disbursement_date"])
                                    + timedelta(days=rng.randint(7, 120))
                                ).isoformat(),
                                repaid,
                                rng.choice(["Cash", "Bank Transfer", "Mobile Money"]),
                                f"PAY-{loan_id:04d}-01",
                            ),
                        )

                elif record["status"] == "Overdue":
                    repaid = round(total * rng.uniform(0.0, 0.55), 2)
                    if repaid > 0:
                        connection.execute(
                            """
                            INSERT INTO repayments
                            (
                                loan_id, payment_date, amount,
                                payment_method, reference_number
                            )
                            VALUES (?, ?, ?, ?, ?)
                            """,
                            (
                                loan_id,
                                (
                                    date.fromisoformat(record["disbursement_date"])
                                    + timedelta(days=rng.randint(10, max(11, record["term_months"] * 20)))
                                ).isoformat(),
                                repaid,
                                rng.choice(["Cash", "Bank Transfer", "Mobile Money"]),
                                f"PAY-{loan_id:04d}-01",
                            ),
                        )

                    outstanding = max(0.0, total - repaid)
                    penalty = round(outstanding * 0.02, 2)
                    if penalty > 0:
                        connection.execute(
                            """
                            INSERT INTO penalties
                            (loan_id, amount, reason, paid)
                            VALUES (?, ?, 'Overdue loan penalty', ?)
                            """,
                            (loan_id, penalty, 1 if rng.random() < 0.25 else 0),
                        )

    return {
        "customers": len(customers),
        "loans": len(loans),
    }


def export_dataset_csv(path: Path | None = None) -> Path:
    target = path or (DATA_DIR / "loan_dataset_650_records.csv")
    target.parent.mkdir(parents=True, exist_ok=True)

    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT
                l.loan_id,
                c.customer_code,
                c.full_name AS customer_name,
                c.employment_status,
                c.monthly_income,
                l.principal,
                l.annual_interest_rate,
                l.term_months,
                l.application_date,
                l.approval_date,
                l.disbursement_date,
                l.due_date,
                l.status,
                l.eligibility_score,
                l.purpose,
                COALESCE((
                    SELECT SUM(r.amount)
                    FROM repayments r
                    WHERE r.loan_id=l.loan_id
                ),0) AS total_repaid,
                COALESCE((
                    SELECT SUM(p.amount)
                    FROM penalties p
                    WHERE p.loan_id=l.loan_id AND p.paid=0
                ),0) AS outstanding_penalties
            FROM loans l
            JOIN customers c ON c.customer_id=l.customer_id
            ORDER BY l.loan_id
            """
        ).fetchall()

    fields = list(rows[0].keys()) if rows else []

    with target.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow(dict(row))

    return target


def dataset_summary() -> dict:
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT
                (SELECT COUNT(*) FROM customers) AS customers,
                (SELECT COUNT(*) FROM loans) AS loans,
                (SELECT COUNT(*) FROM repayments) AS repayments,
                (SELECT COUNT(*) FROM penalties) AS penalties,
                (SELECT COUNT(*) FROM loans WHERE status='Pending') AS pending,
                (SELECT COUNT(*) FROM loans WHERE status='Approved') AS approved,
                (SELECT COUNT(*) FROM loans WHERE status='Rejected') AS rejected,
                (SELECT COUNT(*) FROM loans WHERE status='Disbursed') AS disbursed,
                (SELECT COUNT(*) FROM loans WHERE status='Completed') AS completed,
                (SELECT COUNT(*) FROM loans WHERE status='Overdue') AS overdue
            """
        ).fetchone()
    return dict(row)


def main() -> None:
    counts = populate_database()
    path = export_dataset_csv()
    summary = dataset_summary()

    print("SmartLoan synthetic dataset generated successfully.")
    print("Inserted:", counts)
    print("Summary:", summary)
    print("CSV:", path)


if __name__ == "__main__":
    main()
