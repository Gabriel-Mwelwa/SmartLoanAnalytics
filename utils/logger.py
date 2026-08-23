"""Application logging configuration for SmartLoan Analytics."""

import logging
from logging.handlers import RotatingFileHandler

from config import LOG_DIR, LOG_FILE


def configure_logging() -> None:
    """Configure rotating application logging once."""
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    for handler in root_logger.handlers:
        if isinstance(handler, RotatingFileHandler):
            return

    handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=1_000_000,
        backupCount=3,
        encoding="utf-8",
    )
    handler.setFormatter(
        logging.Formatter(
            "%(asctime)s %(levelname)s %(name)s %(message)s"
        )
    )
    root_logger.addHandler(handler)


def log_system_event(message: str, level: int = logging.INFO) -> None:
    """Write a named system event."""
    logging.getLogger("smartloan.system").log(level, message)
