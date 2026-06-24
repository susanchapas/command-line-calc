"""Configuration management via environment variables and ``dotenv``.

Settings are read from the process environment (optionally seeded from a
``.env`` file) and validated eagerly so misconfiguration fails fast with a
clear message instead of surfacing deep inside the application.
"""

import os
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

DEFAULT_HISTORY_FILE = "calculator_history.csv"
DEFAULT_AUTO_SAVE = "true"
DEFAULT_MAX_HISTORY = "100"

_TRUE_VALUES = {"1", "true", "yes", "on"}
_FALSE_VALUES = {"0", "false", "no", "off"}


class ConfigError(Exception):
    """Raised when an environment value cannot be parsed or is invalid."""


def _parse_bool(raw_value: str) -> bool:
    value = raw_value.strip().lower()
    if value in _TRUE_VALUES:
        return True
    if value in _FALSE_VALUES:
        return False
    raise ConfigError(f"Expected a boolean for auto-save, got {raw_value!r}.")


def _parse_positive_int(raw_value: str) -> int:
    try:
        value = int(raw_value)
    except ValueError as exc:
        raise ConfigError(f"Expected an integer for max history, got {raw_value!r}.") from exc
    if value <= 0:
        raise ConfigError(f"Max history must be positive, got {value}.")
    return value


@dataclass(frozen=True, slots=True)
class CalculatorConfig:
    history_file: Path
    auto_save: bool
    max_history_size: int

    @classmethod
    def from_env(cls, env: Mapping[str, str] | None = None) -> "CalculatorConfig":
        if env is None:
            load_dotenv()
            env = os.environ

        return cls(
            history_file=Path(env.get("CALCULATOR_HISTORY_FILE", DEFAULT_HISTORY_FILE)),
            auto_save=_parse_bool(env.get("CALCULATOR_AUTO_SAVE", DEFAULT_AUTO_SAVE)),
            max_history_size=_parse_positive_int(env.get("CALCULATOR_MAX_HISTORY", DEFAULT_MAX_HISTORY)),
        )
