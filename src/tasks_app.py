from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

try:
    from .models import Task
    from .validators import validar_data
except ImportError:
    from models import Task
    from validators import validar_data

RUTA_DADES = Path("data") / "tasks.json"
ERROR_DUE = "Error: cal indicar la data límit amb --due."
ERROR_DATA = (
    "Error: data límit no vàlida. "
    "Utilitza YYYY-MM-DD amb una data existent."
)


def assegurar_fitxer(ruta: Path = RUTA_DADES) -> None:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    if not ruta.exists() or ruta.stat().st_size == 0:
        ruta.write_text("[]", encoding="utf-8")


def carregar_tasques(ruta: Path = RUTA_DADES) -> list[Task]:
    assegurar_fitxer(ruta)
    with ruta.open("r", encoding="utf-8") as fitxer:
        dades = json.load(fitxer)
    return [Task.from_dict(registre) for registre in dades]


def desar_tasques(tasques: list[Task], ruta: Path = RUTA_DADES) -> None:
    assegurar_fitxer(ruta)
    with ruta.open("w", encoding="utf-8") as fitxer:
        json.dump(
            [tasca.to_dict() for tasca in tasques],
            fitxer,
            ensure_ascii=False,
            indent=2,
        )
        fitxer.write("\n")


def afegir_tasca(
    titol: str,
    assignatura: str,
    ruta: Path = RUTA_DADES,
    data_limit: str | None = None,
) -> Task:
    tasques = carregar_tasques(ruta)
    seguent_id = max((tasca.id for tasca in tasques), default=0) + 1
    tasca = Task(
        id=seguent_id,
        titol=titol,
        assignatura=assignatura,
        data_limit=data_limit,
    )
    tasques.append(tasca)
    desar_tasques(tasques, ruta)
    return tasca


def llistar_tasques(ruta: Path = RUTA_DADES) -> str:
    tasques = carregar_tasques(ruta)
    if not tasques:
        return "Registre de tasques buit."
    return "\n".join(
        f"[{tasca.id}] {tasca.titol} ({tasca.assignatura}) - estat: {tasca.estat}"
        for tasca in tasques
    )


def crear_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="tasks_app",
        description="Gestió de tasques acadèmiques.",
    )
    subcomandaments = parser.add_subparsers(dest="comandament", required=True)

    afegir = subcomandaments.add_parser("add", help="Afegeix una tasca nova.")
    afegir.add_argument("--title", required=True, help="Títol de la tasca.")
    afegir.add_argument("--subject", required=True, help="Assignatura de la tasca.")
    afegir.add_argument("--due", help="Data límit de la tasca (YYYY-MM-DD).")

    subcomandaments.add_parser("list", help="Mostra totes les tasques.")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    arguments = crear_parser().parse_args(argv)
    if arguments.comandament == "add":
        if arguments.due is None:
            print(ERROR_DUE, file=sys.stderr)
            return 2
        if not validar_data(arguments.due):
            print(ERROR_DATA, file=sys.stderr)
            return 2
        tasca = afegir_tasca(
            arguments.title,
            arguments.subject,
            data_limit=arguments.due,
        )
        print(f"Tasca [ID: {tasca.id}] creada amb èxit")
    else:
        print(llistar_tasques())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
