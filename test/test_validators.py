from __future__ import annotations

import pytest

from src.validators import validar_data, validar_estat, validar_id


@pytest.mark.parametrize(
    "data",
    ["2026-11-22", "2026-11-23", "2026-12-10", "2024-02-29"],
)
def test_validar_data_valides(data: str) -> None:
    assert validar_data(data) is True


@pytest.mark.parametrize(
    "data",
    [
        "2026-02-30",
        "10/12/2026",
        "2026-2-3",
        "2026-13-01",
        "2026-00-10",
        "",
    ],
)
def test_validar_data_invalides(data: str) -> None:
    assert validar_data(data) is False


@pytest.mark.parametrize("identificador", ["1", "99", 1, 42])
def test_validar_id_positiu(identificador: str | int) -> None:
    assert validar_id(identificador) is True


@pytest.mark.parametrize(
    "identificador",
    ["abc", "0", 0, "-1", -1, "", "1.5"],
)
def test_validar_id_invalid(identificador: str | int) -> None:
    assert validar_id(identificador) is False


@pytest.mark.parametrize("estat", ["pendent", "completada"])
def test_validar_estat_admes(estat: str) -> None:
    assert validar_estat(estat) is True


@pytest.mark.parametrize("estat", ["acabada", "PENDENT", "pendent ", ""])
def test_validar_estat_no_admes(estat: str) -> None:
    assert validar_estat(estat) is False
