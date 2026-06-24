from calculator.main import main


def test_main_configures_logging_and_runs(monkeypatch):
    monkeypatch.setattr("calculator.main.run_repl", lambda: 7)

    assert main() == 7
