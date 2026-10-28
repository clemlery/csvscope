import pytest

from csvscope.columns import describe_mix, is_identifier
from csvscope.values import DATE_FORMATS, DECIMAL_SEPARATORS


# Rôle identifiant


@pytest.mark.parametrize(
    "name",
    ["id", "ID", "uuid", "UUID", "identifier", "Identifier", "identifiant",
     "product_id", "Client_ID"],
)
def test_identifier_names(name):
    assert is_identifier(name)


@pytest.mark.parametrize(
    "name",
    ["id_client", "paid", "uid", "ids", "identifiants", "product-id", "productid", "nom"],
)
def test_not_identifier_names(name):
    assert not is_identifier(name)


# Description d'un mélange de libellés


def test_describe_mix_none():
    assert describe_mix([], DECIMAL_SEPARATORS) == "aucun"


def test_describe_mix_single():
    assert describe_mix(["virgule", "virgule"], DECIMAL_SEPARATORS) == "virgule"


def test_describe_mix_uses_fixed_order():
    assert describe_mix(["virgule", "point"], DECIMAL_SEPARATORS) == "mixte (point, virgule)"
    assert (
        describe_mix(["JJ/MM/AAAA", "AAAA-MM-JJ"], DATE_FORMATS)
        == "mixte (AAAA-MM-JJ, JJ/MM/AAAA)"
    )
