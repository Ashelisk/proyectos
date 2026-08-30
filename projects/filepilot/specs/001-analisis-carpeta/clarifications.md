# Clarificación — Análisis e informe de una carpeta

**Resultado: lista para planificación.** Revisión documental de [spec.md](spec.md) contrastada con la [constitución](../../docs/constitution.md). Los siete hallazgos están resueltos e incorporados a los requisitos; no queda ninguna decisión abierta. No se ha modificado ni ejecutado código de producto.

El alcance de solo lectura sigue siendo coherente con la constitución. Se conservan las decisiones cerradas de la especificación: analizar e informar sin mover nada, clasificación por extensión, primer nivel con opción recursiva, resumen en consola y exclusiones contabilizadas.

## Hallazgos resueltos

## CL-1 — Clasificación delegada al plan

- **Prioridad alta · resuelto.** RF-5.
- **Escenario e impacto:** dos implementaciones podían asignar `.svg` o `.csv` a una categoría específica o a «otros». Ambas encajaban en el texto y producían informes distintos.
- **Decisión:** RF-5 incorpora el mapa de extensiones de las seis categorías, con `svg` en imágenes y `csv` en documentos, y se aplica a la última extensión sin distinguir mayúsculas. Ampliar el mapa exige actualizar antes ese requisito.

## CL-2 — Alcance de las exclusiones en el recorrido

- **Prioridad alta · resuelto.** RF-3, RF-9, RF-14, RF-15 y RF-16.
- **Escenario e impacto:** con `--recursivo`, una carpeta `.privada` con `foto.jpg` podía recorrerse o no, y no estaba definido si se rechazaba una ruta inicial que fuera un enlace a un directorio.
- **Decisión:** RF-15 define oculto como el nombre que empieza por punto en cualquier plataforma y, en Windows, también el atributo de sistema. Las carpetas ocultas no se recorren; RF-14 añade `--incluir-ocultos` para examinarlas. RF-16 resuelve la ruta inicial cuando es un enlace a un directorio y limita la exclusión de enlaces a lo encontrado durante el recorrido.

## CL-3 — Recuento de elementos omitidos

- **Prioridad media · resuelto.** RF-4 y RF-9.
- **Escenario e impacto:** un enlace simbólico llamado `.enlace` cumplía dos motivos y podía contarse dos veces; una carpeta inaccesible no permitía conocer sus descendientes.
- **Decisión:** RF-9 asigna un único motivo por entrada con la prioridad oculto → enlace → sin permiso → error de lectura, de forma que los motivos suman el total de omitidos. RF-4 fija que una subcarpeta no recorrida cuenta entre las encontradas y como una única entrada omitida, sin estimar su contenido.

## CL-4 — Significado del destino propuesto

- **Prioridad media · resuelto.** RF-7.
- **Escenario e impacto:** al analizar recursivamente `entrada/sub/foto.jpg`, la fila podía proponer `entrada/imagenes` o una carpeta dentro de `sub`.
- **Decisión:** RF-7 fija un destino único por grupo, `<ruta analizada>/<categoría>`, siempre en la raíz analizada, también en modo recursivo.

## CL-5 — Lectura y fallos durante el análisis

- **Prioridad media · resuelto.** RF-9, RF-10 y RF-13.
- **Escenario e impacto:** no estaba definido qué información debía poder leerse, y un archivo que desaparecía durante el recorrido podía atribuirse a una falta de permisos que no era la causa.
- **Decisión:** RF-10 declara analizable el archivo cuyo nombre y tamaño pueden obtenerse, sin abrir su contenido. RF-9 añade «error de lectura» como cuarto motivo y RF-13 obliga a continuar el análisis conservando la causa real y la ruta afectada.

## CL-6 — Extensiones más frecuentes

- **Prioridad media · resuelto.** RF-8.
- **Escenario e impacto:** varias extensiones de «otros» con el mismo recuento producían listas distintas según la implementación.
- **Decisión:** RF-8 mantiene el detalle, limitado a cinco extensiones, ordenadas por recuento descendente y por orden alfabético en caso de empate.

## CL-7 — Caso de una carpeta que solo contiene subcarpetas

- **Prioridad baja · resuelto.** RF-3, RF-12 y casos límite.
- **Escenario e impacto:** el caso límite remitía a «no hay archivos» aunque con `--recursivo` esas subcarpetas pudieran contener archivos analizables.
- **Decisión:** los casos límite distinguen ahora ambos modos y RF-12 se refiere a la ausencia de archivos analizables dentro del alcance del recorrido.

## Correcciones asociadas

Al incorporar las respuestas se precisaron además dos contratos que dependían de ellas: RF-2 y RF-11 separan el código de salida uno, para el uso incorrecto del comando, del código dos, para cualquier problema con la ruta indicada, cuyo mensaje distingue si no existe, no es un directorio o no puede leerse. RF-12 describe qué muestra el informe cuando no hay archivos analizables.

## Cierre de la revisión

Todos los hallazgos están cerrados y los requisitos afectados vuelven a ser coherentes entre sí y con la constitución. Esta revisión es documental: no valida la implementación ni la compatibilidad con las plataformas de RNF-2, y no añade requisitos de movimiento, duplicados, configuración o recuperación fuera del alcance de la especificación.
