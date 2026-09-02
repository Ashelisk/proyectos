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

Destino personal: `~/.agents/skills/`. Se siguió la ubicación personal indicada en la documentación actual de Codex. Las fuentes editables se conservan en `skills/`, en la raíz del repositorio.

Se comprobó antes de copiar que ninguno de los nueve nombres existía en destino. Se copiaron 19 archivos: dos por skill y una referencia adicional de la coordinadora. Todos coinciden con las fuentes mediante SHA-256. Después, las nueve entradas `SKILL.md` se leyeron correctamente desde el entorno restringido. La skill previa `hf-cli` no se modificó.

No se ha verificado visualmente que el selector de la aplicación haya refrescado el catálogo. La instalación en disco y su legibilidad sí están comprobadas; si las skills no aparecen, se puede reiniciar Codex conforme a la documentación oficial.

## Límites y siguiente uso

La evaluación conductual cubre dos fases y dos escenarios, no todas las combinaciones posibles. Las otras fases se revisaron estructuralmente. Se deberán ajustar las instrucciones solo cuando el uso real muestre un problema concreto.

Esta validación cubre únicamente las herramientas SDD, no certifica el funcionamiento de FilePilot ni de los demás productos.

## Puente de programación y revisión

**Resultado: cumple RF-14 a RF-18 en el alcance ejecutado.** Fecha: 2026-08-30. Windows 11, Python 3.14.7, Git y Claude Code 2.1.251 con acceso autenticado. Se evalúan el código y protocolo incluidos en el mismo commit que este informe. Es autorrevisión del puente; el ejemplo de programación fue implementado por Claude y comprobado por el coordinador.

### Comprobaciones locales

Desde la raíz del repositorio:

```powershell
.\projects\filepilot\.venv\Scripts\python.exe -B -m unittest discover -s tools/puente_agentes -p test_puente.py -v
```

**11 pruebas superadas, sin omisiones, en 9,90 segundos.** La primera ejecución anterior a la implementación falló porque faltaba el módulo del puente. La suite final crea repositorios temporales y comprueba aislamiento, sesión explícita, revisión obligatoria, huella obsoleta, cambios fuera del alcance, bloqueo exclusivo, rutas inválidas, límite de envíos, presupuesto, decisiones pendientes, sesión incorrecta, permisos denegados, respuestas inválidas y tiempo agotado. El transporte de modelo es simulado en esas pruebas; una comprobación adicional de la misma suite termina realmente un proceso Python desechable al vencer su tiempo.

### Intercambios reales

1. **Lectura y continuación.** Encargo `prueba-puente`, copia aislada de `a11e72d`, sin permisos de edición ni shell. Claude leyó la constitución y la spec de FilePilot e identificó el producto y el código de RF-11. Después de contrastar la respuesta y registrar revisión, se reanudó la misma sesión. Recuperó una señal del primer mensaje que no figuraba en el segundo. Ambas respuestas fueron JSON válido; las huellas inicial y final coincidieron y la copia no tenía cambios. La aprobación correspondió al coordinador.
2. **Edición delimitada.** Repositorio sintético bajo `.sdd-check/puente/fixture/`, independiente de los productos. Una función incumplía el requisito de devolver el doble de un entero. Los casos positivo, cero y negativo fallaban inicialmente. Claude recibió permiso de edición únicamente en `src`, cambió solo `src/calculo.py` y dejó las pruebas pendientes para el coordinador. Este ejecutó `python -B -m unittest discover -v` con el intérprete anterior en la copia aislada: la prueba y sus tres casos pasaron. El diff no alteró requisitos ni pruebas. Se aprobó la huella exacta sin integrar el ejemplo en un producto.

Se ejecutaron las cuatro operaciones del CLI: `iniciar`, `enviar`, `revisar` y `estado`, además de su ayuda. Los mensajes se leyeron de archivos UTF-8 y las respuestas se validaron sin ejecutar instrucciones de shell procedentes del modelo. Tres invocaciones reales de Claude en total; estimación acumulada comunicada por su CLI: aproximadamente 0,2061 USD, no una medición de facturación ni de cuota de suscripción.

### Trazabilidad y límites

| Requisito | Evidencia | Resultado y límite |
| --- | --- | --- |
| RF-14 | Worktrees desechables, original intacto, sesión conservada | Cumple; no se ejecutó una tarea completa de producto |
| RF-15 | JSON, transiciones, revisión por huella y rechazo si cambia la entrega | Cumple; el contenido técnico de la revisión depende del coordinador |
| RF-16 | Corrección y continuación, decisiones pendientes y límites | Cumple; cuotas y errores del proveedor se simulan, no se agotó una cuenta real |
| RF-17 | Herramientas restringidas, edición real solo en src, pruebas ejecutadas por el coordinador | Cumple en los escenarios comprobados; no es una garantía de aislamiento del sistema operativo |
| RF-18 | Once pruebas locales y tres intercambios reales | Cumple; Python 3.11, Linux y macOS no ejecutados |

La versión de FilePilot cambió a `a11e72d` desde otra sesión durante la preparación del puente; se preservó y no se revisó ni modificó su implementación en este trabajo. Ninguna skill ni sus copias se modificaron. Los intercambios, estados y ejemplos quedan en `.sdd-check/`, excluidos de Git; las sesiones también permanecen en el almacenamiento habitual de Claude Code para su continuidad. No se crearon credenciales, automatizaciones permanentes ni procesos que sigan trabajando tras estas pruebas.

El circuito requiere una conversación activa de coordinación. No se afirma que continúe después de detener esa conversación. La integración de cambios aprobados y su verificación final pertenecen al coordinador, no al script.

### Perfil del programador — RF-19

**Cumple en el alcance ejecutado**, 2026-08-30, con el código de este commit. Windows, Python 3.14.7 y Claude Code 2.1.251. Autorrevisión de la selección explícita y sus controles; las comprobaciones anteriores a RF-19 no fijaban el modelo principal.

Mismo comando de unittest del puente, con `PYTHONIOENCODING=utf-8`: **17 pruebas superadas, ninguna omitida, en 17,19 segundos**. Antes de implementar el cambio, las cuatro nuevas pruebas iniciales fallaban por ausencia de las opciones de perfil y de la marca de corrección fallida. La suite final comprueba Opus 5 extra al iniciar y reanudar, ajustes con motivo, conservación del perfil, escalada después de dos correcciones fallidas sin excepciones injustificadas, rechazo de una sustitución de modelo y respeto de rondas y presupuesto. Una comprobación con proceso real confirma que el esfuerzo heredado `low` se sustituye por `xhigh` solo en el hijo y que el entorno original no cambia.

Prueba real adicional: encargo `prueba-opus-extra`, solo lectura sobre una copia de `2e9944f`. El puente pasó `--model claude-opus-5 --effort xhigh`; el resultado incluyó `claude-opus-5` en `modelUsage`, junto con Haiku como auxiliar del CLI. La respuesta fue válida, la huella no cambió y el coordinador aprobó la comprobación. Estimación del CLI: 0,1254 USD, sin equivalencia garantizada con facturación o cuota. Estado y evidencia temporal en `.sdd-check/puente/prueba-opus-extra/`.

Se verificó la ayuda de `enviar` con las opciones nuevas. No se ejecutaron llamadas reales a modelos alternativos ni una comparación de calidad entre niveles. La escalada se probó con transporte simulado; el nivel de esfuerzo se acredita como configuración enviada, no como medición del razonamiento interno. Permanecen los límites de tres envíos: la entrega inicial y dos correcciones agotan el valor predeterminado, aunque corresponda elevar el esfuerzo en una continuación autorizada. No se ampliaron permisos, rondas ni presupuesto, ni se cambiaron tareas de FilePilot o las skills.
