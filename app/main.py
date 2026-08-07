"""Entry point for the calculator application."""

from .calculator_config import CalculatorConfig
from .cli import run_repl
from .exceptions import ConfigError
from .logger import configure_logging


def main() -> int:
    try:
        log_file = CalculatorConfig.from_env().log_file
    except ConfigError:
        log_file = None  # run_repl reports the configuration error and exits

    configure_logging(log_file=log_file)
    return run_repl()


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
