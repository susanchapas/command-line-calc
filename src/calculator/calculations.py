"""Calculation objects and factory for the calculator application."""

from dataclasses import dataclass
from typing import ClassVar

from .operations import add, divide, multiply, subtract


@dataclass(frozen=True, slots=True)
class Calculation:
    """Base calculation that knows how to format itself."""

    left: float
    right: float

    name: ClassVar[str]
    symbol: ClassVar[str]

    def execute(self) -> float:
        raise NotImplementedError  # pragma: no cover

    def render(self, result: float | None = None) -> str:
        if result is None:
            result = self.execute()

        return f"{self.left:g} {self.symbol} {self.right:g} = {result:g}"


@dataclass(frozen=True, slots=True)
class Addition(Calculation):
    name: ClassVar[str] = "add"
    symbol: ClassVar[str] = "+"

    def execute(self) -> float:
        return add(self.left, self.right)


@dataclass(frozen=True, slots=True)
class Subtraction(Calculation):
    name: ClassVar[str] = "subtract"
    symbol: ClassVar[str] = "-"

    def execute(self) -> float:
        return subtract(self.left, self.right)


@dataclass(frozen=True, slots=True)
class Multiplication(Calculation):
    name: ClassVar[str] = "multiply"
    symbol: ClassVar[str] = "*"

    def execute(self) -> float:
        return multiply(self.left, self.right)


@dataclass(frozen=True, slots=True)
class Division(Calculation):
    name: ClassVar[str] = "divide"
    symbol: ClassVar[str] = "/"

    def execute(self) -> float:
        return divide(self.left, self.right)


class CalculationFactory:
    """Build calculation objects from user-entered operation names."""

    _registry: ClassVar[dict[str, type[Calculation]]] = {
        Addition.name: Addition,
        Subtraction.name: Subtraction,
        Multiplication.name: Multiplication,
        Division.name: Division,
    }

    @classmethod
    def available_operations(cls) -> tuple[str, ...]:
        return tuple(cls._registry)

    @classmethod
    def describe_operations(cls) -> str:
        return ", ".join(
            f"{operation} ({cls._registry[operation].symbol})" for operation in cls.available_operations()
        )

    def create(self, operation_name: str, left: float, right: float) -> Calculation:
        try:
            calculation_type = self._registry[operation_name.strip().lower()]
        except KeyError as exc:
            valid_operations = ", ".join(self.available_operations())
            raise ValueError(f"Choose one of: {valid_operations}.") from exc

        return calculation_type(left=left, right=right)