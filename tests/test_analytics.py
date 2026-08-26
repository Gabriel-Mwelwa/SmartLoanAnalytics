"""Analytics services for SmartLoan Analytics."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pandas as pd

# Use a non-interactive Matplotlib backend.
# This allows pytest, PDF reporting, and chart exports to work
# without requiring a Tkinter display/window.
import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt

from algorithms.risk_ranking import calculate_risk_score
from config import CHART_DIR
from database import get_connection
from modules.loan_management import calculate_outstanding_balance
from modules.repayment_management import refresh_overdue_loans


def get_dashboard_kpis() -> dict:
    """Return headline loan-management KPIs."""
    refresh_overdue_loans()

    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT
                (SELECT COUNT(*)
                 FROM customers) AS total_customers,

                (SELECT COUNT(*)
                 FROM customers
                 WHERE status = 'Active') AS active_customers,

                (SELECT COUNT(*)
                 FROM loans) AS total_loans,

                (SELECT COUNT(*)
                 FROM loans
                 WHERE status = 'Pending') AS pending_loans,

                (SELECT COUNT(*)
                 FROM loans
                 WHERE status = 'Approved') AS approved_loans,

                (SELECT COUNT(*)
                 FROM loans
                 WHERE status = 'Rejected') AS rejected_loans,

                (SELECT COUNT(*)
                 FROM loans
                 WHERE status = 'Disbursed') AS disbursed_loans,

                (SELECT COUNT(*)
                 FROM loans
                 WHERE status = 'Completed') AS completed_loans,

                (SELECT COUNT(*)
                 FROM loans
                 WHERE status = 'Overdue') AS overdue_loans,

                (
                    SELECT COALESCE(SUM(principal), 0)
                    FROM loans
                    WHERE status IN (
                        'Approved',
                        'Disbursed',
                        'Overdue',
                        'Completed'
                    )
                ) AS approved_principal,

                (
                    SELECT COALESCE(SUM(amount), 0)
                    FROM repayments
                ) AS total_repayments,

                (
                    SELECT COALESCE(SUM(amount), 0)
                    FROM penalties
                    WHERE paid = 0
                ) AS outstanding_penalties
            """
        ).fetchone()

    total_loans = int(row["total_loans"])

    approved_or_disbursed = (
        int(row["approved_loans"])
        + int(row["disbursed_loans"])
        + int(row["completed_loans"])
        + int(row["overdue_loans"])
    )

    approval_rate = (
        approved_or_disbursed / total_loans * 100
        if total_loans
        else 0.0
    )

    total_portfolio_outstanding = 0.0

    with get_connection() as connection:
        loan_ids = connection.execute(
            """
            SELECT loan_id
            FROM loans
            WHERE status IN ('Disbursed', 'Overdue')
            """
        ).fetchall()

    for item in loan_ids:
        total_portfolio_outstanding += calculate_outstanding_balance(
            item["loan_id"]
        )

    return {
        "total_customers": int(row["total_customers"]),
        "active_customers": int(row["active_customers"]),
        "total_loans": total_loans,
        "pending_loans": int(row["pending_loans"]),
        "approved_loans": int(row["approved_loans"]),
        "rejected_loans": int(row["rejected_loans"]),
        "disbursed_loans": int(row["disbursed_loans"]),
        "completed_loans": int(row["completed_loans"]),
        "overdue_loans": int(row["overdue_loans"]),
        "approval_rate": round(approval_rate, 1),
        "approved_principal": round(
            float(row["approved_principal"] or 0),
            2,
        ),
        "total_repayments": round(
            float(row["total_repayments"] or 0),
            2,
        ),
        "outstanding_penalties": round(
            float(row["outstanding_penalties"] or 0),
            2,
        ),
        "outstanding_portfolio": round(
            total_portfolio_outstanding,
            2,
        ),
    }


def get_status_distribution() -> list[dict]:
    """Return the number of loans grouped by status."""
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT
                status,
                COUNT(*) AS total
            FROM loans
            GROUP BY status
            ORDER BY total DESC
            """
        ).fetchall()

    return [dict(row) for row in rows]


def get_monthly_application_trend(
    limit: int = 12,
) -> list[dict]:
    """Return monthly loan application totals."""
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT
                substr(application_date, 1, 7) AS month,
                COUNT(*) AS applications
            FROM loans
            GROUP BY substr(application_date, 1, 7)
            ORDER BY month DESC
            LIMIT ?
            """,
            (max(1, int(limit)),),
        ).fetchall()

    return [dict(row) for row in reversed(rows)]


def get_monthly_repayment_trend(
    limit: int = 12,
) -> list[dict]:
    """Return monthly repayment collection totals."""
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT
                substr(payment_date, 1, 7) AS month,
                SUM(amount) AS repayments
            FROM repayments
            GROUP BY substr(payment_date, 1, 7)
            ORDER BY month DESC
            LIMIT ?
            """,
            (max(1, int(limit)),),
        ).fetchall()

    return [dict(row) for row in reversed(rows)]


def get_top_customers(
    limit: int = 10,
) -> list[dict]:
    """Rank customers by total principal applied for."""
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT
                c.customer_code,
                c.full_name,
                COUNT(l.loan_id) AS loans,
                COALESCE(SUM(l.principal), 0) AS total_principal
            FROM customers c
            LEFT JOIN loans l
                ON l.customer_id = c.customer_id
            GROUP BY c.customer_id
            HAVING COUNT(l.loan_id) > 0
            ORDER BY
                total_principal DESC,
                c.full_name ASC
            LIMIT ?
            """,
            (max(1, int(limit)),),
        ).fetchall()

    return [dict(row) for row in rows]


def get_overdue_risk_ranking(
    limit: int = 10,
) -> list[dict]:
    """Rank overdue loans by a transparent risk score."""
    today = date.today()

    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT
                l.loan_id,
                l.due_date,
                c.customer_code,
                c.full_name AS customer_name
            FROM loans l
            JOIN customers c
                ON c.customer_id = l.customer_id
            WHERE l.status = 'Overdue'
            ORDER BY l.loan_id
            """
        ).fetchall()

    ranked = []

    for row in rows:
        due = date.fromisoformat(row["due_date"])

        overdue_days = max(
            0,
            (today - due).days,
        )

        balance = calculate_outstanding_balance(
            row["loan_id"]
        )

        score = calculate_risk_score(
            overdue_days,
            balance,
            0,
        )

        ranked.append(
            {
                "loan_id": row["loan_id"],
                "customer_code": row["customer_code"],
                "customer_name": row["customer_name"],
                "overdue_days": overdue_days,
                "outstanding_balance": round(
                    balance,
                    2,
                ),
                "risk_score": score,
            }
        )

    # This sorting is for displaying the analytics ranking.
    # The project's original manual risk-ranking algorithm
    # remains documented separately for complexity analysis.
    ranked.sort(
        key=lambda item: item["risk_score"],
        reverse=True,
    )

    return ranked[: max(1, int(limit))]


def get_summary_statistics() -> dict:
    """Return statistical summaries for the current loan portfolio."""
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT
                principal,
                annual_interest_rate,
                term_months,
                eligibility_score
            FROM loans
            """
        ).fetchall()

    if not rows:
        return {
            "average_principal": 0.0,
            "average_interest_rate": 0.0,
            "average_term_months": 0.0,
            "average_eligibility_score": 0.0,
            "maximum_principal": 0.0,
        }

    df = pd.DataFrame(
        [dict(row) for row in rows]
    )

    return {
        "average_principal": round(
            float(df["principal"].mean()),
            2,
        ),
        "average_interest_rate": round(
            float(
                df["annual_interest_rate"].mean()
            ),
            2,
        ),
        "average_term_months": round(
            float(df["term_months"].mean()),
            1,
        ),
        "average_eligibility_score": round(
            float(
                df["eligibility_score"]
                .fillna(0)
                .mean()
            ),
            2,
        ),
        "maximum_principal": round(
            float(df["principal"].max()),
            2,
        ),
    }


def get_recommendations() -> list[str]:
    """Generate management recommendations from portfolio metrics."""
    kpis = get_dashboard_kpis()

    recommendations = []

    if kpis["overdue_loans"] > 0:
        recommendations.append(
            "Prioritize follow-up on overdue loans and review "
            "the highest-risk accounts."
        )

    if (
        kpis["approval_rate"] < 50
        and kpis["total_loans"] > 0
    ):
        recommendations.append(
            "Review application quality and eligibility criteria "
            "because the approval rate is below 50%."
        )

    if (
        kpis["outstanding_portfolio"]
        > kpis["total_repayments"] * 2
        and kpis["total_loans"] > 0
    ):
        recommendations.append(
            "Strengthen repayment monitoring because outstanding "
            "portfolio value is high relative to repayments collected."
        )

    if kpis["outstanding_penalties"] > 0:
        recommendations.append(
            "Follow up unpaid penalties and confirm whether "
            "penalty rules remain appropriate."
        )

    if not recommendations:
        recommendations.append(
            "Portfolio indicators are currently stable; continue "
            "routine monitoring and periodic review."
        )

    return recommendations


def chart_loan_status(
    path: Path | None = None,
) -> Path:
    """Generate the loan-status distribution chart."""
    data = get_status_distribution()

    target = (
        path
        or CHART_DIR / "loan_status_distribution.png"
    )

    target.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    labels = (
        [row["status"] for row in data]
        or ["No Data"]
    )

    values = (
        [row["total"] for row in data]
        or [1]
    )

    plt.figure(figsize=(8, 5))
    plt.bar(labels, values)

    plt.title(
        "Loan Status Distribution"
    )
    plt.xlabel(
        "Loan Status"
    )
    plt.ylabel(
        "Number of Loans"
    )

    plt.xticks(
        rotation=25
    )

    plt.tight_layout()
    plt.savefig(
        target,
        dpi=150,
        bbox_inches="tight",
    )
    plt.close()

    return target


def chart_monthly_applications(
    path: Path | None = None,
) -> Path:
    """Generate the monthly loan application trend chart."""
    data = get_monthly_application_trend()

    target = (
        path
        or CHART_DIR / "monthly_loan_applications.png"
    )

    target.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    months = (
        [row["month"] for row in data]
        or ["No Data"]
    )

    values = (
        [row["applications"] for row in data]
        or [0]
    )

    plt.figure(figsize=(8, 5))

    plt.plot(
        months,
        values,
        marker="o",
    )

    plt.title(
        "Monthly Loan Application Trend"
    )

    plt.xlabel(
        "Month"
    )

    plt.ylabel(
        "Applications"
    )

    plt.xticks(
        rotation=45
    )

    plt.tight_layout()

    plt.savefig(
        target,
        dpi=150,
        bbox_inches="tight",
    )

    plt.close()

    return target


def chart_monthly_repayments(
    path: Path | None = None,
) -> Path:
    """Generate the monthly repayment collection chart."""
    data = get_monthly_repayment_trend()

    target = (
        path
        or CHART_DIR / "monthly_repayments.png"
    )

    target.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    months = (
        [row["month"] for row in data]
        or ["No Data"]
    )

    values = (
        [
            float(
                row["repayments"] or 0
            )
            for row in data
        ]
        or [0]
    )

    plt.figure(figsize=(8, 5))

    plt.bar(
        months,
        values,
    )

    plt.title(
        "Monthly Repayment Collections"
    )

    plt.xlabel(
        "Month"
    )

    plt.ylabel(
        "Amount Collected (K)"
    )

    plt.xticks(
        rotation=45
    )

    plt.tight_layout()

    plt.savefig(
        target,
        dpi=150,
        bbox_inches="tight",
    )

    plt.close()

    return target


def chart_top_customers(
    path: Path | None = None,
) -> Path:
    """Generate the top-customer loan-principal chart."""
    data = get_top_customers()

    target = (
        path
        or CHART_DIR / "top_customers.png"
    )

    target.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    labels = (
        [
            row["customer_code"]
            for row in data
        ]
        or ["No Data"]
    )

    values = (
        [
            float(
                row["total_principal"] or 0
            )
            for row in data
        ]
        or [0]
    )

    plt.figure(figsize=(8, 5))

    plt.barh(
        labels,
        values,
    )

    plt.title(
        "Top Customers by Loan Principal"
    )

    plt.xlabel(
        "Total Principal (K)"
    )

    plt.ylabel(
        "Customer"
    )

    plt.tight_layout()

    plt.savefig(
        target,
        dpi=150,
        bbox_inches="tight",
    )

    plt.close()

    return target


def export_all_charts(
    directory: Path | None = None,
) -> list[Path]:
    """Generate and export all management analytics charts."""
    target = directory or CHART_DIR

    target.mkdir(
        parents=True,
        exist_ok=True,
    )

    return [
        chart_loan_status(
            target / "loan_status_distribution.png"
        ),
        chart_monthly_applications(
            target / "monthly_loan_applications.png"
        ),
        chart_monthly_repayments(
            target / "monthly_repayments.png"
        ),
        chart_top_customers(
            target / "top_customers.png"
        ),
    ]