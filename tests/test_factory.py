import pytest

from app.exceptions import OperationError
from app.factory import OperationFactory
from app.operations import AbsDiff, Add, Root


def test_create_returns_matching_operation():
    factory = OperationFactory()

    assert isinstance(factory.create("add"), Add)
    assert isinstance(factory.create("root"), Root)
    assert isinstance(factory.create("abs_diff"), AbsDiff)


def test_create_normalizes_input():
    factory = OperationFactory()

    assert isinstance(factory.create("  ADD  "), Add)


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


def test_register_makes_the_operation_available(extra_operation):
    factory = OperationFactory()

    assert "triple_sum" in factory.available_operations()
    assert isinstance(factory.create("triple_sum"), extra_operation)
    assert factory.symbol("triple_sum") == "+++"


def test_unregistering_removes_the_operation():
    assert "triple_sum" not in OperationFactory.available_operations()
