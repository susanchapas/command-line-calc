import pytest

from calculator.calculations import Addition, CalculationFactory, Division, Multiplication, Subtraction


@pytest.mark.parametrize(
    ("operation", "expected_type", "left", "right", "expected_result", "expected_render"),
    [
        ("add", Addition, 1, 2, 3, "1 + 2 = 3"),
        ("subtract", Subtraction, 7, 2, 5, "7 - 2 = 5"),
        ("multiply", Multiplication, 3, 4, 12, "3 * 4 = 12"),
        ("divide", Division, 8, 2, 4, "8 / 2 = 4"),
    ],
)
def test_factory_creates_expected_calculation(operation, expected_type, left, right, expected_result, expected_render):
    factory = CalculationFactory()

    calculation = factory.create(operation, left, right)

    assert isinstance(calculation, expected_type)
    assert calculation.execute() == expected_result
    assert calculation.render() == expected_render


def test_factory_rejects_unknown_operation():
    factory = CalculationFactory()

    with pytest.raises(ValueError, match="Choose one of"):
        factory.create("mod", 1, 2)


def test_factory_lists_supported_operations():
    assert CalculationFactory.available_operations() == ("add", "subtract", "multiply", "divide")
    assert CalculationFactory.describe_operations() == "add (+), subtract (-), multiply (*), divide (/)"