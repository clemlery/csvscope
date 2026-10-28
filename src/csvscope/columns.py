"""Analyse d'une colonne : rôle et type."""

from collections.abc import Iterable

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
