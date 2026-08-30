"""T1: la aplicación instalada arranca por sus dos vías y muestra su ayuda."""

import shutil
import subprocess
import sys
from pathlib import Path

import pytest


def ejecutar(orden, directorio):
    """Ejecuta la orden desde `directorio`, ajeno al proyecto."""
    return subprocess.run(
        orden,
        cwd=directorio,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def test_modulo_muestra_ayuda(tmp_path):
    resultado = ejecutar([sys.executable, "-m", "filepilot", "--help"], tmp_path)

    assert resultado.returncode == 0
    assert "filepilot" in resultado.stdout


def localizar_orden():
    """Busca `filepilot` junto al intérprete en uso y, si no, en el PATH."""
    junto_al_interprete = shutil.which("filepilot", path=str(Path(sys.executable).parent))
    return junto_al_interprete or shutil.which("filepilot")


def test_orden_instalada_muestra_ayuda(tmp_path):
    orden = localizar_orden()
    if orden is None:
        pytest.skip("la orden `filepilot` no está instalada en este entorno")

    resultado = ejecutar([orden, "--help"], tmp_path)

    assert resultado.returncode == 0
    assert "filepilot" in resultado.stdout


def test_aplicacion_sin_dependencias_de_ejecucion():
    """Las de pytest son de desarrollo: van marcadas con un extra (RNF-1)."""
    from importlib import metadata

    declaradas = metadata.requires("filepilot") or []
    de_ejecucion = [linea for linea in declaradas if "extra ==" not in linea]

    assert de_ejecucion == []
