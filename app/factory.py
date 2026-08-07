"""Factory pattern: build operation strategies from user-entered names."""

from typing import ClassVar

from .strategies import (
    AddStrategy,
    DivideStrategy,
    MultiplyStrategy,
    OperationStrategy,
    PowerStrategy,
    RootStrategy,
    SubtractStrategy,
)


class OperationFactory:
    """Create :class:`OperationStrategy` instances keyed by operation name."""

    _registry: ClassVar[dict[str, type[OperationStrategy]]] = {
        AddStrategy.name: AddStrategy,
        SubtractStrategy.name: SubtractStrategy,
        MultiplyStrategy.name: MultiplyStrategy,
        DivideStrategy.name: DivideStrategy,
        PowerStrategy.name: PowerStrategy,
        RootStrategy.name: RootStrategy,
    }

    @classmethod
    def available_operations(cls) -> tuple[str, ...]:
        return tuple(cls._registry)

    @classmethod
    def symbol(cls, operation_name: str) -> str:
        return cls._registry[operation_name].symbol

    @classmethod
    def describe_operations(cls) -> str:
        return ", ".join(
            f"{name} ({strategy.symbol})" for name, strategy in cls._registry.items()
        )

    def create(self, operation_name: str) -> OperationStrategy:
        try:
            strategy_type = self._registry[operation_name.strip().lower()]
        except KeyError as exc:
            valid_operations = ", ".join(self.available_operations())
            raise ValueError(f"Choose one of: {valid_operations}.") from exc

        return strategy_type()
