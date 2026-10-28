from pathlib import Path

import pytest

from csvscope.analysis import analyze_file, file_date_format, file_decimal_separator
from csvscope.columns import DATE, FLOAT, INTEGER, STRING
from csvscope.reading import EmptyFileError

SAMPLES = Path(__file__).resolve().parent.parent / "samples"


def column(column_type, decimal_separator=None, date_format=None):
    return {
        "type": column_type,
        "decimal_separator": decimal_separator,
        "date_format": date_format,
    }


# Séparateur décimal du fichier


def test_decimal_separator_without_float_column():
    columns = [column(INTEGER), column(STRING)]
    assert file_decimal_separator(columns) == "aucun"


def test_decimal_separator_common_to_float_columns():
    columns = [column(FLOAT, "virgule"), column(INTEGER), column(FLOAT, "virgule")]
    assert file_decimal_separator(columns) == "virgule"


def test_decimal_separator_of_single_mixed_column():
    columns = [column(FLOAT, "mixte (point, virgule)")]
    assert file_decimal_separator(columns) == "mixte (point, virgule)"


@pytest.mark.parametrize(
    "separators",
    [("virgule", "point"), ("point", "mixte (point, virgule)")],
)
def test_decimal_separator_mixed_between_columns(separators):
    columns = [column(FLOAT, separator) for separator in separators]
    assert file_decimal_separator(columns) == "mixte (point, virgule)"


# Format de date du fichier


def test_date_format_without_date_column():
    # Une colonne string aux dates mélangées ne compte pas.
    assert file_date_format([column(STRING), column(INTEGER)]) == "aucun"


def test_date_format_common_to_date_columns():
    columns = [column(DATE, date_format="JJ/MM/AAAA")] * 2
    assert file_date_format(columns) == "JJ/MM/AAAA"


def test_date_format_mixed_between_columns():
    columns = [column(DATE, date_format="JJ/MM/AAAA"), column(DATE, date_format="AAAA-MM-JJ")]
    assert file_date_format(columns) == "mixte (AAAA-MM-JJ, JJ/MM/AAAA)"


# Analyse du fichier


def test_analyze_file_returns_file_and_columns():
    path = str(SAMPLES / "clean.csv")
    file_info, columns = analyze_file(path)
    assert file_info == {
        "path": path,
        "row_count": 5,
        "column_count": 5,
        "separator": ",",
        "decimal_separator": "point",
        "date_format": "AAAA-MM-JJ",
    }
    assert [c["name"] for c in columns] == ["id", "nom", "age", "score", "date_inscription"]


def test_comma_is_a_decimal_separator_unless_it_separates_columns():
    _, columns = analyze_file(str(SAMPLES / "quoted_comma.csv"))
    assert columns[1]["invalid"] == 1
    _, columns = analyze_file(str(SAMPLES / "fr_export.csv"))
    assert columns[2]["invalid"] == 0


def test_analyze_file_raises_on_empty_file():
    with pytest.raises(EmptyFileError):
        analyze_file(str(SAMPLES / "empty.csv"))


def test_analyze_file_raises_on_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        analyze_file(str(tmp_path / "inexistant.csv"))
