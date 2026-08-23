"""PDF and CSV reporting services for SmartLoan Analytics."""

from __future__ import annotations

import csv
import logging
from datetime import datetime
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    Image,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from config import REPORT_DIR
from database import get_connection
from modules.analytics import (
    export_all_charts,
    get_dashboard_kpis,
    get_monthly_application_trend,
    get_monthly_repayment_trend,
    get_overdue_risk_ranking,
    get_recommendations,
    get_status_distribution,
    get_summary_statistics,
    get_top_customers,
)

CSV_DIR = REPORT_DIR / "csv"
PDF_DIR = REPORT_DIR / "pdf"


def _timestamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def _ensure_dirs() -> None:
    CSV_DIR.mkdir(parents=True, exist_ok=True)
    PDF_DIR.mkdir(parents=True, exist_ok=True)


def _audit(user_id: int | None, action: str, details: str) -> None:
    try:
        with get_connection() as connection:
            safe_user_id = user_id
            if user_id is not None:
                exists = connection.execute(
                    "SELECT 1 FROM users WHERE user_id=?", (user_id,)
                ).fetchone()
                if exists is None:
                    safe_user_id = None
            connection.execute(
                "INSERT INTO audit_logs (user_id, action, details) VALUES (?, ?, ?)",
                (safe_user_id, action, details),
            )
    except Exception:
        logging.exception("Unable to write report audit event.")


def export_management_csv(user_id: int | None = None) -> Path:
    """Export management KPIs, rankings and recommendations to one CSV."""
    _ensure_dirs()
    path = CSV_DIR / f"smartloan_management_report_{_timestamp()}.csv"

    kpis = get_dashboard_kpis()
    stats = get_summary_statistics()
    statuses = get_status_distribution()
    customers = get_top_customers()
    risks = get_overdue_risk_ranking()
    recommendations = get_recommendations()

    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)

        writer.writerow(["SmartLoan Analytics Management Report"])
        writer.writerow(["Generated", datetime.now().strftime("%Y-%m-%d %H:%M")])
        writer.writerow([])

        writer.writerow(["KEY PERFORMANCE INDICATORS"])
        writer.writerow(["Metric", "Value"])
        labels = {
            "total_customers": "Total customers",
            "active_customers": "Active customers",
            "total_loans": "Total loans",
            "pending_loans": "Pending loans",
            "approved_loans": "Approved loans",
            "rejected_loans": "Rejected loans",
            "disbursed_loans": "Disbursed loans",
            "completed_loans": "Completed loans",
            "overdue_loans": "Overdue loans",
            "approval_rate": "Approval rate (%)",
            "approved_principal": "Approved principal (K)",
            "total_repayments": "Total repayments (K)",
            "outstanding_portfolio": "Outstanding portfolio (K)",
            "outstanding_penalties": "Outstanding penalties (K)",
        }

        for key, label in labels.items():
            writer.writerow([label, kpis[key]])

        writer.writerow([])
        writer.writerow(["SUMMARY STATISTICS"])
        writer.writerow(["Metric", "Value"])
        for key, value in stats.items():
            writer.writerow([key.replace("_", " ").title(), value])

        writer.writerow([])
        writer.writerow(["LOAN STATUS DISTRIBUTION"])
        writer.writerow(["Status", "Total"])
        for row in statuses:
            writer.writerow([row["status"], row["total"]])

        writer.writerow([])
        writer.writerow(["TOP CUSTOMERS"])
        writer.writerow(["Customer Code", "Customer", "Loans", "Total Principal"])
        for row in customers:
            writer.writerow([
                row["customer_code"],
                row["full_name"],
                row["loans"],
                row["total_principal"],
            ])

        writer.writerow([])
        writer.writerow(["OVERDUE RISK RANKING"])
        writer.writerow([
            "Loan ID",
            "Customer Code",
            "Customer",
            "Overdue Days",
            "Outstanding Balance",
            "Risk Score",
        ])
        for row in risks:
            writer.writerow([
                row["loan_id"],
                row["customer_code"],
                row["customer_name"],
                row["overdue_days"],
                row["outstanding_balance"],
                row["risk_score"],
            ])

        writer.writerow([])
        writer.writerow(["MANAGEMENT RECOMMENDATIONS"])
        for index, recommendation in enumerate(recommendations, start=1):
            writer.writerow([index, recommendation])

    _audit(user_id, "MANAGEMENT_CSV_EXPORTED", path.name)
    logging.info("Management CSV report generated: %s", path)
    return path


def export_loan_records_csv(user_id: int | None = None) -> Path:
    """Export detailed loan records joined with customer information."""
    _ensure_dirs()
    path = CSV_DIR / f"loan_records_{_timestamp()}.csv"

    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT
                l.loan_id,
                c.customer_code,
                c.full_name AS customer_name,
                l.principal,
                l.annual_interest_rate,
                l.term_months,
                l.application_date,
                l.approval_date,
                l.disbursement_date,
                l.due_date,
                l.status,
                l.eligibility_score,
                l.purpose
            FROM loans l
            JOIN customers c ON c.customer_id=l.customer_id
            ORDER BY l.loan_id DESC
            """
        ).fetchall()

    fields = [
        "loan_id",
        "customer_code",
        "customer_name",
        "principal",
        "annual_interest_rate",
        "term_months",
        "application_date",
        "approval_date",
        "disbursement_date",
        "due_date",
        "status",
        "eligibility_score",
        "purpose",
    ]

    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow(dict(row))

    _audit(user_id, "LOAN_CSV_EXPORTED", path.name)
    logging.info("Loan CSV report generated: %s", path)
    return path


def export_repayment_records_csv(user_id: int | None = None) -> Path:
    """Export detailed repayment records."""
    _ensure_dirs()
    path = CSV_DIR / f"repayment_records_{_timestamp()}.csv"

    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT
                r.repayment_id,
                r.loan_id,
                c.customer_code,
                c.full_name AS customer_name,
                r.payment_date,
                r.amount,
                r.payment_method,
                r.reference_number
            FROM repayments r
            JOIN loans l ON l.loan_id=r.loan_id
            JOIN customers c ON c.customer_id=l.customer_id
            ORDER BY r.repayment_id DESC
            """
        ).fetchall()

    fields = [
        "repayment_id",
        "loan_id",
        "customer_code",
        "customer_name",
        "payment_date",
        "amount",
        "payment_method",
        "reference_number",
    ]

    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow(dict(row))

    _audit(user_id, "REPAYMENT_CSV_EXPORTED", path.name)
    logging.info("Repayment CSV report generated: %s", path)
    return path


def _styled_table(data, widths=None):
    table = Table(data, colWidths=widths, repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E7E7E7")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.35, colors.grey),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    return table


def export_management_pdf(user_id: int | None = None) -> Path:
    """Generate a management PDF containing KPIs, charts, rankings and recommendations."""
    _ensure_dirs()
    path = PDF_DIR / f"smartloan_management_report_{_timestamp()}.pdf"
    chart_dir = PDF_DIR / "charts"
    chart_paths = export_all_charts(chart_dir)

    kpis = get_dashboard_kpis()
    stats = get_summary_statistics()
    statuses = get_status_distribution()
    customers = get_top_customers()
    risks = get_overdue_risk_ranking()
    recommendations = get_recommendations()

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "TitleCenter",
        parent=styles["Title"],
        alignment=TA_CENTER,
        fontSize=20,
        spaceAfter=8,
    )
    section_style = ParagraphStyle(
        "Section",
        parent=styles["Heading2"],
        fontSize=13,
        spaceBefore=10,
        spaceAfter=6,
    )
    body = styles["BodyText"]

    doc = SimpleDocTemplate(
        str(path),
        pagesize=A4,
        leftMargin=16 * mm,
        rightMargin=16 * mm,
        topMargin=15 * mm,
        bottomMargin=15 * mm,
        title="SmartLoan Analytics Management Report",
        author="SmartLoan Analytics",
    )

    story = [
        Paragraph("SmartLoan Analytics", title_style),
        Paragraph("Loan Portfolio Management & Analytics Report", styles["Heading2"]),
        Paragraph(
            f"Generated: {datetime.now().strftime('%d %B %Y at %H:%M')}",
            body,
        ),
        Spacer(1, 8),
        Paragraph(
            "This report summarizes loan applications, portfolio exposure, repayment "
            "performance, overdue risk and management recommendations.",
            body,
        ),
        Spacer(1, 10),
        Paragraph("1. Key Performance Indicators", section_style),
    ]

    kpi_data = [
        ["Metric", "Value"],
        ["Total customers", kpis["total_customers"]],
        ["Active customers", kpis["active_customers"]],
        ["Total loans", kpis["total_loans"]],
        ["Pending loans", kpis["pending_loans"]],
        ["Approved loans", kpis["approved_loans"]],
        ["Rejected loans", kpis["rejected_loans"]],
        ["Disbursed loans", kpis["disbursed_loans"]],
        ["Completed loans", kpis["completed_loans"]],
        ["Overdue loans", kpis["overdue_loans"]],
        ["Approval rate", f'{kpis["approval_rate"]}%'],
        ["Approved principal", f'K{kpis["approved_principal"]:,.2f}'],
        ["Repayments collected", f'K{kpis["total_repayments"]:,.2f}'],
        ["Outstanding portfolio", f'K{kpis["outstanding_portfolio"]:,.2f}'],
        ["Outstanding penalties", f'K{kpis["outstanding_penalties"]:,.2f}'],
    ]
    story += [_styled_table(kpi_data, [75 * mm, 85 * mm]), Spacer(1, 10)]

    story.append(Paragraph("2. Summary Statistics", section_style))
    stat_data = [["Metric", "Value"]] + [
        [key.replace("_", " ").title(), value] for key, value in stats.items()
    ]
    story += [_styled_table(stat_data, [80 * mm, 80 * mm]), Spacer(1, 10)]

    story.append(Paragraph("3. Loan Status Distribution", section_style))
    status_data = [["Status", "Total"]] + [
        [row["status"], row["total"]] for row in statuses
    ]
    story += [_styled_table(status_data, [100 * mm, 60 * mm]), Spacer(1, 10)]

    story.append(Paragraph("4. Analytics Visualizations", section_style))
    for chart_path in chart_paths:
        story.append(Image(str(chart_path), width=165 * mm, height=95 * mm))
        story.append(Spacer(1, 8))

    story.append(PageBreak())
    story.append(Paragraph("5. Top Customers", section_style))
    customer_data = [["Code", "Customer", "Loans", "Total Principal"]]
    for row in customers:
        customer_data.append(
            [
                row["customer_code"],
                Paragraph(str(row["full_name"]), body),
                row["loans"],
                f'K{float(row["total_principal"]):,.2f}',
            ]
        )
    if len(customer_data) == 1:
        customer_data.append(["-", "No loan data", "-", "-"])
    story += [
        _styled_table(customer_data, [30 * mm, 65 * mm, 25 * mm, 40 * mm]),
        Spacer(1, 10),
    ]

    story.append(Paragraph("6. Overdue Risk Ranking", section_style))
    risk_data = [
        ["Loan", "Customer", "Days Overdue", "Outstanding", "Risk Score"]
    ]
    for row in risks:
        risk_data.append(
            [
                row["loan_id"],
                row["customer_code"],
                row["overdue_days"],
                f'K{row["outstanding_balance"]:,.2f}',
                row["risk_score"],
            ]
        )
    if len(risk_data) == 1:
        risk_data.append(["-", "No overdue loans", "-", "-", "-"])
    story += [
        _styled_table(risk_data, [22 * mm, 35 * mm, 30 * mm, 42 * mm, 28 * mm]),
        Spacer(1, 10),
    ]

    story.append(Paragraph("7. Management Recommendations", section_style))
    for index, recommendation in enumerate(recommendations, start=1):
        story.append(Paragraph(f"{index}. {recommendation}", body))
        story.append(Spacer(1, 5))

    story.append(Paragraph("8. Visualization Justification", section_style))
    story.append(
        Paragraph(
            "The loan-status bar chart compares discrete loan states. The monthly "
            "application line chart shows changes over time. The repayment bar chart "
            "compares monthly collection amounts. The horizontal customer-ranking chart "
            "supports easy comparison of portfolio concentration by customer.",
            body,
        )
    )

    doc.build(story)

    _audit(user_id, "MANAGEMENT_PDF_EXPORTED", path.name)
    logging.info("Management PDF report generated: %s", path)
    return path
