import logging

import pytest

from app.calculation import Calculation
from app.logger import CONSOLE_LEVEL, LOG_FORMAT, LOGGER_NAME, configure_logging, get_logger
from app.observers import LoggingObserver


@pytest.fixture
def restore_root_logger():
    root = logging.getLogger()
    saved_handlers, saved_level = root.handlers[:], root.level

    yield

    for handler in root.handlers:
        if handler not in saved_handlers:
            handler.close()
    root.handlers[:] = saved_handlers
    root.setLevel(saved_level)


def test_defaults_to_the_application_logger():
    assert get_logger().name == LOGGER_NAME


def test_accepts_an_explicit_name():
    assert get_logger("calculator.child").name == "calculator.child"


def test_configure_logging_applies_level_and_format(monkeypatch):
    captured = {}
    monkeypatch.setattr("app.logger.logging.basicConfig", lambda **kwargs: captured.update(kwargs))

    configure_logging(logging.DEBUG)

    assert captured["level"] == logging.DEBUG
    assert captured["format"] == LOG_FORMAT
    assert [type(handler) for handler in captured["handlers"]] == [logging.StreamHandler]


def test_configure_logging_adds_a_file_handler(monkeypatch, tmp_path):
    captured = {}
    monkeypatch.setattr("app.logger.logging.basicConfig", lambda **kwargs: captured.update(kwargs))

    configure_logging(log_file=tmp_path / "calculator.log", encoding="latin-1")

    assert [type(handler) for handler in captured["handlers"]] == [
        logging.StreamHandler,
        logging.FileHandler,
    ]
    assert captured["handlers"][1].encoding == "latin-1"
    for handler in captured["handlers"]:
        handler.close()


def test_logged_calculations_reach_the_log_file(tmp_path, restore_root_logger):
    log_file = tmp_path / "logs" / "calculator.log"

    configure_logging(log_file=log_file)
    LoggingObserver().notify(Calculation("add", 2, 3, 5))

    assert "Calculation: add(2, 3) = 5" in log_file.read_text()


def test_console_handler_is_limited_to_warnings(monkeypatch):
    captured = {}
    monkeypatch.setattr("app.logger.logging.basicConfig", lambda **kwargs: captured.update(kwargs))

    configure_logging()

    assert captured["handlers"][0].level == CONSOLE_LEVEL


@pytest.mark.parametrize(
    ("level", "expected"),
    [(logging.INFO, "INFO"), (logging.WARNING, "WARNING"), (logging.ERROR, "ERROR")],
)
def test_log_file_records_the_level_name(tmp_path, restore_root_logger, level, expected):
    log_file = tmp_path / "calculator.log"

    configure_logging(log_file=log_file)
    get_logger().log(level, "something happened")

    assert f"{expected} {LOGGER_NAME}: something happened" in log_file.read_text()
