# Résultats attendus pour csvscope

Toutes les valeurs ci-dessous ont été calculées à la main à partir des fichiers de `samples/`.

Conventions :
- `Manquantes` = nombre (taux %). Le taux est calculé sur le nombre de lignes de données, arrondi à une décimale.
- Une cellule est soit manquante, soit invalide, soit valide. Jamais deux à la fois : une cellule manquante n'est jamais comptée comme invalide.
- Pour chaque colonne : lignes = manquantes + invalides + valides.
- Min et max des colonnes `float` : 2 décimales. Moyenne : toujours 2 décimales.
- Arrondis au demi supérieur (`0.125` → `0.13`), pas à l'arrondi bancaire de `round()`.
- Dates écrites en AAAA-MM-JJ, quel que soit le format du fichier.
- Les colonnes supplémentaires des tableaux (`Séparateur décimal`, `Format de date`, `Remarque`) ne sont présentes que pour les fichiers où elles s'appliquent. Une case vide signifie que l'information n'est pas affichée.

# Fichiers d'origine

## samples/clean.csv

### Fichier
| Clé | Valeur |
| --- | --- |
| lignes | 5 |
| colonnes | 5 |
| séparateur | `,` |
| séparateur décimal | point |
| format de date | AAAA-MM-JJ |

### Colonnes
| Colonne | Type | Rôle | Manquantes | Invalides | Min | Max | Moyenne | Distribution |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| id | integer | identifiant | 0 (0.0 %) | 0 | | | | |
| nom | string | | 0 (0.0 %) | 0 | | | | non, 5 valeurs distinctes |
| age | integer | | 0 (0.0 %) | 0 | 22 | 41 | 31.00 | |
| score | float | | 0 (0.0 %) | 0 | 9.40 | 18.90 | 14.54 | |
| date_inscription | date | | 0 (0.0 %) | 0 | 2026-01-15 | 2026-05-30 | | |

## samples/fr_export.csv

### Fichier
| Clé | Valeur |
| --- | --- |
| lignes | 5 |
| colonnes | 5 |
| séparateur | `;` |
| séparateur décimal | virgule |
| format de date | JJ/MM/AAAA |

### Colonnes
| Colonne | Type | Rôle | Manquantes | Invalides | Min | Max | Moyenne | Distribution |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| id | integer | identifiant | 0 (0.0 %) | 0 | | | | |
| produit | string | | 0 (0.0 %) | 0 | | | | non, 5 valeurs distinctes |
| prix | float | | 0 (0.0 %) | 0 | 8.99 | 249.90 | 76.83 | |
| quantite | integer | | 0 (0.0 %) | 0 | 2 | 10 | 4.80 | |
| date_vente | date | | 0 (0.0 %) | 0 | 2026-01-15 | 2026-05-30 | | |

## samples/missing.csv

### Fichier
| Clé | Valeur |
| --- | --- |
| lignes | 6 |
| colonnes | 6 |
| séparateur | `,` |
| séparateur décimal | point |
| format de date | aucun |

### Colonnes
| Colonne | Type | Rôle | Manquantes | Invalides | Min | Max | Moyenne | Distribution |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| id | integer | identifiant | 0 (0.0 %) | 0 | | | | |
| nom | string | | 1 (16.7 %) | 0 | | | | non, 5 valeurs distinctes |
| age | integer | | 4 (66.7 %) | 0 | 28 | 30 | 29.00 | |
| commentaire | string | | 5 (83.3 %) | 0 | | | | non, 1 valeur distincte |
| colonne_vide | unknown | | 6 (100.0 %) | 0 | | | | |
| score | float | | 4 (66.7 %) | 0 | 12.80 | 15.20 | 14.00 | |

Ce fichier couvre :
- les marqueurs `NA`, `N/A`, `Absent` et la cellule vide,
- une cellule ne contenant qu'un espace (`commentaire`, ligne 6), manquante après suppression des espaces,
- une colonne entièrement vide (`unknown`).

## samples/product_categories.csv

### Fichier
| Clé | Valeur |
| --- | --- |
| lignes | 20 |
| colonnes | 4 |
| séparateur | `,` |
| séparateur décimal | point |
| format de date | aucun |

### Colonnes
| Colonne | Type | Rôle | Manquantes | Invalides | Min | Max | Moyenne | Distribution |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| product_id | integer | identifiant | 0 (0.0 %) | 0 | | | | |
| category_name | string | | 0 (0.0 %) | 0 | | | | oui : Electronics 7, Home Appliances 7, Furniture 6 |
| product_name | string | | 0 (0.0 %) | 0 | | | | non, 20 valeurs distinctes |
| price | float | | 0 (0.0 %) | 0 | 50.00 | 1000.00 | 322.50 | |

Ce fichier couvre :
- la règle identifiant par suffixe `_id` (`product_id`),
- une distribution affichée, avec un tri alphabétique entre deux valeurs à égalité (`Electronics` et `Home Appliances`, 7 chacune),
- une distribution non affichée alors qu'il y a exactement 20 valeurs distinctes (`product_name` : aucune valeur répétée),
- une colonne `float` dont toutes les valeurs finissent par `.0`.

# Rendu texte

## Rendu texte attendu pour samples/clean.csv

```text
Fichier            : samples/clean.csv
Lignes             : 5
Colonnes           : 5
Séparateur         : ,
Séparateur décimal : point
Format de date     : AAAA-MM-JJ

[id]
  Type        : integer
  Rôle        : identifiant
  Manquantes  : 0 (0.0 %)
  Invalides   : 0

[nom]
  Type        : string
  Manquantes  : 0 (0.0 %)
  Invalides   : 0
  Distincts   : 5

[age]
  Type        : integer
  Manquantes  : 0 (0.0 %)
  Invalides   : 0
  Min         : 22
  Max         : 41
  Moyenne     : 31.00

[score]
  Type        : float
  Manquantes  : 0 (0.0 %)
  Invalides   : 0
  Min         : 9.40
  Max         : 18.90
  Moyenne     : 14.54

[date_inscription]
  Type        : date
  Manquantes  : 0 (0.0 %)
  Invalides   : 0
  Plus ancienne : 2026-01-15
  Plus récente  : 2026-05-30
```

## Formes attendues des autres éléments

Distribution, quand elle est affichée (ici pour `category_name`). Elle remplace la ligne `Distincts` :

```text
  Distribution :
    Electronics : 7
    Home Appliances : 7
    Furniture : 6
```

