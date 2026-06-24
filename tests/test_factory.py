import pytest

from calculator.factory import OperationFactory
from calculator.strategies import AddStrategy, RootStrategy


def test_create_returns_matching_strategy():
    factory = OperationFactory()

    assert isinstance(factory.create("add"), AddStrategy)
    assert isinstance(factory.create("root"), RootStrategy)


def test_create_normalizes_input():
    factory = OperationFactory()

    assert isinstance(factory.create("  ADD  "), AddStrategy)


def test_create_rejects_unknown_operation():
    factory = OperationFactory()

    with pytest.raises(ValueError, match="Choose one of"):
        factory.create("modulo")


def test_available_operations():
    assert OperationFactory.available_operations() == (
        "add",
        "subtract",
        "multiply",
        "divide",
        "power",
        "root",
    )


def test_symbol_lookup():
    assert OperationFactory.symbol("multiply") == "*"


def test_describe_operations():
    assert OperationFactory.describe_operations() == (
        "add (+), subtract (-), multiply (*), divide (/), power (^), root (√)"
    )
