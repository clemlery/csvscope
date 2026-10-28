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

# Partie 1 : nouvelles règles

## samples/mixed_decimal.csv

### Fichier
| Clé | Valeur |
| --- | --- |
| lignes | 4 |
| colonnes | 5 |
| séparateur | `;` |
| séparateur décimal | mixte (point, virgule) |
| format de date | aucun |

### Colonnes
| Colonne | Type | Rôle | Manquantes | Invalides | Séparateur décimal | Min | Max | Moyenne | Distribution |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| id | integer | identifiant | 0 (0.0 %) | 0 | | | | | |
| poids | float | | 0 (0.0 %) | 0 | virgule | 7.75 | 12.50 | 9.63 | |
| taille | float | | 0 (0.0 %) | 0 | point | 1.62 | 1.90 | 1.77 | |
| temperature | float | | 0 (0.0 %) | 0 | virgule | -3.50 | 2.00 | -0.56 | |
| mesure | float | | 0 (0.0 %) | 0 | mixte (point, virgule) | 1.50 | 4.00 | 2.75 | |

Ce fichier couvre :
- un fichier dont les colonnes `float` utilisent des séparateurs décimaux différents (B1),
- une colonne qui mélange elle-même point et virgule (`mesure`),
- des décimaux négatifs (`temperature` : `-3,5`, `-1,25`) (B4),
- des entiers valides dans une colonne `float` (`poids` : `10`, `temperature` : `2`) (B7),
- l'arrondi au demi supérieur : moyenne de `poids` = 38.5 / 4 = 9.625 → `9.63` (B8).

## samples/mixed_dates.csv

### Fichier
| Clé | Valeur |
| --- | --- |
| lignes | 5 |
| colonnes | 4 |
| séparateur | `,` |
| séparateur décimal | aucun |
| format de date | mixte (AAAA-MM-JJ, JJ/MM/AAAA) |

### Colonnes
| Colonne | Type | Rôle | Manquantes | Invalides | Format de date | Remarque | Min | Max | Distribution |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| id | integer | identifiant | 0 (0.0 %) | 0 | | | | | |
| debut | date | | 0 (0.0 %) | 1 | AAAA-MM-JJ | | 2025-12-01 | 2026-03-10 | |
| fin | date | | 0 (0.0 %) | 0 | JJ/MM/AAAA | | 2025-12-31 | 2026-04-20 | |
| evenement | string | | 0 (0.0 %) | 0 | | dates dans plusieurs formats (AAAA-MM-JJ, JJ/MM/AAAA), colonne traitée comme string | | | non, 5 valeurs distinctes |

Ce fichier couvre :
- un fichier dont les colonnes `date` utilisent des formats différents (B3),
- une colonne dont les dates mélangent deux formats : elle devient `string`, avec une remarque (B6). Elle n'est pas prise en compte dans le format de date du fichier (B2),
- la forme stricte des dates : `2026-1-5` n'est pas une date, donc c'est une valeur invalide dans `debut` (B6),
- un fichier sans valeur décimale (séparateur décimal `aucun`).

## samples/ragged.csv

### Fichier
| Clé | Valeur |
| --- | --- |
| lignes | 4 |
| colonnes | 3 |
| séparateur | `,` |
| séparateur décimal | aucun |
| format de date | aucun |

### Colonnes
| Colonne | Type | Rôle | Manquantes | Invalides | Min | Max | Moyenne | Distribution |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| id | integer | identifiant | 0 (0.0 %) | 0 | | | | |
| nom | string | | 0 (0.0 %) | 0 | | | | non, 4 valeurs distinctes |
| age | integer | | 1 (25.0 %) | 0 | 22 | 41 | 30.33 | |

Ce fichier couvre :
- une ligne trop courte (ligne 2) : le champ absent compte comme manquant (B12),
- une ligne trop longue (ligne 3) : le champ en trop (`extra`) est ignoré (B12),
- la détection du séparateur malgré des lignes de longueurs différentes (B11),
- la suppression des espaces avant l'analyse du type et des valeurs : `David ` → `David`, ` 41` → `41` (B5).

## samples/bom.csv

Fichier UTF-8 commençant par un BOM (`EF BB BF`).

### Fichier
| Clé | Valeur |
| --- | --- |
| lignes | 2 |
| colonnes | 2 |
| séparateur | `;` |
| séparateur décimal | aucun |
| format de date | aucun |

### Colonnes
| Colonne | Type | Rôle | Manquantes | Invalides | Min | Max | Moyenne | Distribution |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| id | integer | identifiant | 0 (0.0 %) | 0 | | | | |
| valeur | integer | | 0 (0.0 %) | 0 | 3 | 5 | 4.00 | |

Ce fichier couvre : le retrait du BOM. Le nom de la première colonne est `id`, pas `﻿id`, donc elle est reconnue comme identifiant (B12).

## samples/single_column.csv

### Fichier
| Clé | Valeur |
| --- | --- |
| lignes | 3 |
| colonnes | 1 |
| séparateur | `,` |
| séparateur décimal | aucun |
| format de date | aucun |

### Colonnes
| Colonne | Type | Rôle | Manquantes | Invalides | Min | Max | Moyenne | Distribution |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| valeur | integer | | 0 (0.0 %) | 0 | 10 | 30 | 20.00 | |

Ce fichier couvre : aucun séparateur ne donne plus d'une colonne, donc on retient `,` par défaut (B11).

## samples/header_only.csv

### Fichier
| Clé | Valeur |
| --- | --- |
| lignes | 0 |
| colonnes | 3 |
| séparateur | `,` |
| séparateur décimal | aucun |
| format de date | aucun |

### Colonnes
| Colonne | Type | Rôle | Manquantes | Invalides | Min | Max | Moyenne | Distribution |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| id | unknown | identifiant | 0 (0.0 %) | 0 | | | | |
| nom | unknown | | 0 (0.0 %) | 0 | | | | |
| valeur | unknown | | 0 (0.0 %) | 0 | | | | |

Ce fichier couvre : un en-tête sans ligne de données. Les taux valent 0.0 % (pas de division par zéro) (B12).

## Erreurs

| Commande | Code de sortie | Message sur la sortie d'erreur |
| --- | --- | --- |
| `csvscope samples/empty.csv` | 1 | `Erreur : fichier vide : samples/empty.csv` |
| `csvscope samples/inexistant.csv` | 1 | `Erreur : fichier introuvable : samples/inexistant.csv` |

`samples/empty.csv` fait 0 octet. `samples/inexistant.csv` n'existe pas et ne doit pas être créé. Dans les deux cas, rien n'est écrit sur la sortie standard (B12).

# Partie 2 : règles qui n'étaient pas couvertes

## samples/invalid.csv

### Fichier
| Clé | Valeur |
| --- | --- |
| lignes | 5 |
| colonnes | 7 |
| séparateur | `,` |
| séparateur décimal | point |
| format de date | AAAA-MM-JJ |

### Colonnes
| Colonne | Type | Rôle | Manquantes | Invalides | Min | Max | Moyenne | Distribution |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| id | integer | identifiant | 0 (0.0 %) | 0 | | | | |
| quantite | integer | | 0 (0.0 %) | 1 | -4 | 10 | 5.00 | |
| prix | float | | 0 (0.0 %) | 1 | 1.00 | 4.00 | 2.75 | |
| lot | integer | | 0 (0.0 %) | 2 | 7 | 9 | 8.00 | |
| code | string | | 1 (20.0 %) | 0 | | | | non, 4 valeurs distinctes |
| jour | string | | 1 (20.0 %) | 0 | | | | non, 4 valeurs distinctes |
| livraison | date | | 0 (0.0 %) | 1 | 2026-01-10 | 2026-05-20 | | |

Ce fichier couvre :
- des valeurs invalides exclues des statistiques : `abc` dans `quantite`, `x` dans `prix`, `X1` et `Y2` dans `lot` (C1),
- le seuil de 50 % : `lot` a 3 nombres sur 5 (60 %), donc il est `integer`. `code` a 2 nombres sur 4 valeurs non manquantes (50 % exactement), donc il est `string`. `jour` a 2 dates sur 4 (50 %), donc il est `string` (C2),
- un entier négatif (`-4`) (C6),
- une date bien formée mais qui n'existe pas (`2026-02-30`), invalide dans `livraison` (C7),
- un entier (`4`) valide dans une colonne `float` (C11).

## samples/tabulation.csv

### Fichier
| Clé | Valeur |
| --- | --- |
| lignes | 6 |
| colonnes | 3 |
| séparateur | tabulation |
| séparateur décimal | virgule |
| format de date | aucun |

### Colonnes
| Colonne | Type | Rôle | Manquantes | Invalides | Min | Max | Moyenne | Distribution |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| id | integer | identifiant | 0 (0.0 %) | 0 | | | | |
| mesure | float | | 3 (50.0 %) | 0 | 1.50 | 3.25 | 2.42 | |
| note | string | | 4 (66.7 %) | 0 | | | | oui : bien 2 |

Ce fichier couvre :
- le séparateur tabulation, avec la virgule décimale (C4),
- les marqueurs `NULL` et `None`, l'insensibilité à la casse (`none`, `na`, `ABSENT`) et les espaces autour d'un marqueur (` n/a `) (C8),
- une distribution affichée avec une seule valeur distincte répétée.

Dans le rendu texte, le séparateur s'affiche sous la forme `tabulation`.

## samples/pipe.csv

### Fichier
| Clé | Valeur |
| --- | --- |
| lignes | 3 |
| colonnes | 6 |
| séparateur | `\|` |
| séparateur décimal | aucun |
| format de date | aucun |

### Colonnes
| Colonne | Type | Rôle | Manquantes | Invalides | Min | Max | Moyenne | Distribution |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| UUID | string | identifiant | 0 (0.0 %) | 0 | | | | |
| Identifier | integer | identifiant | 0 (0.0 %) | 0 | | | | |
| identifiant | string | identifiant | 0 (0.0 %) | 0 | | | | |
| Client_ID | integer | identifiant | 0 (0.0 %) | 0 | | | | |
| id_client | integer | | 0 (0.0 %) | 0 | 5 | 7 | 6.00 | |
| paid | integer | | 0 (0.0 %) | 0 | 0 | 1 | 0.67 | |

Ce fichier couvre :
- le séparateur `|` (C4),
- les noms identifiants `uuid`, `identifier`, `identifiant`, et l'insensibilité à la casse (`UUID`, `Identifier`, `Client_ID`) (C5),
- des identifiants de type `string`, sans distribution,
- des noms qui ne sont pas des identifiants : `id_client` (commence par `id_`), `paid` (finit par `id` sans `_`) (C5).

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

Séparateur tabulation :

```text
Séparateur         : tabulation
```

