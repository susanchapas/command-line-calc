from calculator.calculation import Calculation
from calculator.memento import HistoryCaretaker, HistoryMemento


def memento(*results):
    return HistoryMemento(tuple(Calculation("add", r, 0, r) for r in results))


def test_undo_returns_none_when_empty():
    caretaker = HistoryCaretaker()

    assert caretaker.undo(memento(1)) is None


def test_redo_returns_none_when_empty():
    caretaker = HistoryCaretaker()

    assert caretaker.redo(memento(1)) is None


def test_undo_then_redo_round_trip():
    caretaker = HistoryCaretaker()
    empty = memento()
    one = memento(1)
    two = memento(1, 2)

    caretaker.save_state(empty)
    caretaker.save_state(one)

    assert caretaker.undo(two) == one
    assert caretaker.undo(one) == empty
    assert caretaker.undo(empty) is None

    assert caretaker.redo(empty) == one
    assert caretaker.redo(one) == two


def test_save_state_clears_redo_stack():
    caretaker = HistoryCaretaker()
    caretaker.save_state(memento())
    caretaker.undo(memento(1))

    caretaker.save_state(memento(9))

    assert caretaker.redo(memento(9)) is None
