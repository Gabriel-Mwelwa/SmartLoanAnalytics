"""Customer Management GUI for SmartLoan Analytics."""

import tkinter as tk
from tkinter import messagebox, ttk

from modules.customer_management import (
    ALLOWED_EMPLOYMENT,
    add_customer,
    delete_customer,
    list_customers,
    update_customer,
)
from utils.exceptions import SmartLoanError


class CustomerWindow(tk.Toplevel):
    def __init__(self, master, session):
        super().__init__(master)
        self.session = session
        self.selected_customer_id = None
        self.title("SmartLoan Analytics - Customer Management")
        self.geometry("1180x720")
        self.minsize(1040, 650)
        self._build()
        self.refresh()

    def _build(self):
        top = ttk.Frame(self, padding=12)
        top.pack(fill="x")
        ttk.Label(
            top,
            text="Customer Management",
            font=("Arial", 20, "bold"),
        ).pack(side="left")

        search = ttk.Frame(self, padding=(12, 0, 12, 8))
        search.pack(fill="x")

        self.query = tk.StringVar()
        self.status_filter = tk.StringVar(value="All")
        self.employment_filter = tk.StringVar(value="All")
        self.sort_by = tk.StringVar(value="Name A-Z")

        ttk.Label(search, text="Search").pack(side="left")
        ttk.Entry(search, textvariable=self.query, width=25).pack(
            side="left", padx=(5, 10)
        )
        ttk.Combobox(
            search,
            textvariable=self.status_filter,
            values=["All", "Active", "Suspended"],
            width=12,
            state="readonly",
        ).pack(side="left", padx=5)
        ttk.Combobox(
            search,
            textvariable=self.employment_filter,
            values=["All"] + sorted(ALLOWED_EMPLOYMENT),
            width=16,
            state="readonly",
        ).pack(side="left", padx=5)
        ttk.Combobox(
            search,
            textvariable=self.sort_by,
            values=[
                "Name A-Z", "Name Z-A", "Customer Code",
                "Highest Income", "Lowest Income", "Newest"
            ],
            width=16,
            state="readonly",
        ).pack(side="left", padx=5)
        ttk.Button(search, text="Apply", command=self.refresh).pack(
            side="left", padx=5
        )

        body = ttk.Panedwindow(self, orient="horizontal")
        body.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        form = ttk.LabelFrame(body, text="Customer Details", padding=12)
        table_frame = ttk.LabelFrame(body, text="Customer Records", padding=8)
        body.add(form, weight=1)
        body.add(table_frame, weight=3)

        self.vars = {
            "customer_code": tk.StringVar(),
            "full_name": tk.StringVar(),
            "national_id": tk.StringVar(),
            "phone": tk.StringVar(),
            "email": tk.StringVar(),
            "address": tk.StringVar(),
            "employment_status": tk.StringVar(value="Other"),
            "monthly_income": tk.StringVar(value="0"),
            "status": tk.StringVar(value="Active"),
        }

        fields = [
            ("Customer Code", "customer_code"),
            ("Full Name", "full_name"),
            ("National ID", "national_id"),
            ("Phone", "phone"),
            ("Email", "email"),
            ("Address", "address"),
            ("Monthly Income", "monthly_income"),
        ]

        for row, (label, key) in enumerate(fields):
            ttk.Label(form, text=label).grid(row=row, column=0, sticky="w", pady=4)
            ttk.Entry(form, textvariable=self.vars[key], width=28).grid(
                row=row, column=1, sticky="ew", pady=4, padx=(8, 0)
            )

        next_row = len(fields)

        ttk.Label(form, text="Employment").grid(
            row=next_row, column=0, sticky="w", pady=4
        )
        ttk.Combobox(
            form,
            textvariable=self.vars["employment_status"],
            values=sorted(ALLOWED_EMPLOYMENT),
            state="readonly",
            width=25,
        ).grid(row=next_row, column=1, sticky="ew", pady=4, padx=(8, 0))

        ttk.Label(form, text="Status").grid(
            row=next_row + 1, column=0, sticky="w", pady=4
        )
        ttk.Combobox(
            form,
            textvariable=self.vars["status"],
            values=["Active", "Suspended"],
            state="readonly",
            width=25,
        ).grid(row=next_row + 1, column=1, sticky="ew", pady=4, padx=(8, 0))

        buttons = ttk.Frame(form)
        buttons.grid(
            row=next_row + 2,
            column=0,
            columnspan=2,
            sticky="ew",
            pady=(14, 0),
        )
        ttk.Button(buttons, text="Add", command=self.add).pack(
            side="left", padx=3
        )
        ttk.Button(buttons, text="Update", command=self.update).pack(
            side="left", padx=3
        )
        ttk.Button(buttons, text="Delete", command=self.delete).pack(
            side="left", padx=3
        )
        ttk.Button(buttons, text="Clear", command=self.clear_form).pack(
            side="left", padx=3
        )

        columns = (
            "id", "code", "name", "nid", "phone",
            "employment", "income", "status"
        )
        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            height=22,
        )

        headings = {
            "id": "ID",
            "code": "Code",
            "name": "Customer",
            "nid": "National ID",
            "phone": "Phone",
            "employment": "Employment",
            "income": "Monthly Income",
            "status": "Status",
        }

        for col in columns:
            self.tree.heading(col, text=headings[col])
            self.tree.column(col, width=110, anchor="w")

        self.tree.column("id", width=50)
        self.tree.column("name", width=160)
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.load_selected)

    def _payload(self):
        return {key: variable.get() for key, variable in self.vars.items()}

    def refresh(self):
        try:
            rows = list_customers(
                self.query.get(),
                self.status_filter.get(),
                self.employment_filter.get(),
                self.sort_by.get(),
            )
        except SmartLoanError as exc:
            messagebox.showerror("Customers", str(exc))
            return

        for item in self.tree.get_children():
            self.tree.delete(item)

        for customer in rows:
            self.tree.insert(
                "",
                "end",
                values=(
                    customer.customer_id,
                    customer.customer_code,
                    customer.full_name,
                    customer.national_id or "",
                    customer.phone or "",
                    customer.employment_status or "",
                    f"K{customer.monthly_income:,.2f}",
                    customer.status,
                ),
            )

    def add(self):
        try:
            add_customer(self.session, **self._payload())
        except (SmartLoanError, PermissionError) as exc:
            messagebox.showerror("Customers", str(exc))
            return
        self.clear_form()
        self.refresh()
        messagebox.showinfo("Customers", "Customer created successfully.")

    def update(self):
        if self.selected_customer_id is None:
            messagebox.showwarning("Customers", "Select a customer first.")
            return
        try:
            update_customer(
                self.session,
                self.selected_customer_id,
                **self._payload(),
            )
        except (SmartLoanError, PermissionError) as exc:
            messagebox.showerror("Customers", str(exc))
            return
        self.refresh()
        messagebox.showinfo("Customers", "Customer updated successfully.")

    def delete(self):
        if self.selected_customer_id is None:
            messagebox.showwarning("Customers", "Select a customer first.")
            return
        if not self.session.can("delete"):
            messagebox.showerror(
                "Customers",
                "Only an Administrator can delete customer records.",
            )
            return
        if not messagebox.askyesno(
            "Customers",
            "Delete the selected customer?",
        ):
            return
        try:
            delete_customer(self.session, self.selected_customer_id)
        except (SmartLoanError, PermissionError) as exc:
            messagebox.showerror("Customers", str(exc))
            return
        self.clear_form()
        self.refresh()

    def load_selected(self, _event=None):
        selected = self.tree.selection()
        if not selected:
            return

        values = self.tree.item(selected[0], "values")
        customer_id = int(values[0])

        rows = list_customers()
        customer = next(
            (item for item in rows if item.customer_id == customer_id),
            None,
        )
        if customer is None:
            return

        self.selected_customer_id = customer.customer_id
        data = {
            "customer_code": customer.customer_code,
            "full_name": customer.full_name,
            "national_id": customer.national_id or "",
            "phone": customer.phone or "",
            "email": customer.email or "",
            "address": customer.address or "",
            "employment_status": customer.employment_status or "Other",
            "monthly_income": str(customer.monthly_income),
            "status": customer.status,
        }

        for key, value in data.items():
            self.vars[key].set(value)

    def clear_form(self):
        self.selected_customer_id = None
        for key, variable in self.vars.items():
            if key == "employment_status":
                variable.set("Other")
            elif key == "monthly_income":
                variable.set("0")
            elif key == "status":
                variable.set("Active")
            else:
                variable.set("")
