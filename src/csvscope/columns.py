"""Analyse d'une colonne : rôle et type."""

IDENTIFIER = "identifiant"
IDENTIFIER_NAMES = frozenset({"id", "uuid", "identifier", "identifiant"})
IDENTIFIER_SUFFIX = "_id"


def is_identifier(name: str) -> bool:
    """Vrai si le nom de colonne désigne un identifiant, sans tenir compte de la casse."""
    lowered = name.lower()
    return lowered in IDENTIFIER_NAMES or lowered.endswith(IDENTIFIER_SUFFIX)
