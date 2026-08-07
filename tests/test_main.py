from app.main import main


def test_main_configures_logging_and_runs(monkeypatch, tmp_path):
    captured = {}
    log_file = tmp_path / "calculator.log"
    monkeypatch.setenv("CALCULATOR_LOG_FILE", str(log_file))
    monkeypatch.setattr("app.main.configure_logging", lambda **kwargs: captured.update(kwargs))
    monkeypatch.setattr("app.main.run_repl", lambda: 7)

    assert main() == 7
    assert captured["log_file"] == log_file


def test_main_skips_file_logging_when_configuration_is_invalid(monkeypatch):
    captured = {}
    monkeypatch.setenv("CALCULATOR_MAX_HISTORY", "lots")
    monkeypatch.setattr("app.main.configure_logging", lambda **kwargs: captured.update(kwargs))
    monkeypatch.setattr("app.main.run_repl", lambda: 1)

    assert main() == 1
    assert captured["log_file"] is None
