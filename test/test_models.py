from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from src.models import Task


@pytest.fixture
def fitxer_temporal(tmp_path: Path) -> Path:
    return tmp_path / "tasca.json"


def comprovar_anada_i_tornada(
    registre: dict[str, Any], fitxer: Path
) -> Task:
    tasca = Task.from_dict(registre)
    fitxer.write_text(tasca.to_json(), encoding="utf-8")
    reconstruida = Task.from_json(fitxer.read_text(encoding="utf-8"))

    assert reconstruida == tasca
    assert reconstruida.to_dict() == registre
    return reconstruida


def test_conversio_amb_data_limit(fitxer_temporal: Path) -> None:
    registre = {
        "id": 1,
        "titol": "Pràctica 1",
        "assignatura": "RS",
        "estat": "pendent",
        "data_limit": "2026-12-10",
    }

    tasca = comprovar_anada_i_tornada(registre, fitxer_temporal)

    assert tasca.data_limit == "2026-12-10"
    assert tasca.id == 1
    assert tasca.titol == "Pràctica 1"
    assert tasca.assignatura == "RS"
    assert tasca.estat == "pendent"


def test_conversio_sense_data_limit(fitxer_temporal: Path) -> None:
    registre = {
        "id": 2,
        "titol": "Examen parcial",
        "assignatura": "SO",
        "estat": "pendent",
    }

    tasca = comprovar_anada_i_tornada(registre, fitxer_temporal)

    assert tasca.data_limit is None
    assert "data_limit" not in tasca.to_dict()


def test_conversio_amb_data_limit_null(fitxer_temporal: Path) -> None:
    registre = {
        "id": 3,
        "titol": "Treball antic",
        "assignatura": "RS",
        "estat": "pendent",
        "data_limit": None,
    }

    tasca = comprovar_anada_i_tornada(registre, fitxer_temporal)

    assert tasca.data_limit is None
    assert tasca.to_dict()["data_limit"] is None
