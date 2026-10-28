"""Lecture du fichier CSV : texte, séparateur, lignes."""

import csv
import io

SEPARATORS = (",", ";", "\t", "|")
DEFAULT_SEPARATOR = ","


class EmptyFileError(Exception):
    """Le fichier ne contient aucun en-tête."""


def split_rows(text: str, separator: str) -> list[list[str]]:
    """Découpe text en lignes de champs, en ignorant les lignes vides."""
    reader = csv.reader(io.StringIO(text, newline=""), delimiter=separator)
    return [row for row in reader if row]


def fit_row(row: list[str], width: int) -> list[str]:
    """Ramène row à width champs.

    Les champs absents deviennent des chaînes vides (donc manquants), les
    champs en trop sont ignorés.
    """
    return row[:width] + [""] * (width - len(row))


def detect_separator(text: str) -> str:
    """Choisit le séparateur de colonnes parmi SEPARATORS.

    Seuls les candidats qui découpent l'en-tête en plus d'un champ sont
    retenus. Le gagnant est celui pour lequel le plus de lignes ont autant
    de champs que l'en-tête ; l'ordre de SEPARATORS départage les égalités.
    """
    best, best_count = DEFAULT_SEPARATOR, -1
    for separator in SEPARATORS:
        rows = split_rows(text, separator)
        if not rows or len(rows[0]) < 2:
            continue
        width = len(rows[0])
        count = sum(1 for row in rows[1:] if len(row) == width)
        if count > best_count:
            best, best_count = separator, count
    return best


def read_text(path: str) -> str:
    """Lit le fichier en UTF-8 et retire un éventuel BOM."""
    with open(path, encoding="utf-8-sig", newline="") as file:
        return file.read()


def read_table(path: str) -> tuple[str, list[str], list[list[str]]]:
    """Renvoie le séparateur, l'en-tête et les lignes de données du fichier.

    Les noms de colonnes sont débarrassés de leurs espaces ; les lignes de
    données sont ramenées à la largeur de l'en-tête, sans autre nettoyage.
    Lève FileNotFoundError si le fichier n'existe pas, EmptyFileError s'il
    n'a pas d'en-tête.
    """
    text = read_text(path)
    separator = detect_separator(text)
    rows = split_rows(text, separator)
    if not rows:
        raise EmptyFileError(path)
    header = [name.strip() for name in rows[0]]
    data = [fit_row(row, len(header)) for row in rows[1:]]
    return separator, header, data
