"""Interactive REPL for the calculator."""

from collections.abc import Callable

from .calculations import Calculation, CalculationFactory

QUIT_COMMANDS = {"quit", "exit", "q"}
HELP_COMMANDS = {"help"}
HISTORY_COMMANDS = {"history"}
SPECIAL_COMMANDS = QUIT_COMMANDS | HELP_COMMANDS | HISTORY_COMMANDS


def parse_operation(raw_value: str) -> str:
    operation = raw_value.strip().lower()
    if operation in CalculationFactory.available_operations():
        return operation

    valid_operations = ", ".join(CalculationFactory.available_operations())
    raise ValueError(f"Choose one of: {valid_operations}.")


def parse_number(raw_value: str) -> float:
    value = raw_value.strip()
    if not value:
        raise ValueError("Enter a number.")

    try:
        return float(value)
    except ValueError as exc:
        raise ValueError("Enter a valid number.") from exc


def prompt_operation(input_func: Callable[[str], str], output_func: Callable[[str], None]) -> str | None:
    prompt = "Choose an operation [add, subtract, multiply, divide] or type help, history, or exit: "
    while True:
        try:
            raw_value = input_func(prompt)
        except (EOFError, KeyboardInterrupt):
            return None

        operation = raw_value.strip().lower()

        if operation in QUIT_COMMANDS:
            return None

        if operation in HELP_COMMANDS | HISTORY_COMMANDS:
            return operation

        try:
            return parse_operation(raw_value)
        except ValueError as error:
            output_func(str(error))


def prompt_number(label: str, input_func: Callable[[str], str], output_func: Callable[[str], None]) -> float | None:
    prompt = f"Enter the {label} number (or 'quit' to exit): "
    while True:
        try:
            raw_value = input_func(prompt)
        except (EOFError, KeyboardInterrupt):
            return None

        if raw_value.strip().lower() in QUIT_COMMANDS:
            return None

        try:
            return parse_number(raw_value)
        except ValueError as error:
            output_func(str(error))


def format_help() -> tuple[str, ...]:
    return (
        "Available commands: help, history, exit.",
        f"Available operations: {CalculationFactory.describe_operations()}.",
        "Enter an operation first, then the two numbers to calculate.",
    )


def format_history(history: list[tuple[Calculation, float]]) -> tuple[str, ...]:
    if not history:
        return ("History is empty.",)

    lines = ["Calculation history:"]
    for index, (calculation, result) in enumerate(history, start=1):
        lines.append(f"{index}. {calculation.render(result)}")

    return tuple(lines)


def run_repl(input_func: Callable[[str], str] = input, output_func: Callable[[str], None] = print) -> int:
    factory = CalculationFactory()
    history: list[tuple[Calculation, float]] = []

    output_func("Command-line Calculator")
    output_func("Choose an operation, enter two numbers, and read the result.")
    output_func("Type help for commands, history to review past calculations, or exit to quit.")

    while True:
        operation_name = prompt_operation(input_func, output_func)
        if operation_name is None:
            output_func("Goodbye!")
            return 0

        if operation_name == "help":
            for line in format_help():
                output_func(line)
            continue

        if operation_name == "history":
            for line in format_history(history):
                output_func(line)
            continue

        left = prompt_number("first", input_func, output_func)
        if left is None:
            output_func("Goodbye!")
            return 0

        right = prompt_number("second", input_func, output_func)
        if right is None:
            output_func("Goodbye!")
            return 0

        calculation = factory.create(operation_name, left, right)
        try:
            result = calculation.execute()
        except ZeroDivisionError as error:
            output_func(str(error))
            continue

        history.append((calculation, result))
        output_func(f"Result: {calculation.render(result)}")
