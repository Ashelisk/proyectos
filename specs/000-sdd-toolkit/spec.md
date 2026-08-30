# Especificación 000 — Herramientas SDD

## Objetivo y usuario

Preparar herramientas reutilizables para definir, implementar y verificar incrementos de software mediante SDD.

## Alcance y requisitos

- RF-1: Cuando se pida una fase SDD, existirá una skill específica con entradas, entregables y criterio de salida.
- RF-2: Cuando se pida continuar un proyecto SDD, la coordinación identificará el proyecto, la funcionalidad activa y la primera fase pendiente sin reiniciar trabajo válido.
- RF-3: Cuando se especifique una funcionalidad, los requisitos tendrán identificadores estables y resultados observables; las dudas no se presentarán como decisiones aceptadas.
- RF-4: Cuando se planifique, implemente o valide, se mantendrá la relación requisito → tarea → evidencia.
- RF-5: Si una comprobación no se ha ejecutado, la validación la identificará como no verificada y no afirmará cumplimiento total.
- RF-6: Cuando se solicite un cambio de comportamiento, se actualizará primero su especificación y se evaluará qué planes, tareas y pruebas quedan afectados.
- RF-7: Cuando una revisión independiente aporte valor y la delegación esté permitida, se podrá encargar a un subagente acotado; si no está disponible, el flujo seguirá localmente.
- RF-8: Las skills conservarán el alcance y la autorización del usuario: pedir una fase documental no autoriza implementación, publicación ni cambios en servicios externos.
- RF-9: El paquete podrá reutilizarse en CLI, web y móvil desde Codex y Claude Code, sin imponer tecnologías, datos o rutas de un proyecto a otro. Las copias de descubrimiento coincidirán con las fuentes editables.
- RF-10: Al iniciar la creación o revisión de fondo de una constitución, el agente preguntará sobre enfoque, objetivos y restricciones, y propondrá lenguajes antes de elegir. Esperará respuestas y las convertirá en reglas operativas del documento.
- RF-11: Al definir una nueva spec, el agente iniciará una entrevista sobre el comportamiento esperado; en specs existentes preguntará cuando el cambio requiera decisiones no resueltas. Las recomendaciones del agente y una aceptación general del proyecto no se considerarán respuestas a decisiones particulares.
- RF-12: Mientras falten respuestas necesarias de esa entrevista, el documento mantendrá estado de borrador o entrevista en curso. La coordinación no cerrará la fase ni avanzará al trabajo dependiente, aunque el usuario haya autorizado desarrollar el proyecto completo.
- RF-13: Las constituciones de proyectos pequeños contendrán pocos principios breves; las specs añadirán solo el detalle necesario para implementar y verificar. Ninguna incluirá historial de conversación, perfiles del usuario o comparativas resueltas; las respuestas modificarán reglas y requisitos, sin acumularse en otros documentos.

### Puente opcional de programación y revisión

- RF-14: Un encargo autorizado podrá ejecutarse con Codex como coordinador y revisor y Claude Code como programador, mediante una sesión identificada por tarea y una copia Git aislada. Ningún encargo modificará automáticamente el checkout original ni iniciará otra tarea.
- RF-15: Los mensajes y resultados estructurados se conservarán localmente, excluidos de Git. El puente distinguirá entrega para revisión, corrección, decisión pendiente, bloqueo y aprobación; una respuesta del programador no aprobará su propia entrega. La revisión se asociará a la versión de los archivos comprobados.
- RF-16: El coordinador enviará las correcciones y repetirá las verificaciones sin intervención rutinaria. Los requisitos sin resolver se consultarán al usuario. Se limitarán rondas, tiempo y presupuesto estimado por encargo; errores, respuestas inválidas y agotamiento de límites detendrán la ejecución sin darla por completada.
- RF-17: Claude tendrá herramientas de lectura y, solo cuando se indiquen, edición de rutas autorizadas. No tendrá shell, acceso web, MCP ni control de Git desde sus herramientas. El coordinador ejecutará las pruebas necesarias en un entorno permitido y centralizará integración, commits y subidas. No se desactivarán controles de permisos para automatizar el flujo.
- RF-18: La instalación se verificará con pruebas locales del protocolo y un intercambio real de solo lectura que incluya una continuación de sesión. Se distinguirá esa evidencia de una tarea de programación completa y de plataformas no ejecutadas.

## Decisiones y límites

Se eligen nueve skills de instrucciones: una coordinadora y ocho fases. Las fuentes editables están en `skills/`; las copias de descubrimiento, en `~/.agents/skills/` para Codex y `.claude/skills/` para Claude Code. El puente de `tools/puente_agentes/` es opcional y utiliza Claude Code instalado y autenticado; no crea credenciales, servicios permanentes ni proyectos de producto.

La guía sigue Hello SDD: constitución breve, entrevista obligatoria, requisitos observables y fases dependientes secuenciales. Las preguntas se hacen en el chat; los archivos contienen el estado operativo del proyecto.

## Criterios de finalización

Validar formato y metadatos de las nueve skills, revisar sus enlaces y rutas, comprobar escenarios representativos y verificar ambas copias instaladas. Diferenciar estas comprobaciones de una garantía de comportamiento futuro del modelo.

## Dudas abiertas

Ninguna bloquea la preparación del paquete. Las decisiones y el estado de cada producto se consultan en sus propios documentos.
