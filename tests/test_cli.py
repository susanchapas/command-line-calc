import pytest

from calculator.calculations import CalculationFactory
from calculator.cli import format_help, format_history, parse_number, parse_operation, prompt_number, prompt_operation, run_repl
from calculator.main import main


def test_parse_operation_accepts_whitespace_and_case():
    assert parse_operation("  ADD  ") == "add"


@pytest.mark.parametrize("value", ["", "mod", "square"])
def test_parse_operation_rejects_invalid_value(value):
    with pytest.raises(ValueError, match="Choose one of"):
        parse_operation(value)


@pytest.mark.parametrize(
    ("raw_value", "expected"),
    [("3", 3.0), (" 4.5 ", 4.5), ("-2", -2.0)],
)
def test_parse_number(raw_value, expected):
    assert parse_number(raw_value) == expected


@pytest.mark.parametrize("value", ["", "abc", "3,4"])
def test_parse_number_rejects_invalid_value(value):
    with pytest.raises(ValueError):
        parse_number(value)


def test_prompt_operation_retries_until_valid():
    inputs = iter(["bogus", "subtract"])
    messages = []

    result = prompt_operation(lambda prompt: next(inputs), messages.append)

    assert result == "subtract"
    assert messages == ["Choose one of: add, subtract, multiply, divide."]


def test_prompt_operation_can_quit():
    result = prompt_operation(lambda prompt: "quit", lambda message: None)

    assert result is None


@pytest.mark.parametrize("error_type", [EOFError, KeyboardInterrupt])
def test_prompt_operation_handles_interrupts(error_type):
    def raising_input(prompt):
        raise error_type

    assert prompt_operation(raising_input, lambda message: None) is None


@pytest.mark.parametrize("command", ["help", "history"])
def test_prompt_operation_returns_special_commands(command):
    result = prompt_operation(lambda prompt: command, lambda message: None)

    assert result == command


def test_prompt_number_retries_until_valid():
    inputs = iter(["", "nope", "7"])
    messages = []

    result = prompt_number("first", lambda prompt: next(inputs), messages.append)

    assert result == 7.0
    assert messages == ["Enter a number.", "Enter a valid number."]


def test_prompt_number_can_quit():
    result = prompt_number("second", lambda prompt: "q", lambda message: None)

    assert result is None


@pytest.mark.parametrize("error_type", [EOFError, KeyboardInterrupt])
def test_prompt_number_handles_interrupts(error_type):
    def raising_input(prompt):
        raise error_type

    assert prompt_number("second", raising_input, lambda message: None) is None


def test_run_repl_calculates_result_and_exits():
    inputs = iter(["add", "2", "3", "quit"])
    outputs = []

    exit_code = run_repl(lambda prompt: next(inputs), outputs.append)

    assert exit_code == 0
    assert outputs == [
        "Command-line Calculator",
        "Choose an operation, enter two numbers, and read the result.",
        "Type help for commands, history to review past calculations, or exit to quit.",
        "Result: 2 + 3 = 5",
        "Goodbye!",
    ]


def test_run_repl_shows_help_and_history():
    inputs = iter(["help", "history", "add", "1", "2", "history", "exit"])
    outputs = []

    exit_code = run_repl(lambda prompt: next(inputs), outputs.append)

    assert exit_code == 0
    assert outputs == [
        "Command-line Calculator",
        "Choose an operation, enter two numbers, and read the result.",
        "Type help for commands, history to review past calculations, or exit to quit.",
        "Available commands: help, history, exit.",
        "Available operations: add (+), subtract (-), multiply (*), divide (/).",
        "Enter an operation first, then the two numbers to calculate.",
        "History is empty.",
        "Result: 1 + 2 = 3",
        "Calculation history:",
        "1. 1 + 2 = 3",
        "Goodbye!",
    ]


def test_run_repl_handles_division_by_zero():
    inputs = iter(["divide", "4", "0", "quit"])
    outputs = []

    exit_code = run_repl(lambda prompt: next(inputs), outputs.append)

    assert exit_code == 0
    assert outputs == [
        "Command-line Calculator",
        "Choose an operation, enter two numbers, and read the result.",
        "Type help for commands, history to review past calculations, or exit to quit.",
        "Cannot divide by zero.",
        "Goodbye!",
    ]


def test_run_repl_exits_on_quit_before_operation():
    inputs = iter(["quit"])
    outputs = []

    exit_code = run_repl(lambda prompt: next(inputs), outputs.append)

    assert exit_code == 0
    assert outputs == [
        "Command-line Calculator",
        "Choose an operation, enter two numbers, and read the result.",
        "Type help for commands, history to review past calculations, or exit to quit.",
        "Goodbye!",
    ]


def test_run_repl_exits_on_interrupt_before_operation():
    outputs = []

    exit_code = run_repl(lambda prompt: (_ for _ in ()).throw(EOFError()), outputs.append)

    assert exit_code == 0
    assert outputs == [
        "Command-line Calculator",
        "Choose an operation, enter two numbers, and read the result.",
        "Type help for commands, history to review past calculations, or exit to quit.",
        "Goodbye!",
    ]


def test_run_repl_exits_on_quit_during_first_number():
    inputs = iter(["add", "quit"])
    outputs = []

    exit_code = run_repl(lambda prompt: next(inputs), outputs.append)

    assert exit_code == 0
    assert outputs == [
        "Command-line Calculator",
        "Choose an operation, enter two numbers, and read the result.",
        "Type help for commands, history to review past calculations, or exit to quit.",
        "Goodbye!",
    ]


def test_run_repl_exits_on_quit_during_second_number():
    inputs = iter(["add", "1", "quit"])
    outputs = []

    exit_code = run_repl(lambda prompt: next(inputs), outputs.append)

    assert exit_code == 0
    assert outputs == [
        "Command-line Calculator",
        "Choose an operation, enter two numbers, and read the result.",
        "Type help for commands, history to review past calculations, or exit to quit.",
        "Goodbye!",
    ]


def test_format_help_uses_factory_descriptions():
    assert format_help() == (
        "Available commands: help, history, exit.",
        "Available operations: add (+), subtract (-), multiply (*), divide (/).",
        "Enter an operation first, then the two numbers to calculate.",
    )


def test_format_history_handles_empty_and_populated_history():
    assert format_history([]) == ("History is empty.",)

    factory = CalculationFactory()
    calculation = factory.create("add", 2, 3)
    assert format_history([(calculation, calculation.execute())]) == ("Calculation history:", "1. 2 + 3 = 5")


def test_main_returns_run_repl_result(monkeypatch):
    monkeypatch.setattr("calculator.main.run_repl", lambda: 7)

    assert main() == 7
