"""Login screen for SmartLoan Analytics."""

import tkinter as tk
from tkinter import messagebox, ttk

from gui.dashboard import Dashboard
from gui.registration_window import RegistrationWindow
from modules.authentication import authenticate
from utils.exceptions import SmartLoanError


class LoginWindow(ttk.Frame):
    def __init__(self, master):
        super().__init__(master, padding=30)
        self.master = master
        self.pack(fill="both", expand=True)
        self._build()

    def _build(self):
        ttk.Label(
            self,
            text="SmartLoan Analytics",
            font=("Arial", 24, "bold"),
        ).pack(pady=(50, 8))

        ttk.Label(
            self,
            text="Loan Management & Analytics System",
            font=("Arial", 12),
        ).pack(pady=(0, 26))

        form = ttk.Frame(self)
        form.pack()

        self.username = tk.StringVar()
        self.password = tk.StringVar()

        ttk.Label(form, text="Username").grid(row=0, column=0, sticky="w", pady=6)
        ttk.Entry(form, textvariable=self.username, width=34).grid(
            row=0, column=1, pady=6, padx=(10, 0)
        )

        ttk.Label(form, text="Password").grid(row=1, column=0, sticky="w", pady=6)
        password_entry = ttk.Entry(
            form,
            textvariable=self.password,
            width=34,
            show="*",
        )
        password_entry.grid(row=1, column=1, pady=6, padx=(10, 0))
        password_entry.bind("<Return>", lambda _event: self.login())

        buttons = ttk.Frame(self)
        buttons.pack(pady=20)

        ttk.Button(buttons, text="Login", command=self.login).pack(
            side="left", padx=5
        )
        ttk.Button(
            buttons,
            text="Register",
            command=lambda: RegistrationWindow(self),
        ).pack(side="left", padx=5)

        ttk.Label(
            self,
            text="The first registered account is automatically created as Administrator.",
            wraplength=520,
        ).pack(pady=(8, 0))

    def login(self):
        try:
            session = authenticate(self.username.get(), self.password.get())
        except SmartLoanError as exc:
            messagebox.showerror("Login", str(exc))
            return

        self.destroy()
        Dashboard(self.master, session, self.show_login)

    def show_login(self):
        for child in self.master.winfo_children():
            child.destroy()
        LoginWindow(self.master)
