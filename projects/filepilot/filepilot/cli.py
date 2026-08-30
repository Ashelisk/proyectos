"""Entrada de línea de órdenes de FilePilot."""

import argparse
import sys

DESCRIPCION = "Analiza una carpeta y muestra la organización que propondría, sin modificar nada."
CODIGO_USO_INCORRECTO = 1


class AnalizadorDeOrdenes(argparse.ArgumentParser):
    """Analizador que termina con código uno ante un uso incorrecto.

    El comportamiento predeterminado de `argparse` es el código dos, reservado
    a los problemas con la ruta indicada (RF-2, RF-11).
    """

    def error(self, message):
        self.print_usage(sys.stderr)
        print(f"{self.prog}: error: {message}", file=sys.stderr)
        raise SystemExit(CODIGO_USO_INCORRECTO)


def crear_analizador() -> AnalizadorDeOrdenes:
    """Construye el analizador con el subcomando `analizar` y sus opciones."""
    analizador = AnalizadorDeOrdenes(prog="filepilot", description=DESCRIPCION)
    ordenes = analizador.add_subparsers(dest="orden", required=True, metavar="orden")

    analizar = ordenes.add_parser(
        "analizar",
        help="Examina una carpeta y muestra el reparto propuesto",
        description=DESCRIPCION,
    )
    analizar.add_argument("ruta", help="Carpeta que se va a examinar")
    analizar.add_argument(
        "--recursivo",
        action="store_true",
        help="Examina también el contenido de las subcarpetas",
    )
    analizar.add_argument(
        "--incluir-ocultos",
        action="store_true",
        dest="incluir_ocultos",
        help="Examina también los archivos y carpetas ocultos",
    )
    return analizador


def main(argv: list[str] | None = None) -> int:
    """Punto de entrada. Devuelve el código de salida del proceso."""
    analizador = crear_analizador()
    analizador.parse_args(argv)
    # T3 valida la ruta indicada; T8 conecta recorrido e informe.
    return 0
