# Especificación 001 — Análisis e informe de una carpeta

## Contexto y objetivo

Primera funcionalidad de FilePilot: examinar una carpeta, clasificar sus archivos por extensión y mostrar la organización que se propondría, sin modificar nada. Permite conocer el contenido de una carpeta desordenada y valorar el reparto antes de que exista cualquier operación que mueva archivos.

## Usuarios e historias

Persona que administra sus propios archivos desde la terminal, en Linux, macOS o Windows.

- Quiere saber qué hay en una carpeta acumulada y cuánto ocupa cada tipo de contenido.
- Quiere ver el reparto propuesto por FilePilot antes de confiarle sus archivos.
- Quiere que la herramienta le indique qué elementos no ha podido examinar, en lugar de ignorarlos sin avisar.

## Requisitos funcionales

- RF-1: Cuando se ejecute `filepilot analizar <ruta>` sobre un directorio legible, la herramienta emitirá en la salida estándar un informe de su contenido y terminará con código cero.
- RF-2: Si se omite la ruta, la herramienta mostrará el uso del comando en la salida de error y terminará con código distinto de cero, sin analizar ningún directorio.
- RF-3: Por defecto solo se examinarán los elementos del primer nivel del directorio indicado. Cuando se use la opción `--recursivo`, se examinarán también los de todas sus subcarpetas.
- RF-4: Las subcarpetas nunca se clasificarán como archivos. El informe indicará cuántas se encontraron; en modo recursivo, cuántas se recorrieron.
- RF-5: Cada archivo examinado se asignará a una de seis categorías según su extensión, sin distinguir mayúsculas de minúsculas: imágenes, documentos, vídeo, audio, comprimidos y otros. La extensión no reconocida sitúa el archivo en «otros».
- RF-6: Los archivos sin extensión formarán el grupo «sin extensión», independiente de «otros».
- RF-7: El informe presentará una fila por grupo con recuento de archivos, tamaño total y la carpeta de destino que se propondría para ese grupo, más una fila de totales. Los grupos sin archivos podrán omitirse de la tabla.
- RF-8: Cuando existan archivos en «otros», el informe indicará las extensiones no reconocidas más frecuentes con su recuento.
- RF-9: No se clasificarán los archivos ocultos, los enlaces simbólicos ni los elementos cuya lectura no esté permitida. El informe indicará cuántos elementos se omitieron, desglosado por cada uno de esos tres motivos. Ningún elemento se omitirá sin aparecer en ese recuento.
- RF-10: El análisis será de solo lectura: la herramienta no creará, moverá, renombrará ni eliminará ningún archivo ni directorio, incluidas las carpetas de destino que propone.
- RF-11: Si la ruta indicada no existe, no es un directorio o su lectura no está permitida, la herramienta describirá el problema en la salida de error y terminará con código distinto de cero, sin emitir informe.
- RF-12: Si el directorio no contiene ningún archivo analizable, la herramienta indicará que no hay archivos y terminará con código cero. Esta situación no es un error.
- RF-13: Cuando un elemento resulte ilegible durante el recorrido, el análisis continuará con los demás y ese elemento se contabilizará entre los omitidos conforme a RF-9.

## Requisitos no funcionales

- RNF-1: Funcionamiento local: sin acceso a red, cuentas ni servicios externos.
- RNF-2: Ejecución en Linux, macOS y Windows, admitiendo rutas relativas y absolutas y nombres de archivo con caracteres no ASCII.
- RNF-3: Los mensajes de error identificarán la ruta afectada y la causa, en español.

## Casos límite

- Directorio vacío o con solo subcarpetas: RF-12.
- Elementos ocultos, enlaces simbólicos y permisos denegados durante el recorrido: RF-9 y RF-13.
- Archivos con varios puntos en el nombre o con la extensión en mayúsculas: RF-5, que atiende a la última extensión sin distinguir mayúsculas.
- Nombres que empiezan por punto y carecen de otra extensión: se tratan como ocultos según RF-9, antes que como «sin extensión».

## Fuera de alcance

Mover u organizar archivos, confirmación interactiva de operaciones, resolución de conflictos de nombre en destino, detección de duplicados, reglas de clasificación configurables, salida en formato JSON y deshacer operaciones. La organización efectiva de archivos corresponde a una especificación posterior.

## Criterios de finalización

Pruebas de comportamiento que cubran cada RF sobre carpetas temporales desechables, incluida una comprobación de que el árbol de entrada queda intacto tras el análisis (RF-10) y otra de los códigos de salida (RF-1, RF-2, RF-11, RF-12). La validación indicará en qué plataformas de RNF-2 se ejecutaron realmente; no se afirmará compatibilidad sin evidencia.

## Dudas abiertas

- La lista de extensiones de cada categoría de RF-5 se fijará al planificar como conjunto inicial ampliable, no como clasificación cerrada.
- El criterio de «más frecuentes» de RF-8 (cuántas extensiones mostrar) queda por concretar.
