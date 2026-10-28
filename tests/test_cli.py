from pathlib import Path

import pytest

from csvscope.cli import main

ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture(autouse=True)
def at_root(monkeypatch):
    """Lance chaque test depuis la racine du projet, comme dans SPEC.md."""
    monkeypatch.chdir(ROOT)


def test_report_on_stdout(capsys):
    assert main(["samples/clean.csv"]) == 0
    captured = capsys.readouterr()
    assert captured.out.startswith("Fichier            : samples/clean.csv\n")
    assert captured.out.endswith("  Plus récente  : 2026-05-30\n")
    assert captured.err == ""


def test_empty_file(capsys):
    assert main(["samples/empty.csv"]) == 1
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == "Erreur : fichier vide : samples/empty.csv\n"


def test_missing_file(capsys):
    assert not Path("samples/inexistant.csv").exists()
    assert main(["samples/inexistant.csv"]) == 1
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == "Erreur : fichier introuvable : samples/inexistant.csv\n"
    assert not Path("samples/inexistant.csv").exists()
