from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

try:
    from .models import Task
    from .validators import validar_data, validar_estat, validar_id
except ImportError:
    from models import Task
    from validators import validar_data, validar_estat, validar_id

RUTA_DADES = Path("data") / "tasks.json"
ERROR_DUE = "Error: cal indicar la data límit amb --due."
ERROR_DATA = (
    "Error: data límit no vàlida. "
    "Utilitza YYYY-MM-DD amb una data existent."
)
ERROR_ID_FALTA = "Error: cal indicar l'ID de la tasca amb --id."
ERROR_ID_NO_VALID = "Error: l'ID ha de ser un enter positiu."
ERROR_NO_TROBAT = "Error: no existeix cap tasca amb ID {identificador}."
ERROR_SENSE_ATRIBUTS = "Error: cal indicar almenys un atribut per modificar."
ERROR_ESTAT = "Error: estat no vàlid. Utilitza pendent o completada."


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


def cercar_tasca(tasques: list[Task], identificador: int) -> Task:
    tasca = next(
        (element for element in tasques if element.id == identificador),
        None,
    )
    if tasca is None:
        raise ValueError(ERROR_NO_TROBAT.format(identificador=identificador))
    return tasca


def editar_tasca(
    identificador: int,
    titol: str | None,
    assignatura: str | None,
    data_limit: str | None,
    estat: str | None,
    ruta: Path = RUTA_DADES,
) -> Task:
    tasques = carregar_tasques(ruta)
    tasca = cercar_tasca(tasques, identificador)

    if titol is not None:
        tasca.titol = titol
    if assignatura is not None:
        tasca.assignatura = assignatura
    if data_limit is not None:
        tasca.data_limit = data_limit
    if estat is not None:
        tasca.estat = estat

    desar_tasques(tasques, ruta)
    return tasca


def completar_tasca(identificador: int, ruta: Path = RUTA_DADES) -> Task:
    tasques = carregar_tasques(ruta)
    tasca = cercar_tasca(tasques, identificador)
    if tasca.estat != "completada":
        tasca.estat = "completada"
        desar_tasques(tasques, ruta)
    return tasca


def rebutjar(missatge: str) -> int:
    print(missatge, file=sys.stderr)
    return 2


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

    editar = subcomandaments.add_parser("edit", help="Modifica una tasca existent.")
    editar.add_argument("--id", help="ID de la tasca a modificar.")
    editar.add_argument("--title", help="Nou títol de la tasca.")
    editar.add_argument("--subject", help="Nova assignatura de la tasca.")
    editar.add_argument("--due", help="Nova data límit (YYYY-MM-DD).")
    editar.add_argument("--status", help="Nou estat (pendent o completada).")

    completar = subcomandaments.add_parser(
        "complete", help="Marca una tasca com a completada."
    )
    completar.add_argument("--id", help="ID de la tasca a completar.")

    subcomandaments.add_parser("list", help="Mostra totes les tasques.")
    return parser


def validar_argument_id(identificador: str | None) -> int:
    if identificador is None:
        raise ValueError(ERROR_ID_FALTA)
    if not validar_id(identificador):
        raise ValueError(ERROR_ID_NO_VALID)
    return int(identificador)


def processar_edit(arguments: argparse.Namespace) -> int:
    try:
        identificador = validar_argument_id(arguments.id)
    except ValueError as error:
        return rebutjar(str(error))
    if (
        arguments.title is None
        and arguments.subject is None
        and arguments.due is None
        and arguments.status is None
    ):
        return rebutjar(ERROR_SENSE_ATRIBUTS)
    if arguments.due is not None and not validar_data(arguments.due):
        return rebutjar(ERROR_DATA)
    if arguments.status is not None and not validar_estat(arguments.status):
        return rebutjar(ERROR_ESTAT)

    try:
        tasca = editar_tasca(
            identificador,
            arguments.title,
            arguments.subject,
            arguments.due,
            arguments.status,
        )
    except ValueError as error:
        return rebutjar(str(error))

    print(f"Tasca [ID: {tasca.id}] actualitzada amb èxit")
    return 0


def processar_complete(arguments: argparse.Namespace) -> int:
    try:
        identificador = validar_argument_id(arguments.id)
        tasca = completar_tasca(identificador)
    except ValueError as error:
        return rebutjar(str(error))

    print(f"Tasca [ID: {tasca.id}] marcada com a completada")
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    arguments = crear_parser().parse_args(argv)
    if arguments.comandament == "add":
        if arguments.due is None:
            return rebutjar(ERROR_DUE)
        if not validar_data(arguments.due):
            return rebutjar(ERROR_DATA)
        tasca = afegir_tasca(
            arguments.title,
            arguments.subject,
            data_limit=arguments.due,
        )
        print(f"Tasca [ID: {tasca.id}] creada amb èxit")
    elif arguments.comandament == "edit":
        return processar_edit(arguments)
    elif arguments.comandament == "complete":
        return processar_complete(arguments)
    else:
        print(llistar_tasques())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
