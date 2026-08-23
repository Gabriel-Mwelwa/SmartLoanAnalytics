"""SmartLoan Analytics application entry point."""

import logging
import tkinter as tk
from tkinter import messagebox

from config import APP_NAME, APP_VERSION
from database import initialize_database
from gui.login_window import LoginWindow
from utils.error_handler import handle_exception
from utils.logger import configure_logging, log_system_event


def _tk_exception_handler(exc_type, exc_value, exc_traceback):
    message = handle_exception(exc_value, "GUI callback")
    messagebox.showerror("SmartLoan Error", message)


def build_app() -> tk.Tk:
    root = tk.Tk()
    root.title(f"{APP_NAME} v{APP_VERSION}")
    root.geometry("900x620")
    root.minsize(780, 520)
    root.report_callback_exception = _tk_exception_handler
    LoginWindow(root)
    return root


def main() -> None:
    configure_logging()

    try:
        initialize_database()
        log_system_event(f"{APP_NAME} v{APP_VERSION} started")

        app = build_app()
        app.mainloop()

        log_system_event(f"{APP_NAME} closed normally")

    except Exception as exc:
        message = handle_exception(exc, "application startup")
        try:
            messagebox.showerror("Startup Error", message)
        except Exception:
            print(message)
        logging.shutdown()


if __name__ == "__main__":
    main()
