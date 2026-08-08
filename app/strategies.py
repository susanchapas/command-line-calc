"""Strategy pattern: interchangeable operation execution strategies.

Each strategy wraps a single arithmetic operation behind a common
``execute`` interface, so the calculator can swap operations at runtime
without knowing how any of them are implemented.

Strategies declare their own name, symbol, and help text and opt into the
calculator with the :func:`register` decorator, so defining a decorated class
is the only step needed to add an operation: the factory can build it and the
``help`` menu describes it without either being edited.
"""

from abc import ABC, abstractmethod
from typing import ClassVar

from . import operations

OPERATIONS: dict[str, type["OperationStrategy"]] = {}


class OperationStrategy(ABC):
    """Common interface for a runtime-selectable arithmetic operation."""

    name: ClassVar[str]
    symbol: ClassVar[str]
    description: ClassVar[str]

    @abstractmethod
    def execute(self, left: float, right: float) -> float:
        """Return the result of applying this operation to two operands."""


def register(strategy: type[OperationStrategy]) -> type[OperationStrategy]:
    """Decorator that adds ``strategy`` to :data:`OPERATIONS` under its name."""
    OPERATIONS[strategy.name] = strategy
    return strategy


@register
class AddStrategy(OperationStrategy):
    name = "add"
    symbol = "+"
    description = "a plus b"

    def execute(self, left: float, right: float) -> float:
        return operations.add(left, right)


@register
class SubtractStrategy(OperationStrategy):
    name = "subtract"
    symbol = "-"
    description = "a minus b"

    def execute(self, left: float, right: float) -> float:
        return operations.subtract(left, right)


@register
class MultiplyStrategy(OperationStrategy):
    name = "multiply"
    symbol = "*"
    description = "a times b"

    def execute(self, left: float, right: float) -> float:
        return operations.multiply(left, right)


@register
class DivideStrategy(OperationStrategy):
    name = "divide"
    symbol = "/"
    description = "a divided by b"

    def execute(self, left: float, right: float) -> float:
        return operations.divide(left, right)


@register
class PowerStrategy(OperationStrategy):
    name = "power"
    symbol = "^"
    description = "a raised to the power of b"

    def execute(self, left: float, right: float) -> float:
        return operations.power(left, right)


@register
class RootStrategy(OperationStrategy):
    name = "root"
    symbol = "√"
    description = "the bth root of a"

    def execute(self, left: float, right: float) -> float:
        return operations.root(left, right)


@register
class ModulusStrategy(OperationStrategy):
    name = "modulus"
    symbol = "%"
    description = "the remainder of a divided by b"

    def execute(self, left: float, right: float) -> float:
        return operations.modulus(left, right)


@register
class IntDivideStrategy(OperationStrategy):
    name = "int_divide"
    symbol = "//"
    description = "a divided by b, fractional part discarded"

    def execute(self, left: float, right: float) -> float:
        return operations.int_divide(left, right)


@register
class PercentageStrategy(OperationStrategy):
    name = "percent"
    symbol = "%of"
    description = "a as a percentage of b"

    def execute(self, left: float, right: float) -> float:
        return operations.percentage(left, right)


@register
class AbsDiffStrategy(OperationStrategy):
    name = "abs_diff"
    symbol = "|Δ|"
    description = "the absolute difference between a and b"

    def execute(self, left: float, right: float) -> float:
        return operations.abs_diff(left, right)
