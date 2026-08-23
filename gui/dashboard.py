"""Role-aware dashboard for SmartLoan Analytics."""

import tkinter as tk
from tkinter import messagebox, ttk

from gui.registration_window import RegistrationWindow
from gui.customer_window import CustomerWindow
from gui.loan_window import LoanWindow
from gui.repayment_window import RepaymentWindow
from gui.analytics_window import AnalyticsWindow
from gui.reports_window import ReportsWindow
from modules.authentication import Session


class Dashboard(ttk.Frame):
    def __init__(self, master, session: Session, on_logout):
        super().__init__(master, padding=26)
        self.session = session
        self.on_logout = on_logout
        self.pack(fill="both", expand=True)
        self._build()

    def _build(self):
        user = self.session.user

        top = ttk.Frame(self)
        top.pack(fill="x")
        ttk.Label(
            top,
            text="SmartLoan Analytics",
            font=("Arial", 22, "bold"),
        ).pack(side="left")
        ttk.Button(top, text="Logout", command=self.on_logout).pack(side="right")

        ttk.Label(
            self,
            text=f"Welcome, {user.full_name} | Role: {user.role}",
            font=("Arial", 11),
        ).pack(anchor="w", pady=(8, 24))

        actions = ttk.LabelFrame(self, text="Available Functions", padding=18)
        actions.pack(fill="both", expand=True)

        placeholders = [
            ("Customers", "read", None),
            ("Loans", "read", None),
            ("Repayments", "record_repayment", None),
            ("Analytics", "reports", None),
            ("Reports", "reports", None),
        ]

        for label, permission, note in placeholders:
            if self.session.can(permission):
                if label == "Customers":
                    command = lambda: CustomerWindow(self, self.session)
                elif label == "Loans":
                    command = lambda: LoanWindow(self, self.session)
                elif label == "Repayments":
                    command = lambda: RepaymentWindow(self, self.session)
                elif label == "Analytics":
                    command = lambda: AnalyticsWindow(self, self.session)
                elif label == "Reports":
                    command = lambda: ReportsWindow(self, self.session)
                else:
                    command = lambda n=note: messagebox.showinfo(
                        "SmartLoan Analytics", n
                    )

                ttk.Button(
                    actions,
                    text=label,
                    command=command,
                ).pack(fill="x", pady=5)

        if self.session.can("manage_users"):
            ttk.Button(
                actions,
                text="Create User Account",
                command=lambda: RegistrationWindow(self, actor=self.session),
            ).pack(fill="x", pady=5)

        ttk.Label(
            actions,
            text="Role-based access control is active.",
        ).pack(anchor="w", pady=(18, 0))
