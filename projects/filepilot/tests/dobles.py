"""Dobles de enumeración compartidos por las pruebas del recorrido.

`os.scandir` entrega objetos `DirEntry` que no pueden construirse ni alterarse
desde Python. Estas clases imitan su contrato de metadatos para provocar fallos
controlados y enlaces simbólicos sin depender de los privilegios del entorno.
Los fallos así inyectados comprueban el tratamiento del error; no acreditan los
permisos reales del sistema, que se verifican aparte.
"""

import os
from pathlib import Path


def clave(ruta) -> str:
    """Forma comparable de una ruta, indicada como texto o como `Path`."""
    return os.path.normcase(os.path.abspath(os.fspath(ruta)))


class Metadatos:
    """Resultado de `stat` con los campos que consulta el recorrido.

    Sin `atributos` el objeto carece de `st_file_attributes`, como ocurre cuando
    ese dato no llega en los metadatos de la entrada (RF-15).
    """

    def __init__(self, tamano: int = 0, atributos: int | None = 0):
        self.st_size = tamano
        if atributos is not None:
            self.st_file_attributes = atributos


class EntradaSimulada:
    """Entrada de enumeración con tipo y metadatos fijados por la prueba."""

    def __init__(self, ruta, *, carpeta=False, enlace=False, tamano=0, atributos=0, fallo=None):
        self.name = Path(ruta).name
        self.path = str(ruta)
        self._carpeta = carpeta
        self._enlace = enlace
        self._metadatos = Metadatos(tamano, atributos)
        self._fallo = fallo

    def is_symlink(self):
        return self._enlace

    def is_dir(self, *, follow_symlinks=True):
        # Sin seguir el enlace, un enlace a carpeta no se considera carpeta.
        return self._carpeta and (follow_symlinks or not self._enlace)

    def is_file(self, *, follow_symlinks=True):
        return not self._carpeta

    def stat(self, *, follow_symlinks=True):
        if self._fallo is not None:
            raise self._fallo
        return self._metadatos


class Enumeracion:
    """Resultado de enumeración utilizable como iterador y como contexto."""

    def __init__(self, entradas):
        self._entradas = iter(entradas)

    def __iter__(self):
        return self._entradas

    def __next__(self):
        return next(self._entradas)

    def __enter__(self):
        return self

    def __exit__(self, *excepcion):
        return False

    def close(self):
        pass


def _sustituir_enumeracion(monkeypatch, ajustar):
    """Enumera con `os.scandir` y deja que `ajustar` modifique el contenido."""
    real = os.scandir

    def enumerar(ruta="."):
        with real(ruta) as entradas:
            contenido = list(entradas)
        return Enumeracion(ajustar(ruta, contenido))

    monkeypatch.setattr(os, "scandir", enumerar)


def anadir_entradas(monkeypatch, carpeta, entradas):
    """Añade entradas simuladas al contenido real de `carpeta`."""
    objetivo = clave(carpeta)

    def ajustar(ruta, contenido):
        return contenido + list(entradas) if clave(ruta) == objetivo else contenido

    _sustituir_enumeracion(monkeypatch, ajustar)


def fallar_al_enumerar(monkeypatch, carpeta, fallo, omitir=0):
    """Hace fallar `os.scandir` sobre `carpeta` tras `omitir` llamadas correctas.

    `omitir` permite dejar pasar la comprobación de la raíz y provocar el fallo
    en la enumeración posterior del análisis.
    """
    real = os.scandir
    objetivo = clave(carpeta)
    restantes = omitir

    def enumerar(ruta="."):
        nonlocal restantes
        if clave(ruta) == objetivo:
            if restantes <= 0:
                raise fallo
            restantes -= 1
        return real(ruta)

    monkeypatch.setattr(os, "scandir", enumerar)


def fallar_en(monkeypatch, rutas_y_fallos):
    """Hace que la consulta de metadatos de cada ruta falle con su error.

    La entrada real se sustituye por un doble del mismo tipo, de modo que el
    recorrido encuentre el fallo al pedir sus metadatos, tanto si los consulta
    para el atributo de oculto como para el tamaño.
    """
    fallos = {clave(ruta): fallo for ruta, fallo in rutas_y_fallos.items()}

    def ajustar(ruta, contenido):
        return [
            EntradaSimulada(
                entrada.path,
                carpeta=entrada.is_dir(follow_symlinks=False),
                enlace=entrada.is_symlink(),
                fallo=fallos[clave(entrada.path)],
            )
            if clave(entrada.path) in fallos
            else entrada
            for entrada in contenido
        ]

    _sustituir_enumeracion(monkeypatch, ajustar)
