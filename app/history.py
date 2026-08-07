"""pandas-backed calculation history with CSV persistence."""

from pathlib import Path

import pandas as pd

from .calculation import Calculation
from .calculator_config import DEFAULT_ENCODING, DEFAULT_MAX_HISTORY_SIZE
from .exceptions import HistoryError
from .factory import OperationFactory

COLUMNS = ("operation", "a", "b", "result")
NUMERIC_COLUMNS = ("a", "b", "result")


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

    def __len__(self) -> int:
        return len(self._df)

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
        """Write the history to ``path`` as CSV.

        :raises HistoryError: if the file cannot be written.
        """
        try:
            self._df.to_csv(path, index=False, encoding=self._encoding)
        except OSError as exc:
            raise HistoryError(f"Could not write {path}: {exc}") from exc

    def load(self, path: Path | str) -> None:
        """Replace the history with the calculations stored at ``path``.

        :raises HistoryError: if the file is missing, unreadable, or malformed.
        """
        try:
            frame = pd.read_csv(path, encoding=self._encoding)
        except FileNotFoundError as exc:
            raise HistoryError(f"No history file at {path}.") from exc
        except OSError as exc:
            raise HistoryError(f"Could not read {path}: {exc}") from exc
        except pd.errors.EmptyDataError as exc:
            raise HistoryError("History file is empty.") from exc
        except pd.errors.ParserError as exc:
            raise HistoryError(f"History file is not valid CSV: {str(exc).strip()}") from exc
        except UnicodeDecodeError as exc:
            raise HistoryError(f"History file is not valid {self._encoding} text.") from exc

        self._df = self._validated(frame)

    @staticmethod
    def _validated(frame: pd.DataFrame) -> pd.DataFrame:
        """Return ``frame`` narrowed to :data:`COLUMNS`, checking every value.

        Guards the conversions :meth:`calculations` performs later, so bad CSV
        data is reported here instead of failing when the history is read.

        :raises HistoryError: if a column is missing or holds unusable values.
        """
        missing = [column for column in COLUMNS if column not in frame.columns]
        if missing:
            raise HistoryError(f"History file is missing columns: {', '.join(missing)}.")

        frame = frame[list(COLUMNS)].reset_index(drop=True)
        for column in NUMERIC_COLUMNS:
            values = pd.to_numeric(frame[column], errors="coerce")
            if values.isna().any():
                raise HistoryError(f"History column {column!r} has non-numeric values.")
            frame[column] = values

        unknown = sorted(
            set(frame["operation"].astype(str)) - set(OperationFactory.available_operations())
        )
        if unknown:
            raise HistoryError(f"History file has unknown operations: {', '.join(unknown)}.")
        return frame
