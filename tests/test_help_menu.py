import pytest

from app.help_menu import (
    COMMAND_LINES,
    CommandHelp,
    HelpComponent,
    HelpDecorator,
    OperationHelp,
    SectionHeading,
    build_help_menu,
)
from app.operations import OPERATIONS


def operation_lines(menu):
    lines = menu.render()
    return lines[lines.index("Operations:") + 1 :]


def test_help_component_is_abstract():
    with pytest.raises(TypeError):
        HelpComponent()


def test_concrete_component_renders_the_command_list():
    assert CommandHelp().render() == COMMAND_LINES


def test_base_decorator_delegates_to_the_wrapped_component():
    component = CommandHelp()
    decorator = HelpDecorator(component)

    assert decorator.component is component
    assert decorator.render() == component.render()


def test_decorators_wrap_decorators():
    menu = SectionHeading(SectionHeading(CommandHelp(), "first"), "second")

    assert menu.render() == (*COMMAND_LINES, "first", "second")


def test_operation_decorator_appends_one_line():
    menu = OperationHelp(CommandHelp(), OPERATIONS["add"], 8, 3)

    assert menu.render()[:-1] == COMMAND_LINES
    assert menu.render()[-1] == "  add       +    a plus b"


def test_menu_starts_with_the_commands_then_the_operations_heading():
    lines = build_help_menu().render()

    assert lines[: len(COMMAND_LINES)] == COMMAND_LINES
    assert lines[len(COMMAND_LINES)] == "Operations:"


def test_menu_has_one_line_per_registered_operation():
    lines = operation_lines(build_help_menu())

    assert len(lines) == len(OPERATIONS)
    for line, operation in zip(lines, OPERATIONS.values(), strict=True):
        assert line.startswith(f"  {operation.name} ")
        assert operation.symbol in line
        assert line.endswith(operation.description)


def test_menu_aligns_every_description_in_the_same_column():
    lines = operation_lines(build_help_menu())

    columns = {
        len(line) - len(operation.description)
        for line, operation in zip(lines, OPERATIONS.values(), strict=True)
    }

    assert len(columns) == 1


def test_registering_an_operation_adds_a_decorator_layer(extra_operation):
    without_extra = {
        name: operation
        for name, operation in OPERATIONS.items()
        if operation is not extra_operation
    }

    lines = operation_lines(build_help_menu())

    assert len(lines) == len(operation_lines(build_help_menu(without_extra))) + 1
    assert lines[-1].endswith("a plus b, tripled")


def test_a_long_operation_name_widens_every_line():
    narrow = build_help_menu({"add": OPERATIONS["add"]})
    wide = build_help_menu({"add": OPERATIONS["add"], "int_divide": OPERATIONS["int_divide"]})

    assert operation_lines(narrow)[0] == "  add  +  a plus b"
    assert operation_lines(wide)[0] == "  add         +   a plus b"
