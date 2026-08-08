"""Facade pattern: a single simple interface over the calculator subsystems.

``Calculator`` hides the factory, strategies, pandas-backed history,
observers, and memento-based undo/redo behind a handful of methods.
"""

import math
from pathlib import Path

from .calculation import Calculation
from .calculator_config import CalculatorConfig
from .calculator_memento import HistoryCaretaker, HistoryMemento
from .exceptions import HistoryError, OperationError
from .factory import OperationFactory
from .history import HistoryManager
from .input_validators import validate_range
from .logger import get_logger
from .observers import AutoSaveObserver, CalculationObserver, LoggingObserver
from .strategies import OperationStrategy

logger = get_logger()

RESULT_TOO_LARGE = "Result is too large to represent."


class Calculator:
    def __init__(
        self,
        config: CalculatorConfig | None = None,
        observers: list[CalculationObserver] | None = None,
    ) -> None:
        self.config = config or CalculatorConfig.from_env()
        self.config.ensure_directories()
        self.factory = OperationFactory()
        self.history = HistoryManager(
            max_size=self.config.max_history_size,
            encoding=self.config.default_encoding,
        )
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
        logger.info(
            "Calculator ready: precision=%d, max history=%d, auto-save=%s.",
            self.config.precision,
            self.config.max_history_size,
            self.config.auto_save,
        )

    def _load_existing_history(self) -> None:
        if not Path(self.config.history_file).exists():
            return
        try:
            self.history.load(self.config.history_file)
        except HistoryError as error:
            logger.error(
                "Ignoring unreadable history at %s: %s. It will be overwritten "
                "by the next calculation.",
                self.config.history_file,
                error,
            )
            return
        logger.info(
            "Restored %d calculations from %s.",
            len(self.history),
            self.config.history_file,
        )

    def add_observer(self, observer: CalculationObserver) -> None:
        self._observers.append(observer)

    def _notify(self, calculation: Calculation) -> None:
        for observer in self._observers:
            observer.notify(calculation)

    def _snapshot(self) -> HistoryMemento:
        return HistoryMemento(self.history.calculations())

    def _auto_persist(self) -> None:
        """Mirror in-memory history to disk when auto-save is enabled.

        Every change to the history reaches disk: ``perform`` through
        :class:`AutoSaveObserver`, and ``undo``, ``redo``, ``clear``, and
        ``load`` through here, so what the user sees survives a restart. A
        failed auto-save is logged rather than raised, because the in-memory
        history is still correct and an explicit ``save`` reports the problem
        directly.
        """
        if not self.config.auto_save:
            return
        try:
            self.save()
        except HistoryError as error:
            logger.error("Auto-save failed: %s", error)

    @staticmethod
    def _execute(strategy: OperationStrategy, left: float, right: float) -> float:
        """Return the strategy's result, rejecting values floats cannot hold.

        :raises OperationError: if the result overflows or is not finite.
        """
        try:
            result = strategy.execute(left, right)
        except OverflowError as exc:
            raise OperationError(RESULT_TOO_LARGE) from exc
        if not math.isfinite(result):
            raise OperationError(RESULT_TOO_LARGE)
        return result

    def perform(self, operation: str, left: float, right: float) -> Calculation:
        strategy = self.factory.create(operation)
        validate_range(left, self.config.max_input_value)
        validate_range(right, self.config.max_input_value)
        result = round(self._execute(strategy, left, right), self.config.precision)
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
            logger.info("Nothing to undo.")
            return False
        self.history.restore(memento.state)
        logger.info("Undid the last change; %d calculations remain.", len(self.history))
        self._auto_persist()
        return True

    def redo(self) -> bool:
        memento = self.caretaker.redo(self._snapshot())
        if memento is None:
            logger.info("Nothing to redo.")
            return False
        self.history.restore(memento.state)
        logger.info("Redid the last change; %d calculations remain.", len(self.history))
        self._auto_persist()
        return True

    def clear(self) -> None:
        logger.info("Clearing %d calculations from the history.", len(self.history))
        self.caretaker.save_state(self._snapshot())
        self.history.clear()
        self._auto_persist()

    def save(self, path: Path | str | None = None) -> Path:
        target = Path(path) if path is not None else Path(self.config.history_file)
        self.history.save(target)
        logger.info("Saved %d calculations to %s.", len(self.history), target)
        return target

    def load(self, path: Path | str | None = None) -> Path:
        target = Path(path) if path is not None else Path(self.config.history_file)
        snapshot = self._snapshot()
        self.history.load(target)
        self.caretaker.save_state(snapshot)
        logger.info("Loaded %d calculations from %s.", len(self.history), target)
        self._auto_persist()
        return target
