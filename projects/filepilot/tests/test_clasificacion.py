"""T4: clasificación de un nombre de archivo por extensión (RF-5, RF-6, RF-7).

Las expectativas se escriben aquí a partir de la spec, sin importar el mapa de
`clasificacion.py`: una prueba que reutilizara ese mapa no detectaría un cambio
de comportamiento. Ningún caso toca el disco.
"""

import pytest

from filepilot.clasificacion import Categoria, clasificar

# Mapa completo de RF-5, copiado de la especificación.
EXTENSIONES_POR_CATEGORIA = {
    Categoria.IMAGENES: ["jpg", "jpeg", "png", "gif", "bmp", "webp", "tiff", "svg", "heic"],
    Categoria.DOCUMENTOS: [
        "pdf", "doc", "docx", "odt", "rtf", "txt", "md",
        "xls", "xlsx", "ods", "csv", "ppt", "pptx", "odp", "epub",
    ],
    Categoria.VIDEO: ["mp4", "mkv", "avi", "mov", "wmv", "webm", "mpg", "mpeg"],
    Categoria.AUDIO: ["mp3", "wav", "flac", "aac", "ogg", "m4a", "wma"],
    Categoria.COMPRIMIDOS: ["zip", "rar", "7z", "tar", "gz", "bz2", "xz"],
}

CARPETAS_PROPUESTAS = {
    Categoria.IMAGENES: "imagenes",
    Categoria.DOCUMENTOS: "documentos",
    Categoria.VIDEO: "video",
    Categoria.AUDIO: "audio",
    Categoria.COMPRIMIDOS: "comprimidos",
    Categoria.OTROS: "otros",
    Categoria.SIN_EXTENSION: "sin-extension",
}

RECONOCIDAS = [
    pytest.param(extension, categoria, id=f"{categoria.name.lower()}-{extension}")
    for categoria, extensiones in EXTENSIONES_POR_CATEGORIA.items()
    for extension in extensiones
]


@pytest.mark.parametrize("extension, categoria", RECONOCIDAS)
def test_cada_extension_del_mapa(extension, categoria):
    """RF-5: toda extensión listada cae en su categoría."""
    assert clasificar(f"archivo.{extension}") is categoria


@pytest.mark.parametrize(
    "nombre, categoria",
    [
        ("FOTO.JPG", Categoria.IMAGENES),
        ("Informe.PdF", Categoria.DOCUMENTOS),
        ("PELICULA.Mp4", Categoria.VIDEO),
    ],
)
def test_mayusculas_no_distinguen(nombre, categoria):
    """RF-5: la extensión se compara sin distinguir mayúsculas."""
    assert clasificar(nombre) is categoria


@pytest.mark.parametrize(
    "nombre, categoria",
    [
        ("copia.tar.gz", Categoria.COMPRIMIDOS),
        ("informe.pdf.zip", Categoria.COMPRIMIDOS),
        ("respaldo.zip.pdf", Categoria.DOCUMENTOS),
        ("clip.mp4.desconocida", Categoria.OTROS),
    ],
)
def test_solo_cuenta_la_ultima_extension(nombre, categoria):
    """RF-5: con varios puntos decide la última extensión."""
    assert clasificar(nombre) is categoria


@pytest.mark.parametrize("nombre", ["programa.exe", "datos.xyz", "hoja.QQQ"])
def test_extension_desconocida_va_a_otros(nombre):
    """RF-5: una extensión fuera del mapa sitúa el archivo en «otros»."""
    assert clasificar(nombre) is Categoria.OTROS


@pytest.mark.parametrize("nombre", ["LEEME", "Makefile", "notas"])
def test_sin_extension_es_un_grupo_propio(nombre):
    """RF-6: los archivos sin extensión no se mezclan con «otros»."""
    assert clasificar(nombre) is Categoria.SIN_EXTENSION


def test_las_siete_carpetas_propuestas():
    """RF-7: destinos exactos, en minúscula y sin acentos.

    La comparación del conjunto completo también descarta categorías ajenas a
    RF-5 y RF-6.
    """
    assert {categoria: categoria.carpeta for categoria in Categoria} == CARPETAS_PROPUESTAS
