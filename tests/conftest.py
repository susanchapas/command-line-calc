import pytest

from app.calculator import Calculator
from app.calculator_config import CalculatorConfig
from app.strategies import OPERATIONS, OperationStrategy, register


@pytest.fixture
def extra_operation():
    """Register an operation for one test, then unregister it."""

    @register
    class TripleSumStrategy(OperationStrategy):
        name = "triple_sum"
        symbol = "+++"
        description = "a plus b, tripled"

        def execute(self, left, right):
            return (left + right) * 3

    yield TripleSumStrategy
    del OPERATIONS[TripleSumStrategy.name]


@pytest.fixture
def config(tmp_path):
    return CalculatorConfig(
        log_dir=tmp_path / "logs",
        history_dir=tmp_path,
        auto_save=False,
        history_filename="history.csv",
    )


@pytest.fixture
def calculator(config):
    return Calculator(config=config, observers=[])
