# Especificación 001 — Análisis e informe de una carpeta

## Contexto y objetivo

Primera funcionalidad de FilePilot: examinar una carpeta, clasificar sus archivos por extensión y mostrar la organización que se propondría, sin modificar nada. Permite conocer el contenido de una carpeta desordenada y valorar el reparto antes de que exista cualquier operación que mueva archivos.

## Usuarios e historias

Persona que administra sus propios archivos desde la terminal, en Linux o Windows.

- Quiere saber qué hay en una carpeta acumulada y cuánto ocupa cada tipo de contenido.
- Quiere ver el reparto propuesto por FilePilot antes de confiarle sus archivos.
- Quiere que la herramienta le indique qué elementos no ha podido examinar, en lugar de ignorarlos sin avisar.

## Requisitos funcionales

### Invocación y recorrido

- RF-1: Cuando se ejecute `filepilot analizar <ruta>` sobre un directorio legible, la herramienta emitirá en la salida estándar un informe de su contenido y terminará con código cero, salvo que se aplique el código tres de RF-13.
- RF-2: Ante un uso incorrecto —ruta omitida u opción desconocida—, la herramienta mostrará el uso del comando en la salida de error y terminará con código uno, sin analizar ningún directorio.
- RF-3: Por defecto solo se examinarán los elementos del primer nivel del directorio indicado. Cuando se use la opción `--recursivo`, se examinarán también los de todas sus subcarpetas no excluidas.
- RF-4: Las subcarpetas nunca se clasificarán como archivos. El informe indicará cuántas se encontraron y, en modo recursivo, cuántas se recorrieron. En modo recursivo, una subcarpeta que no se recorre por exclusión se cuenta entre las encontradas y además como una única entrada omitida, sin estimar su contenido. En modo no recursivo ninguna subcarpeta se recorre, por lo que ninguna se contabiliza como omitida.
- RF-16: Cuando la ruta indicada sea un enlace simbólico a un directorio, se resolverá y se analizará su destino. La exclusión de enlaces de RF-9 se aplica únicamente a los elementos encontrados durante el recorrido.

### Clasificación

- RF-5: Cada archivo examinado se asignará a una de seis categorías según su última extensión, sin distinguir mayúsculas de minúsculas, conforme a este mapa. Una extensión no incluida sitúa el archivo en «otros».

  | Categoría | Extensiones |
  | --- | --- |
  | Imágenes | jpg, jpeg, png, gif, bmp, webp, tiff, svg, heic |
  | Documentos | pdf, doc, docx, odt, rtf, txt, md, xls, xlsx, ods, csv, ppt, pptx, odp, epub |
  | Vídeo | mp4, mkv, avi, mov, wmv, webm, mpg, mpeg |
  | Audio | mp3, wav, flac, aac, ogg, m4a, wma |
  | Comprimidos | zip, rar, 7z, tar, gz, bz2, xz |
  | Otros | cualquier otra extensión |

  El mapa es ampliable: añadir o mover una extensión cambia el comportamiento observable y exige actualizar antes este requisito.

- RF-6: Los archivos sin extensión formarán el grupo «sin extensión», independiente de «otros».

### Informe

- RF-7: El informe presentará una fila por grupo con recuento de archivos, tamaño total y la carpeta de destino que se propondría, más una fila de totales. El destino de cada grupo es `<ruta analizada>/<carpeta>`, siempre en la raíz analizada: en modo recursivo, los archivos de las subcarpetas comparten ese mismo destino. Las carpetas propuestas son `imagenes`, `documentos`, `video`, `audio`, `comprimidos`, `otros` y `sin-extension`, sin acentos y en minúscula, aunque el informe muestre el nombre de la categoría acentuado. El tamaño total se expresará en la unidad adecuada en base 1024 con un decimal, por ejemplo `1,4 MB`. Los grupos sin archivos podrán omitirse de la tabla.
- RF-8: Cuando existan archivos en «otros», el informe mostrará hasta cinco extensiones no reconocidas con su recuento, ordenadas por recuento descendente y, en caso de empate, alfabéticamente.
- RF-12: Si dentro del alcance del recorrido no hay ningún archivo analizable, la herramienta indicará que no se han encontrado archivos analizables, mostrará los recuentos de omitidos y subcarpetas cuando existan, y terminará con código cero. La ausencia de archivos analizables no es un error; si además alguna entrada quedó omitida por falta de permisos o por error de lectura, se aplica el código tres de RF-13.

### Exclusiones

- RF-9: No se clasificarán los archivos ocultos, los enlaces simbólicos, los elementos cuya lectura no esté permitida ni aquellos cuya lectura falle por otra causa. El informe indicará cuántas entradas se omitieron, desglosado por esos cuatro motivos. Cada entrada omitida se contabilizará una sola vez, aplicando la prioridad oculto → enlace simbólico → sin permiso → error de lectura, de modo que la suma por motivos coincida con el total de omitidos. Ninguna entrada se omitirá sin aparecer en ese recuento.
- RF-15: Se considerará oculto todo elemento cuyo nombre empiece por punto en cualquier plataforma y, además en Windows, todo elemento con el atributo de sistema «oculto». Cuando en Windows ese atributo no pueda consultarse para un elemento, este no se dará por visible: se omitirá respetando la prioridad de RF-9, por falta de permisos si esa es la causa o por error de lectura en los demás fallos, con el aviso de RF-13. Fuera de Windows el atributo no es aplicable y su ausencia no afecta al análisis.
- RF-14: La carpeta raíz indicada se analizará aunque sea oculta, también si se accede a ella mediante el enlace de RF-16. Las exclusiones se aplican a su contenido: sin `--incluir-ocultos`, no se recorren las subcarpetas ocultas ni se enumera su contenido. Con esa opción, los archivos y las carpetas ocultos encontrados se examinan como cualquier otro elemento y no se omiten por ocultación; las demás exclusiones de RF-9 siguen vigentes.

### Seguridad y fallos

- RF-10: El análisis será de solo lectura: la herramienta no creará, moverá, renombrará ni eliminará ningún archivo ni directorio, incluidas las carpetas de destino que propone, y no abrirá el contenido de los archivos. Un archivo se considera analizable cuando pueden obtenerse su nombre y su tamaño.
- RF-11: Si la ruta indicada no existe, no es un directorio o su lectura no está permitida, la herramienta describirá el problema y la ruta afectada en la salida de error y terminará con código dos, sin emitir informe. El mensaje distinguirá cuál de esas tres causas se ha producido. Una ruta vacía se rechazará del mismo modo, indicando que no se ha señalado ninguna carpeta; nunca se interpretará como el directorio actual. Cualquier otro fallo al resolver o leer la carpeta raíz, como un bucle de enlaces o un error de entrada y salida, se comunicará igualmente con código dos indicando la ruta y la causa, en lugar de interrumpir la ejecución.
- RF-13: Cuando un elemento falle durante el recorrido —por ejemplo, si desaparece entre su enumeración y la consulta de su tamaño, o si su lectura da error—, el análisis continuará con los demás y esa entrada se contabilizará entre los omitidos con su motivo real conforme a RF-9. Cada fallo generará además un aviso en la salida de error con la ruta afectada y la causa, en español, conforme a RNF-3; el resumen conservará el recuento correspondiente. Cuando el informe se haya emitido pero alguna entrada haya quedado omitida por falta de permisos o por error de lectura, la herramienta terminará con código tres. Las omisiones por ocultación o por enlace simbólico no alteran el código de salida.

## Requisitos no funcionales

- RNF-1: Funcionamiento local: sin acceso a red, cuentas ni servicios externos.
- RNF-2: Ejecución en Linux y Windows, admitiendo rutas relativas y absolutas y nombres de archivo con caracteres no ASCII.
- RNF-3: Los mensajes de error identificarán la ruta afectada y la causa, en español.

## Casos límite

- Directorio vacío: RF-12. Directorio con solo subcarpetas: sin `--recursivo`, RF-12; con `--recursivo`, se clasifican los archivos que contengan sus subcarpetas según RF-3.
- Directorio en el que todos los elementos quedan excluidos: RF-12 junto con los recuentos de RF-9.
- Elementos ocultos, enlaces simbólicos, permisos denegados y fallos de lectura durante el recorrido: RF-9, RF-13, RF-14 y RF-15.
- Raíz oculta, indicada directamente o mediante un enlace: RF-14 y RF-16; se analiza sin exigir `--incluir-ocultos`, manteniendo las exclusiones para su contenido.
- Ruta vacía, bucle de enlaces o fallo al resolver la raíz: RF-11; ninguno de estos casos analiza el directorio actual ni interrumpe la ejecución con un error sin tratar.
- Archivos con varios puntos en el nombre, como `copia.tar.gz`: RF-5, que atiende a la última extensión.
- Nombres que empiezan por punto y carecen de otra extensión: RF-15 los trata como ocultos antes que como «sin extensión» de RF-6.

## Fuera de alcance

Mover u organizar archivos, confirmación interactiva de operaciones, resolución de conflictos de nombre en destino, detección de duplicados, reglas de clasificación configurables, salida en formato JSON y deshacer operaciones. La organización efectiva de archivos corresponde a una especificación posterior.

## Criterios de finalización

Pruebas de comportamiento que cubran cada RF sobre carpetas temporales desechables, incluidas una comprobación de que el árbol de entrada queda intacto tras el análisis (RF-10), otra de los cuatro códigos de salida (RF-1, RF-2, RF-11, RF-12 y RF-13) y otra del reparto de motivos de exclusión frente a su total (RF-9). La validación indicará en qué plataformas de RNF-2 se ejecutaron realmente; no se afirmará compatibilidad sin evidencia.
