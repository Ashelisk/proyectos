"""Recorrido de una carpeta y recuento de sus subcarpetas (RF-3, RF-4)."""

import os
from dataclasses import dataclass
from pathlib import Path

from .clasificacion import Categoria, clasificar


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


def recorrer(raiz: Path, recursivo: bool = False) -> ResultadoRecorrido:
    """Enumera la raíz ya validada y, si `recursivo`, sus subcarpetas.

    La profundidad se gestiona con una pila propia sobre `os.scandir`, sin
    seguir enlaces simbólicos y sin abrir el contenido de ningún archivo
    (RF-10). Las demás exclusiones de RF-9 corresponden a tareas posteriores.
    """
    archivos = []
    omitidas = []
    encontradas = 0
    recorridas = 0
    pendientes = [Path(raiz)]

    while pendientes:
        with os.scandir(pendientes.pop()) as entradas:
            for entrada in entradas:
                ruta = Path(entrada.path)
                # El enlace se comprueba primero: su destino no se consulta.
                if entrada.is_symlink():
                    omitidas.append(EntradaOmitida(ruta, "enlace", ""))
                elif entrada.is_dir(follow_symlinks=False):
                    encontradas += 1
                    if recursivo:
                        pendientes.append(ruta)
                        recorridas += 1
                else:
                    tamano = entrada.stat(follow_symlinks=False).st_size
                    archivos.append(ArchivoAnalizado(ruta, clasificar(entrada.name), tamano))

    return ResultadoRecorrido(tuple(archivos), tuple(omitidas), encontradas, recorridas)
