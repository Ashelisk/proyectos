"""Clasificación de un archivo por su extensión (RF-5, RF-6, RF-7)."""

from enum import Enum


class Categoria(Enum):
    """Grupo de un archivo; su valor es la carpeta propuesta de RF-7."""

    IMAGENES = "imagenes"
    DOCUMENTOS = "documentos"
    VIDEO = "video"
    AUDIO = "audio"
    COMPRIMIDOS = "comprimidos"
    OTROS = "otros"
    SIN_EXTENSION = "sin-extension"

    @property
    def carpeta(self) -> str:
        """Carpeta de destino del grupo, en minúscula y sin acentos."""
        return self.value


# Mapa de RF-5: añadir o mover una extensión exige actualizar antes el requisito.
CATEGORIA_POR_EXTENSION = {
    extension: categoria
    for categoria, extensiones in (
        (Categoria.IMAGENES, ("jpg", "jpeg", "png", "gif", "bmp", "webp", "tiff", "svg", "heic")),
        (
            Categoria.DOCUMENTOS,
            ("pdf", "doc", "docx", "odt", "rtf", "txt", "md",
             "xls", "xlsx", "ods", "csv", "ppt", "pptx", "odp", "epub"),
        ),
        (Categoria.VIDEO, ("mp4", "mkv", "avi", "mov", "wmv", "webm", "mpg", "mpeg")),
        (Categoria.AUDIO, ("mp3", "wav", "flac", "aac", "ogg", "m4a", "wma")),
        (Categoria.COMPRIMIDOS, ("zip", "rar", "7z", "tar", "gz", "bz2", "xz")),
    )
    for extension in extensiones
}


def extension(nombre: str) -> str:
    """Última extensión en minúscula, o cadena vacía si el nombre no tiene.

    Carecen de extensión tanto un nombre sin punto como uno que solo lo lleve al
    principio, como `.gitignore`, o al final (RF-6); excluir los ocultos
    corresponde al recorrido. El informe reutiliza esta regla para agrupar las
    extensiones desconocidas (RF-8).
    """
    base, punto, ultima = nombre.rpartition(".")
    if not punto or not base or not ultima:
        return ""
    return ultima.lower()


def clasificar(nombre: str) -> Categoria:
    """Devuelve la categoría del nombre indicado según su última extensión.

    La comparación no distingue mayúsculas y una extensión ajena al mapa sitúa
    el archivo en «otros» (RF-5).
    """
    ultima = extension(nombre)
    if not ultima:
        return Categoria.SIN_EXTENSION
    return CATEGORIA_POR_EXTENSION.get(ultima, Categoria.OTROS)
