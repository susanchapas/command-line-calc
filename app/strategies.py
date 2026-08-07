"""Strategy pattern: interchangeable operation execution strategies.

Each strategy wraps a single arithmetic operation behind a common
``execute`` interface, so the calculator can swap operations at runtime
without knowing how any of them are implemented.
"""

from abc import ABC, abstractmethod
from typing import ClassVar

from . import operations


class OperationStrategy(ABC):
    """Common interface for a runtime-selectable arithmetic operation."""

    name: ClassVar[str]
    symbol: ClassVar[str]

    @abstractmethod
    def execute(self, left: float, right: float) -> float:
        """Return the result of applying this operation to two operands."""


class AddStrategy(OperationStrategy):
    name = "add"
    symbol = "+"

    def execute(self, left: float, right: float) -> float:
        return operations.add(left, right)


class SubtractStrategy(OperationStrategy):
    name = "subtract"
    symbol = "-"

    def execute(self, left: float, right: float) -> float:
        return operations.subtract(left, right)


class MultiplyStrategy(OperationStrategy):
    name = "multiply"
    symbol = "*"

    def execute(self, left: float, right: float) -> float:
        return operations.multiply(left, right)


class DivideStrategy(OperationStrategy):
    name = "divide"
    symbol = "/"

    def execute(self, left: float, right: float) -> float:
        return operations.divide(left, right)


class PowerStrategy(OperationStrategy):
    name = "power"
    symbol = "^"

    def execute(self, left: float, right: float) -> float:
        return operations.power(left, right)


class RootStrategy(OperationStrategy):
    name = "root"
    symbol = "√"

    def execute(self, left: float, right: float) -> float:
        return operations.root(left, right)
