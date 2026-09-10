"""
Structured Logging Configuration

WHY THIS EXISTS:
    Print statements are useless in production. Structured logging means every
    log entry is a machine-parseable record (JSON) with consistent fields.
    This lets you search, filter, and alert on logs programmatically.

HOW IT WORKS:
    Python's built-in `logging` module is configured with a JSON formatter
    (python-json-logger). Every log message automatically includes:
      - timestamp, level, logger name, message
      - Any extra fields passed by the application (case_id, operation, etc.)

WHAT NOT TO LOG:
    - Passwords, tokens, API keys, or any secrets
    - Full request/response bodies in production (may contain PII)
    - Personally Identifiable Information (PII) without explicit consent

CURRICULUM CONNECTION:
    Week 1 requires: structured logging with useful fields (timestamp,
    log level, event, operation, case ID, status, error information).
"""

import logging
import sys
from typing import Optional

from pythonjsonlogger import json as json_logger

from app.config import get_settings


def setup_logging(log_level: Optional[str] = None) -> None:
    """
    Configure structured JSON logging for the entire application.

    Args:
        log_level: Override the log level from settings. Useful in tests.
    """
    settings = get_settings()
    level = log_level or settings.log_level

    # ── Create JSON formatter ────────────────────────────────────
    # This formatter converts every log record into a JSON object.
    # The 'format' string tells it which standard fields to include.
    formatter = json_logger.JsonFormatter(
        fmt="%(asctime)s %(levelname)s %(name)s %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S%z",
        rename_fields={
            "asctime": "timestamp",
            "levelname": "level",
            "name": "logger",
        },
    )

    # ── Configure root logger ────────────────────────────────────
    # All loggers in the app inherit from the root logger.
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Remove existing handlers to avoid duplicate log lines
    root_logger.handlers.clear()

    # Send logs to stdout (standard for containerized apps)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    root_logger.addHandler(handler)

    # Quiet noisy third-party loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Get a named logger for a specific module.

    Usage:
        logger = get_logger(__name__)
        logger.info("Case created", extra={"case_id": 42, "operation": "create"})

    WHY NAMED LOGGERS:
        Each module gets its own logger (e.g., 'app.services.case_service').
        This appears in log output, making it trivial to find which module
        produced a log line.
    """
    return logging.getLogger(name)
