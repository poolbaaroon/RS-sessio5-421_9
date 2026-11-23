from __future__ import annotations

import re
from datetime import date

FORMAT_DATA = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}")
FORMAT_ID = re.compile(r"[0-9]+")
ESTATS_ADMESOS = frozenset({"pendent", "completada"})


def validar_data(data: str) -> bool:
    if not isinstance(data, str) or FORMAT_DATA.fullmatch(data) is None:
        return False
    try:
        date.fromisoformat(data)
    except ValueError:
        return False
    return True


def validar_id(identificador: str | int) -> bool:
    if isinstance(identificador, bool):
        return False
    if isinstance(identificador, int):
        return identificador > 0
    if isinstance(identificador, str) and FORMAT_ID.fullmatch(identificador):
        return int(identificador) > 0
    return False


def validar_estat(estat: str) -> bool:
    return isinstance(estat, str) and estat in ESTATS_ADMESOS
