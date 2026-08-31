"""T8 y T9: composición del informe (RF-7, RF-8, RF-12).

Todas las comprobaciones trabajan sobre datos en memoria: el informe no consulta
el sistema de archivos, de modo que la raíz puede ser una ruta cualquiera.
"""

from pathlib import Path

import pytest

from filepilot.clasificacion import clasificar
from filepilot.informe import SIN_ARCHIVOS, componer, formatear_tamano
from filepilot.recorrido import (
    ENLACE,
    ERROR_LECTURA,
    OCULTO,
    SIN_PERMISO,
    ArchivoAnalizado,
    EntradaOmitida,
    ResultadoRecorrido,
)

RAIZ = Path("datos") / "descargas"


def archivo(relativa: str, tamano: int = 0) -> ArchivoAnalizado:
    ruta = RAIZ / relativa
    return ArchivoAnalizado(ruta, clasificar(ruta.name), tamano)


def resultado(archivos=(), omitidas=(), encontradas=0, recorridas=0) -> ResultadoRecorrido:
    return ResultadoRecorrido(tuple(archivos), tuple(omitidas), encontradas, recorridas)


def fila(informe: str, encabezado: str) -> str:
    """Línea de la tabla que corresponde a un grupo o a los totales."""
    return next(linea for linea in informe.splitlines() if linea.startswith(encabezado))


@pytest.mark.parametrize(
    "tamano, esperado",
    [
        (0, "0,0 B"),
        (100, "100,0 B"),
        (1000, "1000,0 B"),  # base 1024: mil bytes todavía no son un kilobyte
        (1024, "1,0 KB"),
        (1536, "1,5 KB"),
        (1048575, "1,0 MB"),  # el redondeo no debe producir «1024,0 KB»
        (1468006, "1,4 MB"),
        (1024**3, "1,0 GB"),
        (1024**4, "1,0 TB"),
        (1024**5, "1,0 PB"),
        (1024**6, "1024,0 PB"),  # sin unidad mayor, se conserva la última
    ],
)
def test_formato_de_tamano(tamano, esperado):
    """RF-7: unidad en base 1024, un decimal y coma decimal fija."""
    assert formatear_tamano(tamano) == esperado


def test_el_separador_decimal_no_depende_del_sistema():
    """RF-7: la coma se escribe siempre, sin recurrir a la configuración regional."""
    escrito = formatear_tamano(1536)

    assert "," in escrito
    assert "." not in escrito


def test_una_fila_por_grupo_con_destino_y_totales():
    """RF-7: recuento, tamaño y carpeta propuesta de cada grupo con archivos."""
    informe = componer(
        RAIZ,
        resultado([archivo("foto.jpg", 1024), archivo("otra.png", 2048), archivo("nota.txt", 100)]),
    )

    imagenes = fila(informe, "Imágenes")
    assert "2" in imagenes.split()
    assert "3,0 KB" in imagenes
    assert str(RAIZ / "imagenes") in imagenes

    documentos = fila(informe, "Documentos")
    assert "100,0 B" in documentos
    assert str(RAIZ / "documentos") in documentos

    totales = fila(informe, "Total")
    assert "3" in totales.split()
    assert "3,1 KB" in totales


def test_los_grupos_sin_archivos_se_omiten():
    """RF-7: la tabla solo muestra los grupos con contenido."""
    informe = componer(RAIZ, resultado([archivo("nota.txt", 10)]))

    assert "Documentos" in informe
    assert "Vídeo" not in informe
    assert "Sin extensión" not in informe


def test_el_destino_es_siempre_la_raiz_analizada():
    """RF-7 y CL-4: en modo recursivo los destinos no dependen de la subcarpeta."""
    informe = componer(RAIZ, resultado([archivo("sub/profunda/foto.jpg", 10)]), recursivo=True)

    assert str(RAIZ / "imagenes") in fila(informe, "Imágenes")
    assert str(RAIZ / "sub") not in informe


def test_extensiones_desconocidas_limitadas_y_ordenadas():
    """RF-8: cinco como máximo, por recuento y alfabéticamente en los empates."""
    archivos = [archivo(f"registro{numero}.log") for numero in range(3)]
    archivos += [archivo(f"temporal{numero}.tmp") for numero in range(2)]
    archivos += [archivo(nombre) for nombre in ("copia.bak", "datos.aaa", "ajuste.cfg", "final.zzz")]

    informe = componer(RAIZ, resultado(archivos))

    assert (
        fila(informe, "Extensiones desconocidas")
        == "Extensiones desconocidas: .log (3), .tmp (2), .aaa (1), .bak (1), .cfg (1)"
    )


def test_sin_grupo_otros_no_hay_extensiones_desconocidas():
    """RF-8: el detalle solo aparece cuando «otros» tiene archivos."""
    informe = componer(RAIZ, resultado([archivo("nota.txt", 10), archivo("LEEME")]))

    assert "Extensiones desconocidas" not in informe
    assert "Sin extensión" in informe


@pytest.mark.parametrize(
    "recursivo, esperado",
    [
        (False, "Subcarpetas: 3 encontradas"),
        (True, "Subcarpetas: 3 encontradas, 2 recorridas"),
    ],
    ids=["primer_nivel", "recursivo"],
)
def test_recuento_de_subcarpetas(recursivo, esperado):
    """RF-4: las recorridas solo se informan en modo recursivo."""
    informe = componer(
        RAIZ, resultado([archivo("nota.txt", 10)], encontradas=3, recorridas=2), recursivo
    )

    assert fila(informe, "Subcarpetas") == esperado


def test_desglose_de_omitidos_por_motivo():
    """RF-9: el total y los cuatro motivos aparecen en el informe."""
    omitidas = [
        EntradaOmitida(RAIZ / ".secreto", OCULTO, ""),
        EntradaOmitida(RAIZ / "atajo", ENLACE, ""),
        EntradaOmitida(RAIZ / "cerrado.txt", SIN_PERMISO, "permiso denegado"),
        EntradaOmitida(RAIZ / "roto.txt", ERROR_LECTURA, "error de entrada y salida"),
        EntradaOmitida(RAIZ / ".otro", OCULTO, ""),
    ]

    informe = componer(RAIZ, resultado([archivo("nota.txt", 10)], omitidas))

    assert (
        fila(informe, "Omitidos")
        == "Omitidos: 5 (ocultos 2, enlaces 1, sin permiso 1, errores de lectura 1)"
    )


def test_sin_omitidos_el_recuento_es_cero():
    informe = componer(RAIZ, resultado([archivo("nota.txt", 10)]))

    assert fila(informe, "Omitidos") == "Omitidos: 0"


def test_sin_archivos_analizables_se_avisa_con_los_recuentos():
    """RF-12: sin tabla de categorías, con los recuentos que existan."""
    omitidas = [EntradaOmitida(RAIZ / ".secreto", OCULTO, "")]

    informe = componer(RAIZ, resultado((), omitidas, encontradas=2), recursivo=False)

    assert SIN_ARCHIVOS in informe
    assert "Categoría" not in informe
    assert "Total" not in informe
    assert fila(informe, "Subcarpetas") == "Subcarpetas: 2 encontradas"
    assert (
        fila(informe, "Omitidos")
        == "Omitidos: 1 (ocultos 1, enlaces 0, sin permiso 0, errores de lectura 0)"
    )


def test_carpeta_vacia_solo_avisa():
    """RF-12: sin subcarpetas ni omitidos no se añaden recuentos."""
    informe = componer(RAIZ, resultado())

    assert SIN_ARCHIVOS in informe
    assert "Subcarpetas" not in informe
    assert "Omitidos" not in informe
