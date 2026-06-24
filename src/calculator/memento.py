"""Memento pattern: capture and restore history state for undo/redo."""

from dataclasses import dataclass

from .calculation import Calculation


@dataclass(frozen=True, slots=True)
class HistoryMemento:
    """An immutable snapshot of the calculation history."""

    state: tuple[Calculation, ...]


class HistoryCaretaker:
    """Maintain undo/redo stacks of history snapshots."""

    def __init__(self) -> None:
        self._undo: list[HistoryMemento] = []
        self._redo: list[HistoryMemento] = []

    def save_state(self, memento: HistoryMemento) -> None:
        """Record the pre-change state and invalidate the redo stack."""
        self._undo.append(memento)
        self._redo.clear()

    def undo(self, current: HistoryMemento) -> HistoryMemento | None:
        if not self._undo:
            return None
        self._redo.append(current)
        return self._undo.pop()

    def redo(self, current: HistoryMemento) -> HistoryMemento | None:
        if not self._redo:
            return None
        self._undo.append(current)
        return self._redo.pop()
