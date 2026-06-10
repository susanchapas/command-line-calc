import pytest

from calculator.operations import add, divide, multiply, subtract


@pytest.mark.parametrize(
    ("left", "right", "expected"),
    [
        (1, 2, 3),
        (-4, 7, 3),
        (2.5, 0.5, 3.0),
    ],
)
def test_add(left, right, expected):
    assert add(left, right) == expected


@pytest.mark.parametrize(
    ("left", "right", "expected"),
    [
        (7, 2, 5),
        (-4, 7, -11),
        (2.5, 0.5, 2.0),
    ],
)
def test_subtract(left, right, expected):
    assert subtract(left, right) == expected


@pytest.mark.parametrize(
    ("left", "right", "expected"),
    [
        (3, 2, 6),
        (-4, 7, -28),
        (2.5, 0.5, 1.25),
    ],
)
def test_multiply(left, right, expected):
    assert multiply(left, right) == expected


@pytest.mark.parametrize(
    ("left", "right", "expected"),
    [
        (8, 2, 4),
        (-9, 3, -3),
        (5.0, 2.0, 2.5),
    ],
)
def test_divide(left, right, expected):
    assert divide(left, right) == expected


def test_divide_by_zero():
    with pytest.raises(ZeroDivisionError, match="Cannot divide by zero."):
        divide(1, 0)
