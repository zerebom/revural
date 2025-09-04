"""Logging configuration utilities."""

import logging
import sys
from typing import Any

_RESERVED_LOGRECORD_KEYS = {
    # Core LogRecord attributes that cannot be overwritten via `extra`
    "name",
    "msg",
    "message",
    "levelname",
    "levelno",
    "pathname",
    "filename",
    "module",
    "exc_info",
    "exc_text",
    "stack_info",
    "lineno",
    "funcName",
    "created",
    "msecs",
    "relativeCreated",
    "thread",
    "threadName",
    "processName",
    "process",
    "args",
    "asctime",
}


class StructuredLogger:
    """A wrapper around Python's logging.Logger that supports structured logging."""

    def __init__(self, logger: logging.Logger):
        self.logger = logger

    def _sanitize_extra(self, extra: dict[str, Any]) -> dict[str, Any]:
        """Remove/rename keys that would overwrite LogRecord attributes.

        Conflicting keys are prefixed with "extra_" to avoid KeyError.
        """
        if not extra:
            return {}
        sanitized: dict[str, Any] = {}
        for k, v in extra.items():
            if k in _RESERVED_LOGRECORD_KEYS:
                sanitized[f"extra_{k}"] = v
            else:
                sanitized[k] = v
        return sanitized

    def debug(self, message: str, **kwargs: Any) -> None:
        """Log debug message with structured data."""
        self.logger.debug(message, extra=self._sanitize_extra(kwargs))

    def info(self, message: str, **kwargs: Any) -> None:
        """Log info message with structured data."""
        self.logger.info(message, extra=self._sanitize_extra(kwargs))

    def warning(self, message: str, **kwargs: Any) -> None:
        """Log warning message with structured data."""
        self.logger.warning(message, extra=self._sanitize_extra(kwargs))

    def error(self, message: str, exc_info: bool = False, **kwargs: Any) -> None:
        """Log error message with structured data."""
        self.logger.error(
            message, exc_info=exc_info, extra=self._sanitize_extra(kwargs)
        )


def get_logger(name: str) -> StructuredLogger:
    """Get a configured structured logger instance.

    Parameters
    ----------
    name : str
        Logger name (typically __name__)

    Returns
    -------
    StructuredLogger
        Configured structured logger instance
    """
    return StructuredLogger(logging.getLogger(name))


def setup_logging(level: str = "INFO", format_type: str = "console") -> None:
    """Setup logging configuration.

    Parameters
    ----------
    level : str, default="INFO"
        Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format_type : str, default="console"
        Format type (console, json, plain)
    """
    # Convert string level to logging constant
    numeric_level = getattr(logging, level.upper(), logging.INFO)

    # Define format based on type
    if format_type == "json":
        formatter = logging.Formatter(
            '{"timestamp": "%(asctime)s", "level": "%(levelname)s", '
            '"logger": "%(name)s", "message": "%(message)s"}'
        )
    elif format_type == "plain":
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    else:  # console (default)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)

    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Add console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)


def set_log_level(logger: logging.Logger, level: str) -> None:
    """Set log level for a specific logger.

    Parameters
    ----------
    logger : logging.Logger
        Logger instance
    level : str
        Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(numeric_level)
