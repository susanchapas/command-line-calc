"""Logging setup shared by the application."""

import logging
from pathlib import Path

LOGGER_NAME = "calculator"
LOG_FORMAT = "%(asctime)s %(name)s: %(message)s"


def get_logger(name: str | None = None) -> logging.Logger:
    """Return the application logger, or a named child of it."""
    return logging.getLogger(name or LOGGER_NAME)


def configure_logging(level: int = logging.INFO, log_file: Path | str | None = None) -> None:
    """Attach a console handler, plus a file handler when ``log_file`` is given."""
    handlers: list[logging.Handler] = [logging.StreamHandler()]

    if log_file is not None:
        path = Path(log_file)
        path.parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(path, encoding="utf-8"))

    logging.basicConfig(level=level, format=LOG_FORMAT, handlers=handlers, force=True)
