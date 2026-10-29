import json
import os
import subprocess
import sys
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


def test_json_report_on_stdout(capsys):
    assert main(["samples/clean.csv", "--format", "json"]) == 0
    captured = capsys.readouterr()
    assert json.loads(captured.out)["file"]["path"] == "samples/clean.csv"
    assert captured.err == ""


def test_explicit_text_format(capsys):
    assert main(["--format", "text", "samples/clean.csv"]) == 0
    assert capsys.readouterr().out.startswith("Fichier            : samples/clean.csv\n")


def test_json_format_errors_stay_text(capsys):
    assert main(["samples/empty.csv", "--format", "json"]) == 1
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == "Erreur : fichier vide : samples/empty.csv\n"


def test_unknown_format_is_rejected(capsys):
    with pytest.raises(SystemExit) as error:
        main(["samples/clean.csv", "--format", "xml"])
    assert error.value.code == 2
    assert capsys.readouterr().out == ""


def run_module(*args):
    env = {**os.environ, "PYTHONPATH": str(ROOT / "src")}
    return subprocess.run(
        [sys.executable, "-m", "csvscope", *args],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )


def test_python_m_csvscope_prints_report():
    result = run_module("samples/bom.csv")
    assert result.returncode == 0
    assert result.stdout.startswith("Fichier            : samples/bom.csv\n")
    assert result.stderr == ""


def test_python_m_csvscope_exit_code_on_error():
    result = run_module("samples/empty.csv")
    assert result.returncode == 1
    assert result.stdout == ""
    assert result.stderr == "Erreur : fichier vide : samples/empty.csv\n"
