"""Facade pattern: a single simple interface over the calculator subsystems.

``Calculator`` hides the factory, strategies, pandas-backed history,
observers, and memento-based undo/redo behind a handful of methods.
"""

from pathlib import Path

from .calculation import Calculation
from .calculator_config import CalculatorConfig
from .calculator_memento import HistoryCaretaker, HistoryMemento
from .factory import OperationFactory
from .history import HistoryManager
from .observers import AutoSaveObserver, CalculationObserver, LoggingObserver


class Calculator:
    def __init__(
        self,
        config: CalculatorConfig | None = None,
        observers: list[CalculationObserver] | None = None,
    ) -> None:
        self.config = config or CalculatorConfig.from_env()
        self.factory = OperationFactory()
        self.history = HistoryManager(max_size=self.config.max_history_size)
        self.caretaker = HistoryCaretaker()
        self._observers: list[CalculationObserver] = []

        if observers is None:
            self.add_observer(LoggingObserver())
            if self.config.auto_save:
                self.add_observer(AutoSaveObserver(self.history, self.config.history_file))
        else:
            for observer in observers:
                self.add_observer(observer)

        self._load_existing_history()

    def _load_existing_history(self) -> None:
        if Path(self.config.history_file).exists():
            self.history.load(self.config.history_file)

    def add_observer(self, observer: CalculationObserver) -> None:
        self._observers.append(observer)

    def _notify(self, calculation: Calculation) -> None:
        for observer in self._observers:
            observer.notify(calculation)

    def _snapshot(self) -> HistoryMemento:
        return HistoryMemento(self.history.calculations())

    def _auto_persist(self) -> None:
        """Mirror in-memory history to disk when auto-save is enabled.

        ``perform`` is covered by :class:`AutoSaveObserver`; the other
        state-changing methods persist through here.
        """
        if self.config.auto_save:
            self.save()

    def perform(self, operation: str, left: float, right: float) -> Calculation:
        strategy = self.factory.create(operation)
        result = strategy.execute(left, right)
        calculation = Calculation(strategy.name, left, right, result)
        self.caretaker.save_state(self._snapshot())
        self.history.add(calculation)
        self._notify(calculation)
        return calculation

    def format(self, calculation: Calculation) -> str:
        return calculation.render(self.factory.symbol(calculation.operation))

    def calculations(self) -> tuple[Calculation, ...]:
        return self.history.calculations()

    def undo(self) -> bool:
        memento = self.caretaker.undo(self._snapshot())
        if memento is None:
            return False
        self.history.restore(memento.state)
        self._auto_persist()
        return True

    def redo(self) -> bool:
        memento = self.caretaker.redo(self._snapshot())
        if memento is None:
            return False
        self.history.restore(memento.state)
        self._auto_persist()
        return True

    def clear(self) -> None:
        self.caretaker.save_state(self._snapshot())
        self.history.clear()
        self._auto_persist()

    def save(self, path: Path | str | None = None) -> Path:
        target = Path(path) if path is not None else Path(self.config.history_file)
        self.history.save(target)
        return target

    def load(self, path: Path | str | None = None) -> Path:
        target = Path(path) if path is not None else Path(self.config.history_file)
        snapshot = self._snapshot()
        self.history.load(target)
        self.caretaker.save_state(snapshot)
        self._auto_persist()
        return target
