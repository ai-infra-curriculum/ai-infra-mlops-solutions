"""Logging configuration and utilities."""

import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, Optional

from loguru import logger

from src.utils.config import get_config


class InterceptHandler(logging.Handler):
    """Intercept standard logging messages and redirect to loguru."""

    def emit(self, record: logging.LogRecord) -> None:
        """Emit a log record.

        Args:
            record: Log record to emit
        """
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back  # type: ignore
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def setup_logging(
    log_level: Optional[str] = None,
    log_format: Optional[str] = None,
    log_file: Optional[str] = None,
) -> None:
    """Set up logging configuration.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_format: Log format ('json' or 'text')
        log_file: Optional log file path
    """
    config = get_config()

    # Use config values if not provided
    log_level = log_level or config.log_level
    log_format = log_format or config.log_format

    # Remove default handler
    logger.remove()

    # Determine format
    if log_format == "json":
        log_fmt = _json_formatter
    else:
        log_fmt = (
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "<level>{message}</level>"
        )

    # Add stdout handler
    logger.add(
        sys.stdout,
        format=log_fmt,
        level=log_level,
        colorize=log_format != "json",
        serialize=log_format == "json",
    )

    # Add file handler if specified
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        logger.add(
            log_file,
            format=log_fmt,
            level=log_level,
            rotation="500 MB",
            retention="10 days",
            compression="zip",
            serialize=log_format == "json",
        )

    # Intercept standard logging
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

    # Set levels for noisy libraries
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("kafka").setLevel(logging.WARNING)


def _json_formatter(record: Dict[str, Any]) -> str:
    """Format log record as JSON.

    Args:
        record: Log record dictionary

    Returns:
        JSON formatted string
    """
    log_dict = {
        "timestamp": record["time"].isoformat(),
        "level": record["level"].name,
        "logger": record["name"],
        "function": record["function"],
        "line": record["line"],
        "message": record["message"],
    }

    # Add exception info if present
    if record["exception"]:
        log_dict["exception"] = {
            "type": record["exception"].type.__name__,
            "value": str(record["exception"].value),
            "traceback": record["exception"].traceback,
        }

    # Add extra fields
    if record["extra"]:
        log_dict["extra"] = record["extra"]

    return json.dumps(log_dict)


def get_logger(name: Optional[str] = None) -> Any:
    """Get a logger instance.

    Args:
        name: Logger name (defaults to calling module)

    Returns:
        Logger instance
    """
    if name:
        return logger.bind(name=name)
    return logger


# Context manager for logging context
class LogContext:
    """Context manager for adding context to logs."""

    def __init__(self, **kwargs: Any):
        """Initialize log context.

        Args:
            **kwargs: Context key-value pairs
        """
        self.context = kwargs
        self.token: Optional[int] = None

    def __enter__(self) -> "LogContext":
        """Enter context."""
        self.token = logger.contextualize(**self.context).id
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit context."""
        if self.token is not None:
            logger.remove(self.token)


# Initialize logging
setup_logging()
