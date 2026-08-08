"""Immutable record of a single completed calculation."""

from dataclasses import dataclass, field
from datetime import datetime


def now() -> datetime:
    """Return the current local time, with its UTC offset attached."""
    return datetime.now().astimezone()


def parse_timestamp(value: str) -> datetime | None:
    """Return the datetime ``value`` denotes, or ``None`` if it is not ISO 8601."""
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


@dataclass(frozen=True, slots=True)
class Calculation:
    """A completed calculation and the moment it was made.

    ``timestamp`` is excluded from equality so two calculations compare by the
    arithmetic they record. It is ``None`` only for history loaded from a CSV
    written before the column existed.
    """

    operation: str
    a: float
    b: float
    result: float
    timestamp: datetime | None = field(default_factory=now, compare=False)

    def render(self, symbol: str) -> str:
        return f"{self.a:g} {symbol} {self.b:g} = {self.result:g}"
