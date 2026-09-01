# Tarea activa

- **Objetivo:** crear un flujo compartido y seguro para continuar el desarrollo entre clones independientes de Windows y Linux mediante GitHub.
- **Rama:** `chore/cross-platform-agent-workflow`
- **Estado:** `IN_PROGRESS` — implementación y Linux completos; pendiente CI multiplataforma.
- **Identificador:** `cross-platform-agent-workflow`

## Criterios de aceptación

- Documentación raíz con roles, contexto comprobado, tablero y criterios objetivos.
- Estado compartido pequeño, documentado y validable, separado de datos locales.
- Router y lanzadores que cubren `doctor`, `sync`, `status`, `test`, `cycle` y `checkpoint` sin rutas locales codificadas.
- Adaptadores basados en las interfaces instaladas de Claude Code y Codex, validados sin ejecutar agentes reales durante el bootstrap.
- Pruebas automatizadas multiplataforma y GitHub Actions para Linux, Windows y macOS, respetando las plataformas de cada producto.
- Verificación local, commit y push de esta rama; `main` permanece sin integrar.

## Pendiente

- Crear el commit y subir la rama.
- Esperar los jobs Linux, Windows y macOS de GitHub Actions.
- Corregir únicamente hallazgos reproducibles de CI; no integrar todavía en `main`.

## Resultados por plataforma

- **Linux:** `PASS`; router 12/12, puente 21/21, FilePilot 209 superadas/4 omitidas (solo Windows), CLI recursivo con código cero, JSON/bytecode/diff/secretos correctos.
- **Windows:** pendiente de CI y de la siguiente ejecución local aplicable.
- **macOS:** pendiente de CI para el router; FilePilot no declara compatibilidad con macOS.
- **CI:** pendiente tras subir la rama.

## Bloqueadores

Ninguno.

## Siguiente acción exacta

Subir `chore/cross-platform-agent-workflow` y comprobar el workflow `Pruebas multiplataforma` en GitHub Actions.
