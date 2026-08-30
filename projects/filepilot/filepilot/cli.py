"""Entrada de línea de órdenes de FilePilot."""

import argparse
import errno
import os
import re
import stat
import sys
from pathlib import Path

DESCRIPCION = "Analiza una carpeta y muestra la organización que propondría, sin modificar nada."
CODIGO_USO_INCORRECTO = 1
CODIGO_RUTA_INVALIDA = 2

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


class RutaInvalida(Exception):
    """La ruta indicada no puede analizarse; su texto describe la causa (RF-11)."""


# Causas en español a partir del código del fallo, no del idioma del sistema.
FALLOS_CONOCIDOS = {
    errno.EACCES: "permiso denegado",
    errno.EPERM: "operación no permitida",
    errno.ENOENT: "no existe",
    errno.ENOTDIR: "no es un directorio",
    errno.ELOOP: "demasiados enlaces simbólicos encadenados",
    errno.ENAMETOOLONG: "el nombre es demasiado largo",
    errno.EIO: "error de entrada y salida",
}


def describir_fallo(fallo: OSError) -> str:
    """Describe en español la causa de un fallo del sistema de archivos."""
    conocida = FALLOS_CONOCIDOS.get(fallo.errno)
    if conocida:
        return conocida
    if fallo.errno is None:
        return "error del sistema"
    return f"error del sistema (código {fallo.errno})"


def citar(ruta: str, destino: Path) -> str:
    """Cita la ruta tal como se indicó y, si es un enlace, también su destino."""
    if os.path.islink(ruta):
        return f"«{ruta}» (enlace a «{destino}»)"
    return f"«{ruta}»"


def resolver_raiz(ruta: str) -> Path:
    """Devuelve el directorio legible que se va a analizar (RF-11, RF-16).

    Sigue los enlaces antes de comprobar el destino, de modo que una raíz
    enlazada se analiza en su ubicación real. La raíz no se descarta por estar
    oculta: las exclusiones se aplican a su contenido (RF-14).
    """
    if not ruta:
        raise RutaInvalida("la ruta indicada está vacía")

    try:
        destino = Path(ruta).resolve()
    except OSError as fallo:
        raise RutaInvalida(f"no se puede resolver la ruta «{ruta}»: {describir_fallo(fallo)}") from fallo

    referencia = citar(ruta, destino)
    try:
        informacion = destino.stat()
    except FileNotFoundError as fallo:
        raise RutaInvalida(f"la ruta {referencia} no existe") from fallo
    except NotADirectoryError as fallo:
        # Un componente intermedio no es un directorio, como en `notas.txt/sub`.
        raise RutaInvalida(f"la ruta {referencia} no es un directorio") from fallo
    except PermissionError as fallo:
        raise RutaInvalida(f"no se puede leer la ruta {referencia}: permiso denegado") from fallo
    except OSError as fallo:
        raise RutaInvalida(f"no se puede leer la ruta {referencia}: {describir_fallo(fallo)}") from fallo

    if not stat.S_ISDIR(informacion.st_mode):
        raise RutaInvalida(f"la ruta {referencia} no es un directorio")

    # Enumerar una entrada comprueba el acceso sin abrir el contenido (RF-10).
    try:
        with os.scandir(destino) as entradas:
            next(entradas, None)
    except PermissionError as fallo:
        raise RutaInvalida(f"no se puede leer la carpeta {referencia}: permiso denegado") from fallo
    except OSError as fallo:
        raise RutaInvalida(f"no se puede leer la carpeta {referencia}: {describir_fallo(fallo)}") from fallo

    return destino


def main(argv: list[str] | None = None) -> int:
    """Punto de entrada. Devuelve el código de salida del proceso."""
    analizador = crear_analizador()
    opciones = analizador.parse_args(argv)

    try:
        resolver_raiz(opciones.ruta)
    except RutaInvalida as problema:
        print(f"filepilot: error: {problema}", file=sys.stderr)
        return CODIGO_RUTA_INVALIDA

    # T5 a T8 recorren la raíz resuelta y componen el informe.
    return 0
