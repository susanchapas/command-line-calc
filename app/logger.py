"""Logging setup shared by the application."""

import logging
from pathlib import Path

from .calculator_config import DEFAULT_ENCODING

LOGGER_NAME = "calculator"
LOG_FORMAT = "%(asctime)s %(levelname)s %(name)s: %(message)s"
CONSOLE_LEVEL = logging.WARNING


def get_logger(name: str | None = None) -> logging.Logger:
    """Return the application logger, or a named child of it."""
    return logging.getLogger(name or LOGGER_NAME)


def configure_logging(
    level: int = logging.INFO,
    log_file: Path | str | None = None,
    encoding: str = DEFAULT_ENCODING,
) -> None:
    """Record ``level`` and above in ``log_file``, warnings and above on the console.

    Holding the console to :data:`CONSOLE_LEVEL` keeps the REPL readable while
    the file still captures every calculation and history change.
    """
    console = logging.StreamHandler()
    console.setLevel(CONSOLE_LEVEL)
    handlers: list[logging.Handler] = [console]

    if log_file is not None:
        path = Path(log_file)
        path.parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(path, encoding=encoding))

    logging.basicConfig(level=level, format=LOG_FORMAT, handlers=handlers, force=True)
