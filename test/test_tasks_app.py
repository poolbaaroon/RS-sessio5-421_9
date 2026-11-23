from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from src.tasks_app import main


RUTA_RELATIVA = Path("data") / "tasks.json"


@pytest.fixture
def ruta_tasques(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.chdir(tmp_path)
    ruta = tmp_path / RUTA_RELATIVA
    ruta.parent.mkdir(parents=True, exist_ok=True)
    return ruta


def escriure_registres(ruta: Path, registres: list[dict[str, Any]]) -> None:
    ruta.write_text(
        json.dumps(registres, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def test_gs01_crear_tasca(ruta_tasques: Path, capsys: pytest.CaptureFixture[str]) -> None:
    escriure_registres(ruta_tasques, [])

    assert main(["add", "--title", "Pràctica 1", "--subject", "RS"]) == 0
    assert capsys.readouterr().out == "Tasca [ID: 1] creada amb èxit\n"
    assert json.loads(ruta_tasques.read_text(encoding="utf-8")) == [
        {
            "id": 1,
            "titol": "Pràctica 1",
            "assignatura": "RS",
            "estat": "pendent",
        }
    ]


def test_gs02_llistat_buit(ruta_tasques: Path, capsys: pytest.CaptureFixture[str]) -> None:
    escriure_registres(ruta_tasques, [])

    assert main(["list"]) == 0
    assert capsys.readouterr().out == "Registre de tasques buit.\n"


def test_gs03_llistat_amb_tasques(
    ruta_tasques: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    escriure_registres(
        ruta_tasques,
        [
            {
                "id": 1,
                "titol": "Pràctica 1",
                "assignatura": "RS",
                "estat": "pendent",
            },
            {
                "id": 2,
                "titol": "Examen parcial",
                "assignatura": "SO",
                "estat": "pendent",
            },
        ],
    )

    assert main(["list"]) == 0
    assert capsys.readouterr().out == (
        "[1] Pràctica 1 (RS) - estat: pendent\n"
        "[2] Examen parcial (SO) - estat: pendent\n"
    )
