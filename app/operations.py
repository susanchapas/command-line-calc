"""Arithmetic operations and the registry the factory builds from.

Each operation declares its own name, symbol, and help text and opts into the
calculator with the :func:`register` decorator, so defining a decorated class is
the only step needed to add an operation: the factory can build it and the
``help`` menu describes it without either being edited.
"""

from abc import ABC, abstractmethod
from typing import ClassVar

from .exceptions import OperationError

OPERATIONS: dict[str, type["Operation"]] = {}


class Operation(ABC):
    """A two-operand arithmetic operation."""

    name: ClassVar[str]
    symbol: ClassVar[str]
    description: ClassVar[str]

    @abstractmethod
    def execute(self, left: float, right: float) -> float:
        """Return the result of applying this operation to two operands."""


def register(operation: type[Operation]) -> type[Operation]:
    """Decorator that adds ``operation`` to :data:`OPERATIONS` under its name."""
    OPERATIONS[operation.name] = operation
    return operation


@register
class Add(Operation):
    name = "add"
    symbol = "+"
    description = "a plus b"

    def execute(self, left: float, right: float) -> float:
        return left + right


@register
class Subtract(Operation):
    name = "subtract"
    symbol = "-"
    description = "a minus b"

    def execute(self, left: float, right: float) -> float:
        return left - right


@register
class Multiply(Operation):
    name = "multiply"
    symbol = "*"
    description = "a times b"

    def execute(self, left: float, right: float) -> float:
        return left * right


@register
class Divide(Operation):
    name = "divide"
    symbol = "/"
    description = "a divided by b"

    def execute(self, left: float, right: float) -> float:
        if right == 0:
            raise OperationError("Cannot divide by zero.")
        return left / right


@register
class Power(Operation):
    name = "power"
    symbol = "^"
    description = "a raised to the power of b"

    def execute(self, left: float, right: float) -> float:
        if left == 0 and right < 0:
            raise OperationError("Cannot raise zero to a negative power.")
        result = left**right
        if isinstance(result, complex):
            raise OperationError("Result is not a real number.")
        return result


@register
class Root(Operation):
    name = "root"
    symbol = "√"
    description = "the bth root of a"

    def execute(self, left: float, right: float) -> float:
        if right == 0:
            raise OperationError("Cannot take the zeroth root.")
        if left < 0:
            if right != int(right) or int(right) % 2 == 0:
                raise OperationError(
                    "Only odd integer roots of a negative number are real."
                )
            return -((-left) ** (1 / right))
        if left == 0 and right < 0:
            raise OperationError("Cannot take a negative root of zero.")
        return left ** (1 / right)


@register
class Modulus(Operation):
    name = "modulus"
    symbol = "%"
    description = "the remainder of a divided by b"

    def execute(self, left: float, right: float) -> float:
        if right == 0:
            raise OperationError("Cannot take the modulus by zero.")
        return left % right


@register
class IntDivide(Operation):
    name = "int_divide"
    symbol = "//"
    description = "a divided by b, fractional part discarded"

    def execute(self, left: float, right: float) -> float:
        if right == 0:
            raise OperationError("Cannot divide by zero.")
        return left // right


@register
class Percentage(Operation):
    name = "percent"
    symbol = "%of"
    description = "a as a percentage of b"

    def execute(self, left: float, right: float) -> float:
        if right == 0:
            raise OperationError("Cannot take a percentage with zero as the base.")
        return left / right * 100


@register
class AbsDiff(Operation):
    name = "abs_diff"
    symbol = "|Δ|"
    description = "the absolute difference between a and b"

    def execute(self, left: float, right: float) -> float:
        return abs(left - right)
