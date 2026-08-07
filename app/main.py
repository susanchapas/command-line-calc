"""Entry point for the calculator application."""

from .calculator_config import DEFAULT_ENCODING, CalculatorConfig
from .cli import run_repl
from .exceptions import ConfigError
from .logger import configure_logging


def main() -> int:
    log_file, encoding = None, DEFAULT_ENCODING
    try:
        config = CalculatorConfig.from_env()
    except ConfigError:
        pass  # run_repl reports the configuration error and exits
    else:
        config.ensure_directories()
        log_file, encoding = config.log_file, config.default_encoding

    configure_logging(log_file=log_file, encoding=encoding)
    return run_repl()


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
