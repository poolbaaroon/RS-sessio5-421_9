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


TASCA_INICIAL: dict[str, Any] = {
    "id": 1,
    "titol": "Pràctica 1",
    "assignatura": "RS",
    "estat": "pendent",
    "data_limit": "2026-12-10",
}


def comprovar_rebuig(
    arguments: list[str],
    ruta: Path,
    registres: list[dict[str, Any]],
    missatge: str,
    capsys: pytest.CaptureFixture[str],
) -> None:
    escriure_registres(ruta, registres)
    contingut = ruta.read_bytes()

    assert main(arguments) == 2
    captura = capsys.readouterr()
    assert captura.out == ""
    assert captura.err == missatge + "\n"
    assert ruta.read_bytes() == contingut


def test_gs01_crear_tasca(ruta_tasques: Path, capsys: pytest.CaptureFixture[str]) -> None:
    escriure_registres(ruta_tasques, [])

    assert main(
        [
            "add",
            "--title",
            "Pràctica 1",
            "--subject",
            "RS",
            "--due",
            "2026-12-10",
        ]
    ) == 0
    captura = capsys.readouterr()
    assert captura.out == "Tasca [ID: 1] creada amb èxit\n"
    assert captura.err == ""
    assert json.loads(ruta_tasques.read_text(encoding="utf-8")) == [TASCA_INICIAL]


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


def test_gs04_crear_tasca_amb_data_limit(
    ruta_tasques: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    escriure_registres(ruta_tasques, [])

    assert main(
        [
            "add",
            "--title",
            "Pràctica 2",
            "--subject",
            "RS",
            "--due",
            "2026-12-10",
        ]
    ) == 0
    captura = capsys.readouterr()
    assert captura.out == "Tasca [ID: 1] creada amb èxit\n"
    assert captura.err == ""
    assert json.loads(ruta_tasques.read_text(encoding="utf-8")) == [
        {
            "id": 1,
            "titol": "Pràctica 2",
            "assignatura": "RS",
            "estat": "pendent",
            "data_limit": "2026-12-10",
        }
    ]


def test_gs05_rebutjar_creacio_sense_due(
    ruta_tasques: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    comprovar_rebuig(
        ["add", "--title", "Pràctica 2", "--subject", "RS"],
        ruta_tasques,
        [TASCA_INICIAL],
        "Error: cal indicar la data límit amb --due.",
        capsys,
    )


def test_gs06_rebutjar_data_amb_format_incorrecte(
    ruta_tasques: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    comprovar_rebuig(
        [
            "add",
            "--title",
            "Pràctica 2",
            "--subject",
            "RS",
            "--due",
            "10/12/2026",
        ],
        ruta_tasques,
        [TASCA_INICIAL],
        "Error: data límit no vàlida. "
        "Utilitza YYYY-MM-DD amb una data existent.",
        capsys,
    )


def test_gs07_rebutjar_data_inexistent_al_calendari(
    ruta_tasques: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    comprovar_rebuig(
        [
            "add",
            "--title",
            "Pràctica 2",
            "--subject",
            "RS",
            "--due",
            "2026-02-30",
        ],
        ruta_tasques,
        [TASCA_INICIAL],
        "Error: data límit no vàlida. "
        "Utilitza YYYY-MM-DD amb una data existent.",
        capsys,
    )


def test_gs28_crear_tasca_amb_data_passada(
    ruta_tasques: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    escriure_registres(ruta_tasques, [])

    assert main(
        [
            "add",
            "--title",
            "Tasca endarrerida",
            "--subject",
            "RS",
            "--due",
            "2026-11-22",
        ]
    ) == 0
    captura = capsys.readouterr()
    assert captura.out == "Tasca [ID: 1] creada amb èxit\n"
    assert captura.err == ""
    assert json.loads(ruta_tasques.read_text(encoding="utf-8")) == [
        {
            "id": 1,
            "titol": "Tasca endarrerida",
            "assignatura": "RS",
            "estat": "pendent",
            "data_limit": "2026-11-22",
        }
    ]


def test_id_incremental_en_crear_tasca(
    ruta_tasques: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    segona_tasca = {
        "id": 2,
        "titol": "Examen parcial",
        "assignatura": "SO",
        "estat": "pendent",
    }
    escriure_registres(ruta_tasques, [TASCA_INICIAL, segona_tasca])

    assert main(
        [
            "add",
            "--title",
            "Pràctica 3",
            "--subject",
            "RS",
            "--due",
            "2026-12-15",
        ]
    ) == 0
    captura = capsys.readouterr()
    assert captura.out == "Tasca [ID: 3] creada amb èxit\n"
    assert captura.err == ""
    assert json.loads(ruta_tasques.read_text(encoding="utf-8")) == [
        TASCA_INICIAL,
        segona_tasca,
        {
            "id": 3,
            "titol": "Pràctica 3",
            "assignatura": "RS",
            "estat": "pendent",
            "data_limit": "2026-12-15",
        },
    ]
