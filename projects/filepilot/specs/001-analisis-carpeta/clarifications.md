# Clarificación — Análisis e informe de una carpeta

**Resultado: necesita decisión.** Revisión documental de [spec.md](spec.md) en el commit `fd4ee8c`, contrastada con la [constitución](../../docs/constitution.md). No se ha modificado la spec ni ejecutado código de producto.

El alcance de solo lectura es coherente con la constitución. La spec identifica requisitos, errores, límites y comprobaciones con datos desechables. Los siguientes puntos impiden cerrar el comportamiento de las partes afectadas; no requieren ampliar la funcionalidad.

## CL-1 — Clasificación delegada al plan

- **Prioridad alta · abierto · decisión pendiente.** RF-5; líneas 21 y 54.
- **Escenario e impacto:** dos implementaciones pueden asignar `.svg` o `.csv` a una categoría específica o a «otros». Ambas encajan en el texto, pero generan informes distintos. El mapa de extensiones determina comportamiento observable y debe estar en la spec; ser ampliable no elimina la necesidad de una lista inicial verificable.
- **Pregunta:** ¿qué extensiones reconoce inicialmente cada categoría? Las ampliaciones posteriores deberán actualizar ese contrato antes de cambiar el comportamiento.

## CL-2 — Alcance de las exclusiones en el recorrido

- **Prioridad alta · abierto · ambigüedad.** RF-3, RF-9, RF-11 y RNF-2; líneas 19, 25, 27, 34 y 42.
- **Escenario e impacto:** con `--recursivo`, una carpeta `.privada` contiene `foto.jpg`. RF-3 incluye todas las subcarpetas, mientras RF-9 excluye archivos ocultos sin precisar si se evita entrar en carpetas ocultas. Tampoco queda definido si se rechaza una ruta inicial que sea un enlace a un directorio. El conjunto examinado puede variar.
- **Pregunta:** ¿qué elementos se consideran ocultos en cada plataforma y qué exclusiones impiden recorrer un directorio, incluida la ruta inicial? Windows dispone de un atributo de archivo oculto; debe aclararse si también determina la exclusión. Referencia técnica: [atributos de archivo en Python](https://docs.python.org/3/library/stat.html#stat.FILE_ATTRIBUTE_HIDDEN).

## CL-3 — Recuento de elementos omitidos

- **Prioridad media · abierto · ambigüedad.** RF-4 y RF-9; líneas 20 y 25.
- **Escenario e impacto:** un enlace simbólico llamado `.enlace` cumple dos motivos de exclusión. Puede contarse una o dos veces según la implementación. Una carpeta inaccesible tampoco permite conocer cuántos descendientes contiene; «ningún elemento» no delimita si se refiere solo a entradas encontradas. Los totales no tienen un resultado único.
- **Pregunta:** ¿se asigna un único motivo a cada entrada omitida y con qué prioridad? Precisar también si una carpeta no recorrida cuenta como una entrada, sin contabilizar descendientes desconocidos, y cómo se relaciona con el recuento de subcarpetas.

## CL-4 — Significado del destino propuesto

- **Prioridad media · abierto · contrato incompleto.** RF-7; línea 23.
- **Escenario e impacto:** al analizar recursivamente `entrada/sub/foto.jpg`, la fila podría proponer `entrada/imagenes` o una carpeta dentro de `sub`. La spec no fija nombres ni ubicación base de los destinos. Aunque no se muevan archivos, la propuesta mostrada cambia.
- **Pregunta:** ¿qué carpeta se propone para cada grupo y respecto a qué ubicación? Esta aclaración no necesita resolver conflictos de nombres ni diseñar operaciones de movimiento, excluidos de esta entrega.

## CL-5 — Lectura y fallos durante el análisis

- **Prioridad media · abierto · ambigüedad.** RF-9, RF-13 y RNF-3; líneas 25, 29 y 35.
- **Escenario e impacto:** un archivo permite consultar nombre y tamaño, pero no abrir su contenido; no se define si es analizable. Si desaparece entre la enumeración y la consulta de tamaño, RF-13 exige continuar ante elementos ilegibles, pero RF-9 solo ofrece oculto, enlace o lectura no permitida como motivos. Se puede terminar mal o atribuir el fallo a permisos sin que esa sea la causa.
- **Pregunta:** ¿qué información debe poder leerse para considerar un archivo analizable y cómo se contabilizan y comunican los fallos de lectura ajenos a permisos? El resultado debe conservar la causa real y la ruta afectada.

## CL-6 — Extensiones más frecuentes

- **Prioridad media · abierto · decisión ya reconocida.** RF-8 y dudas abiertas; líneas 24 y 55.
- **Escenario e impacto:** varias extensiones de «otros» tienen el mismo recuento. Mostrar todas, limitar la lista o cortar un empate produce resultados distintos; no hay un criterio de aceptación completo.
- **Pregunta:** ¿cuántas extensiones se muestran y cómo se resuelven los empates en el límite? Debe concretarse antes de implementar esa parte del informe.

## CL-7 — Caso de una carpeta que solo contiene subcarpetas

- **Prioridad baja · abierto · incoherencia de redacción.** RF-3, RF-12 y casos límite; líneas 19, 28 y 39.
- **Escenario e impacto:** `entrada` contiene únicamente `sub`, que contiene un archivo analizable. El caso límite remite a «no hay archivos», aunque con `--recursivo` RF-3 exige examinar ese archivo. Una prueba derivada literalmente del caso límite contradiría el recorrido.
- **Aclaración necesaria:** delimitar el caso según el modo de recorrido y la ausencia de archivos analizables dentro de su alcance. RF-3 ya define que el modo recursivo incluye los descendientes; no hace falta una nueva decisión de producto.

## Cierre de la revisión

No hay hallazgos resueltos. CL-1 y CL-2 son las primeras decisiones que deben aclararse; CL-3 a CL-6 afectan a contratos concretos del informe y los errores. CL-7 es una precisión editorial. Tras incorporar las respuestas a los requisitos afectados, debe repetirse la comprobación de coherencia antes de cerrar el plan.

Esta revisión no valida la implementación ni la compatibilidad con plataformas. No añade requisitos de movimiento, duplicados, configuración o recuperación fuera del alcance de la spec.
