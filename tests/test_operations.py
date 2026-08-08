import pytest

from app.exceptions import OperationError
from app.operations import (
    abs_diff,
    add,
    divide,
    int_divide,
    modulus,
    multiply,
    percentage,
    power,
    root,
    subtract,
)


@pytest.mark.parametrize(
    ("func", "left", "right", "expected"),
    [
        (add, 1, 2, 3),
        (add, -4, 7, 3),
        (subtract, 7, 2, 5),
        (subtract, -4, 7, -11),
        (multiply, 3, 4, 12),
        (multiply, 2.5, 0.5, 1.25),
        (divide, 8, 2, 4),
        (divide, -9, 3, -3),
        (power, 2, 10, 1024),
        (power, -2, 2, 4),
        (root, 9, 2, 3),
        (root, 27, 3, 3),
        (modulus, 7, 3, 1),
        (modulus, -7, 3, 2),
        (int_divide, 7, 2, 3),
        (int_divide, -7, 2, -4),
        (percentage, 25, 200, 12.5),
        (percentage, -5, 20, -25),
        (abs_diff, 3, 10, 7),
        (abs_diff, 10, 3, 7),
    ],
)
def test_operations(func, left, right, expected):
    assert func(left, right) == pytest.approx(expected)


@pytest.mark.parametrize(
    ("func", "left", "right", "expected"),
    [
        (power, 2, -2, 0.25),
        (power, -2, -3, -0.125),
        (power, 5, 0, 1),
        (power, 0, 5, 0),
        (power, 4, 0.5, 2),
        (root, 8, -3, 0.5),
        (root, 0, 2, 0),
        (root, 5, 1, 5),
        (modulus, 7, -3, -2),
        (modulus, 7.5, 2, 1.5),
        (int_divide, 7, -2, -4),
        (int_divide, -7, -2, 3),
        (percentage, 0, 5, 0),
        (percentage, 50, 50, 100),
        (abs_diff, -3, -10, 7),
        (abs_diff, 4, 4, 0),
        (divide, 1, 4, 0.25),
        (subtract, 5, 5, 0),
    ],
)
def test_operation_edge_cases(func, left, right, expected):
    assert func(left, right) == pytest.approx(expected)


def test_results_are_not_rounded():
    """Rounding belongs to the calculator, which applies the configured precision."""
    assert add(0.1, 0.2) == 0.30000000000000004


@pytest.mark.parametrize(
    ("func", "left", "right", "message"),
    [
        (divide, 1, 0, "Cannot divide by zero."),
        (int_divide, 7, 0, "Cannot divide by zero."),
        (modulus, 7, 0, "modulus by zero"),
        (percentage, 7, 0, "percentage of zero"),
        (power, -2, 0.5, "not a real number"),
        (power, 0, -1, "zero to a negative power"),
        (root, 8, 0, "zeroth root"),
        (root, -8, 2, "negative number"),
        (root, 0, -1, "negative root of zero"),
    ],
)
def test_invalid_operands_raise_operation_error(func, left, right, message):
    with pytest.raises(OperationError, match=message):
        func(left, right)


@pytest.mark.parametrize(
    ("func", "left", "right"),
    [(power, 1e10, 1e10), (root, 0.5, -1e-300)],
)
def test_overflowing_results_raise_overflow_error(func, left, right):
    with pytest.raises(OverflowError):
        func(left, right)
