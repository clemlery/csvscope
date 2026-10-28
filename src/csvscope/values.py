"""Reconnaissance des valeurs d'une cellule : manquantes, nombres, dates.

Toutes les fonctions reçoivent une valeur déjà nettoyée (espaces retirés en
début et en fin).
"""

import re
from datetime import date, datetime
from decimal import Decimal

MISSING_MARKERS = frozenset({"na", "n/a", "null", "none", "absent"})

POINT = "point"
COMMA = "virgule"
DECIMAL_SEPARATORS = (POINT, COMMA)

ISO_DATE = "AAAA-MM-JJ"
FR_DATE = "JJ/MM/AAAA"
DATE_FORMATS = (ISO_DATE, FR_DATE)

# [0-9] et non \d : \d accepte aussi les chiffres non ASCII.
_INTEGER = re.compile(r"-?[0-9]+")
_DECIMAL_POINT = re.compile(r"-?[0-9]+\.[0-9]+")
_DECIMAL_COMMA = re.compile(r"-?[0-9]+,[0-9]+")

_DATE_PATTERNS = (
    (re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}"), "%Y-%m-%d", ISO_DATE),
    (re.compile(r"[0-9]{2}/[0-9]{2}/[0-9]{4}"), "%d/%m/%Y", FR_DATE),
)


def is_missing(value: str) -> bool:
    """Vrai si la valeur est vide ou est un marqueur de valeur manquante."""
    return value == "" or value.lower() in MISSING_MARKERS


def parse_integer(value: str) -> int | None:
    """Renvoie l'entier représenté par value, ou None."""
    if _INTEGER.fullmatch(value):
        return int(value)
    return None


def parse_decimal(value: str, allow_comma: bool) -> tuple[Decimal, str] | None:
    """Renvoie le décimal représenté par value et son séparateur, ou None.

    Un entier sans séparateur n'est pas un décimal. La virgule n'est acceptée
    que si allow_comma est vrai.
    """
    if _DECIMAL_POINT.fullmatch(value):
        return Decimal(value), POINT
    if allow_comma and _DECIMAL_COMMA.fullmatch(value):
        return Decimal(value.replace(",", ".")), COMMA
    return None


def parse_date(value: str) -> tuple[date, str] | None:
    """Renvoie la date représentée par value et son format, ou None.

    La forme est vérifiée par expression régulière, car strptime accepte
    aussi des formes plus courtes comme 2026-1-5.
    """
    for pattern, strptime_format, label in _DATE_PATTERNS:
        if pattern.fullmatch(value):
            try:
                return datetime.strptime(value, strptime_format).date(), label
            except ValueError:
                return None
    return None
