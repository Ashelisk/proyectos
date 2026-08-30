# Clarificación — Análisis e informe de una carpeta

**Resultado: lista para planificación.** Revisión documental de [spec.md](spec.md) contrastada con la [constitución](../../docs/constitution.md). Los doce hallazgos están resueltos en los requisitos; no quedan decisiones abiertas dentro del alcance revisado. No se ha implementado ni ejecutado código de producto.

El alcance de solo lectura sigue siendo coherente con la constitución. Se conservan las decisiones cerradas de la especificación: analizar e informar sin mover nada, clasificación por extensión, primer nivel con opción recursiva, resumen en consola y exclusiones contabilizadas.

## Hallazgos resueltos

### CL-8 — Carpeta oculta indicada como raíz

- **Prioridad media · resuelto.** RF-1, RF-14, RF-15 y RF-16.
- **Escenario e impacto:** `filepilot analizar .datos` sobre una carpeta legible con archivos visibles podía analizarla u omitirla según se aplicase la exclusión de ocultos a la raíz.
- **Decisión:** RF-14 exige analizar la raíz aunque sea oculta, también cuando se accede a ella mediante el enlace permitido por RF-16. Las exclusiones se aplican a su contenido. `--incluir-ocultos` elimina solo la exclusión por ocultación, sin desactivar las demás.

### CL-5 — Comunicación de fallos durante el análisis

- **Prioridad media · resuelto.** RF-9, RF-10, RF-13 y RNF-3.
- **Escenario e impacto:** si `informe.pdf` desaparece entre la enumeración y la consulta de tamaño, un recuento agregado no identifica el archivo afectado ni explica su causa concreta.
- **Decisión:** RF-10 usa nombre y tamaño sin abrir el contenido. RF-9 distingue los errores de lectura de la falta de permisos. RF-13 exige continuar, contabilizar la entrada con su motivo real y emitir por cada fallo un aviso en la salida de error con ruta y causa en español, además del recuento del resumen.

### CL-1 — Clasificación delegada al plan

- **Prioridad alta · resuelto.** RF-5.
- **Escenario e impacto:** dos implementaciones podían asignar `.svg` o `.csv` a una categoría específica o a «otros». Ambas encajaban en el texto y producían informes distintos.
- **Decisión:** RF-5 incorpora el mapa de extensiones de las seis categorías, con `svg` en imágenes y `csv` en documentos, y se aplica a la última extensión sin distinguir mayúsculas. Ampliar el mapa exige actualizar antes ese requisito.

### CL-2 — Alcance de las exclusiones en el recorrido

- **Prioridad alta · resuelto.** RF-3, RF-9, RF-14, RF-15 y RF-16.
- **Escenario e impacto:** con `--recursivo`, una carpeta `.privada` con `foto.jpg` podía recorrerse o no, y no estaba definido si se rechazaba una ruta inicial que fuera un enlace a un directorio.
- **Decisión:** RF-15 define oculto como el nombre que empieza por punto en cualquier plataforma y, en Windows, también el atributo de sistema. Las carpetas ocultas encontradas durante el recorrido no se recorren; RF-14 añade `--incluir-ocultos` para examinarlas. RF-16 resuelve la ruta inicial cuando es un enlace a un directorio y limita la exclusión de enlaces a lo encontrado durante el recorrido. La interacción con una raíz oculta se examina en CL-8.

### CL-3 — Recuento de elementos omitidos

- **Prioridad media · resuelto.** RF-4 y RF-9.
- **Escenario e impacto:** un enlace simbólico llamado `.enlace` cumplía dos motivos y podía contarse dos veces; una carpeta inaccesible no permitía conocer sus descendientes.
- **Decisión:** RF-9 asigna un único motivo por entrada con la prioridad oculto → enlace → sin permiso → error de lectura, de forma que los motivos suman el total de omitidos. RF-4 fija que una subcarpeta no recorrida cuenta entre las encontradas y como una única entrada omitida, sin estimar su contenido.

### CL-4 — Significado del destino propuesto

- **Prioridad media · resuelto.** RF-7.
- **Escenario e impacto:** al analizar recursivamente `entrada/sub/foto.jpg`, la fila podía proponer `entrada/imagenes` o una carpeta dentro de `sub`.
- **Decisión:** RF-7 fija un destino único por grupo, `<ruta analizada>/<categoría>`, siempre en la raíz analizada, también en modo recursivo.

### CL-6 — Extensiones más frecuentes

- **Prioridad media · resuelto.** RF-8.
- **Escenario e impacto:** varias extensiones de «otros» con el mismo recuento producían listas distintas según la implementación.
- **Decisión:** RF-8 mantiene el detalle, limitado a cinco extensiones, ordenadas por recuento descendente y por orden alfabético en caso de empate.

### CL-7 — Caso de una carpeta que solo contiene subcarpetas

- **Prioridad baja · resuelto.** RF-3, RF-12 y casos límite.
- **Escenario e impacto:** el caso límite remitía a «no hay archivos» aunque con `--recursivo` esas subcarpetas pudieran contener archivos analizables.
- **Decisión:** los casos límite distinguen ahora ambos modos y RF-12 se refiere a la ausencia de archivos analizables dentro del alcance del recorrido.

### CL-9 — Código de salida con fallos parciales

- **Prioridad media · resuelto.** RF-1 y RF-13.
- **Escenario e impacto:** un análisis que emite su informe pero deja tres archivos sin leer podía terminar en cero o en un código de aviso; un script no podía distinguir un informe completo de otro con lagunas.
- **Decisión:** RF-13 fija el código tres cuando el informe se emite con entradas omitidas por falta de permisos o por error de lectura. Las omisiones por ocultación o por enlace no alteran el código, y RF-1 remite a esa excepción.

### CL-10 — Nombres de las carpetas propuestas

- **Prioridad media · resuelto.** RF-6 y RF-7.
- **Escenario e impacto:** RF-7 fijaba la ubicación del destino pero no su nombre literal, y el grupo «sin extensión» no es una categoría del mapa de RF-5, por lo que su carpeta quedaba indefinida.
- **Decisión:** RF-7 enumera las siete carpetas propuestas —`imagenes`, `documentos`, `video`, `audio`, `comprimidos`, `otros` y `sin-extension`—, sin acentos y en minúscula, mientras el informe muestra la categoría acentuada.

### CL-11 — Subcarpetas excluidas en modo no recursivo

- **Prioridad baja · resuelto.** RF-4 y RF-9.
- **Escenario e impacto:** sin `--recursivo`, una subcarpeta `.privada` de primer nivel podía contarse como entrada omitida por oculta, aunque en ese modo tampoco se habría recorrido una subcarpeta visible.
- **Decisión:** RF-4 precisa que solo el modo recursivo contabiliza subcarpetas excluidas como omitidas; en modo no recursivo las subcarpetas únicamente suman al recuento de encontradas.

### CL-12 — Formato del tamaño

- **Prioridad baja · resuelto.** RF-7.
- **Escenario e impacto:** «tamaño total» admitía bytes exactos o unidades legibles, con resultados distintos en la misma carpeta.
- **Decisión:** RF-7 fija la unidad adecuada en base 1024 con un decimal, por ejemplo `1,4 MB`.

## Correcciones asociadas

RF-2 y RF-11 separan el código de salida uno, para el uso incorrecto del comando, del código dos, para las causas de ruta enumeradas: inexistente, no es un directorio o lectura no permitida. RF-12 fija código cero y describe el informe cuando no hay archivos analizables.

## Cierre de la revisión

CL-1 a CL-12 están resueltos. El siguiente paso es preparar el plan técnico a partir de la spec. Esta revisión no valida la implementación ni la compatibilidad con las plataformas de RNF-2.
