from datetime import datetime, timedelta

from app.calculation import Calculation, now, parse_timestamp


def test_render_formats_integers():
    assert Calculation("add", 2, 3, 5).render("+") == "2 + 3 = 5"


def test_render_formats_floats():
    assert Calculation("divide", 5, 2, 2.5).render("/") == "5 / 2 = 2.5"


def test_timestamp_defaults_to_the_current_time():
    before = now()
    stamp = Calculation("add", 2, 3, 5).timestamp

    assert stamp is not None
    assert stamp.tzinfo is not None
    assert before - timedelta(seconds=5) <= stamp <= now() + timedelta(seconds=5)


def test_timestamp_can_be_given_explicitly():
    stamp = datetime(2026, 8, 7, 12, 30, tzinfo=None)

    assert Calculation("add", 2, 3, 5, stamp).timestamp == stamp


def test_timestamp_is_excluded_from_equality():
    early = Calculation("add", 2, 3, 5, datetime(2020, 1, 1))
    late = Calculation("add", 2, 3, 5, datetime(2026, 8, 7))

    assert early == late


def test_parse_timestamp_round_trips_an_iso_string():
    stamp = now()

    assert parse_timestamp(stamp.isoformat()) == stamp


def test_parse_timestamp_rejects_non_iso_text():
    assert parse_timestamp("not a time") is None
    assert parse_timestamp("") is None
