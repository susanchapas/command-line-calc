"""Pure arithmetic operations for the calculator."""

from .exceptions import OperationError


def add(left: float, right: float) -> float:
    return left + right


def subtract(left: float, right: float) -> float:
    return left - right


def multiply(left: float, right: float) -> float:
    return left * right


def divide(left: float, right: float) -> float:
    if right == 0:
        raise OperationError("Cannot divide by zero.")
    return left / right


def power(left: float, right: float) -> float:
    if left == 0 and right < 0:
        raise OperationError("Cannot raise zero to a negative power.")
    result = left**right
    if isinstance(result, complex):
        raise OperationError("Result is not a real number.")
    return result


def root(left: float, right: float) -> float:
    if right == 0:
        raise OperationError("Cannot take the zeroth root.")
    if left < 0:
        raise OperationError("Cannot take the root of a negative number.")
    if left == 0 and right < 0:
        raise OperationError("Cannot take a negative root of zero.")
    return left ** (1 / right)


def modulus(left: float, right: float) -> float:
    if right == 0:
        raise OperationError("Cannot take the modulus by zero.")
    return left % right


def int_divide(left: float, right: float) -> float:
    if right == 0:
        raise OperationError("Cannot divide by zero.")
    return left // right


def percentage(left: float, right: float) -> float:
    if right == 0:
        raise OperationError("Cannot take a percentage of zero.")
    return left / right * 100


def abs_diff(left: float, right: float) -> float:
    return abs(left - right)
