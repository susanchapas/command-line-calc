import pytest

from app.calculator import Calculator
from app.calculator_config import CalculatorConfig
from app.exceptions import ValidationError
from app.history import HistoryManager


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
        log_dir=tmp_path,
        history_dir=tmp_path,
        history_filename="auto.csv",
        auto_save=True,
    )
    calculator = Calculator(config=config)

    calculator.perform("add", 1, 2)

    assert config.history_file.exists()


def test_default_observers_without_autosave(tmp_path):
    config = CalculatorConfig(
        log_dir=tmp_path,
        history_dir=tmp_path,
        history_filename="noauto.csv",
        auto_save=False,
    )
    calculator = Calculator(config=config)

    calculator.perform("add", 1, 2)

    assert not config.history_file.exists()


@pytest.fixture
def autosave_config(tmp_path):
    return CalculatorConfig(
        log_dir=tmp_path,
        history_dir=tmp_path,
        history_filename="auto.csv",
        auto_save=True,
    )


def reloaded_count(config):
    return len(Calculator(config=config, observers=[]).calculations())


def test_undo_persists_when_autosaving(autosave_config):
    calculator = Calculator(config=autosave_config)
    calculator.perform("add", 1, 1)
    calculator.perform("add", 2, 2)

    calculator.undo()

    assert reloaded_count(autosave_config) == 1


def test_redo_persists_when_autosaving(autosave_config):
    calculator = Calculator(config=autosave_config)
    calculator.perform("add", 1, 1)
    calculator.perform("add", 2, 2)
    calculator.undo()

    calculator.redo()

    assert reloaded_count(autosave_config) == 2


def test_clear_persists_when_autosaving(autosave_config):
    calculator = Calculator(config=autosave_config)
    calculator.perform("add", 1, 1)

    calculator.clear()

    assert reloaded_count(autosave_config) == 0


def test_load_persists_when_autosaving(autosave_config, tmp_path):
    calculator = Calculator(config=autosave_config)
    calculator.perform("add", 4, 4)
    external = tmp_path / "external.csv"
    calculator.save(external)
    calculator.clear()

    calculator.load(external)

    assert reloaded_count(autosave_config) == 1


def test_failed_undo_does_not_persist(autosave_config):
    calculator = Calculator(config=autosave_config, observers=[])

    assert calculator.undo() is False
    assert calculator.redo() is False
    assert not autosave_config.history_file.exists()


def test_undo_does_not_persist_without_autosave(config):
    calculator = Calculator(config=config, observers=[])
    calculator.perform("add", 1, 1)

    calculator.undo()

    assert not config.history_file.exists()


def test_builds_config_from_env_when_omitted(tmp_path, monkeypatch):
    monkeypatch.setattr("app.calculator_config.load_dotenv", lambda: None)
    monkeypatch.setenv("CALCULATOR_LOG_DIR", str(tmp_path / "logs"))
    monkeypatch.setenv("CALCULATOR_HISTORY_DIR", str(tmp_path / "history"))
    monkeypatch.setenv("CALCULATOR_AUTO_SAVE", "false")
    monkeypatch.setenv("CALCULATOR_MAX_HISTORY_SIZE", "10")

    calculator = Calculator()

    assert calculator.config.max_history_size == 10
    assert calculator.calculations() == ()
    assert (tmp_path / "history").is_dir()


def test_creates_configured_directories_on_start(tmp_path):
    config = CalculatorConfig(log_dir=tmp_path / "logs", history_dir=tmp_path / "history")

    Calculator(config=config, observers=[])

    assert config.log_dir.is_dir()
    assert config.history_dir.is_dir()


def test_result_is_rounded_to_configured_precision(tmp_path):
    config = CalculatorConfig(log_dir=tmp_path, history_dir=tmp_path, precision=3)
    calculator = Calculator(config=config, observers=[])

    assert calculator.perform("divide", 2, 3).result == 0.667


def test_zero_precision_rounds_to_whole_numbers(tmp_path):
    config = CalculatorConfig(log_dir=tmp_path, history_dir=tmp_path, precision=0)
    calculator = Calculator(config=config, observers=[])

    assert calculator.perform("divide", 7, 2).result == 4


@pytest.mark.parametrize("left,right", [(1001, 2), (2, -1001)])
def test_rejects_operands_beyond_max_input_value(tmp_path, left, right):
    config = CalculatorConfig(log_dir=tmp_path, history_dir=tmp_path, max_input_value=1000)
    calculator = Calculator(config=config, observers=[])

    with pytest.raises(ValidationError, match=r"within ±1000"):
        calculator.perform("add", left, right)

    assert calculator.calculations() == ()


def test_accepts_operands_at_the_max_input_value(tmp_path):
    config = CalculatorConfig(log_dir=tmp_path, history_dir=tmp_path, max_input_value=1000)
    calculator = Calculator(config=config, observers=[])

    assert calculator.perform("add", 1000, -1000).result == 0


def test_history_uses_configured_encoding(tmp_path):
    config = CalculatorConfig(
        log_dir=tmp_path,
        history_dir=tmp_path,
        default_encoding="latin-1",
        auto_save=False,
    )
    calculator = Calculator(config=config, observers=[])
    calculator.perform("add", 1, 2)
    calculator.save()

    assert config.history_file.read_text(encoding="latin-1").startswith("operation,a,b,result")
