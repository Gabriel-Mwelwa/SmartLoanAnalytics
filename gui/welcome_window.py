from tkinter import ttk
from config import APP_NAME, APP_VERSION


class WelcomeWindow(ttk.Frame):
    def __init__(self, master):
        super().__init__(master, padding=30)
        self.pack(fill='both', expand=True)
        self._build()

    def _build(self):
        ttk.Label(self, text=APP_NAME, font=('Arial',24,'bold')).pack(pady=(40,10))
        ttk.Label(self, text=f'Version {APP_VERSION}', font=('Arial',11)).pack()
        ttk.Label(
            self,
            text='Loan Management & Analytics System\n\nPhase 1 foundation is running successfully.\nAuthentication and role-based access will be added in Phase 2.',
            justify='center',
            font=('Arial',12),
        ).pack(pady=35)
        ttk.Label(self, text='Database: SQLite | Interface: Tkinter | Language: Python').pack()
