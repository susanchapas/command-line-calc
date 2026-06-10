"""Interactive REPL for the calculator."""

from collections.abc import Callable

from .operations import add, divide, multiply, subtract

Operation = Callable[[float, float], float]

OPERATIONS: dict[str, tuple[str, Operation]] = {
    "add": ("+", add),
    "subtract": ("-", subtract),
    "multiply": ("*", multiply),
    "divide": ("/", divide),
}

QUIT_COMMANDS = {"quit", "exit", "q"}


def parse_operation(raw_value: str) -> str:
    operation = raw_value.strip().lower()
    if operation in OPERATIONS:
        return operation
    raise ValueError("Choose one of: add, subtract, multiply, divide.")


def parse_number(raw_value: str) -> float:
    value = raw_value.strip()
    if not value:
        raise ValueError("Enter a number.")

    try:
        return float(value)
    except ValueError as exc:
        raise ValueError("Enter a valid number.") from exc


def prompt_operation(input_func: Callable[[str], str], output_func: Callable[[str], None]) -> str | None:
    prompt = "Choose an operation [add, subtract, multiply, divide] or 'quit': "
    while True:
        raw_value = input_func(prompt)
        if raw_value.strip().lower() in QUIT_COMMANDS:
            return None

        try:
            return parse_operation(raw_value)
        except ValueError as error:
            output_func(str(error))


def prompt_number(label: str, input_func: Callable[[str], str], output_func: Callable[[str], None]) -> float | None:
    prompt = f"Enter the {label} number (or 'quit' to exit): "
    while True:
        raw_value = input_func(prompt)
        if raw_value.strip().lower() in QUIT_COMMANDS:
            return None

        try:
            return parse_number(raw_value)
        except ValueError as error:
            output_func(str(error))


def run_repl(input_func: Callable[[str], str] = input, output_func: Callable[[str], None] = print) -> int:
    output_func("Command-line Calculator")
    output_func("Type 'quit' at any prompt to exit.")

    while True:
        operation_name = prompt_operation(input_func, output_func)
        if operation_name is None:
            output_func("Goodbye!")
            return 0

        left = prompt_number("first", input_func, output_func)
        if left is None:
            output_func("Goodbye!")
            return 0

        right = prompt_number("second", input_func, output_func)
        if right is None:
            output_func("Goodbye!")
            return 0

        _, operation = OPERATIONS[operation_name]
        try:
            result = operation(left, right)
        except ZeroDivisionError as error:
            output_func(str(error))
            continue

        output_func(f"Result: {result}")
