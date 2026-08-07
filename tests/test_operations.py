import pytest

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


def test_divide_by_zero():
    with pytest.raises(ZeroDivisionError, match="Cannot divide by zero."):
        divide(1, 0)


def test_power_rejects_complex_result():
    with pytest.raises(ValueError, match="not a real number"):
        power(-2, 0.5)


def test_root_rejects_zeroth_root():
    with pytest.raises(ZeroDivisionError, match="zeroth root"):
        root(8, 0)


def test_root_rejects_negative_radicand():
    with pytest.raises(ValueError, match="negative number"):
        root(-8, 2)


def test_modulus_rejects_zero_divisor():
    with pytest.raises(ZeroDivisionError, match="modulus of zero"):
        modulus(7, 0)


def test_int_divide_rejects_zero_divisor():
    with pytest.raises(ZeroDivisionError, match="Cannot divide by zero."):
        int_divide(7, 0)


def test_percentage_rejects_zero_whole():
    with pytest.raises(ZeroDivisionError, match="percentage of zero"):
        percentage(7, 0)
