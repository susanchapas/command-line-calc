"""Central exception hierarchy for the calculator.

Every error the application raises on purpose derives from
:class:`CalculatorError`, so a caller can catch the whole family with a
single ``except`` clause.
"""


class CalculatorError(Exception):
    """Base class for all calculator errors."""


class ConfigError(CalculatorError):
    """Raised when an environment value cannot be parsed or is invalid."""


class HistoryError(CalculatorError):
    """Raised when a history file cannot be read, written, or parsed."""


class OperationError(CalculatorError):
    """Raised when an operation cannot produce a usable result."""


class ValidationError(CalculatorError):
    """Raised when user input is not a usable pair of operands."""
