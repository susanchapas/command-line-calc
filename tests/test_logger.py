import logging

from app.logger import LOG_FORMAT, LOGGER_NAME, configure_logging, get_logger


def test_defaults_to_the_application_logger():
    assert get_logger().name == LOGGER_NAME


def test_accepts_an_explicit_name():
    assert get_logger("calculator.child").name == "calculator.child"


def test_configure_logging_applies_level_and_format(monkeypatch):
    captured = {}
    monkeypatch.setattr("app.logger.logging.basicConfig", lambda **kwargs: captured.update(kwargs))

    configure_logging(logging.DEBUG)

    assert captured == {"level": logging.DEBUG, "format": LOG_FORMAT}
