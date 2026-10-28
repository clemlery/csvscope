"""Analyse d'une colonne : rôle, type, valeurs invalides et statistiques."""

from collections import Counter
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

DISTRIBUTION_MAX_VALUES = 20


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


def numeric_stats(numbers: list[int | Decimal], column_type: str) -> dict:
    """Min, max et moyenne : min et max en int pour integer, en float pour float."""
    if not numbers:
        return {"min": None, "max": None, "mean": None}
    convert = int if column_type == INTEGER else float
    total = sum(Decimal(number) for number in numbers)
    return {
        "min": convert(min(numbers)),
        "max": convert(max(numbers)),
        "mean": float(total / len(numbers)),
    }


def date_stats(dates: list[date]) -> dict:
    """Date la plus ancienne et date la plus récente."""
    if not dates:
        return {"min": None, "max": None}
    return {"min": min(dates), "max": max(dates)}


def string_stats(values: list[str]) -> dict:
    """Nombre de valeurs distinctes et, si elle s'applique, la distribution.

    La distribution est donnée s'il y a au plus DISTRIBUTION_MAX_VALUES
    valeurs distinctes et qu'au moins une valeur est répétée. Elle est triée
    par nombre d'occurrences décroissant, puis par ordre alphabétique.
    """
    counts = Counter(values)
    distribution = None
    if len(counts) <= DISTRIBUTION_MAX_VALUES and any(n > 1 for n in counts.values()):
        distribution = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    return {"distinct": len(counts), "distribution": distribution}
