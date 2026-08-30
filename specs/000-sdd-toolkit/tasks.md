# Tareas — Herramientas SDD

- [x] T1 — Contrastar Hello SDD y las convenciones de Codex. RF-1, RF-9. Hecho cuando: las fuentes y las diferencias de adaptación están identificadas.
- [x] T2 — Escribir las nueve skills y sus metadatos. RF-1 a RF-6, RF-8, RF-9. Hecho cuando: cada fase tiene un alcance preciso y entregables verificables.
- [x] T3 — Añadir coordinación, guía de delegación e instrucciones del repositorio. RF-2, RF-7 a RF-9. Hecho cuando: es posible retomar una fase sin ejecutar otras no solicitadas.
- [x] T4 — Validar estructura y escenarios de uso. RF-1 a RF-9. Hecho cuando: se documentan resultados reales, incidencias y límites de las comprobaciones.
- [x] T5 — Instalar las skills personales. RF-9. Hecho cuando: la copia en una ruta de descubrimiento de Codex coincide con las fuentes y no se han sobrescrito skills ajenas.

## Evidencia y cierre

Completado el 2026-08-30. Nueve skills superan el validador de formato y las comprobaciones de metadatos/enlaces. Dos escenarios se ejecutaron mediante una revisión independiente. Diecinueve archivos instalados coinciden por SHA-256 con sus fuentes y las nueve entradas se pueden leer desde el entorno restringido. Detalles y límites en `validation.md`.

T1–T5 describen la entrega inicial. Su evidencia histórica se conserva; no valida por sí sola los cambios siguientes.

## Ajuste CH-1

- [x] T6 — Corregir el flujo de entrevista. RF-10 a RF-12. Hecho cuando: las instrucciones exigen preguntas, respuestas reales y edición del documento, conservando decisiones ya resueltas.
- [x] T7 — Validar y sincronizar las tres skills modificadas. RF-9 a RF-12. Hecho cuando: formato y metadatos son válidos, la revisión documental no encuentra reglas contradictorias y las copias personales coinciden con las fuentes.

Evidencia CH-1: validador repetido con nueve resultados válidos; revisados los seis diffs antes de sincronizar; comprobados sus hashes previos y posteriores. Los 19 archivos del paquete instalado coinciden con las fuentes. Revisión documental de RF-10 a RF-12 completada; no se ha ejecutado una nueva evaluación independiente de entrevista.

El estado de cada producto se consulta en sus documentos; estas tareas no reabren entrevistas ni decisiones ya resueltas.

## Ajuste CH-2

- [x] T8 — Preparar el descubrimiento en Claude Code y documentar las copias. RF-9. Hecho cuando: `CLAUDE.md` importa las instrucciones del repositorio, `.claude/skills/` coincide con las fuentes y `AGENTS.md` y `README.md` describen las dos copias y su sincronización.
- [x] T9 — Alinear las referencias al estado de FilePilot. RF-2 y RF-12. Hecho cuando: el README refleja su constitución vigente y el toolkit no exige repetir decisiones ya resueltas.

Evidencia CH-2: los 19 archivos de `.claude/skills/` coinciden por SHA-256 con `skills/`; no se ha modificado ningún `SKILL.md` ni la copia de `~/.agents/skills/`. T9 se comprueba mediante revisión documental de las referencias al producto.
