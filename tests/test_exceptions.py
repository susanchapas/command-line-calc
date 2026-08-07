import pytest

from app.exceptions import CalculatorError, ConfigError, HistoryError, ValidationError


@pytest.mark.parametrize("error_type", [ConfigError, HistoryError, ValidationError])
def test_every_error_shares_the_calculator_base(error_type):
    with pytest.raises(CalculatorError, match="boom"):
        raise error_type("boom")
