"""Formas comunes de invocar la aplicación desde las pruebas.

Una sola definición evita que la política de codificación de la captura difiera
entre archivos de prueba.
"""

import os
import subprocess
import sys

import pytest


def _ejecutar(orden, directorio):
    """Ejecuta `orden` desde `directorio`, ajeno al proyecto.

    Fija UTF-8 en la escritura del subproceso y en su lectura, de modo que la
    captura no dependa de la codificación del entorno de pruebas.
    """
    return subprocess.run(
        orden,
        cwd=directorio,
        capture_output=True,
        env={**os.environ, "PYTHONIOENCODING": "utf-8"},
        encoding="utf-8",
    )


@pytest.fixture
def ejecutar_orden():
    """Ejecuta una orden completa, como el ejecutable instalado."""
    return _ejecutar


@pytest.fixture
def ejecutar_modulo():
    """Invoca la aplicación como módulo con los argumentos indicados."""

    def invocar(argumentos, directorio):
        return _ejecutar([sys.executable, "-m", "filepilot", *argumentos], directorio)

    return invocar
