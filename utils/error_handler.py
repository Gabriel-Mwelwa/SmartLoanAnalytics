"""Centralized safe exception handling for SmartLoan Analytics."""

from __future__ import annotations

import logging
import sqlite3
from pathlib import Path

from utils.exceptions import SmartLoanError


def user_friendly_message(exc: Exception) -> str:
    """Convert technical exceptions into safe GUI messages."""
    if isinstance(exc, SmartLoanError):
        return str(exc)

    if isinstance(exc, sqlite3.Error):
        return "A database error occurred. The operation was not completed."

    if isinstance(exc, FileNotFoundError):
        name = Path(exc.filename).name if exc.filename else "required file"
        return f"Required file was not found: {name}."

    if isinstance(exc, PermissionError):
        return "The application does not have permission to complete this operation."

    if isinstance(exc, OSError):
        return "A file or system operation failed. Check storage and folder permissions."

    return (
        "An unexpected error occurred. The event has been recorded in the application log."
    )


def handle_exception(exc: Exception, context: str = "application operation") -> str:
    """Log an exception and return a safe user-facing message."""
    logger = logging.getLogger("smartloan.errors")

    if isinstance(exc, SmartLoanError):
        logger.warning("%s failed: %s", context, exc)
    else:
        logger.exception("%s failed", context, exc_info=exc)

    return user_friendly_message(exc)
