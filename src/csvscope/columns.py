"""Analyse d'une colonne : rôle, type et valeurs invalides."""

from collections.abc import Iterable
from datetime import date
from decimal import Decimal

from csvscope.values import (
    DATE_FORMATS,
    DECIMAL_SEPARATORS,
    parse_date,
    parse_decimal,
    parse_integer,
)

INTEGER = "integer"
FLOAT = "float"
DATE = "date"
STRING = "string"
UNKNOWN = "unknown"

IDENTIFIER = "identifiant"
IDENTIFIER_NAMES = frozenset({"id", "uuid", "identifier", "identifiant"})
IDENTIFIER_SUFFIX = "_id"


def is_identifier(name: str) -> bool:
    """Vrai si le nom de colonne désigne un identifiant, sans tenir compte de la casse."""
    lowered = name.lower()
    return lowered in IDENTIFIER_NAMES or lowered.endswith(IDENTIFIER_SUFFIX)


def describe_mix(found: Iterable[str], order: tuple[str, ...]) -> str:
    """Décrit un ensemble de libellés : aucun, le libellé seul, ou mixte (a, b).

    Les libellés sont listés dans l'ordre fixe donné par order.
    """
    present = [label for label in order if label in set(found)]
    if not present:
        return "aucun"
    if len(present) == 1:
        return present[0]
    return f"mixte ({', '.join(present)})"


def _is_majority(count: int, total: int) -> bool:
    """Vrai si count représente strictement plus de 50 % de total."""
    return count * 2 > total


def date_formats(values: list[str]) -> list[str]:
    """Renvoie les formats des valeurs qui sont des dates, dans l'ordre fixe."""
    found = set()
    for value in values:
        parsed = parse_date(value)
        if parsed is not None:
            found.add(parsed[1])
    return [label for label in DATE_FORMATS if label in found]


def mixed_date_formats(values: list[str]) -> list[str]:
    """Renvoie les formats trouvés si plus de 50 % des valeurs sont des dates
    dans plusieurs formats, sinon une liste vide.
    """
    dates = sum(1 for value in values if parse_date(value) is not None)
    formats = date_formats(values)
    if _is_majority(dates, len(values)) and len(formats) > 1:
        return formats
    return []


def infer_type(values: list[str], allow_comma: bool) -> str:
    """Infère le type d'une colonne à partir de ses valeurs non manquantes."""
    if not values:
        return UNKNOWN

    integers = sum(1 for value in values if parse_integer(value) is not None)
    decimals = sum(1 for value in values if parse_decimal(value, allow_comma) is not None)
    if _is_majority(integers + decimals, len(values)):
        return FLOAT if decimals else INTEGER

    dates = sum(1 for value in values if parse_date(value) is not None)
    if _is_majority(dates, len(values)):
        return DATE if len(date_formats(values)) == 1 else STRING

    return STRING


def _convert(value: str, column_type: str, allow_comma: bool) -> int | Decimal | date | None:
    """Convertit value selon le type integer, float ou date, ou renvoie None."""
    if column_type == INTEGER:
        return parse_integer(value)
    if column_type == FLOAT:
        integer = parse_integer(value)
        if integer is not None:
            return Decimal(integer)
        decimal = parse_decimal(value, allow_comma)
        return decimal[0] if decimal is not None else None
    parsed = parse_date(value)
    return parsed[0] if parsed is not None else None


def split_valid(values: list[str], column_type: str, allow_comma: bool) -> tuple[list, int]:
    """Sépare les valeurs non manquantes valides des invalides.

    Renvoie les valeurs valides converties (int pour integer, Decimal pour
    float, date pour date, chaîne sinon) et le nombre de valeurs invalides.
    Une colonne string ou unknown n'a jamais de valeur invalide.
    """
    if column_type not in (INTEGER, FLOAT, DATE):
        return list(values), 0
    converted = (_convert(value, column_type, allow_comma) for value in values)
    valid = [value for value in converted if value is not None]
    return valid, len(values) - len(valid)


def decimal_separator(values: list[str], allow_comma: bool) -> str:
    """Décrit le séparateur des décimaux valides : point, virgule ou mixte."""
    found = []
    for value in values:
        parsed = parse_decimal(value, allow_comma)
        if parsed is not None:
            found.append(parsed[1])
    return describe_mix(found, DECIMAL_SEPARATORS)
