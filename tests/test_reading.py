from csvscope.reading import fit_row, split_rows


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
