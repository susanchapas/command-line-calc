import pytest

from calculator.calculation import Calculation
from calculator.history import COLUMNS, HistoryError, HistoryManager


def make_calc(operation="add", a=1, b=2, result=3):
    return Calculation(operation, a, b, result)


def test_starts_empty():
    history = HistoryManager()

    assert history.is_empty()
    assert history.calculations() == ()


def test_add_and_read_back():
    history = HistoryManager()
    history.add(make_calc("add", 2, 3, 5))
    history.add(make_calc("power", 2, 3, 8))

    calculations = history.calculations()

    assert not history.is_empty()
    assert calculations == (
        Calculation("add", 2.0, 3.0, 5.0),
        Calculation("power", 2.0, 3.0, 8.0),
    )


def test_to_dataframe_columns_and_values():
    history = HistoryManager()
    history.add(make_calc("add", 2, 3, 5))

    frame = history.to_dataframe()

    assert list(frame.columns) == list(COLUMNS)
    assert frame.iloc[0]["operation"] == "add"
    assert frame.iloc[0]["result"] == 5.0


def test_clear_empties_history():
    history = HistoryManager()
    history.add(make_calc())

    history.clear()

    assert history.is_empty()


def test_max_size_keeps_most_recent():
    history = HistoryManager(max_size=2)
    history.add(make_calc("add", 1, 1, 2))
    history.add(make_calc("add", 2, 2, 4))
    history.add(make_calc("add", 3, 3, 6))

    results = [calculation.result for calculation in history.calculations()]

    assert results == [4.0, 6.0]


def test_restore_replaces_state():
    history = HistoryManager()
    history.add(make_calc("add", 9, 9, 18))

    history.restore((Calculation("subtract", 5, 1, 4),))
    assert history.calculations() == (Calculation("subtract", 5.0, 1.0, 4.0),)

    history.restore(())
    assert history.is_empty()


def test_save_and_load_round_trip(tmp_path):
    path = tmp_path / "history.csv"
    history = HistoryManager()
    history.add(make_calc("add", 2, 3, 5))
    history.add(make_calc("divide", 9, 3, 3))
    history.save(path)

    reloaded = HistoryManager()
    reloaded.load(path)

    assert reloaded.calculations() == history.calculations()


def test_load_rejects_missing_columns(tmp_path):
    path = tmp_path / "bad.csv"
    path.write_text("foo,bar\n1,2\n")

    history = HistoryManager()
    with pytest.raises(HistoryError, match="missing columns"):
        history.load(path)


def test_load_rejects_empty_file(tmp_path):
    path = tmp_path / "empty.csv"
    path.write_text("")

    history = HistoryManager()
    with pytest.raises(HistoryError, match="empty"):
        history.load(path)
