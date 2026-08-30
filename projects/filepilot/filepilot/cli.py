"""Entrada de línea de órdenes de FilePilot."""

import argparse
import re
import sys

DESCRIPCION = "Analiza una carpeta y muestra la organización que propondría, sin modificar nada."
CODIGO_USO_INCORRECTO = 1

# `argparse` redacta sus diagnósticos en inglés; RNF-3 los exige en español.
TRADUCCIONES = (
    (
        r"the following arguments are required: (?P<lista>.+)",
        "faltan argumentos obligatorios: {lista}",
    ),
    (r"unrecognized arguments: (?P<lista>.+)", "argumentos no reconocidos: {lista}"),
    (
        r"argument (?P<destino>[^:]+): invalid choice: (?P<valor>.+) \(choose from (?P<admitidos>.+)\)",
        "valor no admitido para {destino}: {valor}; los admitidos son: {admitidos}",
    ),
    (
        r"argument (?P<destino>[^:]+): ignored explicit argument (?P<valor>.+)",
        "la opción {destino} no admite un valor: {valor}",
    ),
    (r"argument (?P<destino>[^:]+): expected one argument", "falta el valor de {destino}"),
    (r"ambiguous option: (?P<opcion>.+)", "opción ambigua: {opcion}"),
)
MENSAJE_GENERICO = "uso incorrecto de la orden"


def traducir_error(mensaje: str) -> str:
    """Devuelve el diagnóstico en español; sin coincidencia, uno genérico."""
    for patron, plantilla in TRADUCCIONES:
        encontrado = re.fullmatch(patron, mensaje)
        if encontrado:
            return plantilla.format(**encontrado.groupdict())
    return MENSAJE_GENERICO


class FormatoEnEspanol(argparse.HelpFormatter):
    """Encabeza la línea de uso en español, también al acompañar a un error."""

    def add_usage(self, usage, actions, groups, prefix=None):
        super().add_usage(usage, actions, groups, "uso: " if prefix is None else prefix)


class AnalizadorDeOrdenes(argparse.ArgumentParser):
    """Analizador que termina con código uno ante un uso incorrecto.

    El comportamiento predeterminado de `argparse` es el código dos, reservado
    a los problemas con la ruta indicada (RF-2, RF-11).
    """

    def error(self, message):
        self.print_usage(sys.stderr)
        print(f"{self.prog}: error: {traducir_error(message)}", file=sys.stderr)
        raise SystemExit(CODIGO_USO_INCORRECTO)


def crear_analizador() -> AnalizadorDeOrdenes:
    """Construye el analizador con el subcomando `analizar` y sus opciones."""
    analizador = AnalizadorDeOrdenes(
        prog="filepilot", description=DESCRIPCION, formatter_class=FormatoEnEspanol
    )
    ordenes = analizador.add_subparsers(dest="orden", required=True, metavar="orden")

    analizar = ordenes.add_parser(
        "analizar",
        help="Examina una carpeta y muestra el reparto propuesto",
        description=DESCRIPCION,
        formatter_class=FormatoEnEspanol,
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
