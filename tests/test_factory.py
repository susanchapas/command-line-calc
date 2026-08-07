import pytest

from app.exceptions import OperationError
from app.factory import OperationFactory
from app.strategies import AbsDiffStrategy, AddStrategy, RootStrategy


def test_create_returns_matching_strategy():
    factory = OperationFactory()

    assert isinstance(factory.create("add"), AddStrategy)
    assert isinstance(factory.create("root"), RootStrategy)
    assert isinstance(factory.create("abs_diff"), AbsDiffStrategy)


def test_create_normalizes_input():
    factory = OperationFactory()

    assert isinstance(factory.create("  ADD  "), AddStrategy)


def test_create_rejects_unknown_operation():
    factory = OperationFactory()

    with pytest.raises(OperationError, match="Choose one of"):
        factory.create("logarithm")


def test_available_operations():
    assert OperationFactory.available_operations() == (
        "add",
        "subtract",
        "multiply",
        "divide",
        "power",
        "root",
        "modulus",
        "int_divide",
        "percent",
        "abs_diff",
    )


def test_symbol_lookup():
    assert OperationFactory.symbol("multiply") == "*"


def test_describe_operations():
    assert OperationFactory.describe_operations() == (
        "add (+), subtract (-), multiply (*), divide (/), power (^), root (√), "
        "modulus (%), int_divide (//), percent (%of), abs_diff (|Δ|)"
    )
