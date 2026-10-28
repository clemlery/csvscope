"""Reconnaissance des valeurs d'une cellule : manquantes, nombres, dates.

Toutes les fonctions reçoivent une valeur déjà nettoyée (espaces retirés en
début et en fin).
"""

MISSING_MARKERS = frozenset({"na", "n/a", "null", "none", "absent"})


def is_missing(value: str) -> bool:
    """Vrai si la valeur est vide ou est un marqueur de valeur manquante."""
    return value == "" or value.lower() in MISSING_MARKERS
