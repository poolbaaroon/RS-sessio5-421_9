from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from typing import Any


@dataclass
class Task:
    id: int
    titol: str
    assignatura: str
    estat: str = "pendent"

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
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False)

    @classmethod
    def from_dict(cls, dades: dict[str, Any]) -> Task:
        return cls(
            id=dades["id"],
            titol=dades.get("titol", dades.get("title")),
            assignatura=dades.get("assignatura", dades.get("subject")),
            estat=dades.get("estat", dades.get("status", "pendent")),
        )

    @classmethod
    def from_json(cls, text: str) -> Task:
        return cls.from_dict(json.loads(text))


Tasca = Task
