"""Rendu texte et JSON du rapport. Seul module qui met les valeurs en forme."""

import json
from datetime import date

from csvscope.columns import DATE, FLOAT, INTEGER, STRING, describe_mix
from csvscope.rounding import round_half_up
from csvscope.values import DATE_FORMATS, DECIMAL_SEPARATORS

FILE_LABEL_WIDTH = 18
COLUMN_LABEL_WIDTH = 11
DATE_LABEL_WIDTH = 13
COLUMN_INDENT = "  "
DISTRIBUTION_INDENT = "    "

MIXED_DECIMAL = describe_mix(DECIMAL_SEPARATORS, DECIMAL_SEPARATORS)
MIXED_DATES = describe_mix(DATE_FORMATS, DATE_FORMATS)


def _field(label: str, value: object, width: int) -> str:
    """Ligne « libellé : valeur », le libellé complété à width caractères."""
    return f"{label.ljust(width)} : {value}"


def _column_field(label: str, value: object, width: int = COLUMN_LABEL_WIDTH) -> str:
    return COLUMN_INDENT + _field(label, value, width)


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


def _render_stats(column: dict) -> list[str]:
    """Lignes de statistiques d'une colonne, selon son type."""
    column_type = column["type"]
    if column_type in (INTEGER, FLOAT):
        if column["min"] is None:
            return []
        return [
            _column_field("Min", format_number(column["min"], column_type)),
            _column_field("Max", format_number(column["max"], column_type)),
            _column_field("Moyenne", format_mean(column["mean"])),
        ]
    if column_type == DATE:
        if column["min"] is None:
            return []
        return [
            _column_field("Plus ancienne", format_date(column["min"]), DATE_LABEL_WIDTH),
            _column_field("Plus récente", format_date(column["max"]), DATE_LABEL_WIDTH),
        ]
    if column_type == STRING:
        if column["distribution"] is None:
            return [_column_field("Distincts", column["distinct"])]
        return [COLUMN_INDENT + "Distribution :"] + [
            f"{DISTRIBUTION_INDENT}{value} : {count}" for value, count in column["distribution"]
        ]
    return []


def render_column(column: dict, file_info: dict) -> list[str]:
    """Lignes du bloc d'une colonne.

    file_info indique si le fichier est mixte, auquel cas le séparateur
    décimal ou le format de date de la colonne est affiché.
    """
    lines = [f"[{column['name']}]", _column_field("Type", column["type"])]
    if column["role"] is not None:
        lines.append(_column_field("Rôle", column["role"]))
    missing = format_missing(column["missing"], column["missing_rate"])
    lines.append(_column_field("Manquantes", missing))
    lines.append(_column_field("Invalides", column["invalid"]))
    if column["role"] is not None:
        return lines

    if column["type"] == FLOAT and file_info["decimal_separator"] == MIXED_DECIMAL:
        lines.append(_column_field("Séparateur décimal", column["decimal_separator"]))
    if column["type"] == DATE and file_info["date_format"] == MIXED_DATES:
        lines.append(_column_field("Format de date", column["date_format"]))
    if column["mixed_date_formats"]:
        lines.append(_column_field("Remarque", format_remark(column["mixed_date_formats"])))
    return lines + _render_stats(column)


def render_report(file_info: dict, columns: list[dict]) -> str:
    """Rapport complet : l'en-tête du fichier, puis un bloc par colonne."""
    lines = render_file(file_info)
    for column in columns:
        lines.append("")
        lines.extend(render_column(column, file_info))
    return "\n".join(lines)


def json_number(value: int | float | None, column_type: str) -> int | float | None:
    """Min ou max en JSON : entier pour integer, arrondi à 2 décimales pour float."""
    if value is None or column_type == INTEGER:
        return value
    return float(round_half_up(value, 2))


def json_column(column: dict) -> dict:
    """Dictionnaire d'une colonne prêt pour JSON : nombres arrondis, dates en chaînes."""
    result = dict(column)
    if column["type"] in (INTEGER, FLOAT):
        result["min"] = json_number(column["min"], column["type"])
        result["max"] = json_number(column["max"], column["type"])
        if column["mean"] is not None:
            result["mean"] = float(round_half_up(column["mean"], 2))
    elif column["type"] == DATE and column["min"] is not None:
        result["min"] = format_date(column["min"])
        result["max"] = format_date(column["max"])
    return result


def render_json(file_info: dict, columns: list[dict]) -> str:
    """Rapport complet en JSON : le fichier, puis la liste des colonnes."""
    report = {"file": file_info, "columns": [json_column(column) for column in columns]}
    return json.dumps(report, ensure_ascii=False, indent=2)
