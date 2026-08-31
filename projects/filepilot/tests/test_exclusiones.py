"""T6: exclusiones con motivo único y `--incluir-ocultos` (RF-9, RF-14, RF-15).

Los árboles se crean en la carpeta temporal de cada prueba. Los enlaces reales
se intentan y se omiten si el entorno no concede el privilegio; su equivalente
simulado comprueba la misma regla en cualquier plataforma, sin sustituir a la
comprobación con un enlace real.
"""

import errno
import stat
from collections import Counter
from pathlib import Path

import pytest

from dobles import EntradaSimulada, anadir_entradas, fallar_en
from filepilot import recorrido
from filepilot.cli import main
from filepilot.clasificacion import Categoria
from filepilot.recorrido import ENLACE, ERROR_LECTURA, MOTIVOS, OCULTO, SIN_PERMISO, recorrer

ARCHIVOS = {
    "nota.txt": "unas notas",
    "informe.pdf": "un informe",
    ".secreto.txt": "oculto por su nombre",
    ".sinextension": "oculto antes que sin extensión",
    "visible/dentro.mp3": "sonido",
    ".privada/foto.jpg": "píxeles",
}


@pytest.fixture
def raiz(tmp_path):
    """Raíz con archivos y carpetas visibles y ocultos."""
    raiz = tmp_path / "raiz"
    for relativa, texto in ARCHIVOS.items():
        destino = raiz / relativa
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text(texto, encoding="utf-8")
    return raiz


def nombres(resultado) -> set:
    return {Path(archivo.ruta).name for archivo in resultado.archivos}


def motivos(resultado) -> dict:
    return {Path(omitida.ruta).name: omitida.motivo for omitida in resultado.omitidas}


def test_los_ocultos_por_nombre_no_se_clasifican(raiz):
    """RF-15: el punto inicial oculta el elemento en cualquier plataforma."""
    resultado = recorrer(raiz)

    assert nombres(resultado) == {"nota.txt", "informe.pdf"}
    assert motivos(resultado) == {".secreto.txt": OCULTO, ".sinextension": OCULTO}
    assert all(omitida.detalle == "" for omitida in resultado.omitidas)


def test_sin_recursion_la_carpeta_oculta_solo_se_cuenta(raiz):
    """RF-4 y CL-11: sin recorrer subcarpetas, ninguna se omite."""
    resultado = recorrer(raiz)

    assert resultado.subcarpetas_encontradas == 2
    assert resultado.subcarpetas_recorridas == 0
    assert ".privada" not in motivos(resultado)


def test_con_recursion_la_carpeta_oculta_se_omite_una_vez(raiz):
    """RF-14: la carpeta oculta no se enumera y cuenta como una omisión."""
    resultado = recorrer(raiz, recursivo=True)

    assert motivos(resultado)[".privada"] == OCULTO
    assert "foto.jpg" not in nombres(resultado)
    assert "dentro.mp3" in nombres(resultado)
    assert resultado.subcarpetas_encontradas == 2
    assert resultado.subcarpetas_recorridas == 1


def test_incluir_ocultos_examina_los_elementos_ocultos(raiz):
    """RF-14: con la opción, lo oculto se examina como cualquier otro elemento."""
    resultado = recorrer(raiz, recursivo=True, incluir_ocultos=True)

    assert nombres(resultado) == {Path(relativa).name for relativa in ARCHIVOS}
    assert not resultado.omitidas
    assert resultado.subcarpetas_encontradas == 2
    assert resultado.subcarpetas_recorridas == 2


def test_el_oculto_sin_extension_no_se_confunde_con_su_grupo(raiz):
    """Caso límite de la spec: `.sinextension` se omite antes de clasificarse."""
    omitidas = recorrer(raiz)

    assert motivos(omitidas)[".sinextension"] == OCULTO

    incluidas = recorrer(raiz, incluir_ocultos=True)
    categorias = {
        Path(archivo.ruta).name: archivo.categoria for archivo in incluidas.archivos
    }

    assert categorias[".sinextension"] is Categoria.SIN_EXTENSION


def test_enlace_visible_se_omite_como_enlace(raiz, crear_enlace):
    """RF-9: un enlace encontrado en el recorrido no se clasifica."""
    crear_enlace(raiz / "atajo", raiz / "nota.txt")

    resultado = recorrer(raiz)

    assert motivos(resultado)["atajo"] == ENLACE
    assert "atajo" not in nombres(resultado)


def test_enlace_oculto_se_cuenta_una_sola_vez(raiz, crear_enlace):
    """RF-9: con dos motivos aplicables prevalece la ocultación."""
    crear_enlace(raiz / ".enlace", raiz / "nota.txt")

    resultado = recorrer(raiz)
    coincidencias = [
        omitida for omitida in resultado.omitidas if Path(omitida.ruta).name == ".enlace"
    ]

    assert len(coincidencias) == 1
    assert coincidencias[0].motivo == OCULTO


def test_enlace_oculto_simulado_se_cuenta_una_sola_vez(monkeypatch, raiz):
    """Misma prioridad sin depender del privilegio de crear enlaces."""
    anadir_entradas(monkeypatch, raiz, [EntradaSimulada(raiz / ".enlace", enlace=True)])

    resultado = recorrer(raiz)
    coincidencias = [
        omitida for omitida in resultado.omitidas if Path(omitida.ruta).name == ".enlace"
    ]

    assert len(coincidencias) == 1
    assert coincidencias[0].motivo == OCULTO


def test_incluir_ocultos_mantiene_las_demas_exclusiones(monkeypatch, raiz):
    """RF-14: la opción solo retira la exclusión por ocultación."""
    anadir_entradas(monkeypatch, raiz, [EntradaSimulada(raiz / ".enlace", enlace=True)])

    resultado = recorrer(raiz, incluir_ocultos=True)

    assert motivos(resultado) == {".enlace": ENLACE}
    assert ".enlace" not in nombres(resultado)


def test_la_ocultacion_prevalece_sobre_un_fallo_de_metadatos(monkeypatch, raiz):
    """RF-9: el nombre oculto se resuelve sin consultar los metadatos."""
    anadir_entradas(
        monkeypatch,
        raiz,
        [EntradaSimulada(raiz / ".roto.txt", fallo=PermissionError(errno.EACCES, "denied"))],
    )

    resultado = recorrer(raiz)

    assert motivos(resultado)[".roto.txt"] == OCULTO


def test_la_suma_por_motivos_coincide_con_el_total(monkeypatch, raiz):
    """RF-9: cada entrada omitida aporta un motivo y solo uno.

    Las dos sustituciones de la enumeración se encadenan: la segunda parte del
    contenido que produce la primera.
    """
    anadir_entradas(monkeypatch, raiz, [EntradaSimulada(raiz / "atajo", enlace=True)])
    fallar_en(
        monkeypatch,
        {
            raiz / "nota.txt": PermissionError(errno.EACCES, "Permission denied"),
            raiz / "informe.pdf": OSError(errno.EIO, "Input/output error"),
        },
    )

    resultado = recorrer(raiz)
    recuentos = Counter(omitida.motivo for omitida in resultado.omitidas)

    assert recuentos == {OCULTO: 2, ENLACE: 1, SIN_PERMISO: 1, ERROR_LECTURA: 1}
    assert sum(recuentos.values()) == len(resultado.omitidas)
    assert set(recuentos) <= set(MOTIVOS)
    assert len({omitida.ruta for omitida in resultado.omitidas}) == len(resultado.omitidas)
    assert not resultado.archivos


@pytest.mark.parametrize(
    "nombre,enlace,atributos,fallo_tipo,fallo_stat,esperado",
    [
        (".dato.txt", False, 0, errno.EACCES, None, OCULTO),
        ("atajo", True, 0, None, errno.EACCES, ENLACE),
        ("dato.txt", False, stat.FILE_ATTRIBUTE_HIDDEN, errno.EACCES, None, OCULTO),
        ("dato.txt", False, 0, errno.EACCES, errno.EIO, SIN_PERMISO),
        ("dato.txt", False, 0, errno.EIO, errno.EACCES, SIN_PERMISO),
    ],
)
def test_los_fallos_no_reemplazan_motivos_superiores(
    tmp_path, monkeypatch, capsys, nombre, enlace, atributos, fallo_tipo, fallo_stat, esperado
):
    """V-9: también fallan las consultas de tipo, no solo la del tamaño."""
    class EntradaConFalloDeTipo(EntradaSimulada):
        def is_dir(self, *, follow_symlinks=True):
            if fallo_tipo:
                raise OSError(fallo_tipo, "foreign type failure")
            return super().is_dir(follow_symlinks=follow_symlinks)

    entrada = EntradaConFalloDeTipo(
        tmp_path / nombre, enlace=enlace, atributos=atributos,
        fallo=OSError(fallo_stat, "foreign metadata failure") if fallo_stat else None,
    )
    monkeypatch.setattr(recorrido, "ES_WINDOWS", True)
    anadir_entradas(monkeypatch, tmp_path, [entrada])

    resultado = recorrer(tmp_path, recursivo=True)
    assert resultado.archivos == ()
    assert len(resultado.omitidas) == 1
    assert resultado.omitidas[0].motivo == esperado

    assert main(["analizar", str(tmp_path), "--recursivo"]) == (
        3 if esperado == SIN_PERMISO else 0
    )
    salida = capsys.readouterr()
    assert "Omitidos: 1" in salida.out
    assert "foreign" not in salida.err
    assert bool(salida.err) == (esperado == SIN_PERMISO)
