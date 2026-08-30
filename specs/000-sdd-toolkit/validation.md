# Validación del paquete SDD

Fecha: 2026-08-30. Resultado: paquete creado e instalado; comprobaciones estructurales y dos escenarios de comportamiento superados en el alcance descrito. No constituye una garantía de todas las futuras ejecuciones de estas instrucciones.

## Actualización CH-1 — Entrevistas obligatorias

La corrección del usuario tras el primer uso real reveló un defecto del flujo original: permitía redactar una constitución sin hacer preguntas. Las pruebas históricas de clarificación y validación de este informe no cubrían ese caso.

Se actualizaron constitución, especificación y coordinación, sus metadatos, `AGENTS.md` y la guía. RF-10 a RF-12 exigen preguntar, esperar respuestas reales, proponer lenguajes antes de elegir y editar los documentos durante la conversación, conservando las decisiones ya resueltas.

Comprobaciones nuevas ejecutadas el 2026-08-30:

- Validador oficial y comprobación de metadatos/enlaces: nueve skills válidas.
- Revisión documental: las tres skills diferencian propuestas de respuestas, bloquean el cierre dependiente de decisiones pendientes y permiten retomar la conversación sin repetir preguntas contestadas.
- Se revisaron los seis diffs antes de sincronizar; no contenían cambios ajenos. Se verificaron hashes del destino y origen antes de copiar y del resultado después.
- Los 19 archivos instalados coinciden con sus fuentes, comprobados desde el entorno restringido.

Límite: no se ha realizado una nueva prueba conductual con subagente para la entrevista. La verificación de esta corrección es estructural y documental; no determina el estado actual de ningún producto.

## Actualización CH-2 — Descubrimiento en Claude Code

Comprobaciones ejecutadas el 2026-08-30:

- Se copiaron las nueve carpetas de `skills/` a `.claude/skills/`. Los 19 archivos coinciden por SHA-256 con sus fuentes; no se sobrescribió ninguna skill ajena ni se tocó la copia de `~/.agents/skills/`.
- Se creó `CLAUDE.md` en la raíz, que importa `AGENTS.md` y añade las notas de invocación y sincronización propias de Claude Code. No duplica el contenido de las instrucciones.
- Ningún `SKILL.md` fue modificado, por lo que la validación de formato anterior sigue vigente para las nueve skills.

Límite: la verificación es estructural. No se ha comprobado visualmente que Claude Code muestre las nueve skills en su catálogo; ese descubrimiento requiere una sesión nueva y no se sustituye por una comprobación de archivos.

## Estructura y metadatos

Se ejecutó `quick_validate.py`, el validador incluido en `skill-creator`, sobre las nueve carpetas de `skills/`: nueve resultados válidos. También se comprobó que el nombre coincide con la carpeta, los metadatos de interfaz son YAML válido, sus descripciones tienen la longitud prevista, los prompts mencionan su skill y la selección implícita permanece habilitada.

Se verificaron los enlaces internos de los archivos `SKILL.md` y que la coordinadora dirige a las ocho skills de fase. No se añadieron dependencias de conectores, modelos específicos, claves ni procesos permanentes.

El validador necesitó PyYAML, ausente en el Python disponible. Se descargó la versión 6.0.3 solo en `.sdd-check/deps`, sin modificar el entorno global. La descarga y lectura de esa dependencia requirieron ejecución autorizada fuera del entorno restringido. No hubo rechazo de permisos ni bloqueo pendiente.

## Prueba independiente de las skills

Un subagente recibió las skills y entradas de cada caso, sin el resultado esperado. Solo pudo escribir informes y pruebas locales en `.sdd-check/`; no se usaron datos reales ni servicios externos.

| Caso | Petición | Resultado observado |
| --- | --- | --- |
| Clarificación de reservas | Revisar y detectar problemas sin cambiar la spec ni decidir reglas | Detectó contradicción de reservas simultáneas, cancelación sin umbral verificable y ambigüedad en intervalos; dejó las decisiones abiertas y no modificó la spec. |
| Validación de movimiento de archivos | Comprobar si una entrega con tests en verde cumple su spec, sin repararla | Ejecutó la suite original: 1/1 correcta. Añadió tres comprobaciones independientes: 2 correctas y 1 fallo que demuestra sobrescritura de destino. Emitió «No cumple» y conservó el producto original. |

El fallo del segundo caso era un defecto del producto de prueba, no de la skill. La validación fue satisfactoria precisamente porque lo detectó y no dio por cerrado el requisito a partir de la suite verde.

El revisor contrastó diez hashes antes/después: no cambiaron las skills evaluadas ni los documentos, código y tests originales de los casos. No observó defectos materiales en las instrucciones. Los informes y evidencias locales permanecen en `.sdd-check/`, excluidos del repositorio para no mezclarlos con requisitos reales.

## Trazabilidad del paquete

| Requisitos del toolkit | Evidencia | Tipo y límite |
| --- | --- | --- |
| RF-1 | Nueve skills con entradas, alcance, entregables y cierre; formato validado | Estructura ejecutada; redacción revisada |
| RF-2 | Coordinadora distingue producto, spec activa, estado y límite de la petición | Inspección de instrucciones; no se simuló un proyecto completo |
| RF-3 | Especificación exige identificadores y resultados observables; clarificación preservó decisiones abiertas | Inspección y caso independiente de clarificación |
| RF-4 | Planificación, tareas e implementación conectan requisitos y evidencia; validación descubrió un requisito sin cobertura original | Inspección y caso independiente de validación |
| RF-5 | Validación diferencia cumple, falla y no verificado; no aceptó una suite insuficiente | Caso ejecutado con incumplimiento; la ausencia total de herramientas no se simuló |
| RF-6 | Cambio conserva identificadores, actualiza spec primero e invalida evidencia afectada | Inspección de instrucciones; no se ejecutó un cambio de producto |
| RF-7 | Guía acota responsabilidades de revisión; se realizó una revisión independiente | Delegación ejecutada; alternativa local documentada |
| RF-8 | Las fases limitan su alcance; el revisor no cambió specs ni reparó el producto | Inspección, casos ejecutados y comprobación de integridad |
| RF-9 | No se fija un stack ni un dominio; paquete instalado en biblioteca personal | Inspección, copia verificada y lectura desde el entorno restringido |

## Instalación

Destino personal: `C:/Users/picop/.agents/skills/`. Se siguió la ubicación personal indicada en la documentación actual de Codex. Las fuentes editables se conservan en `skills/`, en la raíz del repositorio.

Se comprobó antes de copiar que ninguno de los nueve nombres existía en destino. Se copiaron 19 archivos: dos por skill y una referencia adicional de la coordinadora. Todos coinciden con las fuentes mediante SHA-256. Después, las nueve entradas `SKILL.md` se leyeron correctamente desde el entorno restringido. La skill previa `hf-cli` no se modificó.

No se ha verificado visualmente que el selector de la aplicación haya refrescado el catálogo. La instalación en disco y su legibilidad sí están comprobadas; si las skills no aparecen, se puede reiniciar Codex conforme a la documentación oficial.

## Límites y siguiente uso

La evaluación conductual cubre dos fases y dos escenarios, no todas las combinaciones posibles. Las otras fases se revisaron estructuralmente. Se deberán ajustar las instrucciones solo cuando el uso real muestre un problema concreto.

Esta validación cubre únicamente las herramientas SDD, no certifica el funcionamiento de FilePilot ni de los demás productos.
