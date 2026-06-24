"""Observer pattern: react to calculation events.

The calculator is the subject; observers are notified each time a
calculation completes so they can log it or auto-save the history.
"""

import logging
from abc import ABC, abstractmethod
from pathlib import Path

from .calculation import Calculation
from .history import HistoryManager

logger = logging.getLogger("calculator")


class CalculationObserver(ABC):
    """Reacts to a freshly completed calculation."""

    @abstractmethod
    def notify(self, calculation: Calculation) -> None: ...


class LoggingObserver(CalculationObserver):
    """Write each calculation to the application log."""

    def __init__(self, target: logging.Logger | None = None) -> None:
        self._logger = target or logger

    def notify(self, calculation: Calculation) -> None:
        self._logger.info(
            "Calculation: %s(%g, %g) = %g",
            calculation.operation,
            calculation.a,
            calculation.b,
            calculation.result,
        )


class AutoSaveObserver(CalculationObserver):
    """Persist the calculation history to CSV after every calculation."""

    def __init__(self, history: HistoryManager, path: Path) -> None:
        self._history = history
        self._path = path

    def notify(self, calculation: Calculation) -> None:
        self._history.save(self._path)
