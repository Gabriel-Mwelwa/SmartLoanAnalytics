"""Reports and recommendations GUI for SmartLoan Analytics."""

import tkinter as tk
from tkinter import messagebox, ttk

from modules.analytics import get_recommendations
from modules.reports import (
    export_loan_records_csv,
    export_management_csv,
    export_management_pdf,
    export_repayment_records_csv,
)


class ReportsWindow(tk.Toplevel):
    def __init__(self, master, session):
        super().__init__(master)
        self.session = session
        self.title("SmartLoan Analytics - Reports")
        self.geometry("820x580")
        self.minsize(720, 520)
        self._build()
        self.refresh_recommendations()

    def _build(self):
        header = ttk.Frame(self, padding=14)
        header.pack(fill="x")
        ttk.Label(
            header,
            text="Reports & Management Recommendations",
            font=("Arial", 19, "bold"),
        ).pack(side="left")

        actions = ttk.LabelFrame(self, text="Generate / Export", padding=14)
        actions.pack(fill="x", padx=14, pady=(0, 12))

        ttk.Button(
            actions,
            text="Generate Management PDF",
            command=self.make_pdf,
        ).pack(fill="x", pady=4)

        ttk.Button(
            actions,
            text="Export Management CSV",
            command=self.make_management_csv,
        ).pack(fill="x", pady=4)

        ttk.Button(
            actions,
            text="Export Loan Records CSV",
            command=self.make_loan_csv,
        ).pack(fill="x", pady=4)

        ttk.Button(
            actions,
            text="Export Repayment Records CSV",
            command=self.make_repayment_csv,
        ).pack(fill="x", pady=4)

        rec = ttk.LabelFrame(
            self,
            text="Current Management Recommendations",
            padding=14,
        )
        rec.pack(fill="both", expand=True, padx=14, pady=(0, 14))

        self.text = tk.Text(rec, height=13, wrap="word")
        self.text.pack(fill="both", expand=True)

        ttk.Button(
            rec,
            text="Refresh Recommendations",
            command=self.refresh_recommendations,
        ).pack(anchor="e", pady=(8, 0))

    @property
    def user_id(self):
        return self.session.user.user_id

    def refresh_recommendations(self):
        recommendations = get_recommendations()
        content = "\n\n".join(
            f"{index}. {item}"
            for index, item in enumerate(recommendations, start=1)
        )
        self.text.configure(state="normal")
        self.text.delete("1.0", "end")
        self.text.insert("1.0", content)
        self.text.configure(state="disabled")

    def _success(self, title, path):
        messagebox.showinfo(
            title,
            f"Operation completed successfully.\n\nSaved to:\n{path}",
        )

    def make_pdf(self):
        try:
            path = export_management_pdf(self.user_id)
        except Exception as exc:
            messagebox.showerror("Reports", f"Unable to generate PDF.\n\n{exc}")
            return
        self._success("Management PDF", path)

    def make_management_csv(self):
        try:
            path = export_management_csv(self.user_id)
        except Exception as exc:
            messagebox.showerror("Reports", f"Unable to export CSV.\n\n{exc}")
            return
        self._success("Management CSV", path)

    def make_loan_csv(self):
        try:
            path = export_loan_records_csv(self.user_id)
        except Exception as exc:
            messagebox.showerror("Reports", f"Unable to export loan records.\n\n{exc}")
            return
        self._success("Loan CSV", path)

    def make_repayment_csv(self):
        try:
            path = export_repayment_records_csv(self.user_id)
        except Exception as exc:
            messagebox.showerror(
                "Reports",
                f"Unable to export repayment records.\n\n{exc}",
            )
            return
        self._success("Repayment CSV", path)
