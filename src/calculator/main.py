"""Entry point for the calculator application."""

from .cli import run_repl


def main() -> int:
    return run_repl()


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
