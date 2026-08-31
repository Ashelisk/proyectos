"""Recorrido de una carpeta, exclusiones y recuentos (RF-3, RF-4, RF-9, RF-15)."""

import errno
import os
import stat
import sys
from dataclasses import dataclass
from pathlib import Path

from .clasificacion import Categoria, clasificar

ES_WINDOWS = sys.platform == "win32"

# Motivos de RF-9 en su orden de prioridad; cada entrada omitida recibe uno solo.
OCULTO = "oculto"
ENLACE = "enlace"
SIN_PERMISO = "sin_permiso"
ERROR_LECTURA = "error_lectura"
MOTIVOS = (OCULTO, ENLACE, SIN_PERMISO, ERROR_LECTURA)
# Solo estos dos motivos señalan un fallo y llevan al código tres (RF-13).
MOTIVOS_DE_FALLO = (SIN_PERMISO, ERROR_LECTURA)

BUCLE_DE_ENLACES = "demasiados enlaces simbólicos encadenados"
ATRIBUTO_NO_CONSULTABLE = "no se ha podido consultar el atributo de oculto"

# Causas en español a partir del código del fallo, no del idioma del sistema.
FALLOS_CONOCIDOS = {
    errno.EACCES: "permiso denegado",
    errno.EPERM: "operación no permitida",
    errno.ENOENT: "no existe",
    errno.ENOTDIR: "no es un directorio",
    errno.ELOOP: BUCLE_DE_ENLACES,
    errno.ENAMETOOLONG: "el nombre es demasiado largo",
    errno.EIO: "error de entrada y salida",
}


class AtributoNoConsultable(OSError):
    """En Windows, los metadatos no traen el atributo de oculto (RF-15)."""


def describir_fallo(fallo: OSError) -> str:
    """Describe en español la causa de un fallo del sistema de archivos."""
    if isinstance(fallo, AtributoNoConsultable):
        return ATRIBUTO_NO_CONSULTABLE
    conocida = FALLOS_CONOCIDOS.get(fallo.errno)
    if conocida:
        return conocida
    if fallo.errno is None:
        return "error del sistema"
    return f"error del sistema (código {fallo.errno})"


def motivo_del_fallo(fallo: OSError) -> str:
    """Distingue la falta de permisos de cualquier otro error de lectura."""
    if isinstance(fallo, PermissionError) or fallo.errno in (errno.EACCES, errno.EPERM):
        return SIN_PERMISO
    return ERROR_LECTURA


@dataclass(frozen=True)
class ArchivoAnalizado:
    """Archivo clasificado, con su tamaño en bytes."""

    ruta: Path
    categoria: Categoria
    tamano: int


@dataclass(frozen=True)
class EntradaOmitida:
    """Entrada excluida del análisis; `detalle` explica la causa real."""

    ruta: Path
    motivo: str
    detalle: str


@dataclass(frozen=True)
class ResultadoRecorrido:
    """Salida del recorrido: la raíz no entra en el recuento de subcarpetas."""

    archivos: tuple[ArchivoAnalizado, ...]
    omitidas: tuple[EntradaOmitida, ...]
    subcarpetas_encontradas: int
    subcarpetas_recorridas: int


def _es_oculto(entrada) -> bool:
    """Indica si la entrada está oculta (RF-15).

    Un nombre que empieza por punto lo es en cualquier plataforma. En Windows se
    consulta además el atributo del sistema: si los metadatos no lo traen, el
    elemento no se da por visible y el fallo se propaga para que quede omitido
    con su motivo real.
    """
    if entrada.name.startswith("."):
        return True
    if not ES_WINDOWS:
        return False
    atributos = getattr(entrada.stat(follow_symlinks=False), "st_file_attributes", None)
    if atributos is None:
        raise AtributoNoConsultable(ATRIBUTO_NO_CONSULTABLE)
    return bool(atributos & stat.FILE_ATTRIBUTE_HIDDEN)


def recorrer(raiz: Path, recursivo: bool = False, incluir_ocultos: bool = False) -> ResultadoRecorrido:
    """Enumera la raíz ya validada y, si `recursivo`, sus subcarpetas.

    La profundidad se gestiona con una pila propia sobre `os.scandir`, sin
    seguir enlaces simbólicos y sin abrir el contenido de ningún archivo
    (RF-10). Las exclusiones de RF-9 se aplican a lo encontrado dentro y cada
    entrada omitida recibe un único motivo por orden de prioridad. Un fallo de
    la propia raíz se propaga para que el CLI lo trate según RF-11; los demás
    se registran y el recorrido continúa (RF-13).
    """
    archivos: list[ArchivoAnalizado] = []
    omitidas: list[EntradaOmitida] = []
    encontradas = 0
    recorridas = 0

    def examinar(entrada) -> Path | None:
        """Clasifica u omite una entrada; devuelve la carpeta en la que entrar."""
        nonlocal encontradas
        ruta = Path(entrada.path)
        es_enlace = es_carpeta = oculto = False
        fallo = None
        try:
            # El enlace se reconoce antes que la carpeta: su destino no se sigue.
            es_enlace = entrada.is_symlink()
            es_carpeta = not es_enlace and entrada.is_dir(follow_symlinks=False)
        except OSError as problema:
            fallo = problema
        if es_carpeta:
            encontradas += 1
            if not recursivo:
                # RF-4: las subcarpetas no recursivas solo se cuentan.
                return None
        try:
            oculto = not incluir_ocultos and _es_oculto(entrada)
        except OSError as problema:
            if fallo is None or motivo_del_fallo(problema) == SIN_PERMISO:
                fallo = problema

        # Un fallo de consulta no reemplaza una exclusión de mayor prioridad.
        if oculto:
            motivo, detalle = OCULTO, ""
        elif es_enlace:
            motivo, detalle = ENLACE, ""
        else:
            try:
                if fallo is not None:
                    raise fallo
                if es_carpeta:
                    return ruta
                tamano = entrada.stat(follow_symlinks=False).st_size
                archivos.append(ArchivoAnalizado(ruta, clasificar(entrada.name), tamano))
                return None
            except OSError as problema:
                motivo, detalle = motivo_del_fallo(problema), describir_fallo(problema)
        omitidas.append(EntradaOmitida(ruta, motivo, detalle))
        return None

    raiz = Path(raiz)
    pendientes = [raiz]
    while pendientes:
        actual = pendientes.pop()
        try:
            with os.scandir(actual) as entradas:
                for entrada in entradas:
                    dentro = examinar(entrada)
                    if dentro is not None:
                        pendientes.append(dentro)
        except OSError as fallo:
            if actual == raiz:
                raise
            # La subcarpeta ya se contó como encontrada; al fallar su lectura se
            # omite con su causa y no se cuenta entre las recorridas (RF-13).
            omitidas.append(EntradaOmitida(actual, motivo_del_fallo(fallo), describir_fallo(fallo)))
            continue
        if actual != raiz:
            recorridas += 1

    return ResultadoRecorrido(tuple(archivos), tuple(omitidas), encontradas, recorridas)
