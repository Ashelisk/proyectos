"""Formas comunes de invocar la aplicación desde las pruebas.

Una sola definición evita que la política de codificación de la captura difiera
entre archivos de prueba.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

# Guion auxiliar: analiza en un proceso propio y anota los eventos de auditoría
# ocurridos durante el análisis, sin incluir la preparación ni el cierre.
GUION_VIGILANCIA = '''\
"""Ejecuta un análisis vigilando los eventos de auditoría indicados."""

import json
import sys

from filepilot.cli import main

vigilados = tuple(sys.argv[1].split(","))
destino = sys.argv[2]
registro = []
activo = False


def anotar(evento, argumentos):
    if activo and evento.startswith(vigilados):
        registro.append([evento, [str(dato) for dato in argumentos]])


sys.addaudithook(anotar)
activo = True
try:
    codigo = main(sys.argv[3:])
finally:
    # La vigilancia se cierra antes de escribir para no anotar esta escritura.
    activo = False
    with open(destino, "w", encoding="utf-8") as archivo:
        json.dump(registro, archivo)

sys.exit(codigo)
'''


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


@pytest.fixture
def crear_enlace():
    """Crea un enlace simbólico real; omite la prueba si el entorno no lo permite."""

    def crear(enlace, destino):
        try:
            Path(enlace).symlink_to(destino, target_is_directory=Path(destino).is_dir())
        except (OSError, NotImplementedError) as fallo:
            pytest.skip(f"el entorno no permite crear enlaces simbólicos: {fallo}")
        return Path(enlace)

    return crear


@pytest.fixture
def analizar_vigilado(tmp_path):
    """Analiza en un proceso aislado y devuelve su resultado y los eventos.

    `eventos` son prefijos de nombres de eventos de auditoría, como `open` o
    `socket`. El registro solo abarca la llamada al análisis, de modo que la
    preparación de los datos de prueba no aparece en él (RF-10, RNF-1).
    """

    def ejecutar(argumentos, eventos, directorio=None):
        guion = tmp_path / "vigilancia.py"
        guion.write_text(GUION_VIGILANCIA, encoding="utf-8")
        registro = tmp_path / "eventos.json"
        resultado = _ejecutar(
            [sys.executable, str(guion), ",".join(eventos), str(registro), *argumentos],
            directorio or tmp_path,
        )
        anotados = json.loads(registro.read_text(encoding="utf-8")) if registro.exists() else None
        return resultado, anotados

    return ejecutar
