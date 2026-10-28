from decimal import Decimal

import pytest

from csvscope.rounding import round_half_up


@pytest.mark.parametrize(
    ("value", "places", "expected"),
    [
        (Decimal("0.125"), 2, "0.13"),
        (Decimal("9.625"), 2, "9.63"),
        (Decimal("8.875"), 2, "8.88"),
        (Decimal("16.66666"), 1, "16.7"),
        (Decimal("0.05"), 1, "0.1"),
        (Decimal("2.5"), 0, "3"),
    ],
)
def test_ties_round_up(value, places, expected):
    assert round_half_up(value, places) == Decimal(expected)


def test_float_input_uses_its_shortest_repr():
    # 0.125, 9.625 et 2.675 donnent un résultat différent avec round()
    assert round_half_up(0.125, 2) == Decimal("0.13")
    assert round_half_up(9.625, 2) == Decimal("9.63")
    assert round_half_up(2.675, 2) == Decimal("2.68")


def test_int_input():
    assert round_half_up(31, 2) == Decimal("31.00")


def test_result_keeps_requested_places():
    assert str(round_half_up(Decimal("50"), 2)) == "50.00"
    assert str(round_half_up(0.0, 1)) == "0.0"


def test_below_half_rounds_down():
    assert round_half_up(Decimal("14.5449"), 2) == Decimal("14.54")


def test_negative_tie_rounds_away_from_zero():
    assert round_half_up(Decimal("-0.125"), 2) == Decimal("-0.13")
