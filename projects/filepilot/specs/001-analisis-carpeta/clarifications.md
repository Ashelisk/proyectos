# Clarificación — Análisis e informe de una carpeta

**Resultado: lista salvo las partes indicadas.** Revisión documental de [spec.md](spec.md) y [plan.md](plan.md), versión `a9c39c4`, contrastada con la [constitución](../../docs/constitution.md). La spec necesita alinear RF-12 con RF-13; el plan requiere completar los contratos y verificaciones indicados antes de cerrar las tareas afectadas. No se han modificado la spec ni el plan ni ejecutado código de producto.

El alcance de solo lectura sigue siendo coherente con la constitución. Se conservan las decisiones cerradas de la especificación: analizar e informar sin mover nada, clasificación por extensión, primer nivel con opción recursiva, resumen en consola y exclusiones contabilizadas.

## Hallazgos abiertos

### CL-9 — Código de salida cuando no queda ningún archivo analizable

- **Prioridad media · parcialmente resuelto · contradicción.** Spec: RF-1, RF-12 y RF-13, líneas 19, 46 y 58; plan, líneas 42–45.
- **Escenario e impacto:** la raíz es legible, pero su único archivo desaparece antes de obtener el tamaño. RF-12 exige cero porque no hay archivos analizables; RF-13 exige tres porque hay un error de lectura. El plan aplica tres. Dos pruebas derivadas de la spec esperarían resultados incompatibles.
- **Corrección necesaria:** extender a RF-12 la excepción de RF-13, ya recogida en RF-1 y en el plan. Una carpeta vacía o con solo exclusiones voluntarias sigue terminando en cero; con fallos por permisos o lectura, en tres aunque no se clasifique ningún archivo. No requiere redefinir el alcance.

### CL-13 — El contrato de omisiones pierde la causa del fallo

- **Prioridad media · abierto · contrato técnico incompleto.** Plan, líneas 28–32 y 47; RF-13 y RNF-3.
- **Escenario e impacto:** una desaparición y un fallo de E/S se reducen a `EntradaOmitida(ruta, error_lectura)`. Ese dato permite contar, pero no distinguir la causa concreta que debe mostrar el aviso.
- **Corrección necesaria:** conservar el diagnóstico del fallo en el resultado o definir otra vía explícita hasta quien emite el aviso. Separar el motivo del recuento de la causa comunicada y asignar la responsabilidad de emitirla; no reconstruirla por suposición.

### CL-14 — Versión mínima sin justificación de mantenimiento

- **Prioridad media · abierto · riesgo técnico.** Plan, líneas 15 y 63; constitución, principios 2 y 7.
- **Escenario e impacto:** admitir Python 3.9 obliga a mantener una combinación antigua de intérprete y herramientas. Python 3.9 terminó su soporte oficial el 31 de octubre de 2025 y pytest 9 requiere Python 3.10 o superior. El plan no concreta una combinación verificable ni una necesidad de compatibilidad heredada. Fuentes: [ciclo de Python 3.9](https://peps.python.org/pep-0596/) y [compatibilidad de pytest](https://docs.pytest.org/en/stable/backwards-compatibility.html#python-version-support).
- **Corrección necesaria:** justificar la versión mínima por soporte y distribución, y concretar versiones compatibles de desarrollo. Preferir una versión mantenida si no hay una necesidad documentada de 3.9; no confundir compatibilidad sintáctica con soporte vigente.

### CL-15 — Degradación silenciosa de la detección de ocultos

- **Prioridad media · abierto · conflicto entre plan y spec.** Plan, líneas 57 y 81; RF-15.
- **Escenario e impacto:** en la alternativa prevista por el plan para Windows sin `st_file_attributes`, un archivo con atributo oculto y sin punto inicial se clasificaría como visible. RF-15 exige reconocer ese atributo, sin excepciones.
- **Corrección necesaria:** limitar la ausencia tolerada a plataformas donde ese atributo no aplica. En Windows no debe interpretarse un dato no disponible como «visible»; definir una detección compatible o comunicar la imposibilidad de examinarlo. Python documenta el atributo en Windows desde 3.5: [metadatos de archivos](https://docs.python.org/3.9/library/os.html#os.stat_result.st_file_attributes).

### CL-16 — Verificación insuficiente de lectura y fallos

- **Prioridad media · abierto · cobertura incompleta.** Plan, líneas 67–79; RF-10 y RF-13.
- **Escenario e impacto:** abrir un archivo solo para leerlo deja intactas sus rutas, tamaños y fechas de modificación; la instantánea prevista aprobaría una implementación que incumple RF-10. Tampoco se concreta cómo provocar de forma repetible una desaparición o un fallo de E/S para verificar la continuación y el diagnóstico de RF-13.
- **Corrección necesaria:** mantener las pruebas con árboles temporales y añadir una comprobación que detecte aperturas de contenido por la aplicación. Introducir fallos controlados en la consulta de metadatos o enumeración y comprobar continuación, ruta y causa en la salida de error, recuento único y código tres, incluido el caso sin archivos analizables. Las pruebas simuladas complementan, no acreditan por sí solas, los permisos reales de cada plataforma.

### CL-17 — Justificación imprecisa de las APIs de recorrido

- **Prioridad baja · abierto · precisión técnica; no bloquea la arquitectura.** Plan, líneas 15, 53 y 75.
- **Escenario e impacto:** el texto presenta los metadatos de `scandir` como una única consulta en todas las plataformas y atribuye a `walk` una limitación absoluta de diagnóstico. También trata los privilegios administrativos como necesarios en todo Windows. Esas premisas pueden inducir comprobaciones o descartes incorrectos.
- **Corrección necesaria:** mantener `scandir` si conviene al control por entrada, precisando que `DirEntry.stat()` consulta el sistema en Unix y que `walk` permite gestionar errores de enumeración con `onerror` y consultar cada archivo. La creación de enlaces en Windows también puede funcionar sin elevación con modo de desarrollador; omitir la prueba solo cuando no pueda prepararse. Fuentes: [scandir](https://docs.python.org/3.9/library/os.html#os.scandir), [walk](https://docs.python.org/3.9/library/os.html#os.walk) y [symlink](https://docs.python.org/3.9/library/os.html#os.symlink).

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

RF-2 y RF-11 separan el código de salida uno, para el uso incorrecto del comando, del código dos, para las causas de ruta enumeradas: inexistente, no es un directorio o lectura no permitida. RF-12 describe el informe sin archivos analizables; su relación con el código tres se revisa en CL-9.

## Cierre de la revisión

CL-1 a CL-8 y CL-10 a CL-12 conservan sus resoluciones. CL-9 requiere coherencia entre requisitos; CL-13 a CL-16 requieren ajustes técnicos, y CL-17 corrige la justificación sin exigir otra arquitectura. La división en cuatro componentes, la biblioteca estándar en ejecución y las pruebas con datos desechables son proporcionadas. No es necesario reiniciar la definición del producto. Esta revisión no valida implementación ni compatibilidad real con plataformas.
