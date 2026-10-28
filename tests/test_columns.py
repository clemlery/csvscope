from datetime import date
from decimal import Decimal

import pytest

from csvscope.columns import (
    DATE,
    FLOAT,
    INTEGER,
    STRING,
    UNKNOWN,
    date_formats,
    decimal_separator,
    describe_mix,
    infer_type,
    is_identifier,
    mixed_date_formats,
    split_valid,
)
from csvscope.values import DATE_FORMATS, DECIMAL_SEPARATORS


# Rôle identifiant


@pytest.mark.parametrize(
    "name",
    ["id", "ID", "uuid", "UUID", "identifier", "Identifier", "identifiant",
     "product_id", "Client_ID"],
)
def test_identifier_names(name):
    assert is_identifier(name)


@pytest.mark.parametrize(
    "name",
    ["id_client", "paid", "uid", "ids", "identifiants", "product-id", "productid", "nom"],
)
def test_not_identifier_names(name):
    assert not is_identifier(name)


# Description d'un mélange de libellés


def test_describe_mix_none():
    assert describe_mix([], DECIMAL_SEPARATORS) == "aucun"


def test_describe_mix_single():
    assert describe_mix(["virgule", "virgule"], DECIMAL_SEPARATORS) == "virgule"


def test_describe_mix_uses_fixed_order():
    assert describe_mix(["virgule", "point"], DECIMAL_SEPARATORS) == "mixte (point, virgule)"
    assert (
        describe_mix(["JJ/MM/AAAA", "AAAA-MM-JJ"], DATE_FORMATS)
        == "mixte (AAAA-MM-JJ, JJ/MM/AAAA)"
    )


# Formats de date


def test_date_formats_in_fixed_order():
    values = ["05/03/2026", "2026-03-01", "abc"]
    assert date_formats(values) == ["AAAA-MM-JJ", "JJ/MM/AAAA"]


def test_date_formats_ignores_non_dates():
    assert date_formats(["2026-1-5", "2026-02-30", "abc"]) == []


def test_mixed_date_formats_with_majority_of_dates():
    values = ["2026-03-01", "05/03/2026", "2026-03-20", "10/03/2026", "2026-04-02"]
    assert mixed_date_formats(values) == ["AAAA-MM-JJ", "JJ/MM/AAAA"]


def test_mixed_date_formats_empty_with_single_format():
    assert mixed_date_formats(["2026-01-15", "2026-02-20"]) == []


def test_mixed_date_formats_empty_without_majority():
    # 2 dates sur 4 : pas plus de 50 %.
    assert mixed_date_formats(["2026-01-01", "05/03/2026", "a", "b"]) == []


# Type d'une colonne


def test_unknown_without_values():
    assert infer_type([], allow_comma=True) == UNKNOWN


def test_integer():
    assert infer_type(["28", "34", "-4"], allow_comma=True) == INTEGER


def test_integer_with_invalid_values():
    # 3 nombres sur 5 (60 %).
    assert infer_type(["7", "8", "9", "X1", "Y2"], allow_comma=True) == INTEGER


def test_float_with_integers():
    assert infer_type(["12,5", "8,25", "10", "7,75"], allow_comma=True) == FLOAT


def test_float_with_mixed_separators():
    assert infer_type(["1.5", "2,5", "3.0", "4,0"], allow_comma=True) == FLOAT


def test_comma_not_a_decimal_when_not_allowed():
    # "12,5" n'est pas un nombre : 2 nombres sur 3, colonne float.
    assert infer_type(["10.5", "7.25", "12,5"], allow_comma=False) == FLOAT
    # Seules des virgules : aucun nombre, colonne string.
    assert infer_type(["1,5", "2,5"], allow_comma=False) == STRING


def test_exactly_half_numbers_is_string():
    assert infer_type(["A1", "12", "B2", "34"], allow_comma=True) == STRING


def test_date():
    assert infer_type(["15/01/2026", "20/02/2026"], allow_comma=True) == DATE


def test_date_with_invalid_values():
    values = ["2026-01-15", "2026-03-10", "2025-12-01", "2026-02-28", "2026-1-5"]
    assert infer_type(values, allow_comma=True) == DATE


def test_dates_in_several_formats_is_string():
    values = ["2026-03-01", "05/03/2026", "2026-03-20", "10/03/2026", "2026-04-02"]
    assert infer_type(values, allow_comma=True) == STRING


def test_exactly_half_dates_is_string():
    values = ["2026-01-01", "2026-01-02", "inconnu", "demain"]
    assert infer_type(values, allow_comma=True) == STRING


def test_numbers_win_over_dates():
    assert infer_type(["1", "2", "2026-01-01"], allow_comma=True) == INTEGER


def test_string():
    assert infer_type(["Alice", "Benoit", "Claire"], allow_comma=True) == STRING


def test_type_does_not_depend_on_first_value_only():
    assert infer_type(["abc", "1", "2"], allow_comma=True) == INTEGER
    assert infer_type(["1", "abc", "def"], allow_comma=True) == STRING


# Valeurs valides et invalides


def test_split_valid_integer():
    assert split_valid(["10", "abc", "-4", "6"], INTEGER, True) == ([10, -4, 6], 1)


def test_split_valid_integer_refuses_decimals():
    assert split_valid(["1", "2", "2.5"], INTEGER, True) == ([1, 2], 1)


def test_split_valid_float_accepts_integers():
    valid, invalid = split_valid(["2.5", "x", "1.0", "4"], FLOAT, True)
    assert valid == [Decimal("2.5"), Decimal("1.0"), Decimal("4")]
    assert invalid == 1


def test_split_valid_float_with_comma():
    valid, invalid = split_valid(["-3,5", "2", "-1,25"], FLOAT, True)
    assert valid == [Decimal("-3.5"), Decimal("2"), Decimal("-1.25")]
    assert invalid == 0


def test_split_valid_float_refuses_comma_when_not_allowed():
    valid, invalid = split_valid(["10.5", "7.25", "12,5"], FLOAT, False)
    assert valid == [Decimal("10.5"), Decimal("7.25")]
    assert invalid == 1


def test_split_valid_date():
    values = ["2026-01-10", "2026-02-30", "2026-03-15"]
    assert split_valid(values, DATE, True) == ([date(2026, 1, 10), date(2026, 3, 15)], 1)


@pytest.mark.parametrize("column_type", [STRING, UNKNOWN])
def test_split_valid_never_invalid_for_string_or_unknown(column_type):
    assert split_valid(["A1", "12"], column_type, True) == (["A1", "12"], 0)


@pytest.mark.parametrize(
    ("values", "expected"),
    [
        (["12,5", "8,25", "10", "7,75"], "virgule"),
        (["1.75", "1.80"], "point"),
        (["1.5", "2,5", "3.0", "4,0"], "mixte (point, virgule)"),
    ],
)
def test_decimal_separator(values, expected):
    assert decimal_separator(values, allow_comma=True) == expected


def test_decimal_separator_ignores_invalid_comma():
    assert decimal_separator(["10.5", "7.25", "12,5"], allow_comma=False) == "point"
