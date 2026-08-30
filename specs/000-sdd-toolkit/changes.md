# Cambios del paquete SDD

## CH-1 — Definición mediante conversación obligatoria

Fecha: 2026-08-30.

- **Antes:** constitución permitía redactar a partir del contexto y preguntar solo por una decisión material; especificación favorecía un borrador sin entrevista obligatoria. La coordinación podía avanzar demasiado pronto.
- **Después:** la constitución comienza siempre con preguntas de enfoque y una elección informada de lenguaje. Las nuevas specs comienzan con entrevista; las existentes necesitan preguntas cuando sus decisiones no estén resueltas. El agente espera respuestas y edita el archivo correspondiente, sin confundir recomendaciones con elecciones del usuario.
- **Requisitos:** añade RF-10, RF-11 y RF-12; precisa RF-2, RF-3 y RF-8.
- **Impacto:** actualizar constitución, especificación y coordinación, sus metadatos, instrucciones del repositorio y guía. La regla se aplica a decisiones pendientes, sin reabrir las ya resueltas. Sin código ni migraciones.
- **Validación:** las comprobaciones previas de formato sobre los archivos modificados deben repetirse. Los dos casos históricos de clarificación y validación no prueban el nuevo comportamiento de entrevista; no se presentan como evidencia de RF-10 a RF-12.

## CH-2 — Descubrimiento en Claude Code

Fecha: 2026-08-30.

- **Antes:** las instrucciones del repositorio residían solo en `AGENTS.md` y la única copia de descubrimiento era `~/.agents/skills/`, ambas rutas de Codex. Claude Code no cargaba las instrucciones ni encontraba las skills, de modo que el método dependía de indicar los archivos a mano en cada sesión.
- **Después:** `CLAUDE.md` importa `AGENTS.md` y añade las notas propias de esa herramienta; `.claude/skills/` contiene una copia idéntica de las nueve skills. La fuente editable sigue siendo `skills/` y ambas copias se sincronizan tras cada edición.
- **Requisitos:** precisa RF-9, que ahora incluye la reutilización del paquete desde distintos entornos de agente sin duplicar fuentes. No añade requisitos nuevos.
- **Impacto:** `CLAUDE.md`, copia en `.claude/skills/`, `AGENTS.md` y `README.md`. Ningún `SKILL.md` cambia, por lo que la copia de Codex no necesita resincronizarse. Sin código ni migraciones.
- **Validación:** comprobación por SHA-256 de los 19 archivos copiados. El descubrimiento efectivo en la interfaz de Claude Code no se da por verificado.
