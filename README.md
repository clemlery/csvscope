# csvscope
First module of my project for learning how to use agentic AI like claude code.

## Résultat que j'attend: 
### fichier `clean.csv`
| colonne          | type    | example de valeurs | row_number | missing_value |
|------------------|---------|--------------------|------------|---------------|
| id               | integer | 1                  | 5          | 0             |
| nom              | string  | Alice              | 5          | 0             |
| age              | string  | 28                 | 5          | 0             |
| score            | float   | 15.7               | 5          | 0             |
| date_inscription | date    | 2026-01-15         | 5          | 0             |
### fichier `missing.csv`
| colonne          | type    | exemple de valeurs | row_number | missing_value |
|------------------|---------|--------------------|------------|---------------|
| id               | integer | 1                  | 6          | 0             |
| nom              | string  | Alice              | 6          | 1             |
| age              | integer | 28                 | 6          | 3             |
| commentaire      | string  | Absent             | 6          | 4             |
| colonne_vide     | string  | —                  | 6          | 6             |
| score            | float   | 15.2               | 6          | 3             |

### fichier `fr_export.csv`
| colonne    | type    | exemple de valeurs | row_number | missing_value |
|------------|---------|--------------------|------------|---------------|
| id         | integer | 1                  | 5          | 0             |
| produit    | string  | Clavier            | 5          | 0             |
| prix       | float   | 12.5               | 5          | 0             |
| quantite   | integer | 3                  | 5          | 0             |
| date_vente | date    | 2026-01-15         | 5          | 0             |
