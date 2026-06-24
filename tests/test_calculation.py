from calculator.calculation import Calculation


def test_render_formats_integers():
    assert Calculation("add", 2, 3, 5).render("+") == "2 + 3 = 5"


def test_render_formats_floats():
    assert Calculation("divide", 5, 2, 2.5).render("/") == "5 / 2 = 2.5"
