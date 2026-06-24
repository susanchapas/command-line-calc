import logging

import pytest

from calculator.calculation import Calculation
from calculator.history import HistoryManager
from calculator.observers import AutoSaveObserver, CalculationObserver, LoggingObserver


def test_calculation_observer_is_abstract():
    with pytest.raises(TypeError):
        CalculationObserver()


def test_logging_observer_uses_default_logger(caplog):
    observer = LoggingObserver()

    with caplog.at_level(logging.INFO, logger="calculator"):
        observer.notify(Calculation("add", 2, 3, 5))

    assert "add" in caplog.text


def test_logging_observer_accepts_custom_logger():
    records = []
    logger = logging.getLogger("calculator.test")
    logger.setLevel(logging.INFO)
    handler = logging.Handler()
    handler.emit = records.append
    logger.addHandler(handler)

    try:
        LoggingObserver(logger).notify(Calculation("multiply", 2, 3, 6))
    finally:
        logger.removeHandler(handler)

    assert records and records[0].getMessage().startswith("Calculation: multiply")


def test_auto_save_observer_persists_history(tmp_path):
    path = tmp_path / "history.csv"
    history = HistoryManager()
    calculation = Calculation("add", 2, 3, 5)
    history.add(calculation)

    AutoSaveObserver(history, path).notify(calculation)

    assert path.exists()
    reloaded = HistoryManager()
    reloaded.load(path)
    assert reloaded.calculations() == (Calculation("add", 2.0, 3.0, 5.0),)
