## Contexte
Projet Python vide nommé csvscope. Des fichiers d'exemple que j'ai écrits à la main sont dans @samples/.
Les résultats attendus pour chacun de ces fichiers sont dans @SPEC.md.

## Objectif
Une CLI `csvscope <fichier>` qui affiche un rapport en texte brut (pas de Markdown) sur le fichier CSV.

### Informations sur le fichier (description factuelle, entièrement calculée)
- nombre de lignes de données (en-tête exclu) et nombre de colonnes
- séparateur détecté, parmi : `,` `;` tabulation `|`
- séparateur décimal détecté : `point`, `virgule` ou `aucun` (si aucune valeur décimale)
- format de date détecté : `AAAA-MM-JJ`, `JJ/MM/AAAA` ou `aucun`

Le programme ne cherche pas à deviner le sens des données (pas de phrase du type "ce fichier contient des personnes").

### Pour chaque colonne
- type inféré
- rôle : `identifiant` ou rien
- valeurs manquantes : nombre et taux
- valeurs invalides : nombre
- statistiques selon le type (voir règles)

## Règles

### Valeurs manquantes
Une cellule est manquante si, après suppression des espaces en début et en fin, elle est vide ou égale (sans tenir compte de la casse) à l'une de ces chaînes : `NA`, `N/A`, `NULL`, `None`, `Absent`.
Aucune autre chaîne ne compte comme manquante.
Le taux est calculé sur le nombre de lignes de données, en pourcentage, arrondi à une décimale.

### Nombres
- entier : un signe `-` optionnel suivi de chiffres uniquement.
- décimal : chiffres, séparateur décimal, chiffres. Le séparateur décimal est le point, ou la virgule si le séparateur du fichier n'est pas la virgule.

### Dates
Une valeur est une date si elle correspond à l'un de ces formats et représente une date réelle (vérifiée avec `datetime.strptime`) :
- `AAAA-MM-JJ`
- `JJ/MM/AAAA`

### Type d'une colonne
Liste fermée des types : `integer`, `float`, `date`, `string`, `unknown`.
On travaille uniquement sur les valeurs non manquantes de la colonne, et jamais sur la seule première valeur. Appliquer ces règles dans l'ordre :
1. `unknown` : aucune valeur non manquante.
2. Si plus de 50 % des valeurs non manquantes sont des nombres :
   - `integer` si tous ces nombres sont des entiers,
   - `float` si au moins un de ces nombres est décimal.
3. `date` : plus de 50 % des valeurs non manquantes sont des dates, toutes dans le même format.
4. `string` : dans tous les autres cas.

### Valeurs invalides
Une valeur invalide est une valeur non manquante qui ne correspond pas au type retenu (par exemple `abc` dans une colonne `integer`).
- Elle est comptée dans "invalides", pas dans "manquantes".
- Elle est exclue des statistiques.
- Une colonne `string` ou `unknown` n'a jamais de valeur invalide.

### Colonnes identifiant
Une colonne est un identifiant si son nom, sans tenir compte de la casse, est exactement `id`, `uuid`, `identifier` ou `identifiant`, ou se termine par `_id`.
Le fait que toutes les valeurs soient uniques ne suffit pas.
Pour une colonne identifiant : afficher type, rôle, manquantes et invalides. Ne calculer ni min, ni max, ni moyenne, ni distribution.

### Statistiques
- `integer` et `float` (hors identifiant) : min, max et moyenne des valeurs valides.
  - min et max d'une colonne `integer` : entiers.
  - min et max d'une colonne `float` : 2 décimales.
  - moyenne : toujours 2 décimales.
- `date` : date la plus ancienne et date la plus récente.
- `string` (hors identifiant) : afficher le nombre d'occurrences de chaque valeur si les deux conditions suivantes sont vraies :
  - la colonne contient au plus 20 valeurs distinctes,
  - au moins une valeur apparaît plusieurs fois.
  Sinon, afficher seulement le nombre de valeurs distinctes. Tri : nombre d'occurrences décroissant, puis ordre alphabétique.
- `unknown` : aucune statistique.

### Format de sortie
- Texte brut lisible dans un terminal : pas de `**`, pas de `<br>`, pas de tableau à `|`.
- Format unique, indépendant du fichier d'entrée : nombres avec un point décimal, dates en `AAAA-MM-JJ`. Le format d'origine est seulement indiqué dans les informations sur le fichier.
- La mise en page exacte est donnée dans @SPEC.md.

## Contraintes
- Python 3.12+, bibliothèque standard uniquement, pytest pour les tests
- Ne jamais modifier les fichiers de samples/
- Ne rien committer sans ma permission
- Ne pas ajouter d'objectif sans ma permission
- Ne jamais coder en dur des noms de colonnes ou des résultats propres aux fichiers de samples/

## Architecture attendue
- Les fonctions d'analyse renvoient des données (un dictionnaire par colonne, un dictionnaire pour le fichier).
- Le rendu texte est une fonction séparée qui prend ces données en entrée.

## Vérification
- Pour chaque fichier listé dans @SPEC.md, un test compare chaque valeur attendue aux dictionnaires renvoyés par l'analyse.
- Un seul test compare le rendu texte complet, sur `samples/clean.csv`.
- Chaque règle de la section "Règles" est couverte par au moins un cas de @SPEC.md. Si une règle n'est couverte par aucun cas, signale-le moi au lieu d'inventer un fichier.
- `pytest` passe sans erreur.

## Méthode de travail
- Commence par lister les points ambigus ou contradictoires de ce prompt et de @SPEC.md, et pose-moi tes questions. N'écris aucun code.
- Ensuite, propose l'arborescence et la liste des fonctions avec leurs signatures. N'écris aucun code.
- Attends ma validation avant chaque étape.
- Divise les commits en briques logiques, le plus finement possible.