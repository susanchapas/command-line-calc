import pytest

from app.exceptions import ValidationError
from app.input_validators import validate_operands, validate_range


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


@pytest.mark.parametrize(
    ("token", "expected"),
    [("1e3", 1000.0), ("-2.5e-2", -0.025), ("  4  ", 4.0), ("+7", 7.0), (".5", 0.5)],
)
def test_parses_accepted_numeric_formats(token, expected):
    assert validate_operands([token, "1"])[0] == expected


@pytest.mark.parametrize("token", ["inf", "-inf", "nan"])
def test_non_finite_tokens_parse_but_fail_the_range_check(token):
    """``float`` accepts these spellings, so the range check is what rejects them."""
    value, _ = validate_operands([token, "1"])

    with pytest.raises(ValidationError, match="finite"):
        validate_range(value, 10.0)


@pytest.mark.parametrize("value", [0.0, 5.0, -5.0, 10.0, -10.0])
def test_range_accepts_values_within_the_limit(value):
    assert validate_range(value, 10.0) == value


@pytest.mark.parametrize("value", [10.5, -10.5, float("inf"), float("-inf"), float("nan")])
def test_range_rejects_out_of_range_or_non_finite_values(value):
    with pytest.raises(ValidationError, match=r"within ±10"):
        validate_range(value, 10.0)
