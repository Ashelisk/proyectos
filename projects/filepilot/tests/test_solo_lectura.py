"""T11: el análisis no modifica el árbol ni abre el contenido (RF-10)."""

import os
from pathlib import Path

import pytest

from filepilot.clasificacion import Categoria
from filepilot.cli import main

ARCHIVOS = {
    "foto.jpg": "píxeles",
    "nota.txt": "unas notas",
    "musica.mp3": "sonido",
    "copia.tar.gz": "comprimido",
    "registro.log": "desconocida",
    "LEEME": "sin extensión",
    ".secreto.txt": "oculto",
    "sub/video.mp4": "escena",
    "sub/.privada/interior.txt": "oculto dentro",
}

MODOS = [
    pytest.param([], id="primer_nivel"),
    pytest.param(["--recursivo"], id="recursivo"),
    pytest.param(["--recursivo", "--incluir-ocultos"], id="recursivo_con_ocultos"),
]


@pytest.fixture
def raiz(tmp_path):
    """Árbol variado dentro de la carpeta temporal de la prueba."""
    raiz = tmp_path / "raiz"
    for relativa, texto in ARCHIVOS.items():
        destino = raiz / relativa
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text(texto, encoding="utf-8")
    return raiz


def instantanea(raiz: Path) -> dict:
    """Rutas, tamaños y fechas de modificación de todo el árbol."""
    registro = {}
    for carpeta, subcarpetas, archivos in os.walk(raiz):
        for nombre in list(subcarpetas) + list(archivos):
            ruta = Path(carpeta) / nombre
            datos = ruta.lstat()
            registro[str(ruta)] = (datos.st_size, datos.st_mtime_ns)
    return registro


def dentro_del_arbol(eventos, raiz: Path) -> list:
    """Eventos cuyo primer argumento apunta a algo del árbol analizado."""
    base = os.path.normcase(str(raiz))
    return [
        anotado
        for anotado in eventos
        if os.path.normcase(os.path.abspath(anotado[1][0])).startswith(base)
    ]


@pytest.mark.parametrize("opciones", MODOS)
def test_el_arbol_queda_intacto(capsys, raiz, opciones):
    """RF-10: rutas, tamaños y fechas coinciden antes y después del análisis."""
    antes = instantanea(raiz)

    codigo = main(["analizar", str(raiz), *opciones])

    capsys.readouterr()
    assert codigo == 0
    assert instantanea(raiz) == antes


def test_no_se_crean_las_carpetas_propuestas(capsys, raiz):
    """RF-10: el destino se propone en el informe, no se crea en el disco."""
    main(["analizar", str(raiz), "--recursivo"])

    salida = capsys.readouterr()
    for categoria in Categoria:
        assert categoria.carpeta in salida.out
        assert not (raiz / categoria.carpeta).exists()


def test_el_analisis_no_abre_el_contenido_de_los_archivos(analizar_vigilado, raiz):
    """RF-10: en un proceso aislado, ningún archivo del árbol se abre.

    La vigilancia solo cubre la llamada al análisis: la creación del árbol y la
    escritura del registro quedan fuera.
    """
    resultado, eventos = analizar_vigilado(
        ["analizar", str(raiz), "--recursivo", "--incluir-ocultos"], ["open"]
    )

    assert resultado.returncode == 0, resultado.stderr
    assert "Imágenes" in resultado.stdout
    assert eventos is not None
    assert dentro_del_arbol(eventos, raiz) == []
