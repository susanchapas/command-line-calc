"""Factory pattern: build operation strategies from user-entered names."""

from typing import ClassVar

from .exceptions import OperationError
from .strategies import OPERATIONS, OperationStrategy


class OperationFactory:
    """Create :class:`OperationStrategy` instances keyed by operation name.

    The registry is the one populated by the :func:`~app.strategies.register`
    decorator, so a newly decorated strategy is buildable without any change
    here.
    """

    _registry: ClassVar[dict[str, type[OperationStrategy]]] = OPERATIONS

    @classmethod
    def available_operations(cls) -> tuple[str, ...]:
        return tuple(cls._registry)

    @classmethod
    def symbol(cls, operation_name: str) -> str:
        return cls._registry[operation_name].symbol

    def create(self, operation_name: str) -> OperationStrategy:
        """Return a strategy instance for ``operation_name``.

        :raises OperationError: if no operation is registered under that name.
        """
        try:
            strategy_type = self._registry[operation_name.strip().lower()]
        except KeyError as exc:
            valid_operations = ", ".join(self.available_operations())
            raise OperationError(f"Choose one of: {valid_operations}.") from exc

        return strategy_type()
