"""Entrada de línea de órdenes de FilePilot."""

import argparse
import sys

DESCRIPCION = "Analiza una carpeta y muestra la organización que propondría, sin modificar nada."


def crear_analizador() -> argparse.ArgumentParser:
    """Construye el analizador de argumentos común a todas las órdenes."""
    return argparse.ArgumentParser(prog="filepilot", description=DESCRIPCION)


def main(argv: list[str] | None = None) -> int:
    """Punto de entrada. Devuelve el código de salida del proceso."""
    analizador = crear_analizador()
    analizador.parse_args(sys.argv[1:] if argv is None else argv)
    # Sin subcomandos todavía: T2 añade `analizar` y el código uno del uso incorrecto.
    analizador.print_help()
    return 0
