"""T10: fallos por entrada, avisos en español y código tres (RF-13, RNF-3).

Los fallos se inyectan sustituyendo la consulta de metadatos o la enumeración de
una carpeta: comprueban el tratamiento del error, no los permisos reales del
sistema, que se verifican con sus propias pruebas.
"""

import errno

import pytest

from dobles import EntradaSimulada, anadir_entradas, fallar_al_enumerar, fallar_en
from filepilot.cli import CODIGO_CON_OMISIONES, CODIGO_RUTA_INVALIDA, main
from filepilot.informe import SIN_ARCHIVOS

ARCHIVOS = {"nota.txt": "unas notas", "foto.jpg": "píxeles", "informe.pdf": "un informe"}

CAUSAS = [
    pytest.param(FileNotFoundError(errno.ENOENT, "No such file"), "no existe", id="desaparecido"),
    pytest.param(
        PermissionError(errno.EACCES, "Permission denied"), "permiso denegado", id="sin_permiso"
    ),
    pytest.param(
        OSError(errno.EIO, "Input/output error"), "error de entrada y salida", id="error_lectura"
    ),
]


@pytest.fixture
def raiz(tmp_path):
    raiz = tmp_path / "raiz"
    raiz.mkdir()
    for nombre, texto in ARCHIVOS.items():
        (raiz / nombre).write_text(texto, encoding="utf-8")
    return raiz


@pytest.mark.parametrize("fallo, causa", CAUSAS)
def test_el_analisis_continua_y_avisa_de_cada_fallo(monkeypatch, capsys, raiz, fallo, causa):
    """RF-13: el resto se analiza, el aviso cita ruta y causa y el código es tres."""
    fallar_en(monkeypatch, {raiz / "informe.pdf": fallo})

    codigo = main(["analizar", str(raiz)])

    salida = capsys.readouterr()
    assert codigo == CODIGO_CON_OMISIONES
    assert str(raiz / "informe.pdf") in salida.err
    assert causa in salida.err
    assert "Imágenes" in salida.out and "Documentos" in salida.out
    assert "Análisis de" in salida.out


def test_el_aviso_no_copia_el_texto_del_sistema(monkeypatch, capsys, raiz):
    """RNF-3: la causa se redacta en español a partir del código del fallo."""
    fallar_en(monkeypatch, {raiz / "informe.pdf": OSError(errno.EIO, "Eingabe-/Ausgabefehler")})

    main(["analizar", str(raiz)])

    salida = capsys.readouterr()
    assert "error de entrada y salida" in salida.err
    assert "Eingabe" not in salida.err


def test_cada_entrada_fallida_se_cuenta_una_sola_vez(monkeypatch, capsys, raiz):
    """RF-9: un fallo produce un aviso y una única omisión con su motivo."""
    fallar_en(monkeypatch, {raiz / "informe.pdf": PermissionError(errno.EACCES, "denied")})

    main(["analizar", str(raiz)])

    salida = capsys.readouterr()
    assert salida.err.count(str(raiz / "informe.pdf")) == 1
    assert "Omitidos: 1 (ocultos 0, enlaces 0, sin permiso 1, errores de lectura 0)" in salida.out


def test_codigo_tres_aunque_no_haya_archivos_analizables(monkeypatch, capsys, tmp_path):
    """RF-12 y CL-9: sin archivos clasificados, el fallo sigue elevando el código."""
    raiz = tmp_path / "sola"
    raiz.mkdir()
    (raiz / "informe.pdf").write_text("un informe", encoding="utf-8")
    fallar_en(monkeypatch, {raiz / "informe.pdf": OSError(errno.EIO, "Input/output error")})

    codigo = main(["analizar", str(raiz)])

    salida = capsys.readouterr()
    assert codigo == CODIGO_CON_OMISIONES
    assert SIN_ARCHIVOS in salida.out
    assert "errores de lectura 1" in salida.out


def test_las_omisiones_voluntarias_no_cambian_el_codigo(monkeypatch, capsys, raiz):
    """RF-13: ocultación y enlace se cuentan, pero el análisis termina en cero."""
    (raiz / ".secreto.txt").write_text("oculto", encoding="utf-8")
    anadir_entradas(monkeypatch, raiz, [EntradaSimulada(raiz / "atajo", enlace=True)])

    codigo = main(["analizar", str(raiz)])

    salida = capsys.readouterr()
    assert codigo == 0
    assert salida.err == ""
    assert "Omitidos: 2 (ocultos 1, enlaces 1, sin permiso 0, errores de lectura 0)" in salida.out


def test_la_subcarpeta_ilegible_se_omite_con_su_causa(monkeypatch, capsys, raiz):
    """RF-13: la subcarpeta ya contada no se recorre y aparece entre las omitidas."""
    cerrada = raiz / "cerrada"
    cerrada.mkdir()
    (cerrada / "dentro.txt").write_text("inalcanzable", encoding="utf-8")
    fallar_al_enumerar(monkeypatch, cerrada, PermissionError(errno.EACCES, "denied"))

    codigo = main(["analizar", str(raiz), "--recursivo"])

    salida = capsys.readouterr()
    assert codigo == CODIGO_CON_OMISIONES
    assert str(cerrada) in salida.err
    assert "permiso denegado" in salida.err
    assert "Subcarpetas: 1 encontradas, 0 recorridas" in salida.out
    assert "sin permiso 1" in salida.out


def test_el_fallo_de_la_propia_raiz_termina_en_dos(monkeypatch, capsys, raiz):
    """RF-11: un fallo al leer la raíz no se trata como una entrada omitida.

    La primera enumeración corresponde a la validación de la ruta; el fallo se
    provoca en la del análisis, ya con la raíz aceptada.
    """
    fallar_al_enumerar(monkeypatch, raiz, OSError(errno.EIO, "Input/output error"), omitir=1)

    codigo = main(["analizar", str(raiz)])

    salida = capsys.readouterr()
    assert codigo == CODIGO_RUTA_INVALIDA
    assert str(raiz) in salida.err
    assert "error de entrada y salida" in salida.err
    assert salida.out == ""


def test_el_aviso_identifica_cada_entrada_afectada(monkeypatch, capsys, raiz):
    """RF-13: dos fallos distintos producen dos avisos con su propia causa."""
    fallar_en(
        monkeypatch,
        {
            raiz / "informe.pdf": PermissionError(errno.EACCES, "denied"),
            raiz / "foto.jpg": FileNotFoundError(errno.ENOENT, "missing"),
        },
    )

    codigo = main(["analizar", str(raiz)])

    salida = capsys.readouterr()
    avisos = [linea for linea in salida.err.splitlines() if "aviso" in linea]
    assert codigo == CODIGO_CON_OMISIONES
    assert len(avisos) == 2
    assert any(str(raiz / "informe.pdf") in aviso and "permiso denegado" in aviso for aviso in avisos)
    assert any(str(raiz / "foto.jpg") in aviso and "no existe" in aviso for aviso in avisos)
    # El archivo intacto se clasifica y los dos motivos se conservan por separado.
    assert "Documentos" in salida.out
    assert "Omitidos: 2 (ocultos 0, enlaces 0, sin permiso 1, errores de lectura 1)" in salida.out
