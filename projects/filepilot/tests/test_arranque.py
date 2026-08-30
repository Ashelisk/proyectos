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


def rutas_de_la_orden():
    """Rutas donde el intérprete en uso instala sus ejecutables, sin mirar el PATH.

    En un entorno aislado solo vale el ejecutable de ese entorno: aceptar otro
    ocultaría una instalación incompleta. Fuera de él se admite además el
    esquema de usuario, donde `pip install --user` deja la orden.
    """
    nombre = "filepilot.exe" if sys.platform == "win32" else "filepilot"
    del_interprete = Path(sysconfig.get_path("scripts")) / nombre
    if sys.prefix != sys.base_prefix:
        return [del_interprete]
    esquema_de_usuario = sysconfig.get_preferred_scheme("user")
    return [del_interprete, Path(sysconfig.get_path("scripts", esquema_de_usuario)) / nombre]


def test_orden_instalada_muestra_ayuda(tmp_path):
    candidatas = rutas_de_la_orden()
    instaladas = [ruta for ruta in candidatas if ruta.is_file()]
    assert instaladas, f"Falta el ejecutable del entorno bajo prueba: {candidatas}"
    orden = instaladas[0]

    resultado = ejecutar([orden, "--help"], tmp_path)

    assert resultado.returncode == 0
    assert "filepilot" in resultado.stdout


def test_aplicacion_sin_dependencias_de_ejecucion():
    """Las de pytest son de desarrollo: van marcadas con un extra (RNF-1)."""
    from importlib import metadata

    declaradas = metadata.requires("filepilot") or []
    de_ejecucion = [linea for linea in declaradas if "extra ==" not in linea]

    assert de_ejecucion == []
