from app.main import main


def test_main_configures_logging_and_runs(monkeypatch, tmp_path):
    captured = {}
    monkeypatch.setenv("CALCULATOR_LOG_DIR", str(tmp_path / "logs"))
    monkeypatch.setenv("CALCULATOR_HISTORY_DIR", str(tmp_path / "history"))
    monkeypatch.setenv("CALCULATOR_DEFAULT_ENCODING", "latin-1")
    monkeypatch.setattr("app.main.configure_logging", lambda **kwargs: captured.update(kwargs))
    monkeypatch.setattr("app.main.run_repl", lambda: 7)

    assert main() == 7
    assert captured["log_file"] == tmp_path / "logs" / "calculator.log"
    assert captured["encoding"] == "latin-1"
    assert (tmp_path / "logs").is_dir()
    assert (tmp_path / "history").is_dir()


def test_main_skips_file_logging_when_configuration_is_invalid(monkeypatch):
    captured = {}
    monkeypatch.setenv("CALCULATOR_MAX_HISTORY_SIZE", "lots")
    monkeypatch.setattr("app.main.configure_logging", lambda **kwargs: captured.update(kwargs))
    monkeypatch.setattr("app.main.run_repl", lambda: 1)

    assert main() == 1
    assert captured["log_file"] is None
    assert captured["encoding"] == "utf-8"
