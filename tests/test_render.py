from datetime import date
from pathlib import Path

import pytest

from csvscope.analysis import analyze_file
from csvscope.render import (
    format_date,
    format_mean,
    format_missing,
    format_number,
    format_remark,
    format_separator,
    render_file,
)

ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture
def at_root(monkeypatch):
    """Lance le test depuis la racine du projet, pour des chemins comme samples/clean.csv."""
    monkeypatch.chdir(ROOT)


def analyze(name):
    return analyze_file(f"samples/{name}")


# Mise en forme des valeurs


def test_format_separator():
    assert format_separator("\t") == "tabulation"
    assert format_separator("|") == "|"


@pytest.mark.parametrize(
    ("value", "column_type", "expected"),
    [
        (-4, "integer", "-4"),
        (9.4, "float", "9.40"),
        (1000.0, "float", "1000.00"),
        (-3.5, "float", "-3.50"),
        (2.675, "float", "2.68"),
    ],
)
def test_format_number(value, column_type, expected):
    assert format_number(value, column_type) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [(31.0, "31.00"), (9.625, "9.63"), (8.875, "8.88"), (2 / 3, "0.67"), (-0.5625, "-0.56")],
)
def test_format_mean(value, expected):
    assert format_mean(value) == expected


def test_format_date():
    assert format_date(date(2025, 12, 31)) == "2025-12-31"


def test_format_missing():
    assert format_missing(1, 16.7) == "1 (16.7 %)"
    assert format_missing(6, 100.0) == "6 (100.0 %)"
    assert format_missing(0, 0.0) == "0 (0.0 %)"


def test_format_remark():
    assert format_remark(["AAAA-MM-JJ", "JJ/MM/AAAA"]) == (
        "dates dans plusieurs formats (AAAA-MM-JJ, JJ/MM/AAAA), colonne traitée comme string"
    )


# En-tête du fichier


def test_header_of_mixed_files(at_root):
    decimal_header = render_file(analyze("mixed_decimal.csv")[0])
    dates_header = render_file(analyze("mixed_dates.csv")[0])
    assert decimal_header[4] == "Séparateur décimal : mixte (point, virgule)"
    assert dates_header[5] == "Format de date     : mixte (AAAA-MM-JJ, JJ/MM/AAAA)"


def test_header_with_tab_separator(at_root):
    assert render_file(analyze("tabulation.csv")[0])[3] == "Séparateur         : tabulation"
