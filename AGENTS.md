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

## Coordinación de programación y revisión

Cuando se autorice el flujo Codex revisor / Claude Code programador, utiliza el [puente local](tools/puente_agentes/README.md). Codex mantiene el ciclo de encargos, pruebas y correcciones dentro de la tarea autorizada hasta validarla o detectar una decisión pendiente, un bloqueo o un límite. No termina el turno solo para preguntar si debe reenviar una corrección técnica. Claude actúa únicamente como programador, no invoca el puente ni se aprueba a sí mismo. El coordinador controla documentos compartidos, integración y Git; ningún agente amplía el alcance ni elude los permisos. Preparar el puente no autoriza nuevas tareas de producto.

## Control de versiones

- Al completar cada cambio importante, revisa el diff, ejecuta las comprobaciones pertinentes y crea un commit con un mensaje claro en español. Agrupa cambios relacionados; no crees un commit por cada ajuste menor.
- Sube los commits al repositorio y rama acordados sin pedir confirmación rutinaria. Si falta el destino o el acceso, conserva el commit local e indica qué falta; no uses otro repositorio por suposición.
- Incluye solo archivos del trabajo autorizado. Excluye credenciales, configuración privada y material temporal; no sobrescribas cambios ajenos ni fuerces subidas o reescribas historial sin autorización expresa.

## Verificación

FilePilot dispone del paquete instalable, el subcomando `analizar` y la validación de la ruta indicada; el análisis del contenido de las carpetas sigue pendiente. Consulta los comandos y el estado vigente en [sus tareas](projects/filepilot/specs/001-analisis-carpeta/tasks.md) y la evidencia en [su validación](projects/filepilot/specs/001-analisis-carpeta/validation.md). No inventes resultados ni afirmes compatibilidad sin ejecutarla. Al crear cada producto, documenta sus comandos reales. Para el paquete SDD, comprueba formato de skills y referencias, y contrasta los cambios importantes con escenarios de uso.

Los recursos de `.sdd-check/` son material temporal de validación, excluido del repositorio. No uses sus ejemplos como requisitos de los productos reales.
