"""Composición del informe de análisis (RF-7, RF-8, RF-12)."""

from collections import Counter
from pathlib import Path

from .clasificacion import Categoria, extension
from .recorrido import ENLACE, ERROR_LECTURA, MOTIVOS, OCULTO, SIN_PERMISO, ResultadoRecorrido

# Nombre acentuado de cada grupo; su carpeta de destino va sin acentos (RF-7).
NOMBRE_CATEGORIA = {
    Categoria.IMAGENES: "Imágenes",
    Categoria.DOCUMENTOS: "Documentos",
    Categoria.VIDEO: "Vídeo",
    Categoria.AUDIO: "Audio",
    Categoria.COMPRIMIDOS: "Comprimidos",
    Categoria.OTROS: "Otros",
    Categoria.SIN_EXTENSION: "Sin extensión",
}
NOMBRE_MOTIVO = {
    OCULTO: "ocultos",
    ENLACE: "enlaces",
    SIN_PERMISO: "sin permiso",
    ERROR_LECTURA: "errores de lectura",
}

UNIDADES = ("B", "KB", "MB", "GB", "TB", "PB")
ENCABEZADOS = ("Categoría", "Archivos", "Tamaño", "Destino propuesto")
ALINEACION = (str.ljust, str.rjust, str.rjust, str.ljust)
SEPARADOR = "  "
MAXIMO_EXTENSIONES = 5
SIN_ARCHIVOS = "No se han encontrado archivos analizables."
TOTAL = "Total"


def formatear_tamano(tamano: int) -> str:
    """Tamaño en base 1024 con un decimal y coma decimal fija (RF-7).

    La coma se escribe directamente, sin `locale`, para que la misma carpeta
    produzca el mismo informe en cualquier plataforma.
    """
    valor = float(tamano)
    for unidad in UNIDADES:
        # El redondeo se comprueba antes de elegir la unidad para no escribir
        # «1024,0 KB» cuando el valor ya llega a la unidad siguiente.
        if round(valor, 1) < 1024 or unidad == UNIDADES[-1]:
            return f"{valor:.1f}".replace(".", ",") + f" {unidad}"
        valor /= 1024


def agrupar(archivos) -> dict[Categoria, tuple[int, int]]:
    """Recuento y tamaño total de cada categoría con archivos, en orden fijo."""
    grupos = {}
    for archivo in archivos:
        recuento, total = grupos.get(archivo.categoria, (0, 0))
        grupos[archivo.categoria] = (recuento + 1, total + archivo.tamano)
    return {categoria: grupos[categoria] for categoria in Categoria if categoria in grupos}


def extensiones_desconocidas(archivos) -> list[tuple[str, int]]:
    """RF-8: hasta cinco extensiones de «otros», por recuento y alfabéticamente."""
    recuentos = Counter(
        extension(Path(archivo.ruta).name)
        for archivo in archivos
        if archivo.categoria is Categoria.OTROS
    )
    ordenadas = sorted(recuentos.items(), key=lambda par: (-par[1], par[0]))
    return ordenadas[:MAXIMO_EXTENSIONES]


def _filas(raiz: Path, grupos) -> list[tuple[str, ...]]:
    """Encabezado, una fila por grupo con su destino y la fila de totales."""
    filas = [ENCABEZADOS]
    archivos = tamano = 0
    for categoria, (recuento, total) in grupos.items():
        archivos += recuento
        tamano += total
        filas.append(
            (
                NOMBRE_CATEGORIA[categoria],
                str(recuento),
                formatear_tamano(total),
                str(raiz / categoria.carpeta),
            )
        )
    filas.append((TOTAL, str(archivos), formatear_tamano(tamano), ""))
    return filas


def _alinear(filas) -> list[str]:
    """Ajusta cada columna al ancho de su contenido, sin espacios finales."""
    anchos = [max(len(fila[columna]) for fila in filas) for columna in range(len(ENCABEZADOS))]
    lineas = []
    for fila in filas:
        celdas = [
            ALINEACION[columna](texto, anchos[columna]) for columna, texto in enumerate(fila)
        ]
        lineas.append(SEPARADOR.join(celdas).rstrip())
    return lineas


def _linea_subcarpetas(resultado: ResultadoRecorrido, recursivo: bool) -> str:
    """RF-4: las recorridas solo tienen sentido en modo recursivo."""
    texto = f"Subcarpetas: {resultado.subcarpetas_encontradas} encontradas"
    if recursivo:
        texto += f", {resultado.subcarpetas_recorridas} recorridas"
    return texto


def _linea_omitidos(resultado: ResultadoRecorrido) -> str:
    """RF-9: total de omitidos y su desglose por los cuatro motivos."""
    recuentos = Counter(omitida.motivo for omitida in resultado.omitidas)
    total = len(resultado.omitidas)
    if not total:
        return "Omitidos: 0"
    desglose = ", ".join(f"{NOMBRE_MOTIVO[motivo]} {recuentos[motivo]}" for motivo in MOTIVOS)
    return f"Omitidos: {total} ({desglose})"


def componer(raiz: Path, resultado: ResultadoRecorrido, recursivo: bool = False) -> str:
    """Devuelve el informe completo del análisis de `raiz`.

    Con archivos analizables se emite la tabla de grupos con sus destinos; sin
    ellos, el aviso de RF-12 y solo los recuentos que existan.
    """
    lineas = [f"Análisis de «{raiz}»", ""]
    grupos = agrupar(resultado.archivos)

    if not grupos:
        lineas.append(SIN_ARCHIVOS)
        if resultado.subcarpetas_encontradas:
            lineas.append(_linea_subcarpetas(resultado, recursivo))
        if resultado.omitidas:
            lineas.append(_linea_omitidos(resultado))
        return "\n".join(lineas)

    lineas.extend(_alinear(_filas(raiz, grupos)))
    desconocidas = extensiones_desconocidas(resultado.archivos)
    if desconocidas:
        detalle = ", ".join(f".{ext} ({recuento})" for ext, recuento in desconocidas)
        lineas.extend(["", f"Extensiones desconocidas: {detalle}"])
    lineas.extend(["", _linea_subcarpetas(resultado, recursivo), _linea_omitidos(resultado)])
    return "\n".join(lineas)
