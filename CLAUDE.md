# Instrucciones del proyecto

@AGENTS.md

## Notas de Claude Code

- Las nueve skills SDD se invocan por su nombre (`/sdd-coordinador`, `/sdd-especificacion`, …) o describiendo la fase en lenguaje natural.
- Claude Code las descubre en `.claude/skills/`, que es una copia; las fuentes editables siguen en `skills/`.
- Después de editar una skill, sincroniza esa copia y la de Codex en `~/.agents/skills/`, y comprueba que coinciden.
