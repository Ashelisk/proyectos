"""T7: atributo de oculto de Windows y consulta fallida (RF-15, RF-9, RF-13).

La comprobación con el atributo real solo puede ejecutarse en Windows y se marca
como omitida en las demás plataformas. El tratamiento de una consulta fallida se
verifica en cualquier sistema forzando la marca de plataforma del módulo, porque
depende del código y no del sistema de archivos.
"""

import errno
import stat
import sys
from pathlib import Path

import pytest

from dobles import EntradaSimulada, anadir_entradas
from filepilot import recorrido
from filepilot.recorrido import ERROR_LECTURA, OCULTO, SIN_PERMISO, recorrer

ES_WINDOWS = sys.platform == "win32"
MOTIVO_NO_WINDOWS = "el atributo de oculto solo existe en Windows"


@pytest.fixture
def raiz(tmp_path):
    """Raíz con un archivo visible; las pruebas añaden lo que necesitan."""
    raiz = tmp_path / "raiz"
    raiz.mkdir()
    (raiz / "nota.txt").write_text("unas notas", encoding="utf-8")
    return raiz


def marcar_como_oculto(ruta: Path) -> None:
    """Activa el atributo de oculto; omite la prueba si el sistema lo rechaza."""
    import ctypes

    if not ctypes.windll.kernel32.SetFileAttributesW(str(ruta), stat.FILE_ATTRIBUTE_HIDDEN):
        pytest.skip(f"el entorno no permite marcar «{ruta}» como oculto")


@pytest.mark.skipif(not ES_WINDOWS, reason=MOTIVO_NO_WINDOWS)
def test_el_atributo_oculta_un_archivo_sin_punto_inicial(raiz):
    """RF-15: en Windows el atributo basta para excluir el archivo."""
    marcado = raiz / "privado.txt"
    marcado.write_text("con atributo", encoding="utf-8")
    marcar_como_oculto(marcado)

    resultado = recorrer(raiz)

    assert [omitida.motivo for omitida in resultado.omitidas] == [OCULTO]
    assert Path(resultado.omitidas[0].ruta).name == "privado.txt"
    assert {Path(archivo.ruta).name for archivo in resultado.archivos} == {"nota.txt"}


@pytest.mark.skipif(not ES_WINDOWS, reason=MOTIVO_NO_WINDOWS)
def test_incluir_ocultos_examina_el_archivo_con_atributo(raiz):
    """RF-14: la opción también levanta la exclusión por atributo."""
    marcado = raiz / "privado.txt"
    marcado.write_text("con atributo", encoding="utf-8")
    marcar_como_oculto(marcado)

    resultado = recorrer(raiz, incluir_ocultos=True)

    assert not resultado.omitidas
    assert {Path(archivo.ruta).name for archivo in resultado.archivos} == {
        "nota.txt",
        "privado.txt",
    }


@pytest.mark.skipif(not ES_WINDOWS, reason=MOTIVO_NO_WINDOWS)
def test_la_carpeta_con_atributo_no_se_enumera(raiz):
    """RF-14: una carpeta oculta por atributo se cuenta y no se recorre."""
    carpeta = raiz / "reservada"
    carpeta.mkdir()
    (carpeta / "foto.jpg").write_text("píxeles", encoding="utf-8")
    marcar_como_oculto(carpeta)

    resultado = recorrer(raiz, recursivo=True)

    assert [omitida.motivo for omitida in resultado.omitidas] == [OCULTO]
    assert "foto.jpg" not in {Path(archivo.ruta).name for archivo in resultado.archivos}
    assert resultado.subcarpetas_encontradas == 1
    assert resultado.subcarpetas_recorridas == 0


@pytest.mark.parametrize(
    "fallo, motivo",
    [
        (PermissionError(errno.EACCES, "Permission denied"), SIN_PERMISO),
        (OSError(errno.EIO, "Input/output error"), ERROR_LECTURA),
    ],
    ids=["sin_permiso", "error_lectura"],
)
def test_la_consulta_fallida_no_da_el_elemento_por_visible(monkeypatch, raiz, fallo, motivo):
    """RF-15: sin poder consultar el atributo, la entrada se omite con su causa."""
    monkeypatch.setattr(recorrido, "ES_WINDOWS", True)
    anadir_entradas(monkeypatch, raiz, [EntradaSimulada(raiz / "dudoso.txt", fallo=fallo)])

    resultado = recorrer(raiz)
    omitida = next(o for o in resultado.omitidas if Path(o.ruta).name == "dudoso.txt")

    assert omitida.motivo == motivo
    assert omitida.detalle
    assert "dudoso.txt" not in {Path(archivo.ruta).name for archivo in resultado.archivos}


def test_los_metadatos_sin_el_atributo_se_omiten_por_error_de_lectura(monkeypatch, raiz):
    """RF-15: un atributo ausente en Windows tampoco significa visible."""
    monkeypatch.setattr(recorrido, "ES_WINDOWS", True)
    anadir_entradas(monkeypatch, raiz, [EntradaSimulada(raiz / "dudoso.txt", atributos=None)])

    resultado = recorrer(raiz)
    omitida = next(o for o in resultado.omitidas if Path(o.ruta).name == "dudoso.txt")

    assert omitida.motivo == ERROR_LECTURA
    assert "atributo" in omitida.detalle


def test_fuera_de_windows_el_atributo_no_se_consulta(monkeypatch, raiz):
    """RF-15: donde el atributo no es aplicable, su ausencia no cambia nada."""
    monkeypatch.setattr(recorrido, "ES_WINDOWS", False)
    anadir_entradas(
        monkeypatch, raiz, [EntradaSimulada(raiz / "informe.pdf", atributos=None, tamano=7)]
    )

    resultado = recorrer(raiz)
    tamanos = {Path(archivo.ruta).name: archivo.tamano for archivo in resultado.archivos}

    assert not resultado.omitidas
    assert tamanos["informe.pdf"] == 7
