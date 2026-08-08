import pytest

from app.calculator import Calculator
from app.calculator_config import CalculatorConfig
from app.operations import OPERATIONS, Operation, register


@pytest.fixture
def extra_operation():
    """Register an operation for one test, then unregister it."""

    @register
    class TripleSum(Operation):
        name = "triple_sum"
        symbol = "+++"
        description = "a plus b, tripled"

        def execute(self, left, right):
            return (left + right) * 3

    yield TripleSum
    del OPERATIONS[TripleSum.name]


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
