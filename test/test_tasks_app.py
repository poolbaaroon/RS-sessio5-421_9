from __future__ import annotations

import json
import subprocess
import sys
from datetime import date, timedelta
from pathlib import Path
from typing import Any

import pytest

from src.tasks_app import main


RUTA_RELATIVA = Path("data") / "tasks.json"
RUTA_SCRIPT = Path(__file__).resolve().parents[1] / "src" / "tasks_app.py"
DATA_REFERENCIA = date(2026, 11, 23)
ERROR_ARGUMENTS = "Error: arguments incorrectes. Utilitza --help."


@pytest.fixture
def ruta_tasques(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.chdir(tmp_path)
    ruta = tmp_path / RUTA_RELATIVA
    ruta.parent.mkdir(parents=True, exist_ok=True)
    return ruta


@pytest.fixture
def avui_fix(monkeypatch: pytest.MonkeyPatch) -> date:
    monkeypatch.setattr("src.tasks_app.data_actual", lambda: DATA_REFERENCIA)
    return DATA_REFERENCIA


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


def comprovar_llistat(
    ruta: Path,
    registre: dict[str, Any],
    linia_esperada: str,
    capsys: pytest.CaptureFixture[str],
) -> None:
    escriure_registres(ruta, [registre])
    contingut = ruta.read_bytes()

    assert main(["list"]) == 0
    captura = capsys.readouterr()
    assert captura.out == linia_esperada + "\n"
    assert captura.err == ""
    assert ruta.read_bytes() == contingut


def comprovar_error_arguments(
    arguments: list[str],
    ruta: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    escriure_registres(ruta, [TASCA_INICIAL])
    contingut = ruta.read_bytes()

    with pytest.raises(SystemExit) as excinfo:
        main(arguments)
    assert excinfo.value.code == 2
    captura = capsys.readouterr()
    assert captura.out == ""
    assert captura.err == ERROR_ARGUMENTS + "\n"
    assert ruta.read_bytes() == contingut


def preparar_cli(
    directori: Path, registres: list[dict[str, Any]] | None = None
) -> Path:
    ruta = directori / RUTA_RELATIVA
    ruta.parent.mkdir(parents=True, exist_ok=True)
    escriure_registres(ruta, [TASCA_INICIAL] if registres is None else registres)
    return ruta


def executar_cli(
    directori: Path, arguments: list[str]
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(RUTA_SCRIPT), *arguments],
        cwd=directori,
        capture_output=True,
        text=True,
    )


def comprovar_rebuig_cli(
    directori: Path, arguments: list[str], missatge: str
) -> None:
    ruta = preparar_cli(directori)
    contingut = ruta.read_bytes()

    resultat = executar_cli(directori, arguments)
    assert (resultat.returncode, resultat.stdout, resultat.stderr) == (
        2,
        "",
        missatge + "\n",
    )
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
    captura = capsys.readouterr()
    assert captura.out == "Registre de tasques buit.\n"
    assert captura.err == ""


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
    captura = capsys.readouterr()
    assert captura.out == (
        "[1] Pràctica 1 (RS) - estat: pendent\n"
        "[2] Examen parcial (SO) - estat: pendent\n"
    )
    assert captura.err == ""


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


def test_gs08_llistar_tasca_antiga_sense_data_limit(
    ruta_tasques: Path,
    avui_fix: date,
    capsys: pytest.CaptureFixture[str],
) -> None:
    registre_antic = {
        "id": 1,
        "titol": "Pràctica 1",
        "assignatura": "RS",
        "estat": "pendent",
    }
    escriure_registres(ruta_tasques, [registre_antic])
    contingut = ruta_tasques.read_bytes()

    assert main(["list"]) == 0
    captura = capsys.readouterr()
    assert captura.out == "[1] Pràctica 1 (RS) - estat: pendent\n"
    assert captura.err == ""
    assert ruta_tasques.read_bytes() == contingut
    assert json.loads(ruta_tasques.read_text(encoding="utf-8")) == [registre_antic]


def test_gs19_llistar_tasca_amb_data_limit_null(
    ruta_tasques: Path,
    avui_fix: date,
    capsys: pytest.CaptureFixture[str],
) -> None:
    registre = {**TASCA_INICIAL, "data_limit": None}
    escriure_registres(ruta_tasques, [registre])
    contingut = ruta_tasques.read_bytes()

    assert main(["list"]) == 0
    captura = capsys.readouterr()
    assert captura.out == "[1] Pràctica 1 (RS) - estat: pendent\n"
    assert captura.err == ""
    assert ruta_tasques.read_bytes() == contingut
    assert json.loads(ruta_tasques.read_text(encoding="utf-8")) == [registre]


def test_llistat_amb_data_limit(
    ruta_tasques: Path,
    avui_fix: date,
    capsys: pytest.CaptureFixture[str],
) -> None:
    escriure_registres(ruta_tasques, [TASCA_INICIAL])
    contingut = ruta_tasques.read_bytes()

    assert main(["list"]) == 0
    captura = capsys.readouterr()
    assert captura.out == (
        "[1] Pràctica 1 (RS) - estat: pendent - data límit: 2026-12-10\n"
    )
    assert captura.err == ""
    assert ruta_tasques.read_bytes() == contingut


def test_llistat_de_tasca_completada(
    ruta_tasques: Path,
    avui_fix: date,
    capsys: pytest.CaptureFixture[str],
) -> None:
    registre = {
        **TASCA_INICIAL,
        "estat": "completada",
        "data_limit": "2026-11-20",
    }
    escriure_registres(ruta_tasques, [registre])

    assert main(["list"]) == 0
    captura = capsys.readouterr()
    assert captura.out == (
        "[1] Pràctica 1 (RS) - estat: completada - data límit: 2026-11-20\n"
    )
    assert captura.err == ""


def test_llistat_conserva_ordre_i_fitxer(
    ruta_tasques: Path,
    avui_fix: date,
    capsys: pytest.CaptureFixture[str],
) -> None:
    registres = [
        TASCA_INICIAL,
        {
            "id": 2,
            "titol": "Examen parcial",
            "assignatura": "SO",
            "estat": "pendent",
        },
        {
            "id": 3,
            "titol": "Treball final",
            "assignatura": "RS",
            "estat": "completada",
            "data_limit": "2026-12-20",
        },
    ]
    escriure_registres(ruta_tasques, registres)
    contingut = ruta_tasques.read_bytes()

    assert main(["list"]) == 0
    captura = capsys.readouterr()
    assert captura.out == (
        "[1] Pràctica 1 (RS) - estat: pendent - data límit: 2026-12-10\n"
        "[2] Examen parcial (SO) - estat: pendent\n"
        "[3] Treball final (RS) - estat: completada - data límit: 2026-12-20\n"
    )
    assert captura.err == ""
    assert ruta_tasques.read_bytes() == contingut
    assert json.loads(ruta_tasques.read_text(encoding="utf-8")) == registres


def test_llistat_data_a_mes_de_set_dies(
    ruta_tasques: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    data_llunyana = (date.today() + timedelta(days=8)).isoformat()
    assert (date.fromisoformat(data_llunyana) - date.today()).days == 8
    registre = {**TASCA_INICIAL, "data_limit": data_llunyana}
    escriure_registres(ruta_tasques, [registre])

    assert main(["list"]) == 0
    captura = capsys.readouterr()
    assert captura.out == (
        f"[1] Pràctica 1 (RS) - estat: pendent - data límit: {data_llunyana}\n"
    )
    assert captura.err == ""


def test_gs14_mostrar_tasca_caducada(
    ruta_tasques: Path,
    avui_fix: date,
    capsys: pytest.CaptureFixture[str],
) -> None:
    comprovar_llistat(
        ruta_tasques,
        {**TASCA_INICIAL, "data_limit": "2026-11-22"},
        "[1] Pràctica 1 (RS) - estat: pendent - data límit: 2026-11-22 [CADUCADA]",
        capsys,
    )


def test_gs15_urgent_quan_venc_avui(
    ruta_tasques: Path,
    avui_fix: date,
    capsys: pytest.CaptureFixture[str],
) -> None:
    comprovar_llistat(
        ruta_tasques,
        {**TASCA_INICIAL, "data_limit": "2026-11-23"},
        "[1] Pràctica 1 (RS) - estat: pendent - data límit: 2026-11-23 [URGENT]",
        capsys,
    )


def test_gs16_urgent_quan_venc_en_sis_dies(
    ruta_tasques: Path,
    avui_fix: date,
    capsys: pytest.CaptureFixture[str],
) -> None:
    comprovar_llistat(
        ruta_tasques,
        {**TASCA_INICIAL, "data_limit": "2026-11-29"},
        "[1] Pràctica 1 (RS) - estat: pendent - data límit: 2026-11-29 [URGENT]",
        capsys,
    )


def test_gs17_sense_etiqueta_a_set_dies(
    ruta_tasques: Path,
    avui_fix: date,
    capsys: pytest.CaptureFixture[str],
) -> None:
    comprovar_llistat(
        ruta_tasques,
        {**TASCA_INICIAL, "data_limit": "2026-11-30"},
        "[1] Pràctica 1 (RS) - estat: pendent - data límit: 2026-11-30",
        capsys,
    )


def test_gs18_sense_etiqueta_en_completada(
    ruta_tasques: Path,
    avui_fix: date,
    capsys: pytest.CaptureFixture[str],
) -> None:
    comprovar_llistat(
        ruta_tasques,
        {
            **TASCA_INICIAL,
            "estat": "completada",
            "data_limit": "2026-11-20",
        },
        "[1] Pràctica 1 (RS) - estat: completada - data límit: 2026-11-20",
        capsys,
    )


def test_gs29_opcio_desconeguda(
    ruta_tasques: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    comprovar_error_arguments(["list", "--desconeguda"], ruta_tasques, capsys)


@pytest.mark.parametrize(
    "arguments",
    [
        ["add", "--title", "Prova", "--subject", "RS", "--due"],
        ["edit", "--id"],
        ["complete", "--id"],
        ["desconegut"],
        ["add", "--subject", "RS", "--due", "2026-12-10"],
        ["add", "--title", "Prova", "--due", "2026-12-10"],
        [],
    ],
)
def test_errors_generals_arguments(
    arguments: list[str],
    ruta_tasques: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    comprovar_error_arguments(arguments, ruta_tasques, capsys)


def test_help_continua_funcionant(
    ruta_tasques: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    escriure_registres(ruta_tasques, [TASCA_INICIAL])
    contingut = ruta_tasques.read_bytes()

    with pytest.raises(SystemExit) as excinfo:
        main(["--help"])
    assert excinfo.value.code == 0
    captura = capsys.readouterr()
    assert captura.err == ""
    assert "usage:" in captura.out
    assert ruta_tasques.read_bytes() == contingut


@pytest.mark.parametrize(
    "arguments",
    [
        ["list", "--desconeguda"],
        ["add", "--title", "Prova", "--subject", "RS", "--due"],
        ["edit", "--id"],
        ["complete", "--id"],
        ["desconegut"],
        ["add", "--subject", "RS", "--due", "2026-12-10"],
        [],
    ],
)
def test_cli_errors_generals(
    arguments: list[str], tmp_path: Path
) -> None:
    comprovar_rebuig_cli(tmp_path, arguments, ERROR_ARGUMENTS)


@pytest.mark.parametrize(
    ("arguments", "missatge"),
    [
        (
            ["add", "--title", "Prova", "--subject", "RS"],
            "Error: cal indicar la data límit amb --due.",
        ),
        (
            ["add", "--title", "Prova", "--subject", "RS", "--due", "2026-02-30"],
            "Error: data límit no vàlida. Utilitza YYYY-MM-DD amb una data existent.",
        ),
        (
            ["edit", "--title", "Nou títol"],
            "Error: cal indicar l'ID de la tasca amb --id.",
        ),
        (
            ["edit", "--id", "abc", "--title", "Nou títol"],
            "Error: l'ID ha de ser un enter positiu.",
        ),
        (
            ["edit", "--id", "99", "--title", "Nou títol"],
            "Error: no existeix cap tasca amb ID 99.",
        ),
        (
            ["edit", "--id", "1"],
            "Error: cal indicar almenys un atribut per modificar.",
        ),
        (
            ["edit", "--id", "1", "--status", "inicial"],
            "Error: estat no vàlid. Utilitza pendent o completada.",
        ),
        (
            ["complete", "--id", "0"],
            "Error: l'ID ha de ser un enter positiu.",
        ),
        (
            ["complete", "--id", "99"],
            "Error: no existeix cap tasca amb ID 99.",
        ),
    ],
)
def test_cli_missatges_especifices_continuen(
    arguments: list[str], missatge: str, tmp_path: Path
) -> None:
    comprovar_rebuig_cli(tmp_path, arguments, missatge)


def test_cli_llistat_correcte(tmp_path: Path) -> None:
    data_llunyana = (date.today() + timedelta(days=8)).isoformat()
    registre = {**TASCA_INICIAL, "data_limit": data_llunyana}
    ruta = preparar_cli(tmp_path, [registre])

    resultat = executar_cli(tmp_path, ["list"])
    assert (resultat.returncode, resultat.stderr) == (0, "")
    assert resultat.stdout == (
        f"[1] Pràctica 1 (RS) - estat: pendent - data límit: {data_llunyana}\n"
    )
    assert ruta.read_bytes() == json.dumps(
        [registre], ensure_ascii=False, indent=2
    ).encode("utf-8")


def test_cli_help_sortida_zero(tmp_path: Path) -> None:
    ruta = preparar_cli(tmp_path)
    contingut = ruta.read_bytes()

    resultat = executar_cli(tmp_path, ["--help"])
    assert (resultat.returncode, resultat.stderr) == (0, "")
    assert "usage:" in resultat.stdout
    assert ruta.read_bytes() == contingut

    resultat = executar_cli(tmp_path, ["list", "--help"])
    assert (resultat.returncode, resultat.stderr) == (0, "")
    assert "usage:" in resultat.stdout
    assert ruta.read_bytes() == contingut


def test_cli_operacions_correctes(tmp_path: Path) -> None:
    data_llunyana = (date.today() + timedelta(days=8)).isoformat()
    registre_pendent = {**TASCA_INICIAL, "data_limit": data_llunyana}
    ruta = preparar_cli(tmp_path, [registre_pendent])

    afegir = executar_cli(
        tmp_path,
        [
            "add",
            "--title",
            "Pràctica 2",
            "--subject",
            "SO",
            "--due",
            "2030-01-01",
        ],
    )
    assert (afegir.returncode, afegir.stdout, afegir.stderr) == (
        0,
        "Tasca [ID: 2] creada amb èxit\n",
        "",
    )

    editar = executar_cli(
        tmp_path, ["edit", "--id", "2", "--title", "Pràctica 2 bis"]
    )
    assert (editar.returncode, editar.stdout, editar.stderr) == (
        0,
        "Tasca [ID: 2] actualitzada amb èxit\n",
        "",
    )

    completar = executar_cli(tmp_path, ["complete", "--id", "2"])
    assert (completar.returncode, completar.stdout, completar.stderr) == (
        0,
        "Tasca [ID: 2] marcada com a completada\n",
        "",
    )

    llistar = executar_cli(tmp_path, ["list"])
    assert (llistar.returncode, llistar.stderr) == (0, "")
    assert llistar.stdout == (
        f"[1] Pràctica 1 (RS) - estat: pendent - data límit: {data_llunyana}\n"
        "[2] Pràctica 2 bis (SO) - estat: completada - data límit: 2030-01-01\n"
    )

    registres = json.loads(ruta.read_text(encoding="utf-8"))
    assert [registre["id"] for registre in registres] == [1, 2]
    assert registres[0] == registre_pendent
    assert registres[1]["titol"] == "Pràctica 2 bis"
    assert registres[1]["estat"] == "completada"
