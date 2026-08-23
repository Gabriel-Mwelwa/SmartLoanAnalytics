"""Registration window for SmartLoan Analytics."""

import tkinter as tk
from tkinter import messagebox, ttk

from modules.authentication import Session, register_user
from utils.exceptions import SmartLoanError


class RegistrationWindow(tk.Toplevel):
    def __init__(self, master, actor: Session | None = None):
        super().__init__(master)
        self.actor = actor
        self.title("SmartLoan Analytics - Register User")
        self.geometry("520x520")
        self.resizable(False, False)
        self._build()

    def _build(self):
        frame = ttk.Frame(self, padding=24)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Register User", font=("Arial", 20, "bold")).pack(pady=(0, 18))

        self.full_name = tk.StringVar()
        self.username = tk.StringVar()
        self.email = tk.StringVar()
        self.password = tk.StringVar()
        self.confirm = tk.StringVar()
        self.role = tk.StringVar(value="Loan Officer")

        fields = [
            ("Full Name", self.full_name, False),
            ("Username", self.username, False),
            ("Email", self.email, False),
            ("Password", self.password, True),
            ("Confirm Password", self.confirm, True),
        ]

        for label, variable, secret in fields:
            ttk.Label(frame, text=label).pack(anchor="w")
            ttk.Entry(frame, textvariable=variable, show="*" if secret else "").pack(
                fill="x", pady=(2, 10)
            )

        if self.actor is not None and self.actor.can("manage_users"):
            ttk.Label(frame, text="Role").pack(anchor="w")
            ttk.Combobox(
                frame,
                textvariable=self.role,
                values=["Loan Officer", "Administrator"],
                state="readonly",
            ).pack(fill="x", pady=(2, 12))
        else:
            ttk.Label(
                frame,
                text=(
                    "Public registration creates a Loan Officer account. "
                    "The first account is automatically Administrator."
                ),
                wraplength=450,
            ).pack(anchor="w", pady=(0, 12))

        ttk.Button(
            frame,
            text="Create Account",
            command=self._submit_registration,
        ).pack(fill="x", pady=(8, 0))

    def _submit_registration(self):
        if self.password.get() != self.confirm.get():
            messagebox.showerror("Registration", "Passwords do not match.")
            return

        try:
            user = register_user(
                self.full_name.get(),
                self.username.get(),
                self.email.get(),
                self.password.get(),
                self.role.get(),
                actor=self.actor,
            )
        except SmartLoanError as exc:
            messagebox.showerror("Registration", str(exc))
            return

        messagebox.showinfo(
            "Registration",
            f"Account created successfully.\nRole: {user.role}",
        )
        self.destroy()
