from datetime import datetime

import pytest

from app.calculation import Calculation, now
from app.exceptions import HistoryError
from app.history import COLUMNS, HistoryManager


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


def test_empty_to_dataframe_still_has_the_columns():
    assert list(HistoryManager().to_dataframe().columns) == list(COLUMNS)


def test_to_dataframe_returns_a_copy():
    history = HistoryManager()
    history.add(make_calc("add", 2, 3, 5))

    frame = history.to_dataframe()
    frame.loc[0, "result"] = 999

    assert history.calculations() == (Calculation("add", 2.0, 3.0, 5.0),)


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


def test_empty_history_round_trip(tmp_path):
    path = tmp_path / "empty.csv"
    HistoryManager().save(path)

    reloaded = HistoryManager()
    reloaded.load(path)

    assert reloaded.is_empty()


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


def test_round_trip_honours_the_configured_encoding(tmp_path):
    path = tmp_path / "history.csv"
    history = HistoryManager(encoding="latin-1")
    history.add(make_calc("add", 2, 3, 5))
    history.save(path)

    reloaded = HistoryManager(encoding="latin-1")
    reloaded.load(path)

    assert reloaded.calculations() == history.calculations()


def test_load_rejects_text_the_encoding_cannot_decode(tmp_path):
    path = tmp_path / "history.csv"
    path.write_bytes("operation,a,b,result\naddé,1,2,3\n".encode())

    history = HistoryManager(encoding="ascii")
    with pytest.raises(HistoryError, match="not valid ascii text"):
        history.load(path)


def test_load_rejects_missing_file(tmp_path):
    history = HistoryManager()

    with pytest.raises(HistoryError, match="No history file at"):
        history.load(tmp_path / "nope.csv")


def test_load_rejects_unreadable_path(tmp_path):
    history = HistoryManager()

    with pytest.raises(HistoryError, match="Could not read"):
        history.load(tmp_path)


def test_load_rejects_ragged_rows(tmp_path):
    path = tmp_path / "ragged.csv"
    path.write_text("operation,a,b,result\nadd,1,2,3\nadd,1,2,3,4,5\n")

    history = HistoryManager()
    with pytest.raises(HistoryError, match="not valid CSV"):
        history.load(path)


@pytest.mark.parametrize("column", ["a", "b", "result"])
def test_load_rejects_non_numeric_values(tmp_path, column):
    rows = {"a": "1", "b": "2", "result": "3"}
    rows[column] = "oops"
    path = tmp_path / "text.csv"
    path.write_text(f"operation,a,b,result\nadd,{rows['a']},{rows['b']},{rows['result']}\n")

    history = HistoryManager()
    with pytest.raises(HistoryError, match=f"column '{column}' has non-numeric"):
        history.load(path)


def test_load_rejects_blank_numeric_cells(tmp_path):
    path = tmp_path / "blank.csv"
    path.write_text("operation,a,b,result\nadd,1,,3\n")

    history = HistoryManager()
    with pytest.raises(HistoryError, match="non-numeric"):
        history.load(path)


def test_load_rejects_unknown_operations(tmp_path):
    path = tmp_path / "unknown.csv"
    path.write_text("operation,a,b,result\nlogarithm,8,2,3\n")

    history = HistoryManager()
    with pytest.raises(HistoryError, match="unknown operations: logarithm"):
        history.load(path)


def test_saved_csv_records_the_timestamp(tmp_path):
    path = tmp_path / "history.csv"
    stamp = datetime(2026, 8, 7, 12, 30, 15)
    history = HistoryManager()
    history.add(Calculation("add", 2.0, 3.0, 5.0, stamp))

    history.save(path)

    header, row = path.read_text().splitlines()
    assert header == "operation,a,b,result,timestamp"
    assert row == "add,2.0,3.0,5.0,2026-08-07T12:30:15"


def test_timestamps_survive_a_round_trip(tmp_path):
    path = tmp_path / "history.csv"
    stamp = now()
    history = HistoryManager()
    history.add(Calculation("add", 2, 3, 5, stamp))
    history.save(path)

    reloaded = HistoryManager()
    reloaded.load(path)

    assert reloaded.calculations()[0].timestamp == stamp


def test_load_accepts_history_written_without_a_timestamp_column(tmp_path):
    path = tmp_path / "legacy.csv"
    path.write_text("operation,a,b,result\nadd,2,3,5\n")

    history = HistoryManager()
    history.load(path)

    calculation = history.calculations()[0]
    assert calculation == Calculation("add", 2.0, 3.0, 5.0)
    assert calculation.timestamp is None


def test_load_accepts_a_blank_timestamp_cell(tmp_path):
    path = tmp_path / "blank.csv"
    path.write_text("operation,a,b,result,timestamp\nadd,2,3,5,\n")

    history = HistoryManager()
    history.load(path)

    assert history.calculations()[0].timestamp is None


def test_load_rejects_an_invalid_timestamp(tmp_path):
    path = tmp_path / "bad_time.csv"
    path.write_text("operation,a,b,result,timestamp\nadd,2,3,5,yesterday\n")

    history = HistoryManager()
    with pytest.raises(HistoryError, match="invalid timestamp: 'yesterday'"):
        history.load(path)


def test_history_without_timestamps_can_be_saved_again(tmp_path):
    source = tmp_path / "legacy.csv"
    source.write_text("operation,a,b,result\nadd,2,3,5\n")
    history = HistoryManager()
    history.load(source)

    target = tmp_path / "resaved.csv"
    history.save(target)

    reloaded = HistoryManager()
    reloaded.load(target)
    assert reloaded.calculations()[0].timestamp is None


def test_save_reports_unwritable_path(tmp_path):
    history = HistoryManager()
    history.add(make_calc())

    with pytest.raises(HistoryError, match="Could not write"):
        history.save(tmp_path / "missing" / "out.csv")
