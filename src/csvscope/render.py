"""Rendu texte du rapport. Seul module qui met les valeurs en forme."""

from datetime import date

from csvscope.columns import INTEGER
from csvscope.rounding import round_half_up

FILE_LABEL_WIDTH = 18


def _field(label: str, value: object, width: int) -> str:
    """Ligne « libellé : valeur », le libellé complété à width caractères."""
    return f"{label.ljust(width)} : {value}"


def format_separator(separator: str) -> str:
    """Le séparateur tel qu'affiché : la tabulation est écrite en toutes lettres."""
    return "tabulation" if separator == "\t" else separator


def format_number(value: int | float, column_type: str) -> str:
    """Min ou max : entier tel quel pour integer, 2 décimales pour float."""
    if column_type == INTEGER:
        return str(value)
    return str(round_half_up(value, 2))


def format_mean(value: float) -> str:
    """Moyenne, toujours à 2 décimales."""
    return str(round_half_up(value, 2))


def format_date(value: date) -> str:
    """Date au format AAAA-MM-JJ."""
    return value.isoformat()


def format_missing(missing: int, rate: float) -> str:
    """Nombre et taux de valeurs manquantes : 1 (16.7 %)."""
    return f"{missing} ({rate:.1f} %)"


def format_remark(formats: list[str]) -> str:
    """Remarque d'une colonne dont les dates mélangent plusieurs formats."""
    return f"dates dans plusieurs formats ({', '.join(formats)}), colonne traitée comme string"


def render_file(file_info: dict) -> list[str]:
    """Lignes de l'en-tête du rapport, qui décrit le fichier."""
    fields = [
        ("Fichier", file_info["path"]),
        ("Lignes", file_info["row_count"]),
        ("Colonnes", file_info["column_count"]),
        ("Séparateur", format_separator(file_info["separator"])),
        ("Séparateur décimal", file_info["decimal_separator"]),
        ("Format de date", file_info["date_format"]),
    ]
    return [_field(label, value, FILE_LABEL_WIDTH) for label, value in fields]
