# Proyectos con SDD

Este espacio reúne el método de trabajo para los seis proyectos acordados. El primer entregable es un paquete de nueve skills: una coordinadora y ocho fases. Todavía no se ha empezado a programar FilePilot.

**FilePilot:** [constitución definida](projects/filepilot/docs/constitution.md). CLI local en Python para Linux, macOS y Windows, sin cuentas ni servicios externos; sin sobrescritura de archivos ni eliminación automática de duplicados. Carpeta: `projects/filepilot/`. Siguiente fase: entrevista para definir el alcance de la primera especificación; sin código todavía.

## Qué hace cada skill

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
| `sdd-cambio` | Mantener la spec al evolucionar el producto | `changes.md` y documentos afectados |

Las rutas son relativas a cada producto; los documentos de una funcionalidad se agrupan en `specs/NNN-nombre/`. Se conservan las convenciones existentes cuando el producto ya tiene otra estructura.

## Cómo usarlas

Puedes pedir el trabajo con lenguaje natural, por ejemplo:

> Empecemos FilePilot con SDD. Prepara su constitución y el borrador de la primera especificación. No programes todavía.

El agente pregunta y espera tus respuestas antes de fijar enfoque, lenguaje o requisitos. Después actualiza la regla o requisito correspondiente, sin copiar la entrevista. La constitución contiene unos pocos principios; la spec detalla comportamientos y errores sin redundancias. Ninguno incluye historial de conversación ni comparativas ya resueltas.

También puedes mencionar una fase por su nombre, por ejemplo `$sdd-clarificacion`, para revisar una spec, o `$sdd-validacion` para comprobar una entrega. La selección concreta de skills en la interfaz depende de la versión de Codex; el nombre y una petición clara también permiten expresar la intención.

Para continuar un incremento completo:

> Continúa FilePilot con SDD hasta completar el incremento definido. Si faltan decisiones, pregúntame y actualiza las reglas o requisitos; después trabaja dentro de lo acordado.

Una petición de «solo especificar» acaba en documentos. Una petición de construir un incremento puede recorrer sus fases y tareas, pero no permite saltarse las entrevistas ni sustituir respuestas por suposiciones. Fuera de esas decisiones de definición, no hace falta pedir permiso rutinario para cada paso de trabajo.

## Skills y subagentes

Las skills guardan instrucciones reutilizables; no son procesos que permanezcan trabajando. Un subagente puede aplicar una de esas skills en una revisión concreta. Los mejores puntos para ello son clarificación y validación, cuando una mirada independiente aporta valor.

No se configuran nueve agentes permanentes ni se ejecutan las fases dependientes en paralelo. La coordinadora puede encargar una revisión acotada si el entorno lo permite; también puede completar el flujo localmente. La guía está en [revisiones](skills/sdd-coordinador/references/revisiones.md).

## Fuentes y adaptación

El flujo toma como referencia [Hello SDD de MoureDev](https://github.com/mouredev/hello-sdd). Las instrucciones del paquete son una adaptación propia: mantienen requisitos identificados, diseño previo, pruebas de comportamiento y cambios comenzando en la spec. Por decisión expresa del usuario, preguntar y esperar respuestas es obligatorio al construir la constitución y definir las specs. No se fija un número arbitrario de preguntas ni una duración exacta por tarea.

El formato y el descubrimiento de skills se contrastaron con [la documentación oficial de OpenAI](https://learn.chatgpt.com/docs/build-skills), consultada el 2026-08-30.

## Copias y reutilización

`skills/` conserva las fuentes editables del paquete. Hay dos copias de descubrimiento, cada una en la ruta que lee su herramienta: `.claude/skills/` para Claude Code y `C:/Users/picop/.agents/skills/` para Codex. Los 19 archivos de ambas coinciden con las fuentes. La instalación y sus límites constan en [el informe del toolkit](specs/000-sdd-toolkit/validation.md). No se han modificado credenciales, modelos ni servicios.

Después de cambiar una skill, hay que sincronizar las dos copias y verificar por SHA-256 que coinciden con la fuente. Evita instalar a la vez otra copia con el mismo nombre en el ámbito del proyecto, porque Codex puede mostrar ambas. Si una skill instalada no aparece, reinicia Codex para refrescar su catálogo; la detección visual no se sustituye por una comprobación de archivos.

## Proyectos acordados

1. **FilePilot · CLI:** organización segura de archivos.
2. **API Sentinel · CLI:** comprobación automatizada de APIs.
3. **Freelance Desk · Web:** clientes, trabajos y presupuestos.
4. **Pantry Pocket · Móvil:** despensa y compra sin conexión.
5. **ReservaFlow · Web:** reservas y control de solapamientos.
6. **FieldOps · Móvil y web:** intervenciones técnicas y sincronización.

Los detalles, tecnologías definitivas y criterios de cada producto se concretarán en sus propias especificaciones. Las skills funcionan independientemente de esos seis dominios.
