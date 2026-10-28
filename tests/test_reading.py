import pytest

from csvscope.reading import detect_separator, fit_row, split_rows


# Découpage des lignes


def test_split_rows_keeps_quoted_separator():
    text = 'id,libelle\n1,"Dupont, Jean"\n'
    assert split_rows(text, ",") == [["id", "libelle"], ["1", "Dupont, Jean"]]


def test_split_rows_ignores_blank_lines():
    assert split_rows("a,b\n\n1,2\n\n", ",") == [["a", "b"], ["1", "2"]]


def test_split_rows_handles_crlf():
    assert split_rows("a;b\r\n1;2\r\n", ";") == [["a", "b"], ["1", "2"]]


def test_split_rows_keeps_spaces():
    assert split_rows("a,b\n x , y \n", ",") == [["a", "b"], [" x ", " y "]]


def test_fit_row_pads_short_row():
    assert fit_row(["2", "Benoit"], 3) == ["2", "Benoit", ""]


def test_fit_row_truncates_long_row():
    assert fit_row(["3", "Claire", "22", "extra"], 3) == ["3", "Claire", "22"]


def test_fit_row_keeps_row_of_right_width():
    assert fit_row(["1", "Alice", "28"], 3) == ["1", "Alice", "28"]


# Séparateur de colonnes


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("a,b\n1,2\n", ","),
        ("a;b\n1;2\n", ";"),
        ("a\tb\n1\t2\n", "\t"),
        ("a|b\n1|2\n", "|"),
    ],
)
def test_detect_each_separator(text, expected):
    assert detect_separator(text) == expected


def test_detect_defaults_to_comma_when_header_is_not_split():
    assert detect_separator("valeur\n10\n20\n") == ","


def test_detect_ignores_candidate_that_does_not_split_header():
    # La virgule apparaît dans les données mais pas dans l'en-tête.
    assert detect_separator("id;prix\n1;8,99\n2;249,90\n") == ";"


def test_detect_prefers_most_matching_rows():
    # "," découpe l'en-tête en 2 champs mais aucune ligne de données.
    assert detect_separator("a;b,c\n1;2\n3;4\n") == ";"


def test_detect_breaks_ties_with_fixed_order():
    assert detect_separator("a,b;c\n1,2;3\n") == ","
    assert detect_separator("a;b\tc\n1;2\t3\n") == ";"
    assert detect_separator("a\tb|c\n1\t2|3\n") == "\t"


def test_detect_with_header_only():
    assert detect_separator("id;nom;valeur\n") == ";"
