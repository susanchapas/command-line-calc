"""Entry point for the calculator application."""

import logging

from .cli import run_repl


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s: %(message)s")
    return run_repl()


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
