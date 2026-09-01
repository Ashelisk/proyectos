# Estado compartido de agentes

`state.json` es el relevo versionado entre clones. Debe validar contra `state.schema.json` y contener solo datos portables y concisos. Las fechas usan UTC en formato RFC 3339 con sufijo `Z`; `verified_commit` es el SHA completo del commit realmente cubierto por la última evidencia o `null` si todavía no existe. Puede ser anterior al commit que solo registra esa evidencia, evitando fingir que un commit se verificó antes de crearlo.

Estados permitidos: `IN_PROGRESS`, `PASS`, `FAIL`, `BLOCKED` y `NEEDS_HUMAN`. Cada plataforma (`linux`, `windows`, `macos`, `ci`) registra `PENDING`, `PASS`, `FAIL`, `BLOCKED` o `NOT_APPLICABLE`, más el comando y un resumen comprobable.

No se versionan rutas absolutas, nombres de usuario, credenciales, sesiones, prompts, respuestas ni logs. El router guarda esos datos bajo `.agent-local/`, excluido por Git y separado de esta carpeta compartida. Antes de cambiar de sistema, `checkpoint` actualiza el relevo, crea un commit normal en la rama de tarea y lo sube a GitHub.
