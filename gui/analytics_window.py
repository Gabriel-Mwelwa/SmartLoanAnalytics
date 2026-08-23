"""Analytics dashboard GUI for SmartLoan Analytics."""

import tkinter as tk
from tkinter import messagebox, ttk

from modules.analytics import (
    export_all_charts,
    get_dashboard_kpis,
    get_overdue_risk_ranking,
    get_recommendations,
    get_summary_statistics,
    get_top_customers,
)


class AnalyticsWindow(tk.Toplevel):
    def __init__(self, master, session):
        super().__init__(master)
        self.session = session
        self.title("SmartLoan Analytics - Analytics Dashboard")
        self.geometry("1100x720")
        self.minsize(980, 620)
        self._build()
        self.refresh()

    def _build(self):
        header = ttk.Frame(self, padding=12)
        header.pack(fill="x")
        ttk.Label(
            header,
            text="Loan Analytics Dashboard",
            font=("Arial", 20, "bold"),
        ).pack(side="left")
        ttk.Button(
            header,
            text="Export Charts",
            command=self.export_charts,
        ).pack(side="right")

        self.kpi_frame = ttk.LabelFrame(
            self, text="Key Performance Indicators", padding=12
        )
        self.kpi_frame.pack(fill="x", padx=12, pady=(0, 10))

        body = ttk.Panedwindow(self, orient="horizontal")
        body.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        left = ttk.LabelFrame(body, text="Summary & Recommendations", padding=10)
        right = ttk.LabelFrame(body, text="Risk & Customer Rankings", padding=10)
        body.add(left, weight=1)
        body.add(right, weight=1)

        self.summary_text = tk.Text(left, wrap="word", height=24)
        self.summary_text.pack(fill="both", expand=True)

        self.rank_text = tk.Text(right, wrap="word", height=24)
        self.rank_text.pack(fill="both", expand=True)

        ttk.Button(
            self,
            text="Refresh Analytics",
            command=self.refresh,
        ).pack(pady=(0, 12))

    def refresh(self):
        kpis = get_dashboard_kpis()

        for widget in self.kpi_frame.winfo_children():
            widget.destroy()

        cards = [
            ("Customers", kpis["total_customers"]),
            ("Loans", kpis["total_loans"]),
            ("Pending", kpis["pending_loans"]),
            ("Overdue", kpis["overdue_loans"]),
            ("Approval Rate", f'{kpis["approval_rate"]}%'),
            ("Outstanding", f'K{kpis["outstanding_portfolio"]:,.2f}'),
            ("Repayments", f'K{kpis["total_repayments"]:,.2f}'),
            ("Penalties", f'K{kpis["outstanding_penalties"]:,.2f}'),
        ]

        for index, (label, value) in enumerate(cards):
            frame = ttk.Frame(self.kpi_frame, padding=8)
            frame.grid(row=index // 4, column=index % 4, sticky="nsew", padx=5, pady=5)
            ttk.Label(frame, text=label).pack()
            ttk.Label(frame, text=str(value), font=("Arial", 14, "bold")).pack()

        for col in range(4):
            self.kpi_frame.columnconfigure(col, weight=1)

        stats = get_summary_statistics()
        recs = get_recommendations()

        summary_lines = [
            "SUMMARY STATISTICS",
            f"Average principal: K{stats['average_principal']:,.2f}",
            f"Average interest rate: {stats['average_interest_rate']}%",
            f"Average loan term: {stats['average_term_months']} months",
            f"Average eligibility score: {stats['average_eligibility_score']}",
            f"Maximum principal: K{stats['maximum_principal']:,.2f}",
            "",
            "MANAGEMENT RECOMMENDATIONS",
        ]
        summary_lines += [f"{i}. {item}" for i, item in enumerate(recs, start=1)]

        self.summary_text.delete("1.0", "end")
        self.summary_text.insert("1.0", "\n".join(summary_lines))

        risk = get_overdue_risk_ranking()
        customers = get_top_customers()

        rank_lines = ["OVERDUE RISK RANKING"]
        if risk:
            for row in risk:
                rank_lines.append(
                    f"Loan {row['loan_id']} | {row['customer_code']} | "
                    f"{row['overdue_days']} days | K{row['outstanding_balance']:,.2f} | "
                    f"Risk {row['risk_score']}"
                )
        else:
            rank_lines.append("No overdue loans.")

        rank_lines += ["", "TOP CUSTOMERS BY PRINCIPAL"]
        if customers:
            for i, row in enumerate(customers, start=1):
                rank_lines.append(
                    f"{i}. {row['customer_code']} - {row['full_name']} | "
                    f"{row['loans']} loan(s) | K{float(row['total_principal']):,.2f}"
                )
        else:
            rank_lines.append("No loan data available.")

        self.rank_text.delete("1.0", "end")
        self.rank_text.insert("1.0", "\n".join(rank_lines))

    def export_charts(self):
        try:
            paths = export_all_charts()
        except Exception as exc:
            messagebox.showerror("Analytics", f"Unable to export charts.\n\n{exc}")
            return
        messagebox.showinfo(
            "Analytics",
            f"{len(paths)} chart(s) exported successfully to the charts folder.",
        )
