"""Interactive REPL for the calculator."""

from collections.abc import Callable

from .calculator import Calculator
from .config import ConfigError
from .history import HistoryError

QUIT_COMMANDS = {"exit", "quit", "q"}


def banner() -> tuple[str, ...]:
    return (
        "Command-line Calculator",
        "Type an operation like 'add 2 3', or 'help' for all commands.",
    )


def format_help(calculator: Calculator) -> tuple[str, ...]:
    return (
        "Commands:",
        "  <operation> <a> <b>   run a calculation (e.g. add 2 3)",
        "  history               show the calculation history",
        "  undo / redo           step backward or forward through history",
        "  save [path]           save history to a CSV file",
        "  load [path]           load history from a CSV file",
        "  clear                 erase the current history",
        "  help                  show this message",
        "  exit                  quit the calculator",
        f"Operations: {calculator.factory.describe_operations()}.",
    )


def format_history(calculator: Calculator) -> tuple[str, ...]:
    calculations = calculator.calculations()
    if not calculations:
        return ("History is empty.",)

    lines = ["Calculation history:"]
    for index, calculation in enumerate(calculations, start=1):
        lines.append(f"{index}. {calculator.format(calculation)}")
    return tuple(lines)


def run_operation(calculator: Calculator, operation: str, args: list[str]) -> tuple[str, ...]:
    if len(args) != 2:
        return ("Usage: <operation> <number> <number>.",)

    try:
        left = float(args[0])
        right = float(args[1])
    except ValueError:
        return ("Enter two valid numbers.",)

    try:
        calculation = calculator.perform(operation, left, right)
    except (ZeroDivisionError, ValueError) as error:
        return (str(error),)

    return (f"Result: {calculator.format(calculation)}",)


def cmd_help(calculator: Calculator, args: list[str]) -> tuple[str, ...]:
    return format_help(calculator)


def cmd_history(calculator: Calculator, args: list[str]) -> tuple[str, ...]:
    return format_history(calculator)


def cmd_clear(calculator: Calculator, args: list[str]) -> tuple[str, ...]:
    calculator.clear()
    return ("History cleared.",)


def cmd_undo(calculator: Calculator, args: list[str]) -> tuple[str, ...]:
    return ("Undid the last change.",) if calculator.undo() else ("Nothing to undo.",)


def cmd_redo(calculator: Calculator, args: list[str]) -> tuple[str, ...]:
    return ("Redid the last change.",) if calculator.redo() else ("Nothing to redo.",)


def cmd_save(calculator: Calculator, args: list[str]) -> tuple[str, ...]:
    try:
        target = calculator.save(args[0] if args else None)
    except OSError as error:
        return (f"Could not save history: {error}",)
    return (f"History saved to {target}.",)


def cmd_load(calculator: Calculator, args: list[str]) -> tuple[str, ...]:
    try:
        target = calculator.load(args[0] if args else None)
    except (OSError, HistoryError) as error:
        return (f"Could not load history: {error}",)
    return (f"History loaded from {target}.",)


COMMANDS: dict[str, Callable[[Calculator, list[str]], tuple[str, ...]]] = {
    "help": cmd_help,
    "history": cmd_history,
    "clear": cmd_clear,
    "undo": cmd_undo,
    "redo": cmd_redo,
    "save": cmd_save,
    "load": cmd_load,
}


def run_repl(
    input_func: Callable[[str], str] = input,
    output_func: Callable[[str], None] = print,
    calculator: Calculator | None = None,
) -> int:
    if calculator is None:
        try:
            calculator = Calculator()
        except (ConfigError, HistoryError) as error:
            output_func(f"Startup error: {error}")
            return 1

    for line in banner():
        output_func(line)

    while True:
        try:
            raw_value = input_func("> ")
        except (EOFError, KeyboardInterrupt):
            output_func("Goodbye!")
            return 0

        tokens = raw_value.strip().split()
        if not tokens:
            continue

        command = tokens[0].lower()
        args = tokens[1:]

        if command in QUIT_COMMANDS:
            output_func("Goodbye!")
            return 0

        handler = COMMANDS.get(command)
        if handler is not None:
            messages = handler(calculator, args)
        elif command in calculator.factory.available_operations():
            messages = run_operation(calculator, command, args)
        else:
            messages = (f"Unknown command: {command}. Type 'help' for options.",)

        for message in messages:
            output_func(message)
