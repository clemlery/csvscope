# Fonctionnalités envisagées pour csvscope

Ce fichier liste des idées, pas des objectifs validés. Chaque fonctionnalité retenue devra être décrite dans `prompt/PROMPT.md` et `prompt/SPEC.md` avant d'être codée.

La contrainte **« bibliothèque standard uniquement »** de `PROMPT.md` devra être précisée : le paquet d'analyse peut la respecter, mais le serveur et l'interface demandent des dépendances (voir plus bas).

## Priorités proposées

| Ordre | Fonctionnalité | Effort | Dépend de |
| --- | --- | --- | --- |
| 1 | Interface React | élevé | sortie JSON (faite) |
| 2 | Statistiques supplémentaires | faible à moyen, par petites briques | — |
| 3 | Nouveaux types (booléen, etc.) | moyen, touche à l'inférence | — |
| 4 | Autres idées (export, comparaison, schéma) | variable | — |

---

## 1. Interface React

### Objectif
Ouvrir un fichier CSV depuis le navigateur et voir le rapport de façon lisible : un résumé du fichier en haut, puis une ligne ou une carte par colonne, avec des couleurs pour les problèmes (manquantes, invalides) et des graphiques (distribution, histogramme).

La CLI est conservée : l'interface est une nouvelle façon d'afficher les mêmes données, à côté de `render_report` et `render_json`.

### Architecture recommandée : React pour l'affichage, Python pour l'analyse

```
navigateur (React)  --envoi du CSV-->  serveur Python (FastAPI)  -->  analyze_file
                    <--rapport JSON--
```

- **L'analyse reste en Python.** On ne la réécrit pas en TypeScript : il faudrait maintenir deux fois chaque règle de `PROMPT.md`, avec le risque que les deux versions divergent.
- **Le contrat entre les deux est le rendu JSON** déjà décrit dans `SPEC.md` (section « Rendu JSON ») : le serveur renvoie exactement la sortie de `csvscope --format json`.

### Pile technique proposée

| Rôle | Choix | Pourquoi |
| --- | --- | --- |
| Langage du front | TypeScript | les types du rapport JSON sont écrits une fois et vérifiés partout |
| Outil de build | Vite | standard actuel pour un projet React, démarrage rapide |
| Composants | Mantine (ou shadcn/ui) | composants prêts à l'emploi : envoi de fichier, cartes, onglets, badges |
| Tableau des colonnes | TanStack Table | tri, filtre et recherche, utiles pour les fichiers à plus de 120 colonnes comme `samples/data-es.csv` |
| Graphiques | Recharts | barres pour les distributions, histogrammes pour les nombres |
| Serveur | FastAPI + uvicorn | une route suffit (`POST /api/analyze`) ; validation et documentation automatiques |
| Tests du front | Vitest + React Testing Library | même outillage que Vite |
| Tests du serveur | pytest + `TestClient` de FastAPI | s'ajoute aux tests existants |

### Organisation du dépôt
- `src/csvscope/` : inchangé, toujours sans dépendance.
- `src/csvscope/server.py` : la route FastAPI, installée seulement avec une dépendance optionnelle (`pip install -e '.[server]'`). Le cœur de l'analyse respecte donc toujours la contrainte « bibliothèque standard ».
- `web/` : le projet React (Vite), avec son propre `package.json`.
- En développement : Vite sert le front et redirige `/api` vers FastAPI (proxy). En production : `npm run build`, puis FastAPI sert aussi les fichiers construits, et une commande (par exemple `csvscope-ui`) lance le serveur et ouvre le navigateur.

### Changements nécessaires côté Python
- `analyze_file` prend un chemin, alors que le fichier envoyé arrive en mémoire. Il faut ajouter une fonction qui analyse un texte (`read_table` sépare déjà la lecture du fichier de son découpage), et le nom du fichier envoyé remplace `path` dans le rapport.
- Exposer aussi les erreurs (`fichier vide`) dans la réponse du serveur, avec un code HTTP adapté.
- Pour aider l'interface : des exemples de valeurs invalides par colonne (aujourd'hui seul leur nombre est connu) et les premières lignes brutes du fichier.

### Écrans proposés
1. **Accueil** : zone de dépôt du fichier.
2. **Résumé du fichier** : lignes, colonnes, séparateur, séparateur décimal, format de date, sous forme de cartes.
3. **Tableau des colonnes** : nom, type, rôle, manquantes, invalides, avec recherche et filtres par type ou par problème.
4. **Détail d'une colonne** : statistiques, distribution ou histogramme, remarques sur les dates mélangées.
5. **Aperçu brut** : les premières lignes du fichier, pour comprendre les valeurs invalides.

### Alternatives écartées
- **Réécrire l'analyse en TypeScript**, sans serveur : double maintenance des règles.
- **Pyodide** (Python dans le navigateur, sans serveur) : rien ne quitte la machine et le site peut être hébergé tel quel, mais le chargement est lourd (plusieurs Mo) et l'outillage est moins courant. Ce serait une piste si l'on voulait plus tard une version en ligne sans serveur.
- **Tauri ou Electron** : utiles seulement si l'on veut une application de bureau installable. Ils pourraient être ajoutés plus tard autour du même front React.

### Points à préciser
- Taille maximale des fichiers envoyés, et comportement pour les gros fichiers.
- Le serveur écoute seulement en local (`127.0.0.1`) : l'outil n'est pas prévu pour être exposé sur un réseau.
- Langue de l'interface : en français, comme le rapport texte.

---

## 2. Statistiques et analyses supplémentaires

### Colonnes numériques (`integer`, `float`)
- médiane, premier et troisième quartiles ;
- écart-type ;
- valeurs aberrantes, avec la règle de l'écart interquartile (en dehors de Q1 − 1,5 × EIQ et Q3 + 1,5 × EIQ) ;
- nombre de zéros et de valeurs négatives ;
- histogramme (surtout utile dans l'interface).

Le module `statistics` de la bibliothèque standard couvre médiane, quantiles et écart-type.

### Colonnes `date`
- étendue en jours entre la plus ancienne et la plus récente ;
- dates dans le futur (souvent une erreur de saisie) ;
- répartition par année ou par mois.

### Colonnes `string`
- longueur minimale, maximale et moyenne ;
- les N valeurs les plus fréquentes, même quand il y a plus de 20 valeurs distinctes ;
- **incohérences de saisie** : valeurs qui ne diffèrent que par la casse ou les accents (`Paris`, `paris`, `PARIS`) ;
- motifs reconnus : e-mail, URL, code postal, numéro de téléphone, listes JSON (`["Bus"]`, très présentes dans `samples/data-es.csv`).

### Colonnes identifiant
- vérifier l'**unicité** : aujourd'hui rien n'est calculé pour un identifiant, alors que des doublons d'identifiant sont souvent le premier problème à signaler.

### Fichier entier
- lignes entièrement dupliquées ;
- nombre de lignes trop courtes ou trop longues (aujourd'hui corrigées en silence) ;
- colonnes constantes (une seule valeur distincte) ;
- taux de remplissage global ;
- lignes avec beaucoup de valeurs manquantes ;
- corrélations entre colonnes numériques (Pearson), sous forme de tableau ou de carte de chaleur dans l'interface ;
- un **score de qualité** simple, qui résume manquantes, invalides et doublons. Sa formule doit être documentée dans `SPEC.md`.

Chaque statistique ajoutée doit apparaître dans les trois rendus (texte, JSON, interface) et être couverte par un cas de `SPEC.md`.

---

## 3. Nouveaux types

- `boolean` : `true`/`false`, `oui`/`non`, `0`/`1` ? À trancher, car `0`/`1` est aujourd'hui un `integer`. Dans `samples/data-es.csv`, beaucoup de colonnes sont `true`/`false` et sortent aujourd'hui en `string`.
- `datetime` (`2026-01-15T10:30:00`) et heure seule.
- coordonnées géographiques (`48.662, 6.17509`).

Chaque nouveau type modifie les règles d'inférence de `PROMPT.md` et demande de nouveaux fichiers de `samples/`, à écrire par toi.

---

## 4. Autres idées

- **Export du rapport** en HTML ou en Markdown, pour le partager.
- **Comparaison de deux fichiers** : colonnes ajoutées ou supprimées, types qui changent, écarts de statistiques. Utile pour deux exports successifs d'une même source.
- **Export du schéma déduit** : `CREATE TABLE` SQL ou JSON Schema à partir des types inférés.
- **Validation contre un schéma** : vérifier qu'un nouveau fichier respecte les types attendus, avec un code de sortie non nul si ce n'est pas le cas (utile en intégration continue).
- **Autres encodages** : aujourd'hui seul l'UTF-8 est lu. Les exports Excel français sont souvent en Windows-1252.
- **Gros fichiers** : lecture en flux ou analyse d'un échantillon, avec une indication claire dans le rapport.
- **Choix du séparateur** forcé par une option, quand la détection automatique se trompe.
