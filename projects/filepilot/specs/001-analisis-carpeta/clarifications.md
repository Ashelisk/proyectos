# Clarificación — Análisis e informe de una carpeta

**Resultado: lista para planificación.** El plan técnico también está revisado y listo para tareas. Se han contrastado [spec.md](spec.md), [plan.md](plan.md) y la [constitución](../../docs/constitution.md): los diecisiete hallazgos están resueltos y no quedan bloqueos dentro del alcance revisado. La comprobación abarca requisitos, contratos y verificaciones previstas; no se ha implementado ni ejecutado código de producto.

El alcance de solo lectura sigue siendo coherente con la constitución. Se conservan las decisiones cerradas de la especificación: analizar e informar sin mover nada, clasificación por extensión, primer nivel con opción recursiva, resumen en consola y exclusiones contabilizadas.

## Hallazgos resueltos

### CL-9 — Código de salida cuando no queda ningún archivo analizable

- **Prioridad media · resuelto · contradicción.** RF-1, RF-12 y RF-13.
- **Escenario e impacto:** la raíz es legible, pero su único archivo desaparece antes de obtener el tamaño. RF-12 exigía cero por no haber archivos analizables y RF-13 tres por el error de lectura; dos pruebas derivadas de la spec esperarían resultados incompatibles.
- **Decisión:** RF-12 incorpora la excepción de RF-13. Una carpeta vacía o con solo exclusiones voluntarias termina en cero; con omisiones por permiso o por error de lectura termina en tres aunque no se clasifique ningún archivo.

### CL-13 — El contrato de omisiones pierde la causa del fallo

- **Prioridad media · resuelto · contrato técnico incompleto.** Plan: datos y contratos; RF-13 y RNF-3.
- **Escenario e impacto:** una desaparición y un fallo de entrada/salida se reducían a un mismo motivo `error_lectura`, suficiente para contar pero no para redactar el aviso con su causa concreta.
- **Decisión:** `EntradaOmitida.detalle` expresa en español la causa real a partir del tipo y código del fallo, sin copiar el idioma del sistema; `motivo` determina el recuento y el código de salida. El recorrido devuelve estos datos y `cli.py` emite los avisos. La verificación incluye errores cuyo texto original esté en otro idioma.

### CL-14 — Versión mínima sin justificación de mantenimiento

- **Prioridad media · resuelto · riesgo técnico.** Plan: enfoque y pruebas; constitución, principios 2 y 7.
- **Escenario e impacto:** admitir Python 3.9 obligaba a mantener una combinación sin soporte desde octubre de 2025, incompatible además con las versiones actuales de pytest, que exigen 3.10 o superior.
- **Decisión:** Python 3.11 es la versión mínima, con soporte de seguridad previsto hasta octubre de 2027. El plan prevé pruebas con la versión mínima y la última estable de cada plataforma, registrando las versiones realmente verificadas.

### CL-15 — Degradación silenciosa de la detección de ocultos

- **Prioridad media · resuelto · conflicto entre plan y spec.** RF-9, RF-13 y RF-15.
- **Escenario e impacto:** ante un atributo no consultable, el plan permitía clasificar como visible un archivo oculto de Windows sin punto inicial, contra lo exigido por RF-15.
- **Decisión:** RF-15 impide dar por visible un elemento cuyo atributo no pueda consultarse en Windows y conserva la prioridad de RF-9: falta de permisos cuando esa sea la causa y error de lectura para los demás fallos, con aviso y código tres. Fuera de Windows el atributo no es aplicable. La misma regla figura en el plan y en sus verificaciones.

### CL-16 — Verificación insuficiente de lectura y fallos

- **Prioridad media · resuelto · cobertura incompleta.** Plan: verificación; RF-10 y RF-13.
- **Escenario e impacto:** la instantánea de rutas, tamaños y fechas aprobaría una implementación que abriera el contenido de los archivos, y no había forma repetible de provocar una desaparición o un error de entrada/salida.
- **Decisión:** el plan compara el árbol antes y después del análisis y registra las aperturas de contenido en una prueba aislada. Los fallos inyectados verifican continuación, diagnóstico en español, recuento único y código tres, incluido el caso sin archivos analizables. Estas pruebas complementan las de permisos reales, que se marcarán como omitidas si el entorno no permite prepararlas.

### CL-17 — Justificación imprecisa de las APIs de recorrido

- **Prioridad baja · resuelto · precisión técnica.** Plan: enfoque, decisiones y verificación.
- **Escenario e impacto:** el plan presentaba los metadatos de `scandir` como una consulta única en todas las plataformas, atribuía a `os.walk` una limitación absoluta de diagnóstico y daba por necesaria la elevación de privilegios en Windows para crear enlaces.
- **Decisión:** se mantiene `scandir` por el control entrada a entrada, precisando que en Unix `DirEntry.stat()` consulta el sistema la primera vez y guarda el resultado, que `os.walk` admite `onerror` y permite consultar cada archivo pero agrupa los directorios en listas, y que en Windows la creación de enlaces también funciona con el modo de desarrollador: la prueba se intenta y solo se omite si la creación falla.

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
- **Decisión:** RF-9 asigna un único motivo por entrada con la prioridad oculto → enlace → sin permiso → error de lectura, de forma que los motivos suman el total. En modo recursivo, RF-4 cuenta una subcarpeta excluida como encontrada y como una entrada omitida, sin estimar su contenido; en modo no recursivo solo cuenta como encontrada.

### CL-4 — Significado del destino propuesto

- **Prioridad media · resuelto.** RF-7.
- **Escenario e impacto:** al analizar recursivamente `entrada/sub/foto.jpg`, la fila podía proponer `entrada/imagenes` o una carpeta dentro de `sub`.
- **Decisión:** RF-7 fija un destino único por grupo, `<ruta analizada>/<carpeta>`, siempre en la raíz analizada, también en modo recursivo. Los nombres literales se recogen en RF-7 y CL-10.

### CL-6 — Extensiones más frecuentes

- **Prioridad media · resuelto.** RF-8.
- **Escenario e impacto:** varias extensiones de «otros» con el mismo recuento producían listas distintas según la implementación.
- **Decisión:** RF-8 mantiene el detalle, limitado a cinco extensiones, ordenadas por recuento descendente y por orden alfabético en caso de empate.

### CL-7 — Caso de una carpeta que solo contiene subcarpetas

- **Prioridad baja · resuelto.** RF-3, RF-12 y casos límite.
- **Escenario e impacto:** el caso límite remitía a «no hay archivos» aunque con `--recursivo` esas subcarpetas pudieran contener archivos analizables.
- **Decisión:** los casos límite distinguen ahora ambos modos y RF-12 se refiere a la ausencia de archivos analizables dentro del alcance del recorrido.

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

RF-2 y RF-11 separan el código de salida uno, para el uso incorrecto del comando, del código dos, para las causas de ruta enumeradas: inexistente, no es un directorio o lectura no permitida. RF-12 describe el informe sin archivos analizables y remite al código tres de RF-13 conforme a CL-9.

## Cierre de la revisión

CL-1 a CL-17 están resueltos en la spec y el plan vigentes. La división en cuatro componentes, la biblioteca estándar en ejecución y las pruebas con datos desechables se conservan sin cambios; el siguiente paso es descomponer el plan en tareas. Esta revisión no valida implementación ni compatibilidad real con plataformas.
