import pytest

from csvscope.columns import is_identifier


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
