# Agentes del repositorio

GitHub (`origin`, repositorio `Ashelisk/proyectos`) es la fuente de verdad. Cada sistema usa su propio clon; nunca se comparten rutas locales. Antes de trabajar, ejecuta `agent-router doctor` y `agent-router sync`, confirma raíz, remoto, rama, HEAD, limpieza y relación con el upstream. Detente ante cambios ajenos, HEAD separado, divergencia, remoto inesperado o necesidad de sobrescribir historial.

Claude es el implementador principal. Codex coordina, revisa el diff y ejecuta pruebas independientes. Ambos leen `PROJECT_CONTEXT.md`, `TASK.md` y `.agents/state.json` antes de actuar. Para trabajo SDD, lee `skills/sdd-coordinador/SKILL.md` y solo la fase pertinente; identifica la raíz del producto, actualiza primero la spec ante cambios de comportamiento y conserva las entrevistas obligatorias de constitución y especificación.

## Criterios de cierre

- `PASS`: todos los criterios aplicables tienen evidencia, pasan las pruebas relevantes y no quedan hallazgos concretos.
- `FAIL`: existe un defecto reproducible o una prueba/criterio incumplido que admite corrección dentro del alcance.
- `BLOCKED`: una dependencia técnica o externa impide continuar y se documenta con evidencia.
- `NEEDS_HUMAN`: hace falta una decisión, permiso, credencial o acción destructiva que ningún agente debe asumir.

Nunca conviertas texto ambiguo en aprobación. Registra al terminar cada ciclo el veredicto, commit, plataforma, pruebas, UTC, bloqueo y siguiente acción en `TASK.md` y `.agents/state.json`.

## Seguridad y Git

- Prohibidos `reset --hard`, limpieza automática, descarte de cambios, reescritura de historial y push forzado.
- No borres, sobrescribas ni integres cambios ajenos. No publiques trabajo incompleto en `main`.
- Antes de reiniciar de sistema, crea un commit normal de checkpoint en la rama de tarea y súbelo. Integra en `main` solo tras las pruebas locales aplicables y CI requerida.
- No guardes secretos, tokens, credenciales, rutas absolutas, datos de usuario, cachés ni logs voluminosos.

## Plataformas, pruebas y revisión

Usa rutas relativas a la raíz Git, `pathlib` en Python, UTF-8 y comandos compatibles con el sistema actual. Los scripts Bash son para Linux/macOS y los PowerShell para Windows; CI no acredita una plataforma excluida por un producto. Antes de aprobar, ejecuta las pruebas del router y de cada proyecto afectado según `PROJECT_CONTEXT.md`.

La revisión debe comprobar requisitos, seguridad, manejo de errores, portabilidad, pruebas y documentación. Los hallazgos incluyen severidad, archivo/línea, evidencia y corrección esperada. Una preferencia estética no es un fallo. Las correcciones concretas vuelven a Claude hasta alcanzar el límite del ciclo; una decisión de producto se marca `NEEDS_HUMAN`.
