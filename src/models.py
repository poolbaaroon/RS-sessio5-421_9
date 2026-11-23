from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Task:
    id: int
    titol: str
    assignatura: str
    estat: str = "pendent"
    data_limit: str | None = None
    _te_clau_data_limit: bool = field(default=False, repr=False, compare=False)

    @property
    def title(self) -> str:
        return self.titol

    @property
    def subject(self) -> str:
        return self.assignatura

    @property
    def status(self) -> str:
        return self.estat

    def to_dict(self) -> dict[str, Any]:
        registre: dict[str, Any] = {
            "id": self.id,
            "titol": self.titol,
            "assignatura": self.assignatura,
            "estat": self.estat,
        }
        if self._te_clau_data_limit or self.data_limit is not None:
            registre["data_limit"] = self.data_limit
        return registre

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False)

    @classmethod
    def from_dict(cls, dades: dict[str, Any]) -> Task:
        return cls(
            id=dades["id"],
            titol=dades.get("titol", dades.get("title")),
            assignatura=dades.get("assignatura", dades.get("subject")),
            estat=dades.get("estat", dades.get("status", "pendent")),
            data_limit=dades.get("data_limit", dades.get("due")),
            _te_clau_data_limit="data_limit" in dades or "due" in dades,
        )

    @classmethod
    def from_json(cls, text: str) -> Task:
        return cls.from_dict(json.loads(text))


Tasca = Task
