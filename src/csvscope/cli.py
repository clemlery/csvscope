"""Point d'entrée de la commande csvscope."""

import argparse
import sys

from csvscope.analysis import analyze_file
from csvscope.reading import EmptyFileError
from csvscope.render import render_json, render_report

RENDERERS = {"text": render_report, "json": render_json}


def main(argv: list[str] | None = None) -> int:
    """Affiche le rapport du fichier donné en argument et renvoie le code de sortie.

    En cas d'erreur, le message va sur la sortie d'erreur, rien n'est écrit
    sur la sortie standard et le code de sortie vaut 1.
    """
    parser = argparse.ArgumentParser(
        prog="csvscope", description="Affiche un rapport en texte brut sur un fichier CSV."
    )
    parser.add_argument("fichier", help="chemin du fichier CSV")
    parser.add_argument(
        "--format", choices=RENDERERS, default="text", help="format du rapport (défaut : text)"
    )
    args = parser.parse_args(argv)
    path = args.fichier

    try:
        file_info, columns = analyze_file(path)
    except FileNotFoundError:
        print(f"Erreur : fichier introuvable : {path}", file=sys.stderr)
        return 1
    except EmptyFileError:
        print(f"Erreur : fichier vide : {path}", file=sys.stderr)
        return 1

    print(RENDERERS[args.format](file_info, columns))
    return 0
