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


def test_gs09_modificar_titol_i_conservar_atributs(
    ruta_tasques: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    escriure_registres(ruta_tasques, [TASCA_INICIAL])

    assert main(["edit", "--id", "1", "--title", "Pràctica final"]) == 0
    captura = capsys.readouterr()
    assert captura.out == "Tasca [ID: 1] actualitzada amb èxit\n"
    assert captura.err == ""
    assert json.loads(ruta_tasques.read_text(encoding="utf-8")) == [
        {**TASCA_INICIAL, "titol": "Pràctica final"}
    ]


def test_gs10_modificar_diversos_atributs(
    ruta_tasques: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    escriure_registres(ruta_tasques, [TASCA_INICIAL])

    assert main(
        [
            "edit",
            "--id",
            "1",
            "--subject",
            "SO",
            "--due",
            "2026-12-15",
            "--status",
            "completada",
        ]
    ) == 0
    captura = capsys.readouterr()
    assert captura.out == "Tasca [ID: 1] actualitzada amb èxit\n"
    assert captura.err == ""
    assert json.loads(ruta_tasques.read_text(encoding="utf-8")) == [
        {
            **TASCA_INICIAL,
            "assignatura": "SO",
            "estat": "completada",
            "data_limit": "2026-12-15",
        }
    ]


def test_gs11_rebutjar_modificacio_sense_canvis_parcials(
    ruta_tasques: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    comprovar_rebuig(
        ["edit", "--id", "1", "--title", "Títol modificat", "--due", "2026-02-30"],
        ruta_tasques,
        [TASCA_INICIAL],
        "Error: data límit no vàlida. "
        "Utilitza YYYY-MM-DD amb una data existent.",
        capsys,
    )


def test_gs12_rebutjar_id_inexistent(
    ruta_tasques: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    comprovar_rebuig(
        ["edit", "--id", "99", "--title", "Nou títol"],
        ruta_tasques,
        [TASCA_INICIAL],
        "Error: no existeix cap tasca amb ID 99.",
        capsys,
    )


def test_gs20_rebutjar_edit_sense_id(
    ruta_tasques: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    comprovar_rebuig(
        ["edit", "--title", "Nou títol"],
        ruta_tasques,
        [TASCA_INICIAL],
        "Error: cal indicar l'ID de la tasca amb --id.",
        capsys,
    )


@pytest.mark.parametrize("identificador", ["abc", "0", "-1"])
def test_gs22_rebutjar_id_no_enter_positiu(
    identificador: str,
    ruta_tasques: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    comprovar_rebuig(
        ["edit", "--id", identificador, "--title", "Nou títol"],
        ruta_tasques,
        [TASCA_INICIAL],
        "Error: l'ID ha de ser un enter positiu.",
        capsys,
    )


def test_gs23_rebutjar_edit_sense_atributs(
    ruta_tasques: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    comprovar_rebuig(
        ["edit", "--id", "1"],
        ruta_tasques,
        [TASCA_INICIAL],
        "Error: cal indicar almenys un atribut per modificar.",
        capsys,
    )


def test_gs24_rebutjar_estat_no_admes(
    ruta_tasques: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    comprovar_rebuig(
        ["edit", "--id", "1", "--status", "acabada"],
        ruta_tasques,
        [TASCA_INICIAL],
        "Error: estat no vàlid. Utilitza pendent o completada.",
        capsys,
    )


def test_gs27_tornar_tasca_completada_a_pendent(
    ruta_tasques: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    tasca_completada = {**TASCA_INICIAL, "estat": "completada"}
    escriure_registres(ruta_tasques, [tasca_completada])

    assert main(["edit", "--id", "1", "--status", "pendent"]) == 0
    captura = capsys.readouterr()
    assert captura.out == "Tasca [ID: 1] actualitzada amb èxit\n"
    assert captura.err == ""
    assert json.loads(ruta_tasques.read_text(encoding="utf-8")) == [TASCA_INICIAL]


def test_edit_amb_data_passada(
    ruta_tasques: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    escriure_registres(ruta_tasques, [TASCA_INICIAL])

    assert main(["edit", "--id", "1", "--due", "2026-11-22"]) == 0
    captura = capsys.readouterr()
    assert captura.out == "Tasca [ID: 1] actualitzada amb èxit\n"
    assert captura.err == ""
    assert json.loads(ruta_tasques.read_text(encoding="utf-8")) == [
        {**TASCA_INICIAL, "data_limit": "2026-11-22"}
    ]


def test_edit_preserva_registre_sense_data_limit(
    ruta_tasques: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    registre_antic = {
        "id": 1,
        "titol": "Pràctica 1",
        "assignatura": "RS",
        "estat": "pendent",
    }
    escriure_registres(ruta_tasques, [registre_antic])

    assert main(["edit", "--id", "1", "--title", "Pràctica final"]) == 0
    captura = capsys.readouterr()
    assert captura.out == "Tasca [ID: 1] actualitzada amb èxit\n"
    assert captura.err == ""
    assert json.loads(ruta_tasques.read_text(encoding="utf-8")) == [
        {**registre_antic, "titol": "Pràctica final"}
    ]


def test_gs13_completar_tasca_i_conservar_canvi(
    ruta_tasques: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    escriure_registres(ruta_tasques, [TASCA_INICIAL])

    assert main(["complete", "--id", "1"]) == 0
    captura = capsys.readouterr()
    assert captura.out == "Tasca [ID: 1] marcada com a completada\n"
    assert captura.err == ""
    assert json.loads(ruta_tasques.read_text(encoding="utf-8")) == [
        {**TASCA_INICIAL, "estat": "completada"}
    ]


def test_gs21_rebutjar_complete_sense_id(
    ruta_tasques: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    comprovar_rebuig(
        ["complete"],
        ruta_tasques,
        [TASCA_INICIAL],
        "Error: cal indicar l'ID de la tasca amb --id.",
        capsys,
    )


@pytest.mark.parametrize("identificador", ["abc", "0", "-1"])
def test_gs22_complete_rebutja_id_no_enter_positiu(
    identificador: str,
    ruta_tasques: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    comprovar_rebuig(
        ["complete", "--id", identificador],
        ruta_tasques,
        [TASCA_INICIAL],
        "Error: l'ID ha de ser un enter positiu.",
        capsys,
    )


def test_gs25_rebutjar_complete_amb_id_inexistent(
    ruta_tasques: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    comprovar_rebuig(
        ["complete", "--id", "99"],
        ruta_tasques,
        [TASCA_INICIAL],
        "Error: no existeix cap tasca amb ID 99.",
        capsys,
    )


def test_gs26_completar_tasca_ja_completada(
    ruta_tasques: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    tasca_completada = {**TASCA_INICIAL, "estat": "completada"}
    escriure_registres(ruta_tasques, [tasca_completada])
    contingut = ruta_tasques.read_bytes()

    assert main(["complete", "--id", "1"]) == 0
    captura = capsys.readouterr()
    assert captura.out == "Tasca [ID: 1] marcada com a completada\n"
    assert captura.err == ""
    assert ruta_tasques.read_bytes() == contingut
    assert json.loads(ruta_tasques.read_text(encoding="utf-8")) == [tasca_completada]


def test_complete_preserva_registre_sense_data_limit(
    ruta_tasques: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    registre_antic = {
        "id": 1,
        "titol": "Pràctica 1",
        "assignatura": "RS",
        "estat": "pendent",
    }
    escriure_registres(ruta_tasques, [registre_antic])

    assert main(["complete", "--id", "1"]) == 0
    captura = capsys.readouterr()
    assert captura.out == "Tasca [ID: 1] marcada com a completada\n"
    assert captura.err == ""
    assert json.loads(ruta_tasques.read_text(encoding="utf-8")) == [
        {**registre_antic, "estat": "completada"}
    ]
