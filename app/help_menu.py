"""Decorator pattern: the ``help`` menu, built by wrapping components.

:class:`CommandHelp` is the concrete component and holds the fixed command
list. :class:`HelpDecorator` is the base decorator, storing a wrapped component
and delegating to it. Each concrete decorator renders the component it wraps
and adds its own lines to the result.

:func:`build_help_menu` stacks one :class:`OperationHelp` decorator per
registered operation, so the menu gains a line whenever a strategy is
registered. Nothing in this module names an individual operation.
"""

from abc import ABC, abstractmethod

from .strategies import OPERATIONS, OperationStrategy

COMMAND_LINES = (
    "Commands:",
    "  <operation> <a> <b>   run a calculation (e.g. add 2 3)",
    "  history               show the calculation history",
    "  undo / redo           step backward or forward through history",
    "  save [path]           save history to a CSV file",
    "  load [path]           load history from a CSV file",
    "  clear                 erase the current history",
    "  help                  show this message",
    "  exit                  quit the calculator",
)


class HelpComponent(ABC):
    """The component interface: anything that renders itself as help lines."""

    @abstractmethod
    def render(self) -> tuple[str, ...]:
        """Return the help lines this component contributes."""


class CommandHelp(HelpComponent):
    """Concrete component: the command list, which does not vary."""

    def render(self) -> tuple[str, ...]:
        return COMMAND_LINES


class HelpDecorator(HelpComponent):
    """Base decorator: wraps a component and delegates rendering to it."""

    def __init__(self, component: HelpComponent) -> None:
        self._component = component

    @property
    def component(self) -> HelpComponent:
        return self._component

    def render(self) -> tuple[str, ...]:
        return self.component.render()


class SectionHeading(HelpDecorator):
    """Concrete decorator: adds a heading below the wrapped component."""

    def __init__(self, component: HelpComponent, heading: str) -> None:
        super().__init__(component)
        self._heading = heading

    def render(self) -> tuple[str, ...]:
        return (*self.component.render(), self._heading)


class OperationHelp(HelpDecorator):
    """Concrete decorator: adds one operation's line to the wrapped menu."""

    def __init__(
        self,
        component: HelpComponent,
        strategy: type[OperationStrategy],
        name_width: int,
        symbol_width: int,
    ) -> None:
        super().__init__(component)
        self._strategy = strategy
        self._name_width = name_width
        self._symbol_width = symbol_width

    def render(self) -> tuple[str, ...]:
        strategy = self._strategy
        line = (
            f"  {strategy.name:<{self._name_width}}  "
            f"{strategy.symbol:<{self._symbol_width}}  {strategy.description}"
        )
        return (*self.component.render(), line)


def build_help_menu(
    operations: dict[str, type[OperationStrategy]] | None = None,
) -> HelpComponent:
    """Return the command list wrapped in one decorator per registered operation.

    Widths come from the registry, so a long operation name widens every line
    instead of breaking the alignment.
    """
    registry = OPERATIONS if operations is None else operations
    name_width = max(len(name) for name in registry)
    symbol_width = max(len(strategy.symbol) for strategy in registry.values())

    menu: HelpComponent = SectionHeading(CommandHelp(), "Operations:")
    for strategy in registry.values():
        menu = OperationHelp(menu, strategy, name_width, symbol_width)
    return menu
