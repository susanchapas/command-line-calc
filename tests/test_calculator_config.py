from pathlib import Path

import pytest

from app.calculator_config import CalculatorConfig
from app.exceptions import ConfigError


def test_defaults_when_env_empty():
    config = CalculatorConfig.from_env({})

    assert config.log_dir == Path("logs")
    assert config.history_dir == Path("history")
    assert config.max_history_size == 100
    assert config.auto_save is True
    assert config.precision == 10
    assert config.max_input_value == 1e12
    assert config.default_encoding == "utf-8"
    assert config.log_file == Path("logs/calculator.log")
    assert config.history_file == Path("history/calculator_history.csv")


def test_reads_custom_values():
    config = CalculatorConfig.from_env(
        {
            "CALCULATOR_LOG_DIR": "var/log",
            "CALCULATOR_HISTORY_DIR": "var/history",
            "CALCULATOR_MAX_HISTORY_SIZE": "5",
            "CALCULATOR_AUTO_SAVE": "off",
            "CALCULATOR_PRECISION": "2",
            "CALCULATOR_MAX_INPUT_VALUE": "500",
            "CALCULATOR_DEFAULT_ENCODING": "latin-1",
            "CALCULATOR_LOG_FILE": "calc.log",
            "CALCULATOR_HISTORY_FILE": "calc.csv",
        }
    )

    assert config.log_dir == Path("var/log")
    assert config.history_dir == Path("var/history")
    assert config.max_history_size == 5
    assert config.auto_save is False
    assert config.precision == 2
    assert config.max_input_value == 500.0
    assert config.default_encoding == "latin-1"
    assert config.log_file == Path("var/log/calc.log")
    assert config.history_file == Path("var/history/calc.csv")


def test_absolute_file_names_override_their_directory():
    config = CalculatorConfig.from_env(
        {
            "CALCULATOR_LOG_FILE": "/var/log/calc.log",
            "CALCULATOR_HISTORY_FILE": "/var/lib/calc.csv",
        }
    )

    assert config.log_file == Path("/var/log/calc.log")
    assert config.history_file == Path("/var/lib/calc.csv")


def test_ensure_directories_creates_both(tmp_path):
    config = CalculatorConfig(log_dir=tmp_path / "l", history_dir=tmp_path / "h" / "nested")

    config.ensure_directories()

    assert config.log_dir.is_dir()
    assert config.history_dir.is_dir()


def test_ensure_directories_is_idempotent(tmp_path):
    config = CalculatorConfig(log_dir=tmp_path, history_dir=tmp_path)

    config.ensure_directories()
    config.ensure_directories()

    assert config.log_dir.is_dir()


@pytest.mark.parametrize("value", ["true", "1", "YES", "On"])
def test_auto_save_truthy_values(value):
    assert CalculatorConfig.from_env({"CALCULATOR_AUTO_SAVE": value}).auto_save is True


@pytest.mark.parametrize("value", ["false", "0", "no", "OFF"])
def test_auto_save_falsy_values(value):
    assert CalculatorConfig.from_env({"CALCULATOR_AUTO_SAVE": value}).auto_save is False


def test_invalid_auto_save_raises():
    with pytest.raises(ConfigError, match="boolean for auto-save"):
        CalculatorConfig.from_env({"CALCULATOR_AUTO_SAVE": "maybe"})


def test_non_integer_max_history_size_raises():
    with pytest.raises(ConfigError, match="integer for max history size"):
        CalculatorConfig.from_env({"CALCULATOR_MAX_HISTORY_SIZE": "lots"})


def test_non_positive_max_history_size_raises():
    with pytest.raises(ConfigError, match="max history size of at least 1"):
        CalculatorConfig.from_env({"CALCULATOR_MAX_HISTORY_SIZE": "0"})


def test_non_integer_precision_raises():
    with pytest.raises(ConfigError, match="integer for precision"):
        CalculatorConfig.from_env({"CALCULATOR_PRECISION": "two"})


def test_negative_precision_raises():
    with pytest.raises(ConfigError, match="precision of at least 0"):
        CalculatorConfig.from_env({"CALCULATOR_PRECISION": "-1"})


def test_zero_precision_is_allowed():
    assert CalculatorConfig.from_env({"CALCULATOR_PRECISION": "0"}).precision == 0


def test_non_numeric_max_input_value_raises():
    with pytest.raises(ConfigError, match="number for max input value"):
        CalculatorConfig.from_env({"CALCULATOR_MAX_INPUT_VALUE": "huge"})


@pytest.mark.parametrize("value", ["0", "-1", "inf", "nan"])
def test_non_positive_or_infinite_max_input_value_raises(value):
    with pytest.raises(ConfigError, match="positive, finite max input value"):
        CalculatorConfig.from_env({"CALCULATOR_MAX_INPUT_VALUE": value})


def test_unknown_encoding_raises():
    with pytest.raises(ConfigError, match="Unknown encoding"):
        CalculatorConfig.from_env({"CALCULATOR_DEFAULT_ENCODING": "not-a-codec"})


def test_from_env_uses_process_environment(monkeypatch):
    for key in (
        "CALCULATOR_LOG_DIR",
        "CALCULATOR_HISTORY_DIR",
        "CALCULATOR_MAX_HISTORY_SIZE",
        "CALCULATOR_AUTO_SAVE",
        "CALCULATOR_PRECISION",
        "CALCULATOR_MAX_INPUT_VALUE",
        "CALCULATOR_DEFAULT_ENCODING",
    ):
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setattr("app.calculator_config.load_dotenv", lambda: None)

    config = CalculatorConfig.from_env()

    assert config.max_history_size == 100
    assert config.precision == 10
