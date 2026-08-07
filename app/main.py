"""Entry point for the calculator application."""

from .cli import run_repl
from .logger import configure_logging


def main() -> int:
    configure_logging()
    return run_repl()


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
