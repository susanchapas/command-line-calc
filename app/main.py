"""Entry point for the calculator application."""

from .calculator_config import DEFAULT_ENCODING, CalculatorConfig
from .cli import run_repl
from .exceptions import ConfigError
from .logger import configure_logging, get_logger

logger = get_logger()


def main() -> int:
    log_file, encoding, config_error = None, DEFAULT_ENCODING, None
    try:
        config = CalculatorConfig.from_env()
    except ConfigError as error:
        config_error = error  # reported below, once logging exists; run_repl then exits
    else:
        config.ensure_directories()
        log_file, encoding = config.log_file, config.default_encoding

    configure_logging(log_file=log_file, encoding=encoding)
    if config_error is not None:
        logger.error("Invalid configuration: %s", config_error)
    else:
        logger.info("Calculator started; logging to %s.", log_file)

    exit_code = run_repl()
    logger.info("Calculator exited with status %d.", exit_code)
    return exit_code


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
