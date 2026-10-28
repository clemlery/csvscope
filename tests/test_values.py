import pytest

from csvscope.values import is_missing


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
