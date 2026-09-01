# Tarea activa

- **Objetivo:** crear un flujo compartido y seguro para continuar el desarrollo entre clones independientes de Windows y Linux mediante GitHub.
- **Rama:** `chore/cross-platform-agent-workflow`
- **Estado:** `IN_PROGRESS` — revisión de integración y endurecimiento en Windows.
- **Identificador:** `cross-platform-agent-workflow`

## Criterios de aceptación

- Documentación raíz con roles, contexto comprobado, tablero y criterios objetivos.
- Estado compartido pequeño, documentado y validable, separado de datos locales.
- Router y lanzadores que cubren `doctor`, `sync`, `status`, `test`, la simulación de `cycle` y `checkpoint` sin rutas locales codificadas.
- Ciclos reales de Claude Code y Codex limitados al puente autorizado hasta que el router pueda reutilizar todos sus controles.
- Pruebas automatizadas multiplataforma y GitHub Actions para Linux, Windows y macOS, respetando las plataformas de cada producto.
- Verificación local y CI del commit candidato antes de integrar la rama en `main` mediante avance rápido.

## Pendiente

- Ejecutar CI sobre el commit candidato antes de integrar en `main`.

## Resultados por plataforma

- **Linux:** `PENDING`; FilePilot conserva 209 superadas/4 omitidas por versión y CLI recursivo correcto; la CI debe ejecutar el router endurecido y el puente.
- **Windows:** `PASS`; router 16/16, puente 21/21 y FilePilot 205 superadas/8 omitidas sin privilegios en la regresión actual; se conserva la evidencia privilegiada de 212/1 con Python 3.11.9 y 3.14.7.
- **macOS:** `PENDING`; la CI del commit candidato debe repetir router y puente; FilePilot no aplica.
- **CI:** `PENDING`; la ejecución anterior de diez jobs corresponde a `f3c9249`, anterior al endurecimiento.

## Bloqueadores

Ninguno.

## Siguiente acción exacta

Subir el commit candidato, exigir CI correcta en su `HEAD` e integrar mediante avance rápido en `main`.
