"""T1: la aplicación instalada arranca por sus dos vías y muestra su ayuda."""

import subprocess
import sys
import sysconfig
from pathlib import Path


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


def test_orden_instalada_muestra_ayuda(tmp_path):
    nombre = "filepilot.exe" if sys.platform == "win32" else "filepilot"
    orden = Path(sysconfig.get_path("scripts")) / nombre
    assert orden.is_file(), f"Falta el ejecutable del entorno bajo prueba: {orden}"

    resultado = ejecutar([orden, "--help"], tmp_path)

    assert resultado.returncode == 0
    assert "filepilot" in resultado.stdout


def test_aplicacion_sin_dependencias_de_ejecucion():
    """Las de pytest son de desarrollo: van marcadas con un extra (RNF-1)."""
    from importlib import metadata

    declaradas = metadata.requires("filepilot") or []
    de_ejecucion = [linea for linea in declaradas if "extra ==" not in linea]

    assert de_ejecucion == []
