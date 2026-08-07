"""Configuration management via environment variables and ``dotenv``.

Settings are read from the process environment (optionally seeded from a
``.env`` file) and validated eagerly so misconfiguration fails fast with a
clear message instead of surfacing deep inside the application.
"""

import codecs
import math
import os
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

from .exceptions import ConfigError

DEFAULT_LOG_DIR = "logs"
DEFAULT_HISTORY_DIR = "history"
DEFAULT_LOG_FILE = "calculator.log"
DEFAULT_HISTORY_FILE = "calculator_history.csv"
DEFAULT_AUTO_SAVE = "true"
DEFAULT_MAX_HISTORY_SIZE = "100"
DEFAULT_PRECISION = "10"
DEFAULT_MAX_INPUT_VALUE = "1e12"
DEFAULT_ENCODING = "utf-8"

_TRUE_VALUES = {"1", "true", "yes", "on"}
_FALSE_VALUES = {"0", "false", "no", "off"}


def _parse_bool(raw_value: str) -> bool:
    value = raw_value.strip().lower()
    if value in _TRUE_VALUES:
        return True
    if value in _FALSE_VALUES:
        return False
    raise ConfigError(f"Expected a boolean for auto-save, got {raw_value!r}.")


def _parse_int(raw_value: str, label: str, minimum: int) -> int:
    try:
        value = int(raw_value)
    except ValueError as exc:
        raise ConfigError(f"Expected an integer for {label}, got {raw_value!r}.") from exc
    if value < minimum:
        raise ConfigError(f"Expected {label} of at least {minimum}, got {value}.")
    return value


def _parse_positive_float(raw_value: str, label: str) -> float:
    try:
        value = float(raw_value)
    except ValueError as exc:
        raise ConfigError(f"Expected a number for {label}, got {raw_value!r}.") from exc
    if not math.isfinite(value) or value <= 0:
        raise ConfigError(f"Expected a positive, finite {label}, got {raw_value!r}.")
    return value


def _parse_encoding(raw_value: str) -> str:
    try:
        codecs.lookup(raw_value)
    except LookupError as exc:
        raise ConfigError(f"Unknown encoding for file operations: {raw_value!r}.") from exc
    return raw_value


@dataclass(frozen=True, slots=True)
class CalculatorConfig:
    """Validated application settings.

    File paths are derived from the two base directories, so a deployment
    only has to point ``log_dir``/``history_dir`` somewhere writable. A file
    name given as an absolute path overrides its base directory.
    """

    log_dir: Path = Path(DEFAULT_LOG_DIR)
    history_dir: Path = Path(DEFAULT_HISTORY_DIR)
    max_history_size: int = int(DEFAULT_MAX_HISTORY_SIZE)
    auto_save: bool = True
    precision: int = int(DEFAULT_PRECISION)
    max_input_value: float = float(DEFAULT_MAX_INPUT_VALUE)
    default_encoding: str = DEFAULT_ENCODING
    log_filename: str = DEFAULT_LOG_FILE
    history_filename: str = DEFAULT_HISTORY_FILE

    @property
    def log_file(self) -> Path:
        return self.log_dir / self.log_filename

    @property
    def history_file(self) -> Path:
        return self.history_dir / self.history_filename

    def ensure_directories(self) -> None:
        """Create the configured base directories if they do not exist yet."""
        for directory in (self.log_dir, self.history_dir):
            directory.mkdir(parents=True, exist_ok=True)

    @classmethod
    def from_env(cls, env: Mapping[str, str] | None = None) -> "CalculatorConfig":
        if env is None:
            load_dotenv()
            env = os.environ

        return cls(
            log_dir=Path(env.get("CALCULATOR_LOG_DIR", DEFAULT_LOG_DIR)),
            history_dir=Path(env.get("CALCULATOR_HISTORY_DIR", DEFAULT_HISTORY_DIR)),
            max_history_size=_parse_int(
                env.get("CALCULATOR_MAX_HISTORY_SIZE", DEFAULT_MAX_HISTORY_SIZE),
                "max history size",
                minimum=1,
            ),
            auto_save=_parse_bool(env.get("CALCULATOR_AUTO_SAVE", DEFAULT_AUTO_SAVE)),
            precision=_parse_int(
                env.get("CALCULATOR_PRECISION", DEFAULT_PRECISION),
                "precision",
                minimum=0,
            ),
            max_input_value=_parse_positive_float(
                env.get("CALCULATOR_MAX_INPUT_VALUE", DEFAULT_MAX_INPUT_VALUE),
                "max input value",
            ),
            default_encoding=_parse_encoding(
                env.get("CALCULATOR_DEFAULT_ENCODING", DEFAULT_ENCODING)
            ),
            log_filename=env.get("CALCULATOR_LOG_FILE", DEFAULT_LOG_FILE),
            history_filename=env.get("CALCULATOR_HISTORY_FILE", DEFAULT_HISTORY_FILE),
        )
