"""Arrondi au demi supérieur, avec le module decimal."""

from decimal import ROUND_HALF_UP, Decimal


def round_half_up(value: Decimal | float | int, places: int) -> Decimal:
    """Arrondit value à places décimales, au demi supérieur (0.125 -> 0.13).

    Un float passe par sa représentation textuelle la plus courte, pour que
    9.625 soit traité comme 9.625 et non comme son approximation binaire.
    """
    if isinstance(value, float):
        value = Decimal(repr(value))
    else:
        value = Decimal(value)
    return value.quantize(Decimal(1).scaleb(-places), rounding=ROUND_HALF_UP)
