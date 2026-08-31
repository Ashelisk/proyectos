"""T13: análisis completo de extremo a extremo (RF-1 a RF-16, RNF-1).

Un solo árbol reúne las seis categorías, archivos sin extensión, subcarpetas,
elementos ocultos, un enlace y una entrada que falla al consultar sus metadatos.
El enlace es real cuando el entorno concede el privilegio y, si no, se simula
para que el escenario se compruebe igualmente; el fallo es siempre inyectado y
no acredita los permisos reales del sistema.
"""

import errno
import socket

import pytest

from dobles import EntradaSimulada, anadir_entradas, fallar_en
from filepilot.cli import CODIGO_CON_OMISIONES, CODIGO_RUTA_INVALIDA, CODIGO_USO_INCORRECTO, main
from filepilot.informe import formatear_tamano

ARCHIVOS = {
    "foto.jpg": "imagen",
    "grafico.svg": "vector",
    "memoria.pdf": "memoria anual",
    "nota.txt": "unas notas",
    "clip.mp4": "escena",
    "cancion.mp3": "sonido",
    "copia.tar.gz": "comprimido",
    "registro.log": "una linea",
    "notas.bak": "respaldo",
    "LEEME": "sin extension",
    "roto.pdf": "ilegible",
    ".secreto.txt": "oculto",
    ".privada/interior.txt": "dentro de la carpeta oculta",
    "sub/interior.jpg": "otra imagen",
    "sub/apuntes.md": "apuntes",
}

PRIMER_NIVEL = [
    "foto.jpg",
    "grafico.svg",
    "memoria.pdf",
    "nota.txt",
    "clip.mp4",
    "cancion.mp3",
    "copia.tar.gz",
    "registro.log",
    "notas.bak",
    "LEEME",
]
DESCENDIENTES = ["sub/interior.jpg", "sub/apuntes.md"]
OCULTOS = [".secreto.txt", ".privada/interior.txt"]

CARPETAS = {
    "Imágenes": "imagenes",
    "Documentos": "documentos",
    "Vídeo": "video",
    "Audio": "audio",
    "Comprimidos": "comprimidos",
    "Otros": "otros",
    "Sin extensión": "sin-extension",
}


@pytest.fixture
def arbol(tmp_path, monkeypatch):
    """Árbol completo con su enlace y su entrada fallida."""
    raiz = tmp_path / "raiz"
    for relativa, texto in ARCHIVOS.items():
        destino = raiz / relativa
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text(texto, encoding="utf-8")

    try:
        (raiz / "atajo").symlink_to(raiz / "nota.txt")
    except (OSError, NotImplementedError):
        anadir_entradas(monkeypatch, raiz, [EntradaSimulada(raiz / "atajo", enlace=True)])
    # La segunda sustitución parte del contenido que produce la primera.
    fallar_en(monkeypatch, {raiz / "roto.pdf": OSError(errno.EIO, "Input/output error")})
    return raiz


@pytest.fixture
def arbol_simple(tmp_path):
    """Árbol sin enlaces ni fallos, apto para ejecutarse en otro proceso."""
    raiz = tmp_path / "sencilla"
    (raiz / "sub").mkdir(parents=True)
    (raiz / "foto.jpg").write_text("imagen", encoding="utf-8")
    (raiz / "sub" / "nota.txt").write_text("unas notas", encoding="utf-8")
    return raiz


def fila(informe: str, encabezado: str) -> str:
    return next(linea for linea in informe.splitlines() if linea.startswith(encabezado))


def comprobar_tabla(salida: str, raiz, esperados: dict, clasificados: list) -> None:
    """Cada grupo con su recuento y su destino en la raíz, más los totales."""
    for grupo, recuento in esperados.items():
        linea = fila(salida, grupo)
        assert str(recuento) in linea.split(), f"recuento inesperado en {grupo}: {linea}"
        assert str(raiz / CARPETAS[grupo]) in linea

    tamano = sum(len(ARCHIVOS[relativa]) for relativa in clasificados)
    totales = fila(salida, "Total")
    assert str(len(clasificados)) in totales.split()
    assert formatear_tamano(tamano) in totales


def test_informe_completo_en_primer_nivel(capsys, arbol):
    """RF-1, RF-3, RF-7, RF-8, RF-9 y RF-13 sobre el árbol completo."""
    codigo = main(["analizar", str(arbol)])

    salida = capsys.readouterr()
    assert codigo == CODIGO_CON_OMISIONES
    comprobar_tabla(
        salida.out,
        arbol,
        {
            "Imágenes": 2,
            "Documentos": 2,
            "Vídeo": 1,
            "Audio": 1,
            "Comprimidos": 1,
            "Otros": 2,
            "Sin extensión": 1,
        },
        PRIMER_NIVEL,
    )
    assert fila(salida.out, "Extensiones desconocidas") == (
        "Extensiones desconocidas: .bak (1), .log (1)"
    )
    assert fila(salida.out, "Subcarpetas") == "Subcarpetas: 2 encontradas"
    assert fila(salida.out, "Omitidos") == (
        "Omitidos: 3 (ocultos 1, enlaces 1, sin permiso 0, errores de lectura 1)"
    )
    assert "error de entrada y salida" in salida.err


def test_informe_completo_en_modo_recursivo(capsys, arbol):
    """RF-3, RF-4 y RF-7: los descendientes se suman con destino en la raíz."""
    codigo = main(["analizar", str(arbol), "--recursivo"])

    salida = capsys.readouterr()
    assert codigo == CODIGO_CON_OMISIONES
    comprobar_tabla(
        salida.out,
        arbol,
        {"Imágenes": 3, "Documentos": 3, "Otros": 2, "Sin extensión": 1},
        PRIMER_NIVEL + DESCENDIENTES,
    )
    assert str(arbol / "sub" / "imagenes") not in salida.out
    assert fila(salida.out, "Subcarpetas") == "Subcarpetas: 2 encontradas, 1 recorridas"
    assert fila(salida.out, "Omitidos") == (
        "Omitidos: 4 (ocultos 2, enlaces 1, sin permiso 0, errores de lectura 1)"
    )


def test_informe_completo_con_ocultos(capsys, arbol):
    """RF-14: la opción incorpora lo oculto y conserva las demás exclusiones."""
    codigo = main(["analizar", str(arbol), "--recursivo", "--incluir-ocultos"])

    salida = capsys.readouterr()
    assert codigo == CODIGO_CON_OMISIONES
    comprobar_tabla(
        salida.out,
        arbol,
        {"Imágenes": 3, "Documentos": 5},
        PRIMER_NIVEL + DESCENDIENTES + OCULTOS,
    )
    assert fila(salida.out, "Subcarpetas") == "Subcarpetas: 2 encontradas, 2 recorridas"
    assert fila(salida.out, "Omitidos") == (
        "Omitidos: 2 (ocultos 0, enlaces 1, sin permiso 0, errores de lectura 1)"
    )


def test_raiz_oculta_se_analiza_completa(capsys, tmp_path):
    """RF-14: una raíz oculta se analiza sin `--incluir-ocultos`."""
    raiz = tmp_path / ".archivo"
    raiz.mkdir()
    (raiz / "foto.jpg").write_text("imagen", encoding="utf-8")
    (raiz / "nota.txt").write_text("unas notas", encoding="utf-8")

    codigo = main(["analizar", str(raiz)])

    salida = capsys.readouterr()
    assert codigo == 0
    assert "1" in fila(salida.out, "Imágenes").split()
    assert str(raiz / "documentos") in fila(salida.out, "Documentos")


def test_raiz_enlazada_se_analiza_completa(capsys, tmp_path, crear_enlace):
    """RF-16: el enlace inicial se resuelve y se analiza su destino."""
    real = tmp_path / "real"
    real.mkdir()
    (real / "cancion.mp3").write_text("sonido", encoding="utf-8")
    enlace = crear_enlace(tmp_path / "acceso", real)

    codigo = main(["analizar", str(enlace)])

    salida = capsys.readouterr()
    assert codigo == 0
    assert str(real.resolve() / "audio") in fila(salida.out, "Audio")


@pytest.mark.parametrize(
    "argumentos, codigo",
    [
        pytest.param(["analizar", "sencilla"], 0, id="informe_correcto"),
        pytest.param(["analizar"], CODIGO_USO_INCORRECTO, id="uso_incorrecto"),
        pytest.param(["analizar", "ausente"], CODIGO_RUTA_INVALIDA, id="ruta_invalida"),
    ],
)
def test_codigos_de_salida_del_proceso(ejecutar_modulo, arbol_simple, argumentos, codigo):
    """RF-1, RF-2 y RF-11; el código tres se observa con el fallo inyectado."""
    resultado = ejecutar_modulo(argumentos, arbol_simple.parent)

    assert resultado.returncode == codigo


@pytest.mark.parametrize("contenido", ["vacio", "subcarpeta", "oculto"])
def test_sin_archivos_analizables_desde_el_proceso(ejecutar_modulo, tmp_path, contenido):
    """RF-12: los tres casos vacíos conservan código cero y sus recuentos."""
    if contenido == "subcarpeta":
        (tmp_path / "sub").mkdir()
        (tmp_path / "sub" / "nota.txt").write_text("dato", encoding="utf-8")
    elif contenido == "oculto":
        (tmp_path / ".nota.txt").write_text("dato", encoding="utf-8")

    resultado = ejecutar_modulo(["analizar", str(tmp_path)], tmp_path)

    assert resultado.returncode == 0
    assert resultado.stderr == ""
    assert "No se han encontrado archivos analizables." in resultado.stdout
    assert "Categoría" not in resultado.stdout
    if contenido == "subcarpeta":
        assert "Subcarpetas: 1 encontradas" in resultado.stdout
        assert "Omitidos" not in resultado.stdout
    elif contenido == "oculto":
        assert "Omitidos: 1 (ocultos 1" in resultado.stdout


def test_el_analisis_no_usa_la_red(monkeypatch, capsys, arbol_simple):
    """RNF-1: ninguna fase del análisis abre una conexión."""

    def prohibido(*argumentos, **opciones):
        raise AssertionError("el análisis ha intentado usar la red")

    monkeypatch.setattr(socket.socket, "connect", prohibido)
    monkeypatch.setattr(socket.socket, "connect_ex", prohibido)
    monkeypatch.setattr(socket, "create_connection", prohibido)
    monkeypatch.setattr(socket, "getaddrinfo", prohibido)

    codigo = main(["analizar", str(arbol_simple), "--recursivo"])

    capsys.readouterr()
    assert codigo == 0


def test_ningun_evento_de_red_durante_el_analisis(analizar_vigilado, arbol_simple):
    """RNF-1: en un proceso aislado no se registra actividad de red ni cuentas."""
    resultado, eventos = analizar_vigilado(
        ["analizar", str(arbol_simple), "--recursivo"], ["socket", "urllib"]
    )

    assert resultado.returncode == 0, resultado.stderr
    assert eventos == []
