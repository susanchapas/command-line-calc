import pytest

from calculator.strategies import (
    AddStrategy,
    DivideStrategy,
    MultiplyStrategy,
    OperationStrategy,
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
