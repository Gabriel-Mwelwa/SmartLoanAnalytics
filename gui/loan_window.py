"""Loan application and approval GUI."""

import tkinter as tk
from tkinter import messagebox, ttk

from database import get_connection
from modules.loan_management import (
    apply_for_loan,
    approve_loan,
    disburse_loan,
    list_loans,
    reject_loan,
)
from utils.exceptions import SmartLoanError


class LoanWindow(tk.Toplevel):
    def __init__(self, master, session):
        super().__init__(master)
        self.session = session
        self.title("SmartLoan Analytics - Loan Management")
        self.geometry("1180x720")
        self.minsize(1030, 640)
        self._build()
        self.refresh()

    def _build(self):
        top = ttk.Frame(self, padding=12)
        top.pack(fill="x")
        ttk.Label(top, text="Loan Management", font=("Arial", 20, "bold")).pack(side="left")

        form = ttk.LabelFrame(self, text="New Loan Application", padding=12)
        form.pack(fill="x", padx=12, pady=(0, 10))

        self.customer = tk.StringVar()
        self.amount = tk.StringVar(value="1000")
        self.rate = tk.StringVar(value="18")
        self.term = tk.StringVar(value="12")
        self.purpose = tk.StringVar()

        customers = []
        with get_connection() as connection:
            rows = connection.execute(
                "SELECT customer_id, customer_code, full_name FROM customers ORDER BY full_name"
            ).fetchall()
            customers = [
                f"{r['customer_id']} | {r['customer_code']} | {r['full_name']}"
                for r in rows
            ]

        fields = [
            ("Customer", self.customer),
            ("Loan Amount", self.amount),
            ("Interest Rate %", self.rate),
            ("Term (months)", self.term),
            ("Purpose", self.purpose),
        ]

        for i, (label, var) in enumerate(fields):
            ttk.Label(form, text=label).grid(row=0, column=i*2, sticky="w", padx=(0,4))
            if label == "Customer":
                ttk.Combobox(form, textvariable=var, values=customers, width=28, state="readonly").grid(
                    row=0, column=i*2+1, padx=(0,10)
                )
            else:
                ttk.Entry(form, textvariable=var, width=16).grid(
                    row=0, column=i*2+1, padx=(0,10)
                )

        ttk.Button(form, text="Apply", command=self.apply).grid(row=1, column=0, columnspan=10, sticky="ew", pady=(10,0))

        filters = ttk.Frame(self, padding=(12, 0, 12, 8))
        filters.pack(fill="x")
        self.status = tk.StringVar(value="All")
        self.query = tk.StringVar()
        ttk.Label(filters, text="Status").pack(side="left")
        ttk.Combobox(
            filters,
            textvariable=self.status,
            values=["All","Pending","Approved","Rejected","Disbursed","Completed","Overdue"],
            state="readonly",
            width=12,
        ).pack(side="left", padx=5)
        ttk.Label(filters, text="Search").pack(side="left", padx=(10,0))
        ttk.Entry(filters, textvariable=self.query, width=24).pack(side="left", padx=5)
        ttk.Button(filters, text="Refresh", command=self.refresh).pack(side="left", padx=5)

        table_frame = ttk.Frame(self, padding=(12,0,12,12))
        table_frame.pack(fill="both", expand=True)

        columns = ("id","customer","principal","rate","term","score","status","due")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=20)
        headings = {
            "id":"Loan ID","customer":"Customer","principal":"Principal","rate":"Rate %",
            "term":"Term","score":"Score","status":"Status","due":"Due Date"
        }
        for col in columns:
            self.tree.heading(col, text=headings[col])
            self.tree.column(col, width=120, anchor="w")
        self.tree.column("customer", width=220)
        self.tree.pack(fill="both", expand=True)

        actions = ttk.Frame(self, padding=(12,0,12,12))
        actions.pack(fill="x")
        if self.session.can("approve_loans"):
            ttk.Button(actions, text="Approve", command=self.approve).pack(side="left", padx=4)
            ttk.Button(actions, text="Reject", command=self.reject).pack(side="left", padx=4)
            ttk.Button(actions, text="Disburse", command=self.disburse).pack(side="left", padx=4)

    def selected_loan_id(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Loans", "Select a loan first.")
            return None
        return int(self.tree.item(selected[0], "values")[0])

    def apply(self):
        if not self.customer.get():
            messagebox.showwarning("Loans", "Select a customer.")
            return
        customer_id = int(self.customer.get().split("|")[0].strip())
        try:
            loan = apply_for_loan(
                self.session,
                customer_id,
                self.amount.get(),
                self.rate.get(),
                self.term.get(),
                self.purpose.get(),
            )
        except (SmartLoanError, PermissionError) as exc:
            messagebox.showerror("Loans", str(exc))
            return
        messagebox.showinfo(
            "Loans",
            f"Loan application created.\nEligibility score: {loan.eligibility_score}",
        )
        self.refresh()

    def refresh(self):
        try:
            rows = list_loans(self.status.get(), self.query.get())
        except SmartLoanError as exc:
            messagebox.showerror("Loans", str(exc))
            return
        for item in self.tree.get_children():
            self.tree.delete(item)
        for row in rows:
            self.tree.insert(
                "",
                "end",
                values=(
                    row["loan_id"],
                    f"{row['customer_code']} - {row['customer_name']}",
                    f"K{float(row['principal']):,.2f}",
                    row["annual_interest_rate"],
                    row["term_months"],
                    row["eligibility_score"],
                    row["status"],
                    row["due_date"] or "",
                ),
            )

    def approve(self):
        loan_id = self.selected_loan_id()
        if loan_id is None:
            return
        try:
            approve_loan(self.session, loan_id)
        except (SmartLoanError, PermissionError) as exc:
            messagebox.showerror("Loans", str(exc))
            return
        self.refresh()

    def reject(self):
        loan_id = self.selected_loan_id()
        if loan_id is None:
            return
        try:
            reject_loan(self.session, loan_id)
        except (SmartLoanError, PermissionError) as exc:
            messagebox.showerror("Loans", str(exc))
            return
        self.refresh()

    def disburse(self):
        loan_id = self.selected_loan_id()
        if loan_id is None:
            return
        try:
            disburse_loan(self.session, loan_id)
        except (SmartLoanError, PermissionError) as exc:
            messagebox.showerror("Loans", str(exc))
            return
        self.refresh()
