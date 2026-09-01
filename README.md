# Proyectos con SDD

Repositorio para proyectos CLI, web y móviles con Spec-Driven Development (SDD). Incluye un paquete reutilizable de nueve skills: una coordinadora y ocho fases.

**Estado de FilePilot:** [CLI local en Python](projects/filepilot/README.md) que analiza carpetas sin modificar archivos. Incluye clasificación por extensión, recorrido opcionalmente recursivo, exclusiones con motivo único e informe con tamaños y destinos propuestos. Conserva [constitución](projects/filepilot/docs/constitution.md), [spec 001](projects/filepilot/specs/001-analisis-carpeta/spec.md), [plan](projects/filepilot/specs/001-analisis-carpeta/plan.md) y [tareas](projects/filepilot/specs/001-analisis-carpeta/tasks.md). La [validación](projects/filepilot/specs/001-analisis-carpeta/validation.md) acredita la matriz declarada: Windows con Python 3.11.9 y 3.14.7 (**212 pruebas superadas y una omitida** por versión con privilegios para enlaces) y Linux con Python 3.11.16 y 3.14.4 (**209 superadas y cuatro omisiones exclusivas de Windows** por versión). T1 a T14 están completadas.

## Uso y adaptación

El método puede aplicarse manualmente o con asistencia de IA. La documentación define las reglas, los requisitos y los criterios de validación de cada producto. Las skills son una ayuda opcional para agentes; no son necesarias para trabajar con SDD.

Para desarrollar o adaptar un producto sin IA:

1. Revisar su constitución y definir los principios pendientes; en un producto nuevo, crear `docs/constitution.md`.
2. Especificar el comportamiento y los criterios de aceptación en `specs/NNN-nombre/spec.md`, resolviendo las dudas antes del diseño.
3. Preparar el plan técnico y las tareas; implementar y comprobar cada comportamiento especificado.
4. Registrar la evidencia de validación. Si cambia el comportamiento requerido, actualizar primero la spec y después los documentos, código y pruebas afectados.

Cada producto conserva sus propias decisiones técnicas. El paquete SDD puede reutilizarse sin adoptar el lenguaje, los requisitos ni el dominio de FilePilot.

## Skills para agentes de IA

| Skill | Responsabilidad | Resultado habitual |
| --- | --- | --- |
| `sdd-coordinador` | Identificar estado y dirigir el siguiente paso autorizado | Fase, entregables y siguiente paso |
| `sdd-constitucion` | Preguntar por enfoque y lenguajes, y documentar los principios elegidos | `docs/constitution.md` |
| `sdd-especificacion` | Entrevistar y concretar comportamiento y aceptación | `spec.md` |
| `sdd-clarificacion` | Detectar contradicciones y decisiones pendientes | `clarifications.md` |
| `sdd-planificacion` | Diseñar la solución y su verificación | `plan.md` |
| `sdd-tareas` | Descomponer en trabajo pequeño y comprobable | `tasks.md` |
| `sdd-implementacion` | Programar las tareas autorizadas y verificarlas | Código, pruebas y evidencia |
| `sdd-validacion` | Contrastar cada requisito con resultados reales | `validation.md` |
| `sdd-cambio` | Mantener la spec al evolucionar el producto | Spec y documentos afectados |

Las rutas son relativas a cada producto; los documentos de una funcionalidad se agrupan en `specs/NNN-nombre/`. Se conservan las convenciones existentes cuando el producto ya tiene otra estructura.

### Invocación

Ejemplo de petición para iniciar una especificación:

> Prepara la primera especificación de FilePilot a partir de su constitución. Pregunta por el alcance y los comportamientos pendientes. No implementes código.

Al crear una constitución o especificación, el agente pregunta por las decisiones pendientes y espera respuestas antes de fijarlas. Conserva las decisiones vigentes y actualiza la regla o requisito correspondiente, sin copiar la entrevista. La constitución contiene pocos principios; la spec detalla comportamientos y errores sin redundancias ni historial de conversación.

También puedes mencionar una fase por su nombre, por ejemplo `$sdd-clarificacion`, para revisar una spec, o `$sdd-validacion` para comprobar una entrega. La selección concreta de skills en la interfaz depende de la versión de Codex; el nombre y una petición clara también permiten expresar la intención.

Para continuar un incremento completo:

> Implementa el incremento especificado de FilePilot siguiendo su plan y tareas. Consulta las decisiones pendientes antes de avanzar en el trabajo afectado y valida el resultado contra la spec.

Una petición de «solo especificar» acaba en documentos. Una petición de construir un incremento puede recorrer sus fases y tareas, pero no permite saltarse las entrevistas ni sustituir respuestas por suposiciones. Fuera de esas decisiones de definición, no hace falta pedir permiso rutinario para cada paso de trabajo.

### Revisiones con subagentes

Para trabajar con Codex como coordinador/revisor y Claude Code como programador está disponible el [puente local](tools/puente_agentes/README.md). Intercambia encargos y correcciones por tarea en una copia Git aislada, con permisos y límites explícitos; los mensajes se conservan fuera del repositorio publicado. Su uso es opcional y requiere una conversación activa de coordinación.

Las skills guardan instrucciones reutilizables; no son procesos que permanezcan trabajando. Un subagente puede aplicar una de esas skills en una revisión concreta. Los mejores puntos para ello son clarificación y validación, cuando una mirada independiente aporta valor.

La coordinadora puede encargar una revisión independiente si el entorno lo permite o completarla localmente. Las fases mantienen sus dependencias. La guía está en [revisiones](skills/sdd-coordinador/references/revisiones.md).

## Fuentes y adaptación

El flujo toma como referencia [Hello SDD de MoureDev](https://github.com/mouredev/hello-sdd). El paquete mantiene requisitos identificados, diseño previo, pruebas de comportamiento y cambios comenzando en la spec.

Referencia para el formato y descubrimiento de skills: [documentación oficial de OpenAI](https://learn.chatgpt.com/docs/build-skills).

## Copias y reutilización

`skills/` conserva las fuentes editables. El repositorio incluye una copia en `.claude/skills/` para Claude Code. Para utilizarlas en Codex, copia las nueve carpetas `sdd-*` a `~/.agents/skills/` en el equipo de destino, revisando antes cualquier skill existente con el mismo nombre.

Después de editar una skill, sincroniza `.claude/skills/` y las copias personales instaladas; verifica por SHA-256 que coinciden con la fuente. Evita duplicar nombres de skills en distintos ámbitos de Codex. Comprueba su disponibilidad en la herramienta: la igualdad de archivos no demuestra que se hayan cargado. El [informe del toolkit](specs/000-sdd-toolkit/validation.md) recoge las comprobaciones realizadas y sus límites.

## Proyectos previstos

1. **FilePilot · CLI:** organización segura de archivos.
2. **API Sentinel · CLI:** comprobación automatizada de APIs.
3. **Freelance Desk · Web:** clientes, trabajos y presupuestos.
4. **Pantry Pocket · Móvil:** despensa y compra sin conexión.
5. **ReservaFlow · Web:** reservas y control de solapamientos.
6. **FieldOps · Móvil y web:** intervenciones técnicas y sincronización.

Los detalles, tecnologías definitivas y criterios de cada producto se concretarán en sus propias especificaciones. Las skills funcionan independientemente de esos seis dominios.
