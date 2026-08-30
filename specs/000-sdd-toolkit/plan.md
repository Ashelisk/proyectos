# Plan — Herramientas SDD

1. Mantener nueve carpetas independientes bajo `skills/`, cada una con `SKILL.md` y metadatos de interfaz. Las fases podrán utilizarse sin cargar todo el paquete. Cubre RF-1 y RF-9.
2. Usar una coordinadora para identificar el estado real, elegir la fase y respetar el límite solicitado. Añadir una referencia breve para delegaciones de revisión. Cubre RF-2, RF-7 y RF-8.
3. Describir en cada fase la evidencia necesaria para pasar a la siguiente. Preservar identificadores al cambiar requisitos. Cubre RF-3 a RF-6.
4. Registrar el método SDD en `AGENTS.md`, importarlo desde `CLAUDE.md` y explicar el uso en `README.md`, sin decidir el enfoque ni las tecnologías de los productos desde el toolkit. Cubre RF-8 y RF-9.
5. Validar estructura, referencias y casos de uso; después sincronizar las copias de `~/.agents/skills/` y `.claude/skills/` sin reemplazar skills ajenas. La comprobación de hashes confirmará la igualdad con las fuentes.

Se prefieren skills a nueve agentes permanentes porque el conocimiento es reutilizable y la mayoría de las fases dependen de la anterior. Los subagentes se reservan para revisiones concretas.

## Ajuste CH-1 — Entrevistas

Las instrucciones y metadatos de constitución, especificación y coordinación deben cumplir RF-10 a RF-12: preguntar las decisiones pendientes y conservar las ya resueltas. Propagar la regla a `AGENTS.md` y la guía. Tras modificar skills, repetir la validación de formato, revisar la coherencia de las reglas y sincronizar ambas copias de descubrimiento.
