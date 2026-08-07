import pytest

from app.exceptions import ValidationError
from app.input_validators import validate_operands


def test_parses_two_numbers():
    assert validate_operands(["2", "-3.5"]) == (2.0, -3.5)


@pytest.mark.parametrize("args", [[], ["1"], ["1", "2", "3"]])
def test_rejects_wrong_operand_count(args):
    with pytest.raises(ValidationError, match="Usage:"):
        validate_operands(args)


@pytest.mark.parametrize("args", [["x", "2"], ["2", "y"]])
def test_rejects_non_numeric_operands(args):
    with pytest.raises(ValidationError, match="two valid numbers"):
        validate_operands(args)
