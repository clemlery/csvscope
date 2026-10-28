"""Résultats attendus, recopiés de prompt/SPEC.md.

Les min, max et moyennes sont écrits comme dans SPEC.md, en chaînes à
2 décimales pour les float et les moyennes : le test les compare à la
valeur brute arrondie au demi supérieur. Une case vide de SPEC.md vaut None
(ou [] pour la remarque). Les clés decimal_separator, date_format et
mixed_date_formats ne sont données que pour les fichiers dont le tableau
contient la colonne correspondante.
"""

from datetime import date

ISO = "AAAA-MM-JJ"
FR = "JJ/MM/AAAA"
MIXED_DECIMAL = "mixte (point, virgule)"
MIXED_DATES = "mixte (AAAA-MM-JJ, JJ/MM/AAAA)"


def file(rows, columns, separator, decimal_separator, date_format):
    return {
        "row_count": rows,
        "column_count": columns,
        "separator": separator,
        "decimal_separator": decimal_separator,
        "date_format": date_format,
    }


def col(
    name,
    type,
    role=None,
    missing=0,
    missing_rate=0.0,
    invalid=0,
    min=None,
    max=None,
    mean=None,
    distinct=None,
    distribution=None,
    **extra,
):
    if distribution is not None and distinct is None:
        distinct = len(distribution)
    return {
        "name": name,
        "type": type,
        "role": role,
        "missing": missing,
        "missing_rate": missing_rate,
        "invalid": invalid,
        "min": min,
        "max": max,
        "mean": mean,
        "distinct": distinct,
        "distribution": distribution,
        **extra,
    }


def ident(name, type="integer"):
    return col(name, type, role="identifiant")


EXPECTED = {
    "clean.csv": (
        file(5, 5, ",", "point", ISO),
        [
            ident("id"),
            col("nom", "string", distinct=5),
            col("age", "integer", min=22, max=41, mean="31.00"),
            col("score", "float", min="9.40", max="18.90", mean="14.54"),
            col("date_inscription", "date", min=date(2026, 1, 15), max=date(2026, 5, 30)),
        ],
    ),
    "fr_export.csv": (
        file(5, 5, ";", "virgule", FR),
        [
            ident("id"),
            col("produit", "string", distinct=5),
            col("prix", "float", min="8.99", max="249.90", mean="76.83"),
            col("quantite", "integer", min=2, max=10, mean="4.80"),
            col("date_vente", "date", min=date(2026, 1, 15), max=date(2026, 5, 30)),
        ],
    ),
    "missing.csv": (
        file(6, 6, ",", "point", "aucun"),
        [
            ident("id"),
            col("nom", "string", missing=1, missing_rate=16.7, distinct=5),
            col("age", "integer", missing=4, missing_rate=66.7, min=28, max=30, mean="29.00"),
            col("commentaire", "string", missing=5, missing_rate=83.3, distinct=1),
            col("colonne_vide", "unknown", missing=6, missing_rate=100.0),
            col(
                "score", "float", missing=4, missing_rate=66.7,
                min="12.80", max="15.20", mean="14.00",
            ),
        ],
    ),
    "product_categories.csv": (
        file(20, 4, ",", "point", "aucun"),
        [
            ident("product_id"),
            col(
                "category_name", "string",
                distribution=[("Electronics", 7), ("Home Appliances", 7), ("Furniture", 6)],
            ),
            col("product_name", "string", distinct=20),
            col("price", "float", min="50.00", max="1000.00", mean="322.50"),
        ],
    ),
    "mixed_decimal.csv": (
        file(4, 5, ";", MIXED_DECIMAL, "aucun"),
        [
            col("id", "integer", role="identifiant", decimal_separator=None),
            col(
                "poids", "float", decimal_separator="virgule",
                min="7.75", max="12.50", mean="9.63",
            ),
            col(
                "taille", "float", decimal_separator="point",
                min="1.62", max="1.90", mean="1.77",
            ),
            col(
                "temperature", "float", decimal_separator="virgule",
                min="-3.50", max="2.00", mean="-0.56",
            ),
            col(
                "mesure", "float", decimal_separator=MIXED_DECIMAL,
                min="1.50", max="4.00", mean="2.75",
            ),
        ],
    ),
    "mixed_dates.csv": (
        file(5, 4, ",", "aucun", MIXED_DATES),
        [
            col("id", "integer", role="identifiant", date_format=None, mixed_date_formats=[]),
            col(
                "debut", "date", invalid=1, date_format=ISO, mixed_date_formats=[],
                min=date(2025, 12, 1), max=date(2026, 3, 10),
            ),
            col(
                "fin", "date", date_format=FR, mixed_date_formats=[],
                min=date(2025, 12, 31), max=date(2026, 4, 20),
            ),
            col(
                "evenement", "string", date_format=None, mixed_date_formats=[ISO, FR],
                distinct=5,
            ),
        ],
    ),
    "ragged.csv": (
        file(4, 3, ",", "aucun", "aucun"),
        [
            ident("id"),
            col("nom", "string", distinct=4),
            col("age", "integer", missing=1, missing_rate=25.0, min=22, max=41, mean="30.33"),
        ],
    ),
    "bom.csv": (
        file(2, 2, ";", "aucun", "aucun"),
        [
            ident("id"),
            col("valeur", "integer", min=3, max=5, mean="4.00"),
        ],
    ),
    "single_column.csv": (
        file(3, 1, ",", "aucun", "aucun"),
        [
            col("valeur", "integer", min=10, max=30, mean="20.00"),
        ],
    ),
    "header_only.csv": (
        file(0, 3, ",", "aucun", "aucun"),
        [
            ident("id", "unknown"),
            col("nom", "unknown"),
            col("valeur", "unknown"),
        ],
    ),
    "invalid.csv": (
        file(5, 7, ",", "point", ISO),
        [
            ident("id"),
            col("quantite", "integer", invalid=1, min=-4, max=10, mean="5.00"),
            col("prix", "float", invalid=1, min="1.00", max="4.00", mean="2.75"),
            col("lot", "integer", invalid=2, min=7, max=9, mean="8.00"),
            col("code", "string", missing=1, missing_rate=20.0, distinct=4),
            col("jour", "string", missing=1, missing_rate=20.0, distinct=4),
            col(
                "livraison", "date", invalid=1,
                min=date(2026, 1, 10), max=date(2026, 5, 20),
            ),
        ],
    ),
    "tabulation.csv": (
        file(6, 3, "\t", "virgule", "aucun"),
        [
            ident("id"),
            col(
                "mesure", "float", missing=3, missing_rate=50.0,
                min="1.50", max="3.25", mean="2.42",
            ),
            col("note", "string", missing=4, missing_rate=66.7, distribution=[("bien", 2)]),
        ],
    ),
    "pipe.csv": (
        file(3, 6, "|", "aucun", "aucun"),
        [
            ident("UUID", "string"),
            ident("Identifier"),
            ident("identifiant", "string"),
            ident("Client_ID"),
            col("id_client", "integer", min=5, max=7, mean="6.00"),
            col("paid", "integer", min=0, max=1, mean="0.67"),
        ],
    ),
    "many_values.csv": (
        file(22, 3, ",", "aucun", "aucun"),
        [
            ident("id"),
            col("code", "string", distinct=21),
            col(
                "groupe", "string",
                distribution=[("G01", 2), ("G02", 2)]
                + [(f"G{i:02d}", 1) for i in range(3, 21)],
            ),
        ],
    ),
    "quoted_comma.csv": (
        file(3, 3, ",", "point", "aucun"),
        [
            ident("id"),
            col("montant", "float", invalid=1, min="7.25", max="10.50", mean="8.88"),
            col("libelle", "string", distinct=3),
        ],
    ),
}
