## Contexte
Projet Python vide nommé csvscope. Des fichiers d'exemple que j'ai écrits à la main sont dans @samples/.
Les résultats attendus pour chacun de ces fichiers sont dans @SPEC.md.

## Objectif
Une CLI `csvscope <fichier>` qui affiche un rapport en texte brut (pas de Markdown) sur le fichier CSV.

### Informations sur le fichier (description factuelle, entièrement calculée)
- nombre de lignes de données (en-tête exclu) et nombre de colonnes
- séparateur détecté, parmi : `,` `;` tabulation `|`
- séparateur décimal détecté : `point`, `virgule`, `aucun` (si aucune valeur décimale) ou `mixte (point, virgule)` si les deux sont utilisés
- format de date détecté : `AAAA-MM-JJ`, `JJ/MM/AAAA`, `aucun` ou `mixte (AAAA-MM-JJ, JJ/MM/AAAA)` si des colonnes de dates utilisent des formats différents

Le programme ne cherche pas à deviner le sens des données (pas de phrase du type "ce fichier contient des personnes").

### Pour chaque colonne
- type inféré
- rôle : `identifiant` ou rien
- valeurs manquantes : nombre et taux
- valeurs invalides : nombre
- séparateur décimal de la colonne, seulement si le séparateur décimal du fichier est mixte (colonnes `float`)
- format de date de la colonne, seulement si le format de date du fichier est mixte (colonnes `date`)
- remarque, si les dates de la colonne mélangent plusieurs formats (voir règles)
- statistiques selon le type (voir règles)

## Règles

### Lecture du fichier
- Encodage UTF-8. Un BOM éventuel en début de fichier est retiré.
- Le fichier est lu avec le module `csv` (gestion des guillemets).
- Une ligne trop courte : les champs absents comptent comme manquants. Une ligne trop longue : les champs en trop sont ignorés.

### Séparateur de colonnes
Parmi `,` `;` tabulation `|`, on ne garde que les candidats qui découpent l'en-tête en plus d'un champ. Parmi eux, on retient celui pour lequel le plus de lignes ont autant de champs que l'en-tête. En cas d'égalité, on applique l'ordre `,` `;` tabulation `|`. Si aucun candidat ne découpe l'en-tête en plus d'un champ, le séparateur est `,`.

### Nettoyage des valeurs
Toutes les règles ci-dessous s'appliquent aux valeurs après suppression des espaces en début et en fin : valeurs manquantes, type, statistiques et distribution.

### Valeurs manquantes
Une cellule est manquante si elle est vide ou égale (sans tenir compte de la casse) à l'une de ces chaînes : `NA`, `N/A`, `NULL`, `None`, `Absent`.
Aucune autre chaîne ne compte comme manquante.
Le taux est calculé sur le nombre de lignes de données, en pourcentage, arrondi à une décimale. S'il n'y a aucune ligne de données, le taux vaut 0.0 %.

### Nombres
Chiffres ASCII uniquement.
- entier : un signe `-` optionnel suivi de chiffres uniquement.
- décimal : un signe `-` optionnel, des chiffres, un séparateur décimal, des chiffres. Le point est toujours accepté comme séparateur décimal. La virgule est acceptée aussi si le séparateur du fichier n'est pas la virgule.
- Le signe `+` n'est pas accepté. `.5` et `5.` ne sont pas des nombres.

### Dates
Une valeur est une date si elle a exactement l'une de ces formes et représente une date réelle (vérifiée avec `datetime.strptime`) :
- `AAAA-MM-JJ` : 4 chiffres, `-`, 2 chiffres, `-`, 2 chiffres
- `JJ/MM/AAAA` : 2 chiffres, `/`, 2 chiffres, `/`, 4 chiffres

Par exemple, `2026-1-5` n'est pas une date.

### Type d'une colonne
Liste fermée des types : `integer`, `float`, `date`, `string`, `unknown`.
On travaille uniquement sur les valeurs non manquantes de la colonne, et jamais sur la seule première valeur. Appliquer ces règles dans l'ordre :
1. `unknown` : aucune valeur non manquante.
2. Si plus de 50 % des valeurs non manquantes sont des nombres :
   - `integer` si tous ces nombres sont des entiers,
   - `float` si au moins un de ces nombres est décimal. Les entiers sont alors des valeurs valides de la colonne.
3. `date` : plus de 50 % des valeurs non manquantes sont des dates, toutes dans le même format.
   Si plus de 50 % des valeurs sont des dates mais dans plusieurs formats, la colonne est `string`. Une remarque l'indique dans le rapport et liste les formats trouvés.
4. `string` : dans tous les autres cas.

### Séparateur décimal et format de date
Ils sont calculés uniquement à partir des colonnes typées `float` (pour le séparateur décimal) et `date` (pour le format de date). Les valeurs des autres colonnes ne comptent pas.
- Séparateur décimal d'une colonne `float` : celui de ses décimaux valides (`point`, `virgule` ou `mixte (point, virgule)`).
- Séparateur décimal du fichier : `aucun` s'il n'y a pas de colonne `float`, le séparateur commun s'il n'y en a qu'un, sinon `mixte (point, virgule)`.
- Format de date du fichier : `aucun` s'il n'y a pas de colonne `date`, le format commun s'il n'y en a qu'un, sinon `mixte (AAAA-MM-JJ, JJ/MM/AAAA)`.
- Dans les listes de formats ou de séparateurs, l'ordre est fixe : `point` puis `virgule`, `AAAA-MM-JJ` puis `JJ/MM/AAAA`.

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

### Arrondis
Tous les arrondis (taux, moyenne, min et max des `float`) se font au demi supérieur avec `decimal` (`0.125` → `0.13`), pas avec `round()`.

### Cas limites et erreurs
- Fichier introuvable : message `Erreur : fichier introuvable : <chemin>` sur la sortie d'erreur, code de sortie 1.
- Fichier vide (aucun en-tête) : message `Erreur : fichier vide : <chemin>` sur la sortie d'erreur, code de sortie 1.
- En-tête seul : 0 ligne, toutes les colonnes `unknown`, taux à 0.0 %.
- Dans les cas d'erreur, rien n'est écrit sur la sortie standard.

### Format de sortie
- Texte brut lisible dans un terminal : pas de `**`, pas de `<br>`, pas de tableau à `|`.
- Format unique, indépendant du fichier d'entrée : nombres avec un point décimal, dates en `AAAA-MM-JJ`. Le format d'origine est seulement indiqué dans les informations sur le fichier, et dans les colonnes quand le fichier est mixte.
- Le séparateur tabulation s'affiche `tabulation`.
- La mise en page exacte est donnée dans @SPEC.md.

## Contraintes
- Python 3.12+, bibliothèque standard uniquement, pytest pour les tests
- Ne jamais modifier les fichiers de samples/
- Ne rien committer sans ma permission
- Ne pas ajouter d'objectif sans ma permission
- Ne jamais coder en dur des noms de colonnes ou des résultats propres aux fichiers de samples/

## Architecture attendue
- Les fonctions d'analyse renvoient des données (un dictionnaire par colonne, un dictionnaire pour le fichier).
- Ces dictionnaires contiennent des valeurs brutes (`int`, `float`, `date`, taux déjà arrondi). La mise en forme (2 décimales, dates en `AAAA-MM-JJ`) est faite uniquement par le rendu.
- Le rendu texte est une fonction séparée qui prend ces données en entrée.
- Installation par `pyproject.toml` avec `[project.scripts]` pour la commande `csvscope`. `python -m csvscope` fonctionne aussi.

## Vérification
- Pour chaque fichier listé dans @SPEC.md, un test compare chaque valeur attendue aux dictionnaires renvoyés par l'analyse.
- Un seul test compare le rendu texte complet, sur `samples/clean.csv`.
- Les cas d'erreur de @SPEC.md sont testés (code de sortie et message).
- Chaque règle de la section "Règles" est couverte par au moins un cas de @SPEC.md. Si une règle n'est couverte par aucun cas, signale-le moi au lieu d'inventer un fichier.
- `pytest` passe sans erreur.

## Méthode de travail
- Commence par lister les points ambigus ou contradictoires de ce prompt et de @SPEC.md, et pose-moi tes questions. N'écris aucun code.
- Ensuite, propose l'arborescence et la liste des fonctions avec leurs signatures. N'écris aucun code.
- Attends ma validation avant chaque étape.
- Divise les commits en briques logiques, le plus finement possible.
