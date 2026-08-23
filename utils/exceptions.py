"""Custom exception hierarchy for SmartLoan Analytics."""


class SmartLoanError(Exception):
    """Base exception for expected application errors."""


class ValidationError(SmartLoanError):
    """Raised when submitted data fails validation."""


class AuthenticationError(SmartLoanError):
    """Raised when authentication or authorization fails."""


class DatabaseOperationError(SmartLoanError):
    """Raised when a database operation cannot be completed safely."""


class FileOperationError(SmartLoanError):
    """Raised when file input/output fails."""


class ReportGenerationError(SmartLoanError):
    """Raised when report creation fails."""
