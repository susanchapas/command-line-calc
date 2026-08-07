"""pandas-backed calculation history with CSV persistence."""

from pathlib import Path

import pandas as pd

from .calculation import Calculation
from .calculator_config import DEFAULT_ENCODING, DEFAULT_MAX_HISTORY_SIZE
from .exceptions import HistoryError

COLUMNS = ("operation", "a", "b", "result")


class HistoryManager:
    """Store calculation history in a :class:`pandas.DataFrame`."""

    def __init__(
        self,
        max_size: int = int(DEFAULT_MAX_HISTORY_SIZE),
        encoding: str = DEFAULT_ENCODING,
    ) -> None:
        self._max_size = max_size
        self._encoding = encoding
        self._df = self._empty_frame()

    @staticmethod
    def _empty_frame() -> pd.DataFrame:
        return pd.DataFrame(columns=list(COLUMNS))

    @staticmethod
    def _to_frame(calculations: tuple[Calculation, ...]) -> pd.DataFrame:
        if not calculations:
            return HistoryManager._empty_frame()
        return pd.DataFrame(
            {
                "operation": [c.operation for c in calculations],
                "a": [c.a for c in calculations],
                "b": [c.b for c in calculations],
                "result": [c.result for c in calculations],
            }
        )

    def add(self, calculation: Calculation) -> None:
        row = self._to_frame((calculation,))
        self._df = row if self._df.empty else pd.concat([self._df, row], ignore_index=True)
        if len(self._df) > self._max_size:
            self._df = self._df.iloc[-self._max_size :].reset_index(drop=True)

    def is_empty(self) -> bool:
        return self._df.empty

    def calculations(self) -> tuple[Calculation, ...]:
        return tuple(
            Calculation(str(row.operation), float(row.a), float(row.b), float(row.result))
            for row in self._df.itertuples(index=False)
        )

    def restore(self, calculations: tuple[Calculation, ...]) -> None:
        self._df = self._to_frame(calculations)

    def clear(self) -> None:
        self._df = self._empty_frame()

    def to_dataframe(self) -> pd.DataFrame:
        return self._df.copy()

    def save(self, path: Path | str) -> None:
        self._df.to_csv(path, index=False, encoding=self._encoding)

    def load(self, path: Path | str) -> None:
        try:
            frame = pd.read_csv(path, encoding=self._encoding)
        except pd.errors.EmptyDataError as exc:
            raise HistoryError("History file is empty.") from exc
        except UnicodeDecodeError as exc:
            raise HistoryError(f"History file is not valid {self._encoding} text.") from exc

        missing = [column for column in COLUMNS if column not in frame.columns]
        if missing:
            raise HistoryError(f"History file is missing columns: {', '.join(missing)}.")
        self._df = frame[list(COLUMNS)].reset_index(drop=True)
