import pytest

from calculator.calculator import Calculator
from calculator.config import CalculatorConfig
from calculator.history import HistoryManager


def test_registers_supplied_observers(config):
    seen = []

    class Recorder:
        def notify(self, calculation):
            seen.append(calculation)

    calculator = Calculator(config=config, observers=[Recorder()])
    calculation = calculator.perform("add", 1, 1)

    assert seen == [calculation]


def test_perform_records_and_formats(calculator):
    calculation = calculator.perform("add", 2, 3)

    assert calculation.result == 5
    assert calculator.format(calculation) == "2 + 3 = 5"
    assert calculator.calculations() == (calculation,)


def test_perform_propagates_operation_errors(calculator):
    with pytest.raises(ZeroDivisionError):
        calculator.perform("divide", 1, 0)

    assert calculator.calculations() == ()


def test_undo_and_redo(calculator):
    calculator.perform("add", 1, 1)
    calculator.perform("add", 2, 2)

    assert calculator.undo() is True
    assert len(calculator.calculations()) == 1
    assert calculator.redo() is True
    assert len(calculator.calculations()) == 2


def test_undo_redo_when_nothing_to_do(calculator):
    assert calculator.undo() is False
    assert calculator.redo() is False


def test_clear_is_undoable(calculator):
    calculator.perform("add", 1, 1)

    calculator.clear()
    assert calculator.calculations() == ()

    assert calculator.undo() is True
    assert len(calculator.calculations()) == 1


def test_save_and_load_default_path(config):
    calculator = Calculator(config=config, observers=[])
    calculator.perform("add", 2, 3)

    saved_path = calculator.save()
    assert saved_path == config.history_file

    fresh = Calculator(config=config, observers=[])
    loaded_path = fresh.load()

    assert loaded_path == config.history_file
    assert len(fresh.calculations()) == 1


def test_load_is_undoable(calculator, tmp_path):
    source = HistoryManager()
    source.add(calculator.perform("add", 4, 4))
    path = tmp_path / "saved.csv"
    calculator.save(path)
    calculator.clear()

    calculator.load(path)
    assert len(calculator.calculations()) == 1

    assert calculator.undo() is True
    assert calculator.calculations() == ()


def test_loads_existing_history_on_start(config):
    seed = Calculator(config=config, observers=[])
    seed.perform("add", 7, 8)
    seed.save()

    revived = Calculator(config=config, observers=[])

    assert len(revived.calculations()) == 1
    assert revived.calculations()[0].result == 15


def test_default_observers_autosave_when_enabled(tmp_path):
    config = CalculatorConfig(
        history_file=tmp_path / "auto.csv",
        auto_save=True,
        max_history_size=100,
    )
    calculator = Calculator(config=config)

    calculator.perform("add", 1, 2)

    assert config.history_file.exists()


def test_default_observers_without_autosave(tmp_path):
    config = CalculatorConfig(
        history_file=tmp_path / "noauto.csv",
        auto_save=False,
        max_history_size=100,
    )
    calculator = Calculator(config=config)

    calculator.perform("add", 1, 2)

    assert not config.history_file.exists()


def test_builds_config_from_env_when_omitted(tmp_path, monkeypatch):
    monkeypatch.setattr("calculator.config.load_dotenv", lambda: None)
    monkeypatch.setenv("CALCULATOR_HISTORY_FILE", str(tmp_path / "env.csv"))
    monkeypatch.setenv("CALCULATOR_AUTO_SAVE", "false")
    monkeypatch.setenv("CALCULATOR_MAX_HISTORY", "10")

    calculator = Calculator()

    assert calculator.config.max_history_size == 10
    assert calculator.calculations() == ()
