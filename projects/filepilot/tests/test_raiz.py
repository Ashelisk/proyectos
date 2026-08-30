"""T3: resolución y validación de la raíz indicada (RF-11, RF-14, RF-16)."""

import errno
import os
import subprocess
import sys
from pathlib import Path

import pytest

from filepilot.cli import CODIGO_RUTA_INVALIDA, RutaInvalida, main, resolver_raiz


def crear_enlace(enlace: Path, destino: Path) -> Path:
    """Crea un enlace simbólico; omite la prueba si el entorno no lo permite."""
    try:
        enlace.symlink_to(destino, target_is_directory=destino.is_dir())
    except (OSError, NotImplementedError) as fallo:
        pytest.skip(f"el entorno no permite crear enlaces simbólicos: {fallo}")
    return enlace


# Las tres causas de RF-11 y un fallo de lectura ajeno a ellas.
FALLOS_AL_CONSULTAR = [
    pytest.param(FileNotFoundError(errno.ENOENT, "No such file"), "no existe", id="inexistente"),
    pytest.param(
        NotADirectoryError(errno.ENOTDIR, "Not a directory"),
        "no es un directorio",
        id="componente_intermedio",
    ),
    pytest.param(
        PermissionError(errno.EACCES, "Permission denied"), "permiso denegado", id="sin_permiso"
    ),
    pytest.param(OSError(errno.EIO, "Input/output error"), "error de entrada y salida", id="fallo"),
    pytest.param(
        OSError(errno.ELOOP, "Too many levels of symbolic links"),
        "demasiados enlaces simbólicos",
        id="bucle_de_enlaces",
    ),
]


@pytest.mark.parametrize("fallo, causa", FALLOS_AL_CONSULTAR)
def test_consulta_fallida_de_la_raiz(monkeypatch, tmp_path, fallo, causa):
    """Cada fallo produce su causa en español, sin copiar el texto del sistema."""

    def consultar(self, *argumentos, **opciones):
        raise fallo

    monkeypatch.setattr(Path, "stat", consultar)

    with pytest.raises(RutaInvalida) as problema:
        resolver_raiz(str(tmp_path))

    mensaje = str(problema.value)
    assert causa in mensaje
    assert str(tmp_path) in mensaje
    assert fallo.strerror not in mensaje


def test_carpeta_ilegible_conserva_la_causa(monkeypatch, tmp_path):
    """La raíz existe y es un directorio, pero no puede enumerarse."""

    def enumerar(ruta):
        raise PermissionError(errno.EACCES, "Permission denied", str(ruta))

    monkeypatch.setattr(os, "scandir", enumerar)

    with pytest.raises(RutaInvalida) as problema:
        resolver_raiz(str(tmp_path))

    mensaje = str(problema.value)
    assert "permiso denegado" in mensaje
    assert str(tmp_path) in mensaje


def test_bucle_de_enlaces_al_resolver_termina_en_dos(monkeypatch, capsys, tmp_path):
    """Antes de Python 3.13, `resolve` señala el bucle con `RuntimeError`.

    Ese error no deriva de `OSError`: sin tratarlo, la ejecución terminaría con
    un rastro de excepción en lugar del código dos de RF-11.
    """

    def resolver(self, strict=False):
        raise RuntimeError(f"Symlink loop from {str(self)!r}")

    monkeypatch.setattr(Path, "resolve", resolver)

    codigo = main(["analizar", str(tmp_path)])

    salida = capsys.readouterr()
    assert codigo == CODIGO_RUTA_INVALIDA
    assert "demasiados enlaces simbólicos" in salida.err
    assert str(tmp_path) in salida.err
    assert salida.out == ""


def test_ruta_vacia_termina_en_dos(capsys):
    """RF-11: una ruta vacía se rechaza; no equivale al directorio actual."""
    codigo = main(["analizar", ""])

    salida = capsys.readouterr()
    assert codigo == CODIGO_RUTA_INVALIDA
    assert "la ruta indicada está vacía" in salida.err
    assert salida.out == ""


def test_ruta_vacia_no_analiza_el_directorio_actual(tmp_path):
    with pytest.raises(RutaInvalida):
        resolver_raiz("")


def test_raiz_oculta_se_acepta(tmp_path):
    """RF-14: la raíz se analiza aunque esté oculta, sin `--incluir-ocultos`."""
    oculta = tmp_path / ".privada"
    oculta.mkdir()

    assert resolver_raiz(str(oculta)) == oculta.resolve()


def test_raiz_enlazada_devuelve_su_destino(tmp_path):
    """RF-16: la ruta se resuelve antes de comprobarla."""
    real = tmp_path / "real"
    real.mkdir()
    enlace = crear_enlace(tmp_path / "enlace", real)

    assert resolver_raiz(str(enlace)) == real.resolve()


@pytest.mark.skipif(sys.platform != "win32", reason="las uniones de directorio son de Windows")
def test_raiz_por_union_de_directorio(tmp_path):
    """Complemento para Windows sin privilegio de enlaces simbólicos.

    Una unión creada con `mklink /J` no es un enlace simbólico y no sustituye a
    la prueba de RF-16, pero ejercita la misma resolución de la raíz.
    """
    real = tmp_path / "real"
    real.mkdir()
    union = tmp_path / "union"
    creacion = subprocess.run(
        ["cmd", "/c", "mklink", "/J", str(union), str(real)], capture_output=True
    )
    if creacion.returncode != 0:
        pytest.skip("el entorno no permite crear uniones de directorio")

    assert resolver_raiz(str(union)) == real.resolve()


def test_enlace_roto_cita_su_destino(tmp_path):
    enlace = crear_enlace(tmp_path / "enlace", tmp_path / "ausente")

    with pytest.raises(RutaInvalida) as problema:
        resolver_raiz(str(enlace))

    mensaje = str(problema.value)
    assert "no existe" in mensaje
    assert "enlace a" in mensaje


def test_ruta_inexistente_termina_en_dos(ejecutar_modulo, tmp_path):
    resultado = ejecutar_modulo(["analizar", "carpeta-ausente"], tmp_path)

    assert resultado.returncode == CODIGO_RUTA_INVALIDA
    assert "no existe" in resultado.stderr
    assert "carpeta-ausente" in resultado.stderr
    assert resultado.stdout == ""


def test_archivo_como_raiz_termina_en_dos(ejecutar_modulo, tmp_path):
    (tmp_path / "notas.txt").write_text("contenido", encoding="utf-8")

    resultado = ejecutar_modulo(["analizar", "notas.txt"], tmp_path)

    assert resultado.returncode == CODIGO_RUTA_INVALIDA
    assert "no es un directorio" in resultado.stderr
    assert "notas.txt" in resultado.stderr
    assert resultado.stdout == ""


@pytest.mark.skipif(sys.platform == "win32", reason="chmod no restringe la lectura en Windows")
def test_carpeta_sin_permiso_termina_en_dos(ejecutar_modulo, tmp_path):
    if hasattr(os, "geteuid") and os.geteuid() == 0:
        pytest.skip("con privilegios administrativos la denegación no se reproduce")
    cerrada = tmp_path / "cerrada"
    cerrada.mkdir()
    cerrada.chmod(0o000)

    try:
        resultado = ejecutar_modulo(["analizar", str(cerrada)], tmp_path)
    finally:
        cerrada.chmod(0o700)

    assert resultado.returncode == CODIGO_RUTA_INVALIDA
    assert "permiso denegado" in resultado.stderr
    assert resultado.stdout == ""


@pytest.mark.parametrize("nombre", ["carpeta", ".privada"])
def test_raiz_valida_no_produce_error(ejecutar_modulo, tmp_path, nombre):
    """Ruta relativa, también oculta: se acepta sin mensajes (RF-14, RNF-2)."""
    (tmp_path / nombre).mkdir()

    resultado = ejecutar_modulo(["analizar", nombre], tmp_path)

    assert resultado.returncode == 0
    assert resultado.stderr == ""


def test_raiz_enlazada_se_analiza(ejecutar_modulo, tmp_path):
    real = tmp_path / "real"
    real.mkdir()
    crear_enlace(tmp_path / "enlace", real)

    resultado = ejecutar_modulo(["analizar", "enlace"], tmp_path)

    assert resultado.returncode == 0
    assert resultado.stderr == ""
