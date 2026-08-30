# Plan — Herramientas SDD

1. Mantener nueve carpetas independientes bajo `skills/`, cada una con `SKILL.md` y metadatos de interfaz. Las fases podrán utilizarse sin cargar todo el paquete. Cubre RF-1 y RF-9.
2. Usar una coordinadora para identificar el estado real, elegir la fase y respetar el límite solicitado. Añadir una referencia breve para delegaciones de revisión. Cubre RF-2, RF-7 y RF-8.
3. Describir en cada fase la evidencia necesaria para pasar a la siguiente. Preservar identificadores al cambiar requisitos. Cubre RF-3 a RF-6.
4. Registrar el método SDD en `AGENTS.md`, importarlo desde `CLAUDE.md` y explicar el uso en `README.md`, sin decidir el enfoque ni las tecnologías de los productos desde el toolkit. Cubre RF-8 y RF-9.
5. Validar estructura, referencias y casos de uso; después sincronizar las copias de `~/.agents/skills/` y `.claude/skills/` sin reemplazar skills ajenas. La comprobación de hashes confirmará la igualdad con las fuentes.

Se prefieren skills a nueve agentes permanentes porque el conocimiento es reutilizable y la mayoría de las fases dependen de la anterior. Los subagentes se reservan para revisiones concretas.

## Puente de programación y revisión

RF-14 a RF-18: script Python 3.11+ con biblioteca estándar en `tools/puente_agentes/`, separado de los productos. Usa `git worktree add --detach` para aislar cada tarea y `claude -p --output-format json` con identificador explícito para enviar y continuar encargos. Codex coordina desde la conversación activa; el puente no lanza otro Codex ni es un servicio desatendido.

El estado, los encargos y las respuestas residen en `.sdd-check/puente/`. Un bloqueo exclusivo evita envíos simultáneos y una huella del diff y archivos nuevos vincula la revisión a la entrega. Solo el coordinador registra el veredicto. Claude recibe las instrucciones SDD y un protocolo común; sus herramientas excluyen shell, web y MCP. La edición requiere rutas explícitas, sin permitir modificar instrucciones ni requisitos. Las pruebas las ejecuta el coordinador, no un comando generado y ejecutado automáticamente.

Por defecto: tres envíos, diez minutos por envío y dos dólares de presupuesto estimado acumulado comunicado a Claude Code. El límite monetario es una cota de estimación del CLI, no una garantía de facturación o cuota de suscripción. Ante respuesta inválida, interrupción, permisos insuficientes o falta de acceso, se conserva el estado y se detiene el ciclo. No hay integración ni limpieza destructiva automáticas.

Verificación: datos desechables para aislamiento Git, continuidad, límites, concurrencia, respuestas inválidas y revisión de una entrega alterada; después dos intercambios reales de solo lectura. La aprobación técnica exige pruebas y diff revisados, no solo que el CLI devuelva cero.

RF-19: perfil explícito por encargo con `claude-opus-5` y `xhigh`. Los ajustes de `enviar --modelo/--esfuerzo` requieren motivo cuando cambian el perfil. La revisión puede marcar una corrección fallida; dos marcas consecutivas elevan a `max` el siguiente envío disponible, sin contar como corrección el rechazo de la entrega inicial. Se conservan identificador de sesión y límites. El nivel se pasa también en el entorno del proceso hijo para evitar que una variable heredada lo sustituya; no se modifica la configuración global. El estado registra perfil y modelos comunicados por el CLI. Las pruebas anteriores del puente conservan su alcance, pero no acreditan esta selección hasta verificarla.

## Ajuste CH-1 — Entrevistas

Las instrucciones y metadatos de constitución, especificación y coordinación deben cumplir RF-10 a RF-12: preguntar las decisiones pendientes y conservar las ya resueltas. Propagar la regla a `AGENTS.md` y la guía. Tras modificar skills, repetir la validación de formato, revisar la coherencia de las reglas y sincronizar ambas copias de descubrimiento.
