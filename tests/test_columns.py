from datetime import date
from decimal import Decimal

import pytest

from csvscope.columns import (
    DATE,
    FLOAT,
    INTEGER,
    STRING,
    UNKNOWN,
    analyze_column,
    date_formats,
    date_stats,
    decimal_separator,
    describe_mix,
    infer_type,
    is_identifier,
    missing_rate,
    mixed_date_formats,
    numeric_stats,
    split_valid,
    string_stats,
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


# Statistiques


def test_numeric_stats_integer():
    stats = numeric_stats([28, 34, 22, 41, 30], INTEGER)
    assert stats == {"min": 22, "max": 41, "mean": 31.0}
    assert type(stats["min"]) is int and type(stats["max"]) is int


def test_numeric_stats_float():
    numbers = [Decimal("12.5"), Decimal("8.25"), Decimal("10"), Decimal("7.75")]
    stats = numeric_stats(numbers, FLOAT)
    assert stats == {"min": 7.75, "max": 12.5, "mean": 9.625}
    assert type(stats["min"]) is float and type(stats["max"]) is float


def test_numeric_stats_mean_is_not_rounded():
    assert numeric_stats([0, 1, 1], INTEGER)["mean"] == pytest.approx(2 / 3)


def test_numeric_stats_without_values():
    assert numeric_stats([], INTEGER) == {"min": None, "max": None, "mean": None}


def test_date_stats():
    dates = [date(2026, 3, 1), date(2025, 12, 1), date(2026, 3, 10)]
    assert date_stats(dates) == {"min": date(2025, 12, 1), "max": date(2026, 3, 10)}


def test_date_stats_without_values():
    assert date_stats([]) == {"min": None, "max": None}


def test_string_stats_sorted_by_count_then_alphabetically():
    values = ["Home Appliances", "Furniture", "Electronics", "Electronics", "Home Appliances"]
    assert string_stats(values) == {
        "distinct": 3,
        "distribution": [("Electronics", 2), ("Home Appliances", 2), ("Furniture", 1)],
    }


def test_string_stats_without_repetition():
    assert string_stats(["Alice", "Benoit", "Claire"]) == {"distinct": 3, "distribution": None}


def test_string_stats_single_repeated_value():
    assert string_stats(["bien", "bien"]) == {"distinct": 1, "distribution": [("bien", 2)]}


def test_string_stats_with_20_distinct_values():
    values = [f"G{i:02d}" for i in range(1, 21)] + ["G01", "G02"]
    stats = string_stats(values)
    assert stats["distinct"] == 20
    assert stats["distribution"][:3] == [("G01", 2), ("G02", 2), ("G03", 1)]
    assert len(stats["distribution"]) == 20


def test_string_stats_with_21_distinct_values():
    values = [f"V{i:02d}" for i in range(1, 22)] + ["V01"]
    assert string_stats(values) == {"distinct": 21, "distribution": None}


# Taux de valeurs manquantes


@pytest.mark.parametrize(
    ("missing", "row_count", "expected"),
    [(0, 5, 0.0), (1, 6, 16.7), (4, 6, 66.7), (5, 6, 83.3), (6, 6, 100.0), (1, 4, 25.0)],
)
def test_missing_rate(missing, row_count, expected):
    assert missing_rate(missing, row_count) == expected


def test_missing_rate_without_rows():
    assert missing_rate(0, 0) == 0.0


# Analyse d'une colonne


def test_analyze_integer_column_strips_values():
    column = analyze_column("age", ["28", "", "22", " 41"], allow_comma=True)
    assert column == {
        "name": "age",
        "type": INTEGER,
        "role": None,
        "missing": 1,
        "missing_rate": 25.0,
        "invalid": 0,
        "decimal_separator": None,
        "date_format": None,
        "mixed_date_formats": [],
        "min": 22,
        "max": 41,
        "mean": pytest.approx(91 / 3),
        "distinct": None,
        "distribution": None,
    }


def test_analyze_missing_markers():
    values = ["NULL", "none", "bien", "na", "ABSENT", " n/a "]
    column = analyze_column("note", values, allow_comma=True)
    assert (column["missing"], column["missing_rate"]) == (5, 83.3)


def test_analyze_float_column():
    column = analyze_column("poids", ["12,5", "8,25", "10", "7,75"], allow_comma=True)
    assert column["type"] == FLOAT
    assert column["decimal_separator"] == "virgule"
    assert (column["min"], column["max"], column["mean"]) == (7.75, 12.5, 9.625)


def test_analyze_date_column():
    values = ["2026-01-15", "2026-03-10", "2025-12-01", "2026-02-28", "2026-1-5"]
    column = analyze_column("debut", values, allow_comma=True)
    assert column["type"] == DATE
    assert column["invalid"] == 1
    assert column["date_format"] == "AAAA-MM-JJ"
    assert (column["min"], column["max"]) == (date(2025, 12, 1), date(2026, 3, 10))
    assert column["mean"] is None


def test_analyze_string_column_with_mixed_dates():
    values = ["2026-03-01", "05/03/2026", "2026-03-20", "10/03/2026", "2026-04-02"]
    column = analyze_column("evenement", values, allow_comma=True)
    assert column["type"] == STRING
    assert column["mixed_date_formats"] == ["AAAA-MM-JJ", "JJ/MM/AAAA"]
    assert column["date_format"] is None
    assert (column["distinct"], column["distribution"]) == (5, None)


def test_analyze_identifier_column_has_no_stats():
    column = analyze_column("id", ["1", "2", "3"], allow_comma=True)
    assert column["type"] == INTEGER
    assert column["role"] == "identifiant"
    assert [column[key] for key in ("min", "max", "mean", "distinct", "distribution")] == [
        None
    ] * 5


def test_analyze_string_identifier_has_no_distinct():
    column = analyze_column("UUID", ["a1", "b2", "c3"], allow_comma=True)
    assert (column["type"], column["role"]) == (STRING, "identifiant")
    assert (column["distinct"], column["distribution"]) == (None, None)


def test_analyze_unknown_column():
    column = analyze_column("colonne_vide", ["", "NA", " "], allow_comma=True)
    assert column["type"] == UNKNOWN
    assert (column["missing"], column["missing_rate"], column["invalid"]) == (3, 100.0, 0)
    assert column["distinct"] is None


def test_analyze_column_without_rows():
    column = analyze_column("valeur", [], allow_comma=True)
    assert column["type"] == UNKNOWN
    assert (column["missing"], column["missing_rate"]) == (0, 0.0)
