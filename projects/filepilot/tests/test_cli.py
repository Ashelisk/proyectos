"""T2: contrato de invocación y código uno del uso incorrecto (RF-2, RF-3)."""

import subprocess
import sys

import pytest

from filepilot.cli import crear_analizador


def ejecutar(argumentos, directorio):
    """Invoca la aplicación como módulo desde un directorio ajeno al proyecto."""
    return subprocess.run(
        [sys.executable, "-m", "filepilot", *argumentos],
        cwd=directorio,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


@pytest.mark.parametrize(
    "argumentos",
    [
        pytest.param([], id="sin_subcomando"),
        pytest.param(["analizar"], id="sin_ruta"),
        pytest.param(["analizar", ".", "--inexistente"], id="opcion_desconocida"),
        pytest.param(["ordenar", "."], id="subcomando_desconocido"),
    ],
)
def test_uso_incorrecto_termina_en_uno(argumentos, tmp_path):
    resultado = ejecutar(argumentos, tmp_path)

    assert resultado.returncode == 1, f"código inesperado con {argumentos}"
    assert "usage" in resultado.stderr or "uso" in resultado.stderr
    assert resultado.stdout == ""


@pytest.mark.parametrize("argumentos", [["--help"], ["analizar", "--help"]])
def test_ayuda_termina_en_cero(argumentos, tmp_path):
    resultado = ejecutar(argumentos, tmp_path)

    assert resultado.returncode == 0
    assert "analizar" in resultado.stdout


def test_opciones_del_subcomando():
    """La ruta es obligatoria y las dos opciones están declaradas (RF-3, RF-14)."""
    opciones = crear_analizador().parse_args(["analizar", "carpeta"])

    assert opciones.ruta == "carpeta"
    assert opciones.recursivo is False
    assert opciones.incluir_ocultos is False

    completas = crear_analizador().parse_args(
        ["analizar", "carpeta", "--recursivo", "--incluir-ocultos"]
    )

    assert completas.recursivo is True
    assert completas.incluir_ocultos is True
