"""Reconnaissance des valeurs d'une cellule : manquantes, nombres, dates.

Toutes les fonctions reçoivent une valeur déjà nettoyée (espaces retirés en
début et en fin).
"""

import re
from decimal import Decimal

MISSING_MARKERS = frozenset({"na", "n/a", "null", "none", "absent"})

POINT = "point"
COMMA = "virgule"
DECIMAL_SEPARATORS = (POINT, COMMA)

# [0-9] et non \d : \d accepte aussi les chiffres non ASCII.
_INTEGER = re.compile(r"-?[0-9]+")
_DECIMAL_POINT = re.compile(r"-?[0-9]+\.[0-9]+")
_DECIMAL_COMMA = re.compile(r"-?[0-9]+,[0-9]+")


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
