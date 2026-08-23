"""Repayment and overdue-management GUI."""

import tkinter as tk
from tkinter import messagebox, ttk

from modules.loan_management import calculate_outstanding_balance, list_loans
from modules.repayment_management import (
    create_penalty_if_needed,
    list_repayments,
    record_repayment,
    refresh_overdue_loans,
)
from utils.exceptions import SmartLoanError


class RepaymentWindow(tk.Toplevel):
    def __init__(self, master, session):
        super().__init__(master)
        self.session = session
        self.title("SmartLoan Analytics - Repayments")
        self.geometry("1050x680")
        self.minsize(900, 600)
        self._build()
        self.refresh()

    def _build(self):
        top = ttk.Frame(self, padding=12)
        top.pack(fill="x")
        ttk.Label(top, text="Repayments & Overdue Loans", font=("Arial", 20, "bold")).pack(side="left")

        form = ttk.LabelFrame(self, text="Record Repayment", padding=12)
        form.pack(fill="x", padx=12, pady=(0,10))

        self.loan_id = tk.StringVar()
        self.amount = tk.StringVar()
        self.method = tk.StringVar(value="Bank Transfer")
        self.reference = tk.StringVar()

        active_loans = [
            f"{r['loan_id']} | {r['customer_code']} | {r['status']}"
            for r in list_loans()
            if r["status"] in {"Disbursed","Overdue"}
        ]

        ttk.Label(form, text="Loan").grid(row=0,column=0,sticky="w")
        ttk.Combobox(form,textvariable=self.loan_id,values=active_loans,state="readonly",width=28).grid(row=0,column=1,padx=6)
        ttk.Label(form,text="Amount").grid(row=0,column=2,sticky="w")
        ttk.Entry(form,textvariable=self.amount,width=14).grid(row=0,column=3,padx=6)
        ttk.Label(form,text="Method").grid(row=0,column=4,sticky="w")
        ttk.Combobox(form,textvariable=self.method,values=["Cash","Bank Transfer","Mobile Money"],state="readonly",width=16).grid(row=0,column=5,padx=6)
        ttk.Label(form,text="Reference").grid(row=0,column=6,sticky="w")
        ttk.Entry(form,textvariable=self.reference,width=18).grid(row=0,column=7,padx=6)

        ttk.Button(form,text="Record Payment",command=self.record).grid(row=1,column=0,columnspan=8,sticky="ew",pady=(10,0))

        actions = ttk.Frame(self, padding=(12,0,12,8))
        actions.pack(fill="x")
        ttk.Button(actions,text="Refresh Overdue Status",command=self.mark_overdue).pack(side="left",padx=4)
        ttk.Button(actions,text="Create Selected Penalty",command=self.penalty).pack(side="left",padx=4)
        ttk.Button(actions,text="Check Selected Balance",command=self.balance).pack(side="left",padx=4)

        columns=("repayment","loan","customer","date","amount","method","reference")
        self.tree=ttk.Treeview(self,columns=columns,show="headings",height=20)
        for col,title in [
            ("repayment","Repayment ID"),("loan","Loan ID"),("customer","Customer"),
            ("date","Date"),("amount","Amount"),("method","Method"),("reference","Reference")
        ]:
            self.tree.heading(col,text=title)
            self.tree.column(col,width=130,anchor="w")
        self.tree.column("customer",width=210)
        self.tree.pack(fill="both",expand=True,padx=12,pady=(0,12))

    def selected_active_loan_id(self):
        if not self.loan_id.get():
            messagebox.showwarning("Repayments","Select an active loan.")
            return None
        return int(self.loan_id.get().split("|")[0].strip())

    def record(self):
        loan_id=self.selected_active_loan_id()
        if loan_id is None:
            return
        try:
            record_repayment(
                self.session,
                loan_id,
                self.amount.get(),
                self.method.get(),
                self.reference.get(),
            )
        except (SmartLoanError,PermissionError) as exc:
            messagebox.showerror("Repayments",str(exc))
            return
        messagebox.showinfo("Repayments","Repayment recorded successfully.")
        self.refresh()

    def mark_overdue(self):
        count=refresh_overdue_loans()
        messagebox.showinfo("Repayments",f"{count} loan(s) marked overdue.")
        self.refresh()

    def penalty(self):
        loan_id=self.selected_active_loan_id()
        if loan_id is None:
            return
        try:
            amount=create_penalty_if_needed(self.session,loan_id)
        except (SmartLoanError,PermissionError) as exc:
            messagebox.showerror("Repayments",str(exc))
            return
        messagebox.showinfo("Repayments",f"Penalty amount: K{amount:.2f}")

    def balance(self):
        loan_id=self.selected_active_loan_id()
        if loan_id is None:
            return
        try:
            amount=calculate_outstanding_balance(loan_id)
        except SmartLoanError as exc:
            messagebox.showerror("Repayments",str(exc))
            return
        messagebox.showinfo("Repayments",f"Outstanding balance: K{amount:.2f}")

    def refresh(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for row in list_repayments():
            self.tree.insert(
                "",
                "end",
                values=(
                    row["repayment_id"],
                    row["loan_id"],
                    f"{row['customer_code']} - {row['customer_name']}",
                    row["payment_date"],
                    f"K{float(row['amount']):,.2f}",
                    row["payment_method"],
                    row["reference_number"],
                ),
            )
