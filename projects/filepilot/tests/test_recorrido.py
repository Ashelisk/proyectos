"""T5: recorrido de primer nivel y recursivo con recuentos (RF-3, RF-4).

Las pruebas observan el resultado del recorrido sobre árboles temporales, sin
depender del orden en que el sistema enumere las entradas. Las exclusiones de
RF-9, RF-14 y RF-15 pertenecen a tareas posteriores: los árboles no contienen
elementos ocultos, de modo que aquí ninguna entrada debe omitirse.
"""

import os
from pathlib import Path

import pytest

from filepilot.clasificacion import Categoria
from filepilot.recorrido import (
    ArchivoAnalizado,
    EntradaOmitida,
    ResultadoRecorrido,
    recorrer,
)

# Árbol de tres niveles: contenido de cada archivo y categoría esperada.
ARBOL = {
    "nota.txt": ("unas notas", Categoria.DOCUMENTOS),
    "foto.JPG": ("píxeles", Categoria.IMAGENES),  # mayúsculas y bytes no ASCII
    "LEEME": ("sin extensión", Categoria.SIN_EXTENSION),
    "sub/musica.mp3": ("sonido", Categoria.AUDIO),
    "sub/profunda/video.mp4": ("escena", Categoria.VIDEO),
}

CARPETAS = ("sub", "sub/profunda", "otra")  # «otra» queda vacía a propósito

PRIMER_NIVEL = {"nota.txt", "foto.JPG", "LEEME"}
DESCENDIENTES = {"sub/musica.mp3", "sub/profunda/video.mp4"}


@pytest.fixture
def arbol(tmp_path):
    """Crea el árbol de la prueba dentro de su carpeta temporal."""
    raiz = tmp_path / "raiz"
    for carpeta in CARPETAS:
        (raiz / carpeta).mkdir(parents=True)
    for relativa, (texto, _) in ARBOL.items():
        (raiz / relativa).write_text(texto, encoding="utf-8")
    return raiz


def rutas(resultado) -> set:
    """Rutas de los archivos analizados, sin suponer un orden de enumeración."""
    return {Path(archivo.ruta) for archivo in resultado.archivos}


def nombres(resultado) -> set:
    return {Path(archivo.ruta).name for archivo in resultado.archivos}


def esperadas(raiz: Path, relativas) -> set:
    return {raiz / relativa for relativa in relativas}


def crear_enlace(enlace: Path, destino: Path) -> Path:
    """Crea un enlace simbólico; omite la prueba si el entorno no lo permite."""
    try:
        enlace.symlink_to(destino, target_is_directory=destino.is_dir())
    except (OSError, NotImplementedError) as fallo:
        pytest.skip(f"el entorno no permite crear enlaces simbólicos: {fallo}")
    return enlace


def test_por_defecto_solo_el_primer_nivel(arbol):
    """RF-3: sin modo recursivo no se examina el contenido de las subcarpetas."""
    resultado = recorrer(arbol)

    assert rutas(resultado) == esperadas(arbol, PRIMER_NIVEL)
    assert not resultado.omitidas


def test_modo_recursivo_alcanza_los_descendientes(arbol):
    """RF-3: con `recursivo` se examinan todos los niveles inferiores."""
    resultado = recorrer(arbol, recursivo=True)

    assert rutas(resultado) == esperadas(arbol, PRIMER_NIVEL | DESCENDIENTES)
    assert not resultado.omitidas


@pytest.mark.parametrize(
    "recursivo, encontradas, recorridas",
    [(False, 2, 0), (True, 3, 3)],
    ids=["primer_nivel", "recursivo"],
)
def test_recuento_de_subcarpetas(arbol, recursivo, encontradas, recorridas):
    """RF-4: las subcarpetas se cuentan; la raíz no entra en el recuento.

    Sin recursión se encuentran las dos del primer nivel y no se recorre
    ninguna; con recursión se añade la anidada y todas quedan recorridas,
    incluida la que está vacía.
    """
    resultado = recorrer(arbol, recursivo=recursivo)

    assert resultado.subcarpetas_encontradas == encontradas
    assert resultado.subcarpetas_recorridas == recorridas


@pytest.mark.parametrize("recursivo", [False, True], ids=["primer_nivel", "recursivo"])
def test_las_subcarpetas_no_se_clasifican_como_archivos(arbol, recursivo):
    """RF-4: una carpeta solo aparece en los recuentos, nunca como archivo."""
    resultado = recorrer(arbol, recursivo=recursivo)

    assert nombres(resultado).isdisjoint({"sub", "profunda", "otra"})
    assert all(not Path(archivo.ruta).is_dir() for archivo in resultado.archivos)


def test_categoria_y_tamano_de_cada_archivo(arbol):
    """Categoría de RF-5 y RF-6 y tamaño real en bytes de cada archivo."""
    resultado = recorrer(arbol, recursivo=True)

    obtenido = {
        Path(archivo.ruta).relative_to(arbol).as_posix(): (archivo.categoria, archivo.tamano)
        for archivo in resultado.archivos
    }
    assert obtenido == {
        relativa: (categoria, len(texto.encode("utf-8")))
        for relativa, (texto, categoria) in ARBOL.items()
    }


@pytest.mark.parametrize("recursivo", [False, True], ids=["primer_nivel", "recursivo"])
def test_carpeta_vacia(tmp_path, recursivo):
    """Sin contenido no hay archivos, ni omitidas, ni subcarpetas."""
    vacia = tmp_path / "vacia"
    vacia.mkdir()

    resultado = recorrer(vacia, recursivo=recursivo)

    assert not resultado.archivos
    assert not resultado.omitidas
    assert resultado.subcarpetas_encontradas == 0
    assert resultado.subcarpetas_recorridas == 0


def test_solo_subcarpetas_sin_recursion(arbol):
    """Caso límite de la spec: carpetas presentes y ningún archivo examinado."""
    solo_carpetas = arbol / "otra"
    (solo_carpetas / "interior").mkdir()

    resultado = recorrer(solo_carpetas)

    assert not resultado.archivos
    assert resultado.subcarpetas_encontradas == 1
    assert resultado.subcarpetas_recorridas == 0


def test_arbol_de_muchos_niveles(tmp_path):
    """Un árbol profundo se recorre completo y sus recuentos se conservan.

    La profundidad se mantiene moderada para no superar el límite de longitud
    de ruta de Windows.
    """
    niveles = 30
    raiz = tmp_path / "profundo"
    actual = raiz
    for numero in range(niveles):
        actual = actual / f"n{numero}"
    actual.mkdir(parents=True)
    (actual / "fondo.txt").write_text("final", encoding="utf-8")

    resultado = recorrer(raiz, recursivo=True)

    assert rutas(resultado) == {actual / "fondo.txt"}
    assert resultado.subcarpetas_encontradas == niveles
    assert resultado.subcarpetas_recorridas == niveles


def test_tipos_y_colecciones_inmutables(arbol):
    """El resultado es de solo lectura una vez creado."""
    resultado = recorrer(arbol)

    assert isinstance(resultado, ResultadoRecorrido)
    assert all(isinstance(archivo, ArchivoAnalizado) for archivo in resultado.archivos)
    for coleccion in (resultado.archivos, resultado.omitidas):
        assert not hasattr(coleccion, "append")
    with pytest.raises(AttributeError):
        resultado.subcarpetas_encontradas = 99
    with pytest.raises(AttributeError):
        resultado.archivos[0].tamano = 0


def test_la_entrada_omitida_conserva_sus_datos():
    """Contrato de `EntradaOmitida`; sus motivos se aplican en T6 y T10."""
    omitida = EntradaOmitida(Path("carpeta") / "x", "error_lectura", "no se pudo leer")

    assert Path(omitida.ruta).name == "x"
    assert omitida.motivo == "error_lectura"
    assert omitida.detalle == "no se pudo leer"
    with pytest.raises(AttributeError):
        omitida.motivo = "oculto"


def preparar_destino_externo(tmp_path):
    """Carpeta con contenido fuera de la raíz analizada, más la raíz."""
    externa = tmp_path / "externa"
    externa.mkdir()
    (externa / "secreto.txt").write_text("fuera del alcance", encoding="utf-8")
    raiz = tmp_path / "raiz"
    raiz.mkdir()
    (raiz / "nota.txt").write_text("dentro", encoding="utf-8")
    return raiz, externa


def comprobar_que_no_se_siguio(resultado, externa):
    """El destino del enlace no se enumera ni se cuenta como recorrido."""
    assert "nota.txt" in nombres(resultado)
    assert "secreto.txt" not in nombres(resultado)
    assert all(externa not in Path(archivo.ruta).parents for archivo in resultado.archivos)
    assert resultado.subcarpetas_recorridas == 0


def test_no_sigue_los_enlaces_simbolicos(tmp_path):
    """Un enlace a un directorio no amplía el alcance del recorrido."""
    raiz, externa = preparar_destino_externo(tmp_path)
    crear_enlace(raiz / "atajo", externa)

    comprobar_que_no_se_siguio(recorrer(raiz, recursivo=True), externa)


class EntradaEnlace:
    """Entrada de enumeración que imita un enlace simbólico a un directorio."""

    def __init__(self, ruta: Path, destino: Path):
        self.name = ruta.name
        self.path = str(ruta)
        self._destino = destino

    def is_dir(self, *, follow_symlinks=True):
        return follow_symlinks  # sin seguir el enlace, la entrada no es carpeta

    def is_file(self, *, follow_symlinks=True):
        return False

    def is_symlink(self):
        return True

    def stat(self, *, follow_symlinks=True):
        return os.stat(self._destino)


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


def clave(ruta) -> str:
    """Forma comparable de una ruta, indicada como texto o como `Path`."""
    return os.path.normcase(os.path.abspath(os.fspath(ruta)))


def test_no_sigue_un_enlace_simulado(monkeypatch, tmp_path):
    """Misma protección sin depender del privilegio de crear enlaces.

    La enumeración de la raíz añade una entrada que se comporta como un enlace
    a un directorio y, si el recorrido la sigue, entrega el contenido real del
    destino. Complementa a la prueba anterior, que se omite en los entornos sin
    ese privilegio; no sustituye la comprobación con un enlace real.
    """
    raiz, externa = preparar_destino_externo(tmp_path)
    enlace = raiz / "atajo"
    enumerar = os.scandir

    def enumerar_con_enlace(ruta="."):
        seguido = clave(ruta) == clave(enlace)
        with enumerar(externa if seguido else ruta) as entradas:
            contenido = list(entradas)
        if clave(ruta) == clave(raiz):
            contenido.append(EntradaEnlace(enlace, externa))
        return Enumeracion(contenido)

    monkeypatch.setattr(os, "scandir", enumerar_con_enlace)

    comprobar_que_no_se_siguio(recorrer(raiz, recursivo=True), externa)
