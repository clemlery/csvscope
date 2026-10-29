import json
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
    json_column,
    json_number,
    render_column,
    render_file,
    render_json,
    render_report,
)

ROOT = Path(__file__).resolve().parent.parent

CLEAN_REPORT = """\
Fichier            : samples/clean.csv
Lignes             : 5
Colonnes           : 5
Séparateur         : ,
Séparateur décimal : point
Format de date     : AAAA-MM-JJ

[id]
  Type        : integer
  Rôle        : identifiant
  Manquantes  : 0 (0.0 %)
  Invalides   : 0

[nom]
  Type        : string
  Manquantes  : 0 (0.0 %)
  Invalides   : 0
  Distincts   : 5

[age]
  Type        : integer
  Manquantes  : 0 (0.0 %)
  Invalides   : 0
  Min         : 22
  Max         : 41
  Moyenne     : 31.00

[score]
  Type        : float
  Manquantes  : 0 (0.0 %)
  Invalides   : 0
  Min         : 9.40
  Max         : 18.90
  Moyenne     : 14.54

[date_inscription]
  Type        : date
  Manquantes  : 0 (0.0 %)
  Invalides   : 0
  Plus ancienne : 2026-01-15
  Plus récente  : 2026-05-30"""

CLEAN_JSON = """\
{
  "file": {
    "path": "samples/clean.csv",
    "row_count": 5,
    "column_count": 5,
    "separator": ",",
    "decimal_separator": "point",
    "date_format": "AAAA-MM-JJ"
  },
  "columns": [
    {
      "name": "id",
      "type": "integer",
      "role": "identifiant",
      "missing": 0,
      "missing_rate": 0.0,
      "invalid": 0,
      "decimal_separator": null,
      "date_format": null,
      "mixed_date_formats": [],
      "min": null,
      "max": null,
      "mean": null,
      "distinct": null,
      "distribution": null
    },
    {
      "name": "nom",
      "type": "string",
      "role": null,
      "missing": 0,
      "missing_rate": 0.0,
      "invalid": 0,
      "decimal_separator": null,
      "date_format": null,
      "mixed_date_formats": [],
      "min": null,
      "max": null,
      "mean": null,
      "distinct": 5,
      "distribution": null
    },
    {
      "name": "age",
      "type": "integer",
      "role": null,
      "missing": 0,
      "missing_rate": 0.0,
      "invalid": 0,
      "decimal_separator": null,
      "date_format": null,
      "mixed_date_formats": [],
      "min": 22,
      "max": 41,
      "mean": 31.0,
      "distinct": null,
      "distribution": null
    },
    {
      "name": "score",
      "type": "float",
      "role": null,
      "missing": 0,
      "missing_rate": 0.0,
      "invalid": 0,
      "decimal_separator": "point",
      "date_format": null,
      "mixed_date_formats": [],
      "min": 9.4,
      "max": 18.9,
      "mean": 14.54,
      "distinct": null,
      "distribution": null
    },
    {
      "name": "date_inscription",
      "type": "date",
      "role": null,
      "missing": 0,
      "missing_rate": 0.0,
      "invalid": 0,
      "decimal_separator": null,
      "date_format": "AAAA-MM-JJ",
      "mixed_date_formats": [],
      "min": "2026-01-15",
      "max": "2026-05-30",
      "mean": null,
      "distinct": null,
      "distribution": null
    }
  ]
}"""


@pytest.fixture
def at_root(monkeypatch):
    """Lance le test depuis la racine du projet, pour des chemins comme samples/clean.csv."""
    monkeypatch.chdir(ROOT)


def analyze(name):
    return analyze_file(f"samples/{name}")


def column_block(name, column_name):
    file_info, columns = analyze(name)
    column = next(c for c in columns if c["name"] == column_name)
    return "\n".join(render_column(column, file_info))


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


# Blocs de colonnes


def test_distribution_replaces_distinct_line(at_root):
    assert column_block("product_categories.csv", "category_name") == """\
[category_name]
  Type        : string
  Manquantes  : 0 (0.0 %)
  Invalides   : 0
  Distribution :
    Electronics : 7
    Home Appliances : 7
    Furniture : 6"""


def test_decimal_separator_line_when_file_is_mixed(at_root):
    assert column_block("mixed_decimal.csv", "poids") == """\
[poids]
  Type        : float
  Manquantes  : 0 (0.0 %)
  Invalides   : 0
  Séparateur décimal : virgule
  Min         : 7.75
  Max         : 12.50
  Moyenne     : 9.63"""


def test_date_format_line_when_file_is_mixed(at_root):
    assert column_block("mixed_dates.csv", "fin") == """\
[fin]
  Type        : date
  Manquantes  : 0 (0.0 %)
  Invalides   : 0
  Format de date : JJ/MM/AAAA
  Plus ancienne : 2025-12-31
  Plus récente  : 2026-04-20"""


def test_remark_line(at_root):
    assert column_block("mixed_dates.csv", "evenement") == """\
[evenement]
  Type        : string
  Manquantes  : 0 (0.0 %)
  Invalides   : 0
  Remarque    : dates dans plusieurs formats (AAAA-MM-JJ, JJ/MM/AAAA), colonne traitée comme string
  Distincts   : 5"""


def test_no_mixed_lines_when_file_is_not_mixed(at_root):
    block = column_block("fr_export.csv", "prix")
    assert "Séparateur décimal" not in block
    block = column_block("fr_export.csv", "date_vente")
    assert "Format de date" not in block


def test_string_identifier_has_no_stats(at_root):
    assert column_block("pipe.csv", "UUID") == """\
[UUID]
  Type        : string
  Rôle        : identifiant
  Manquantes  : 0 (0.0 %)
  Invalides   : 0"""


def test_unknown_column_has_no_stats(at_root):
    assert column_block("missing.csv", "colonne_vide") == """\
[colonne_vide]
  Type        : unknown
  Manquantes  : 6 (100.0 %)
  Invalides   : 0"""


def test_no_markdown_in_reports(at_root):
    names = sorted(p.name for p in (ROOT / "samples").glob("*.csv") if p.name != "empty.csv")
    for name in names:
        report = render_report(*analyze(name))
        assert "**" not in report and "<br>" not in report, name
        # Le séparateur | peut apparaître comme valeur, jamais comme bord de tableau.
        assert not any(line.lstrip().startswith("|") for line in report.splitlines()), name


# Rapport complet


def test_full_report_of_clean_file(at_root):
    assert render_report(*analyze("clean.csv")) == CLEAN_REPORT


# Rendu JSON


@pytest.mark.parametrize(
    ("value", "column_type", "expected"),
    [
        (None, "float", None),
        (-4, "integer", -4),
        (9.4, "float", 9.4),
        (2.675, "float", 2.68),
    ],
)
def test_json_number(value, column_type, expected):
    assert json_number(value, column_type) == expected


def test_json_mean_rounded_half_up(at_root):
    file_info, columns = analyze("mixed_decimal.csv")
    poids = next(c for c in columns if c["name"] == "poids")
    assert json_column(poids)["mean"] == 9.63


def test_json_dates_are_iso_strings(at_root):
    file_info, columns = analyze("mixed_dates.csv")
    fin = json_column(next(c for c in columns if c["name"] == "fin"))
    assert (fin["min"], fin["max"]) == ("2025-12-31", "2026-04-20")


def test_json_distribution_pairs(at_root):
    report = json.loads(render_json(*analyze("product_categories.csv")))
    column = next(c for c in report["columns"] if c["name"] == "category_name")
    assert column["distribution"] == [["Electronics", 7], ["Home Appliances", 7], ["Furniture", 6]]


def test_json_tab_separator_kept_raw(at_root):
    assert json.loads(render_json(*analyze("tabulation.csv")))["file"]["separator"] == "\t"


def test_json_reports_are_valid(at_root):
    names = sorted(p.name for p in (ROOT / "samples").glob("*.csv") if p.name != "empty.csv")
    for name in names:
        report = json.loads(render_json(*analyze(name)))
        assert set(report) == {"file", "columns"}, name


def test_full_json_report_of_clean_file(at_root):
    assert render_json(*analyze("clean.csv")) == CLEAN_JSON
