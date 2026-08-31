"""T12: rutas relativas y absolutas y nombres no ASCII (RNF-2).

Las pruebas se ejecutan en cualquier plataforma; la evidencia de validación
indica con qué combinaciones de sistema y versión se han ejecutado realmente.
"""

import os
from pathlib import Path
import subprocess
import sys
import sysconfig

import pytest

from filepilot.cli import main

TEXTO = "contenido de prueba"

NO_ASCII = {
    "cañón.jpg": "Imágenes",
    "Ελλάδα.png": "Imágenes",
    "документ.pdf": "Documentos",
    "日本語.txt": "Documentos",
    "música española.mp3": "Audio",
}

ASCII = ("foto.jpg", "nota.txt", "musica.mp3")


def crear(raiz, nombres):
    """Crea los archivos indicados; omite la prueba si el sistema los rechaza."""
    raiz.mkdir(parents=True, exist_ok=True)
    for nombre in nombres:
        try:
            (raiz / nombre).write_text(TEXTO, encoding="utf-8")
        except (OSError, UnicodeError) as fallo:
            pytest.skip(f"el sistema de archivos no admite el nombre «{nombre}»: {fallo}")
    return raiz


def fila(informe: str, encabezado: str) -> str:
    return next(linea for linea in informe.splitlines() if linea.startswith(encabezado))


def test_la_ruta_relativa_y_la_absoluta_dan_el_mismo_informe(ejecutar_modulo, tmp_path):
    """RNF-2: ambas formas designan la misma carpeta ya resuelta."""
    raiz = crear(tmp_path / "carpeta", ASCII)

    relativa = ejecutar_modulo(["analizar", "carpeta"], tmp_path)
    absoluta = ejecutar_modulo(["analizar", str(raiz)], tmp_path)

    assert relativa.returncode == 0, relativa.stderr
    assert absoluta.returncode == 0, absoluta.stderr
    assert relativa.stdout == absoluta.stdout
    assert str(raiz) in relativa.stdout


def test_los_nombres_no_ascii_se_clasifican(capsys, tmp_path):
    """RNF-2: acentos y otros alfabetos no impiden clasificar ni contar."""
    raiz = crear(tmp_path / "raiz", NO_ASCII)

    codigo = main(["analizar", str(raiz)])

    salida = capsys.readouterr()
    assert codigo == 0
    assert "2" in fila(salida.out, "Imágenes").split()
    assert "2" in fila(salida.out, "Documentos").split()
    assert "1" in fila(salida.out, "Audio").split()
    assert "5" in fila(salida.out, "Total").split()


def test_la_raiz_con_nombre_no_ascii_se_analiza(ejecutar_modulo, tmp_path):
    """RNF-2: el nombre de la carpeta también admite caracteres no ASCII."""
    nombre = "análisis ñandú"
    raiz = crear(tmp_path / nombre, NO_ASCII)

    resultado = ejecutar_modulo(["analizar", nombre], tmp_path)

    assert resultado.returncode == 0, resultado.stderr
    assert str(raiz) in resultado.stdout
    assert "Imágenes" in resultado.stdout


def test_las_subcarpetas_no_ascii_se_recorren(ejecutar_modulo, tmp_path):
    """RNF-2: el modo recursivo alcanza descendientes con nombres acentuados."""
    raiz = tmp_path / "raiz"
    crear(raiz / "año 2024" / "informes ñ", ("memoria.pdf",))

    resultado = ejecutar_modulo(["analizar", str(raiz), "--recursivo"], tmp_path)

    assert resultado.returncode == 0, resultado.stderr
    assert "1" in fila(resultado.stdout, "Documentos").split()
    assert "Subcarpetas: 2 encontradas, 2 recorridas" in resultado.stdout


@pytest.mark.parametrize("entrada", ["modulo", "ejecutable"])
@pytest.mark.parametrize("codificacion", ["utf-8", "cp1252", "ascii"])
@pytest.mark.parametrize("opciones", [[], ["--recursivo"], ["--incluir-ocultos"],
                                     ["--recursivo", "--incluir-ocultos"]])
def test_informe_con_salida_redirigida_y_raiz_unicode(
    tmp_path, entrada, codificacion, opciones
):
    """V-10: la salida respeta su codificación y conserva los caracteres como escapes."""
    raiz = crear(tmp_path / "carpeta-á-Ж-資料", ("documento.pdf",))
    if entrada == "modulo":
        orden = [sys.executable, "-m", "filepilot"]
    else:
        nombre = "filepilot.exe" if sys.platform == "win32" else "filepilot"
        orden = [str(Path(sysconfig.get_path("scripts")) / nombre)]
    proceso = subprocess.run(
        [*orden, "analizar", str(raiz), *opciones], cwd=tmp_path, capture_output=True,
        env={**os.environ, "PYTHONIOENCODING": codificacion}, timeout=30,
    )

    assert proceso.returncode == 0, proceso.stderr
    assert proceso.stderr == b""
    texto = proceso.stdout.decode(codificacion)
    ruta_esperada = str(raiz).encode(codificacion, "backslashreplace").decode(codificacion)
    assert ruta_esperada in texto
    assert "Documentos" in texto
    assert "1" in fila(texto, "Total").split()
