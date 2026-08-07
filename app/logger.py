"""Logging setup shared by the application."""

import logging

LOGGER_NAME = "calculator"
LOG_FORMAT = "%(asctime)s %(name)s: %(message)s"


def get_logger(name: str | None = None) -> logging.Logger:
    """Return the application logger, or a named child of it."""
    return logging.getLogger(name or LOGGER_NAME)


def configure_logging(level: int = logging.INFO) -> None:
    """Attach a console handler and format to the root logger."""
    logging.basicConfig(level=level, format=LOG_FORMAT)
