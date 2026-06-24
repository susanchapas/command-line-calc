import pytest

from calculator.calculator import Calculator
from calculator.config import CalculatorConfig


@pytest.fixture
def config(tmp_path):
    return CalculatorConfig(
        history_file=tmp_path / "history.csv",
        auto_save=False,
        max_history_size=100,
    )


@pytest.fixture
def calculator(config):
    return Calculator(config=config, observers=[])
