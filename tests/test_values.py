from datetime import date
from decimal import Decimal

import pytest

from csvscope.values import (
    COMMA,
    FR_DATE,
    ISO_DATE,
    POINT,
    is_missing,
    parse_date,
    parse_decimal,
    parse_integer,
)


@pytest.mark.parametrize(
    "value",
    ["", "NA", "na", "N/A", "n/a", "NULL", "null", "None", "none", "Absent", "ABSENT"],
)
def test_missing_values(value):
    assert is_missing(value)


@pytest.mark.parametrize(
    "value", ["0", "-", "?", "nan", "NaN", "n.a.", "missing", "vide", "Nones"]
)
def test_other_strings_are_not_missing(value):
    assert not is_missing(value)


@pytest.mark.parametrize(
    ("value", "expected"),
    [("42", 42), ("-4", -4), ("0", 0), ("007", 7)],
)
def test_integers(value, expected):
    assert parse_integer(value) == expected


@pytest.mark.parametrize(
    "value",
    ["", "-", "+4", "--4", "4.0", "4,0", "1e3", "4 2", "abc", "١٢", "１２"],
)
def test_not_integers(value):
    assert parse_integer(value) is None


@pytest.mark.parametrize(
    ("value", "allow_comma", "expected"),
    [
        ("9.4", False, (Decimal("9.4"), POINT)),
        ("9.4", True, (Decimal("9.4"), POINT)),
        ("-3,5", True, (Decimal("-3.5"), COMMA)),
        ("1,25", True, (Decimal("1.25"), COMMA)),
        ("50.0", False, (Decimal("50.0"), POINT)),
    ],
)
def test_decimals(value, allow_comma, expected):
    assert parse_decimal(value, allow_comma) == expected


def test_comma_refused_when_not_allowed():
    assert parse_decimal("12,5", allow_comma=False) is None


@pytest.mark.parametrize(
    "value",
    [
        "10",
        ".5",
        "5.",
        ",5",
        "5,",
        "-.5",
        "+1.5",
        "1.2.3",
        "1,2,3",
        "1.2,3",
        "1.5e3",
        "١.٥",
        "abc",
    ],
)
def test_not_decimals(value):
    assert parse_decimal(value, allow_comma=True) is None


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("2026-01-15", (date(2026, 1, 15), ISO_DATE)),
        ("15/01/2026", (date(2026, 1, 15), FR_DATE)),
        ("2024-02-29", (date(2024, 2, 29), ISO_DATE)),
    ],
)
def test_dates(value, expected):
    assert parse_date(value) == expected


@pytest.mark.parametrize(
    "value",
    [
        "2026-1-5",
        "5/1/2026",
        "2026-02-30",
        "30/02/2026",
        "2025-02-29",
        "01/15/2026",
        "2026/01/15",
        "15-01-2026",
        "20260115",
        "2026-01-15T10:00",
        "２０２６-01-15",
        "abc",
    ],
)
def test_not_dates(value):
    assert parse_date(value) is None
