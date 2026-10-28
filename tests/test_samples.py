"""Compare l'analyse de chaque fichier de samples/ aux valeurs de SPEC.md."""

from decimal import Decimal
from pathlib import Path

import pytest

from csvscope.analysis import analyze_file
from csvscope.rounding import round_half_up
from expected import EXPECTED

SAMPLES = Path(__file__).resolve().parent.parent / "samples"


def _comparable(key, actual, expected):
    """Arrondit la valeur brute quand SPEC.md la donne à 2 décimales."""
    if isinstance(expected, str) and key in ("min", "max", "mean") and actual is not None:
        return round_half_up(actual, 2), Decimal(expected)
    return actual, expected


@pytest.fixture(params=sorted(EXPECTED), scope="module")
def sample(request):
    path = str(SAMPLES / request.param)
    file_info, columns = analyze_file(path)
    expected_file, expected_columns = EXPECTED[request.param]
    return path, file_info, columns, expected_file, expected_columns


def test_file(sample):
    path, file_info, _, expected_file, _ = sample
    assert file_info == {"path": path, **expected_file}


def test_column_names(sample):
    _, _, columns, _, expected_columns = sample
    assert [c["name"] for c in columns] == [c["name"] for c in expected_columns]


def test_columns(sample):
    _, _, columns, _, expected_columns = sample
    for column, expected in zip(columns, expected_columns, strict=True):
        for key, expected_value in expected.items():
            actual, wanted = _comparable(key, column[key], expected_value)
            assert actual == wanted, f"{column['name']}.{key}"
            if key in ("min", "max") and column["type"] == "integer" and actual is not None:
                assert type(actual) is int, f"{column['name']}.{key}"
