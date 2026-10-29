# csvscope
First module of my project for learning how to use agentic AI like claude code.

## Objectif
Une CLI qui affiche un rapport en texte brut sur un fichier CSV :

```
csvscope <fichier>
csvscope <fichier> --format json
```

Le rapport décrit le fichier (lignes, colonnes, séparateur, séparateur décimal, format de date). Pour chaque colonne, il donne le type inféré (`integer`, `float`, `date`, `string`, `unknown`), le rôle éventuel (`identifiant`), les valeurs manquantes et invalides, et des statistiques selon le type.

## Documentation
- `prompt/PROMPT.md` : objectif, règles et contraintes.
- `prompt/SPEC.md` : résultats attendus pour chaque fichier de `samples/`, et mise en page du rapport (texte et JSON).

## Exemple : `samples/clean.csv`
| Colonne | Type | Rôle | Manquantes |
| --- | --- | --- | --- |
| id | integer | identifiant | 0 (0.0 %) |
| nom | string | | 0 (0.0 %) |
| age | integer | | 0 (0.0 %) |
| score | float | | 0 (0.0 %) |
| date_inscription | date | | 0 (0.0 %) |

Le détail complet (statistiques, autres fichiers) est dans `prompt/SPEC.md`.
