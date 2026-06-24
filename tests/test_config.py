from pathlib import Path

import pytest

from calculator.config import CalculatorConfig, ConfigError


def test_defaults_when_env_empty():
    config = CalculatorConfig.from_env({})

    assert config.history_file == Path("calculator_history.csv")
    assert config.auto_save is True
    assert config.max_history_size == 100


def test_reads_custom_values():
    config = CalculatorConfig.from_env(
        {
            "CALCULATOR_HISTORY_FILE": "out/history.csv",
            "CALCULATOR_AUTO_SAVE": "off",
            "CALCULATOR_MAX_HISTORY": "5",
        }
    )

    assert config.history_file == Path("out/history.csv")
    assert config.auto_save is False
    assert config.max_history_size == 5


@pytest.mark.parametrize("value", ["true", "1", "YES", "On"])
def test_auto_save_truthy_values(value):
    assert CalculatorConfig.from_env({"CALCULATOR_AUTO_SAVE": value}).auto_save is True


@pytest.mark.parametrize("value", ["false", "0", "no", "OFF"])
def test_auto_save_falsy_values(value):
    assert CalculatorConfig.from_env({"CALCULATOR_AUTO_SAVE": value}).auto_save is False


def test_invalid_auto_save_raises():
    with pytest.raises(ConfigError, match="boolean for auto-save"):
        CalculatorConfig.from_env({"CALCULATOR_AUTO_SAVE": "maybe"})


def test_non_integer_max_history_raises():
    with pytest.raises(ConfigError, match="integer for max history"):
        CalculatorConfig.from_env({"CALCULATOR_MAX_HISTORY": "lots"})


def test_non_positive_max_history_raises():
    with pytest.raises(ConfigError, match="must be positive"):
        CalculatorConfig.from_env({"CALCULATOR_MAX_HISTORY": "0"})


def test_from_env_uses_process_environment(monkeypatch):
    for key in ("CALCULATOR_HISTORY_FILE", "CALCULATOR_AUTO_SAVE", "CALCULATOR_MAX_HISTORY"):
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setattr("calculator.config.load_dotenv", lambda: None)

    config = CalculatorConfig.from_env()

    assert config.max_history_size == 100
