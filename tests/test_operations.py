import pytest

from app.exceptions import OperationError
from app.operations import (
    AbsDiff,
    Add,
    Divide,
    IntDivide,
    Modulus,
    Multiply,
    Operation,
    Percentage,
    Power,
    Root,
    Subtract,
)


@pytest.mark.parametrize(
    ("operation_cls", "name", "symbol"),
    [
        (Add, "add", "+"),
        (Subtract, "subtract", "-"),
        (Multiply, "multiply", "*"),
        (Divide, "divide", "/"),
        (Power, "power", "^"),
        (Root, "root", "√"),
        (Modulus, "modulus", "%"),
        (IntDivide, "int_divide", "//"),
        (Percentage, "percent", "%of"),
        (AbsDiff, "abs_diff", "|Δ|"),
    ],
)
def test_operation_metadata(operation_cls, name, symbol):
    assert operation_cls.name == name
    assert operation_cls.symbol == symbol


@pytest.mark.parametrize(
    ("operation_cls", "left", "right", "expected"),
    [
        (Add, 1, 2, 3),
        (Add, -4, 7, 3),
        (Subtract, 7, 2, 5),
        (Subtract, -4, 7, -11),
        (Multiply, 3, 4, 12),
        (Multiply, 2.5, 0.5, 1.25),
        (Divide, 8, 2, 4),
        (Divide, -9, 3, -3),
        (Power, 2, 10, 1024),
        (Power, -2, 2, 4),
        (Root, 9, 2, 3),
        (Root, 27, 3, 3),
        (Modulus, 7, 3, 1),
        (Modulus, -7, 3, 2),
        (IntDivide, 7, 2, 3),
        (IntDivide, -7, 2, -4),
        (Percentage, 25, 200, 12.5),
        (Percentage, -5, 20, -25),
        (AbsDiff, 3, 10, 7),
        (AbsDiff, 10, 3, 7),
    ],
)
def test_operations(operation_cls, left, right, expected):
    assert operation_cls().execute(left, right) == pytest.approx(expected)


@pytest.mark.parametrize(
    ("operation_cls", "left", "right", "expected"),
    [
        (Power, 2, -2, 0.25),
        (Power, -2, -3, -0.125),
        (Power, 5, 0, 1),
        (Power, 0, 5, 0),
        (Power, 4, 0.5, 2),
        (Root, 8, -3, 0.5),
        (Root, 0, 2, 0),
        (Root, 5, 1, 5),
        (Root, -8, 3, -2),
        (Root, -8, -3, -0.5),
        (Modulus, 7, -3, -2),
        (Modulus, 7.5, 2, 1.5),
        (IntDivide, 7, -2, -4),
        (IntDivide, -7, -2, 3),
        (Percentage, 0, 5, 0),
        (Percentage, 50, 50, 100),
        (AbsDiff, -3, -10, 7),
        (AbsDiff, 4, 4, 0),
        (Divide, 1, 4, 0.25),
        (Subtract, 5, 5, 0),
    ],
)
def test_operation_edge_cases(operation_cls, left, right, expected):
    assert operation_cls().execute(left, right) == pytest.approx(expected)


def test_results_are_not_rounded():
    """Rounding belongs to the calculator, which applies the configured precision."""
    assert Add().execute(0.1, 0.2) == 0.30000000000000004


@pytest.mark.parametrize(
    ("operation_cls", "left", "right", "message"),
    [
        (Divide, 1, 0, "Cannot divide by zero."),
        (IntDivide, 7, 0, "Cannot divide by zero."),
        (Modulus, 7, 0, "modulus by zero"),
        (Percentage, 7, 0, "zero as the base"),
        (Power, -2, 0.5, "not a real number"),
        (Power, 0, -1, "zero to a negative power"),
        (Root, 8, 0, "zeroth root"),
        (Root, -8, 2, "odd integer roots"),
        (Root, -8, 2.5, "odd integer roots"),
        (Root, 0, -1, "negative root of zero"),
    ],
)
def test_invalid_operands_raise_operation_error(operation_cls, left, right, message):
    with pytest.raises(OperationError, match=message):
        operation_cls().execute(left, right)


@pytest.mark.parametrize(
    ("operation_cls", "left", "right"),
    [(Power, 1e10, 1e10), (Root, 0.5, -1e-300)],
)
def test_overflowing_results_raise_overflow_error(operation_cls, left, right):
    with pytest.raises(OverflowError):
        operation_cls().execute(left, right)


def test_operation_is_abstract():
    with pytest.raises(TypeError):
        Operation()
