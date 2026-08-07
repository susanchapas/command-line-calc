"""Validation of raw REPL tokens before they reach the calculator."""

import math
from collections.abc import Sequence

from .exceptions import ValidationError

OPERAND_COUNT = 2


def validate_operands(args: Sequence[str]) -> tuple[float, float]:
    """Return the two operands parsed from ``args``.

    :raises ValidationError: if the count is wrong or a token is not a number.
    """
    if len(args) != OPERAND_COUNT:
        raise ValidationError("Usage: <operation> <number> <number>.")

    try:
        return float(args[0]), float(args[1])
    except ValueError as exc:
        raise ValidationError("Enter two valid numbers.") from exc


def validate_range(value: float, max_value: float) -> float:
    """Return ``value`` unchanged when it lies within ``±max_value``.

    :raises ValidationError: if the value is not finite or is out of range.
    """
    if not math.isfinite(value) or abs(value) > max_value:
        raise ValidationError(f"Operands must be finite and within ±{max_value:g}.")
    return value
