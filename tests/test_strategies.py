import pytest

from app.strategies import (
    AbsDiffStrategy,
    AddStrategy,
    DivideStrategy,
    IntDivideStrategy,
    ModulusStrategy,
    MultiplyStrategy,
    OperationStrategy,
    PercentageStrategy,
    PowerStrategy,
    RootStrategy,
    SubtractStrategy,
)


@pytest.mark.parametrize(
    ("strategy_cls", "name", "symbol", "left", "right", "expected"),
    [
        (AddStrategy, "add", "+", 1, 2, 3),
        (SubtractStrategy, "subtract", "-", 7, 2, 5),
        (MultiplyStrategy, "multiply", "*", 3, 4, 12),
        (DivideStrategy, "divide", "/", 8, 2, 4),
        (PowerStrategy, "power", "^", 2, 5, 32),
        (RootStrategy, "root", "√", 16, 2, 4),
        (ModulusStrategy, "modulus", "%", 9, 4, 1),
        (IntDivideStrategy, "int_divide", "//", 9, 4, 2),
        (PercentageStrategy, "percentage", "%of", 30, 150, 20),
        (AbsDiffStrategy, "abs_diff", "|Δ|", 4, 9, 5),
    ],
)
def test_strategy_metadata_and_execution(strategy_cls, name, symbol, left, right, expected):
    strategy = strategy_cls()

    assert strategy.name == name
    assert strategy.symbol == symbol
    assert strategy.execute(left, right) == pytest.approx(expected)


def test_operation_strategy_is_abstract():
    with pytest.raises(TypeError):
        OperationStrategy()
