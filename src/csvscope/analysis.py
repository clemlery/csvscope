"""Analyse d'un fichier CSV entier."""

from csvscope.columns import DATE, FLOAT, analyze_column, describe_mix
from csvscope.reading import read_table
from csvscope.values import DATE_FORMATS, DECIMAL_SEPARATORS


def _common_label(labels: set[str], order: tuple[str, ...]) -> str:
    """Libellé commun aux colonnes, aucun s'il n'y en a pas, mixte sinon.

    Avec deux libellés possibles seulement, deux libellés différents (ou un
    libellé déjà mixte) signifient que les deux sont présents.
    """
    if not labels:
        return "aucun"
    if len(labels) == 1:
        return next(iter(labels))
    return describe_mix(order, order)


def file_decimal_separator(columns: list[dict]) -> str:
    """Séparateur décimal du fichier, calculé sur les colonnes float."""
    labels = {column["decimal_separator"] for column in columns if column["type"] == FLOAT}
    return _common_label(labels, DECIMAL_SEPARATORS)


def file_date_format(columns: list[dict]) -> str:
    """Format de date du fichier, calculé sur les colonnes date."""
    labels = {column["date_format"] for column in columns if column["type"] == DATE}
    return _common_label(labels, DATE_FORMATS)


def analyze_file(path: str) -> tuple[dict, list[dict]]:
    """Analyse le fichier et renvoie son dictionnaire et ceux de ses colonnes.

    Lève FileNotFoundError si le fichier n'existe pas, EmptyFileError s'il
    n'a pas d'en-tête.
    """
    separator, header, rows = read_table(path)
    allow_comma = separator != ","
    columns = [
        analyze_column(name, [row[index] for row in rows], allow_comma)
        for index, name in enumerate(header)
    ]
    file_info = {
        "path": path,
        "row_count": len(rows),
        "column_count": len(header),
        "separator": separator,
        "decimal_separator": file_decimal_separator(columns),
        "date_format": file_date_format(columns),
    }
    return file_info, columns
