"""Factory pattern: build operations from user-entered names."""

from typing import ClassVar

from .exceptions import OperationError
from .operations import OPERATIONS, Operation


class OperationFactory:
    """Create :class:`Operation` instances keyed by operation name.

    The registry is the one populated by the :func:`~app.operations.register`
    decorator, so a newly decorated operation is buildable without any change
    here.
    """

    _registry: ClassVar[dict[str, type[Operation]]] = OPERATIONS

    @classmethod
    def available_operations(cls) -> tuple[str, ...]:
        return tuple(cls._registry)

    @classmethod
    def symbol(cls, operation_name: str) -> str:
        return cls._registry[operation_name].symbol

    def create(self, operation_name: str) -> Operation:
        """Return an operation instance for ``operation_name``.

        :raises OperationError: if no operation is registered under that name.
        """
        try:
            operation_type = self._registry[operation_name.strip().lower()]
        except KeyError as exc:
            valid_operations = ", ".join(self.available_operations())
            raise OperationError(f"Choose one of: {valid_operations}.") from exc

        return operation_type()
