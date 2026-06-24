import pytest

from calculator.config import ConfigError
from calculator.history import HistoryError
from calculator.cli import run_repl


def drive(calculator, commands):
    inputs = iter(commands)
    outputs = []
    code = run_repl(lambda prompt: next(inputs), outputs.append, calculator=calculator)
    return code, outputs


def test_banner_and_quit(calculator):
    code, outputs = drive(calculator, ["exit"])

    assert code == 0
    assert outputs == [
        "Command-line Calculator",
        "Type an operation like 'add 2 3', or 'help' for all commands.",
        "Goodbye!",
    ]


@pytest.mark.parametrize("quit_command", ["exit", "quit", "q"])
def test_quit_aliases(calculator, quit_command):
    code, outputs = drive(calculator, [quit_command])

    assert code == 0
    assert outputs[-1] == "Goodbye!"


@pytest.mark.parametrize("error_type", [EOFError, KeyboardInterrupt])
def test_interrupt_exits_cleanly(calculator, error_type):
    def raising_input(prompt):
        raise error_type

    outputs = []
    code = run_repl(raising_input, outputs.append, calculator=calculator)

    assert code == 0
    assert outputs[-1] == "Goodbye!"


def test_blank_line_is_ignored(calculator):
    code, outputs = drive(calculator, ["", "   ", "exit"])

    assert outputs[-1] == "Goodbye!"


def test_runs_operation(calculator):
    code, outputs = drive(calculator, ["add 2 3", "exit"])

    assert "Result: 2 + 3 = 5" in outputs


def test_operation_is_case_insensitive(calculator):
    _, outputs = drive(calculator, ["ADD 2 3", "exit"])

    assert "Result: 2 + 3 = 5" in outputs


def test_operation_wrong_argument_count(calculator):
    _, outputs = drive(calculator, ["add 2", "exit"])

    assert "Usage: <operation> <number> <number>." in outputs


def test_operation_invalid_numbers(calculator):
    _, outputs = drive(calculator, ["add x y", "exit"])

    assert "Enter two valid numbers." in outputs


def test_operation_reports_division_by_zero(calculator):
    _, outputs = drive(calculator, ["divide 1 0", "exit"])

    assert "Cannot divide by zero." in outputs


def test_operation_reports_value_error(calculator):
    _, outputs = drive(calculator, ["power -2 0.5", "exit"])

    assert "Result is not a real number." in outputs


def test_unknown_command(calculator):
    _, outputs = drive(calculator, ["frobnicate", "exit"])

    assert "Unknown command: frobnicate. Type 'help' for options." in outputs


def test_help_lists_commands_and_operations(calculator):
    _, outputs = drive(calculator, ["help", "exit"])

    assert "Commands:" in outputs
    assert any(line.startswith("Operations:") for line in outputs)


def test_history_empty_and_populated(calculator):
    _, outputs = drive(calculator, ["history", "add 1 2", "history", "exit"])

    assert "History is empty." in outputs
    assert "Calculation history:" in outputs
    assert "1. 1 + 2 = 3" in outputs


def test_clear_command(calculator):
    _, outputs = drive(calculator, ["add 1 2", "clear", "history", "exit"])

    assert "History cleared." in outputs
    assert "History is empty." in outputs


def test_undo_and_redo_commands(calculator):
    _, outputs = drive(
        calculator,
        ["add 1 2", "undo", "Nothing left?", "redo", "exit"],
    )

    assert "Undid the last change." in outputs
    assert "Redid the last change." in outputs


def test_undo_and_redo_when_empty(calculator):
    _, outputs = drive(calculator, ["undo", "redo", "exit"])

    assert "Nothing to undo." in outputs
    assert "Nothing to redo." in outputs


def test_save_to_explicit_path(calculator, tmp_path):
    target = tmp_path / "out.csv"

    _, outputs = drive(calculator, ["add 2 3", f"save {target}", "exit"])

    assert f"History saved to {target}." in outputs
    assert target.exists()


def test_save_to_default_path(calculator, config):
    _, outputs = drive(calculator, ["add 2 3", "save", "exit"])

    assert f"History saved to {config.history_file}." in outputs
    assert config.history_file.exists()


def test_save_reports_os_error(calculator, tmp_path):
    target = tmp_path / "missing" / "out.csv"

    _, outputs = drive(calculator, ["add 2 3", f"save {target}", "exit"])

    assert any(line.startswith("Could not save history:") for line in outputs)


def test_load_from_path(calculator, tmp_path):
    target = tmp_path / "saved.csv"

    _, outputs = drive(
        calculator,
        ["add 2 3", f"save {target}", "clear", f"load {target}", "history", "exit"],
    )

    assert f"History loaded from {target}." in outputs
    assert "1. 2 + 3 = 5" in outputs


def test_load_reports_error(calculator, tmp_path):
    missing = tmp_path / "nope.csv"

    _, outputs = drive(calculator, [f"load {missing}", "exit"])

    assert any(line.startswith("Could not load history:") for line in outputs)


def test_load_reports_history_error(calculator, tmp_path):
    bad = tmp_path / "bad.csv"
    bad.write_text("foo,bar\n1,2\n")

    _, outputs = drive(calculator, [f"load {bad}", "exit"])

    assert any(line.startswith("Could not load history:") for line in outputs)


def test_constructs_calculator_when_not_provided(monkeypatch, calculator):
    monkeypatch.setattr("calculator.cli.Calculator", lambda: calculator)

    inputs = iter(["exit"])
    outputs = []
    code = run_repl(lambda prompt: next(inputs), outputs.append)

    assert code == 0
    assert outputs[-1] == "Goodbye!"


@pytest.mark.parametrize("error", [ConfigError("bad config"), HistoryError("bad file")])
def test_reports_startup_error(monkeypatch, error):
    def boom():
        raise error

    monkeypatch.setattr("calculator.cli.Calculator", boom)

    outputs = []
    code = run_repl(lambda prompt: "exit", outputs.append)

    assert code == 1
    assert outputs == [f"Startup error: {error}"]
