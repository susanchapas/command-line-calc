"""Immutable record of a single completed calculation."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Calculation:
    operation: str
    a: float
    b: float
    result: float

    def render(self, symbol: str) -> str:
        return f"{self.a:g} {symbol} {self.b:g} = {self.result:g}"
