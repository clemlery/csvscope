"""Lecture du fichier CSV : texte, séparateur, lignes."""

import csv
import io


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
