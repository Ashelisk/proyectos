# Proyectos de software

## Contexto

El repositorio organiza seis proyectos progresivos con Spec-Driven Development: FilePilot, API Sentinel, Freelance Desk, Pantry Pocket, ReservaFlow y FieldOps. CLI, web y móvil comparten el método; cada producto tendrá su propia constitución y especificaciones.

## Método de trabajo

- Para iniciar o continuar trabajo SDD, lee `skills/sdd-coordinador/SKILL.md` y después solo la fase pertinente. Las fuentes editables del paquete están en `skills/`.
- Las copias de descubrimiento son `.claude/skills/` (Claude Code) y `~/.agents/skills/` (Codex). Al editar una skill, sincroniza ambas y comprueba que coinciden con la fuente.
- Identifica la raíz del producto antes de escribir. Los artefactos de `specs/000-sdd-toolkit/` pertenecen a la preparación de estas skills, no a FilePilot ni a los demás productos. El estado vigente de cada producto reside en sus propios documentos; no reapliques ajustes antiguos del toolkit para deshacer decisiones. Si hay una contradicción sin resolver, señálala y pregunta antes de cambiarlas.
- Para funcionalidades: constitución, especificación, clarificación, plan, tareas, implementación y validación. Ante cambios de comportamiento, actualiza primero la spec. Conserva requisitos y evidencias válidos.
- Constitución: SIEMPRE inicia una conversación con preguntas sobre enfoque, objetivos y restricciones, y presenta alternativas de lenguaje antes de fijar uno. Espera respuestas reales y actualiza `docs/constitution.md` durante la conversación. Una propuesta anterior o un «perfecto» general no elige el stack por el usuario.
- Selección de lenguaje: prioriza adecuación técnica, sencillez, distribución y mantenimiento. La familiaridad previa no limita los candidatos. Presenta diferencias y costes antes de elegir.
- Especificaciones: entrevista al iniciar una nueva spec y pregunta al revisar una existente cuando haya decisiones sin resolver. Mantén el documento como entrevista en curso hasta incorporar las respuestas necesarias. No sustituyas preguntas por supuestos ni avances al trabajo dependiente.
- Documentación SDD: constituciones breves (para proyectos pequeños, unos 5–7 principios y 15 líneas) y specs explicativas sin redundancia. Escribe reglas y requisitos vigentes; excluye historiales, transcripciones, perfil del usuario, comparativas ya resueltas y apartados de quién decidió qué. Las respuestas actualizan el contenido, no se acumulan como un registro. No traslades el historial eliminado a otros archivos.
- Redacción profesional: describe el producto, sus capacidades, restricciones y decisiones técnicas. Omite motivaciones personales o laborales, autoevaluaciones y objetivos didácticos. Menciona herramientas o métodos únicamente cuando aporten una instrucción técnica útil; conserva las limitaciones y el estado real del producto.
- Documentación autónoma: escribe para cualquier persona que use o adapte el proyecto, con IA o sin ella. No presupongas acceso al chat ni al autor, ni aludas a acuerdos, peticiones o intercambios previos entre el creador y un agente. Limita las referencias a IA a instrucciones técnicas necesarias y presenta su uso como opcional. Las instrucciones dirigidas a agentes mantienen las entrevistas obligatorias; los documentos del producto deben poder utilizarse también de forma manual.
- Respeta el alcance solicitado: preparar skills o documentos no implica empezar una aplicación. Conserva respuestas explícitas para no repetirlas. Estas conversaciones de definición son obligatorias; fuera de ellas, no pidas confirmación rutinaria al pasar de fase.
- Utiliza subagentes solo para encargos independientes que aporten valor, conforme a las capacidades y permisos de la sesión. No es necesario crear un agente permanente por fase.
- Habla y documenta en español salvo indicación contraria. Explica las decisiones técnicas con claridad y precisión.

## Coordinación entre sistemas

- GitHub (`origin`, repositorio `Ashelisk/proyectos`) es la fuente de verdad entre clones independientes. No compartas rutas locales ni copies estados de una máquina a otra. Antes de modificar, ejecuta `agent-router doctor` y consulta `agent-router status`; usa `agent-router sync` únicamente con el árbol limpio y detente ante HEAD separado, divergencia, remoto inesperado o cambios ajenos.
- `PROJECT_CONTEXT.md` describe la estructura comprobada, `TASK.md` mantiene la tarea activa y `.agents/state.json` resume el relevo portable. Léelos antes de continuar trabajo procedente de otro sistema. Estos archivos complementan los documentos SDD del producto y nunca los sustituyen ni pueden rebajar sus requisitos.
- El estado compartido contiene solo rama, commit verificado, plataforma, pruebas, bloqueo y siguiente acción. Excluye rutas absolutas, usuarios, credenciales, conversaciones, prompts, respuestas y logs. Los datos locales del router viven en `.agent-local/`, fuera de Git.
- Antes de cambiar de sistema, revisa y prepara explícitamente los archivos autorizados, crea un checkpoint normal en la rama de tarea y súbelo. No uses `main` para trabajo incompleto. La integración exige pruebas locales aplicables y CI correcta en el commit candidato.
- Estados de cierre: `PASS` cuando todos los criterios aplicables tienen evidencia y no quedan hallazgos; `FAIL` ante un defecto reproducible corregible; `BLOCKED` ante un impedimento técnico o externo; `NEEDS_HUMAN` cuando falta una decisión, permiso, credencial o acción destructiva. Un texto ambiguo nunca equivale a aprobación.

## Coordinación de programación y revisión

Cuando se autorice el flujo Codex revisor / Claude Code programador, utiliza el [puente local](tools/puente_agentes/README.md). Codex mantiene el ciclo de encargos, pruebas y correcciones dentro de la tarea autorizada hasta validarla o detectar una decisión pendiente, un bloqueo o un límite. No termina el turno solo para preguntar si debe reenviar una corrección técnica. Claude actúa únicamente como programador, no invoca el puente ni se aprueba a sí mismo. El coordinador controla documentos compartidos, integración y Git; ningún agente amplía el alcance ni elude los permisos. Preparar el puente no autoriza nuevas tareas de producto.

El perfil base del programador en este puente es Opus 5 con esfuerzo extra (`claude-opus-5`, `xhigh`). Ajusta esfuerzo o modelo solo por exigencia de la tarea o correcciones fallidas, registrando un motivo técnico; prioriza cambiar el esfuerzo. Marca las correcciones fallidas con evidencia: dos consecutivas elevan a `max` el siguiente envío permitido. No cuentes como tal la entrega inicial, una limitación del entorno ni una preferencia estética. Mantén los límites de rondas, presupuesto y permisos; no amplíes ninguno silenciosamente.

El router multiplataforma no sustituye el puente. Su comando `cycle` es únicamente informativo mientras no reutilice los mismos controles de rutas editables, modelo real, esfuerzo, rondas, presupuesto y revisión. Los ciclos reales de Claude programador / Codex revisor siguen pasando por `tools/puente_agentes/` y requieren autorización de tarea y límites.

## Control de versiones

- Al completar cada cambio importante, revisa el diff, ejecuta las comprobaciones pertinentes y crea un commit con un mensaje claro en español. Agrupa cambios relacionados; no crees un commit por cada ajuste menor.
- Sube los commits al repositorio y rama acordados sin pedir confirmación rutinaria. Si falta el destino o el acceso, conserva el commit local e indica qué falta; no uses otro repositorio por suposición.
- Incluye solo archivos del trabajo autorizado. Excluye credenciales, configuración privada y material temporal; no sobrescribas cambios ajenos ni fuerces subidas o reescribas historial sin autorización expresa.
- Se prohíben `reset --hard`, limpiezas automáticas, descarte de cambios, reescritura de historial y push forzado. Los checkpoints no preparan cambios implícitamente.

## Verificación

FilePilot integra validación de raíz, clasificación, recorrido, exclusiones e informe de solo lectura. Las correcciones V-9/V-10 están verificadas. Windows registra 212 pruebas superadas y una omitida por versión de Python con privilegios para crear enlaces; Linux registra 209 superadas y cuatro omisiones exclusivas de Windows con Python 3.11.16 y 3.14.4. Permisos, enlaces y comandos de T14 están ejecutados en Linux, por lo que la matriz declarada cumple. Consulta los comandos en [su README](projects/filepilot/README.md), el estado vigente en [sus tareas](projects/filepilot/specs/001-analisis-carpeta/tasks.md) y la evidencia en [su validación](projects/filepilot/specs/001-analisis-carpeta/validation.md). No inventes resultados ni afirmes compatibilidad sin ejecutarla. Al crear cada producto, documenta sus comandos reales. Para el paquete SDD, comprueba formato de skills y referencias, y contrasta los cambios importantes con escenarios de uso.

Para el flujo compartido, ejecuta también las pruebas del router y del puente. Sus lanzadores Bash son para Linux y sus lanzadores PowerShell para Windows; la CI de macOS valida las herramientas comunes, pero no convierte macOS en plataforma objetivo de FilePilot. La revisión debe comprobar requisitos, seguridad, manejo de errores, portabilidad, pruebas y documentación. Todo hallazgo incluye severidad, archivo o línea, evidencia y corrección esperada; una preferencia estética no es un fallo.

Los recursos de `.sdd-check/` son material temporal de validación, excluido del repositorio. No uses sus ejemplos como requisitos de los productos reales.
