# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Projet

`csvscope <fichier>` : CLI Python qui affiche un rapport en texte brut (ou en JSON avec `--format json`) sur un fichier CSV (séparateurs, types de colonnes, manquantes, invalides, statistiques). Les sorties et messages sont en français.

Sources de vérité, à lire avant toute modification de comportement :
- `prompt/PROMPT.md` : règles métier (détection du séparateur, valeurs manquantes, nombres, dates, inférence de type, arrondis, erreurs) et contraintes du projet.
- `prompt/SPEC.md` : résultats attendus pour chaque fichier de `samples/`, et mise en page exacte du rapport (sections « Rendu texte » et « Rendu JSON »).

## Commandes

```bash
pip install -e '.[dev]'                     # installation (venv dans .venv/)
pytest                                       # tous les tests
pytest tests/test_columns.py::test_nom      # un seul test
pytest tests/test_samples.py -k clean.csv   # un seul fichier de samples/
csvscope samples/clean.csv                   # ou : python -m csvscope samples/clean.csv
```

Pas de linter ni de formateur configuré.

## Contraintes (issues de PROMPT.md)

- Python 3.12+, bibliothèque standard uniquement ; pytest seulement pour les tests.
- Ne jamais modifier les fichiers de `samples/`.
- Ne rien committer sans la permission explicite de l'utilisateur. Commits fins, en briques logiques, au format Conventional Commits avec scope par module (`feat(columns): ...`, `test(samples): ...`).
- Ne pas ajouter d'objectif ou de fonctionnalité sans permission.
- Ne jamais coder en dur des noms de colonnes ou des résultats propres aux fichiers de `samples/`.
- Tous les arrondis passent par `rounding.round_half_up` (demi supérieur avec `decimal`), jamais par `round()`.

## Architecture

Pipeline en couches, chaque module ne dépend que des précédents :

`values` → `reading` → `columns` → `analysis` → `render` → `cli`

- `values.py` : analyse d'une valeur isolée (manquante, entier, décimal, date). Définit les libellés affichés (`point`, `virgule`, `AAAA-MM-JJ`, `JJ/MM/AAAA`) et leur ordre canonique (`DECIMAL_SEPARATORS`, `DATE_FORMATS`).
- `reading.py` : lecture UTF-8 (BOM retiré), détection du séparateur, ajustement des lignes à la largeur de l'en-tête. Lève `EmptyFileError`.
- `columns.py` : tout ce qui concerne une colonne (identifiant, inférence de type, valides/invalides, stats). `analyze_column` renvoie un dictionnaire par colonne. `describe_mix` produit les libellés `mixte (...)`.
- `analysis.py` : `analyze_file(path) -> (file_info, columns)` ; calcule le séparateur décimal et le format de date du fichier à partir des colonnes `float` et `date` uniquement.
- `render.py` : seul module qui met en forme. `render_report` (texte : 2 décimales, dates ISO, `tabulation`) et `render_json` (nombres arrondis en nombres JSON, dates en chaînes ISO, clés internes non traduites).
- `cli.py` : argparse (`--format text|json`, via le dictionnaire `RENDERERS`), gestion des erreurs (message sur stderr, code 1, rien sur stdout).

Règle clé : les dictionnaires d'analyse contiennent des valeurs **brutes** (`int`, `Decimal`, `date`, taux déjà arrondi) ; aucune mise en forme hors de `render.py`.

`allow_comma` (virgule acceptée comme séparateur décimal) vaut `separator != ","` et est propagé de `analysis` jusqu'à `values.parse_decimal`.

## Tests

- `tests/expected.py` recopie à la main les tableaux de `SPEC.md` (min/max/moyennes en chaînes à 2 décimales, comparées à la valeur brute arrondie). `tests/test_samples.py` compare chaque fichier de `EXPECTED` aux dictionnaires de `analyze_file`. Ajouter un cas dans `SPEC.md` implique de l'ajouter dans `expected.py`.
- Un seul test par format compare le rendu complet (sur `samples/clean.csv`, dans `test_render.py`).
- `pythonpath = ["src"]` est configuré dans `pyproject.toml` : pas besoin d'installer le paquet pour lancer pytest.
