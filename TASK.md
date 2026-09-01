# Tarea activa

- **Objetivo:** crear un flujo compartido y seguro para continuar el desarrollo entre clones independientes de Windows y Linux mediante GitHub.
- **Rama:** `main`
- **Estado:** `PASS` — flujo integrado y verificado.
- **Identificador:** `cross-platform-agent-workflow`

## Criterios de aceptación

- Documentación raíz con roles, contexto comprobado, tablero y criterios objetivos.
- Estado compartido pequeño, documentado y validable, separado de datos locales.
- Router y lanzadores que cubren `doctor`, `sync`, `status`, `test`, la simulación de `cycle` y `checkpoint` sin rutas locales codificadas.
- Ciclos reales de Claude Code y Codex limitados al puente autorizado hasta que el router pueda reutilizar todos sus controles.
- Pruebas automatizadas multiplataforma y GitHub Actions para Linux, Windows y macOS, respetando las plataformas de cada producto.
- Verificación local y CI del commit candidato antes de integrar la rama en `main` mediante avance rápido.

## Pendiente

Nada para esta tarea.

## Resultados por plataforma

- **Linux:** `PASS`; la CI ejecutó router y puente con Python 3.11 y la última disponible; FilePilot conserva 209 superadas/4 omitidas por versión y CLI recursivo correcto.
- **Windows:** `PASS`; router 16/16, puente 21/21 y FilePilot 205 superadas/8 omitidas sin privilegios en la regresión local; la CI pasó en dos versiones y se conserva la evidencia privilegiada de 212/1 con Python 3.11.9 y 3.14.7.
- **macOS:** `PASS`; router y puente pasaron en dos versiones de Python; FilePilot no aplica.
- **CI:** `PASS`; los diez trabajos de la ejecución 33503661988 pasaron sobre `b2d9bbe` con las acciones oficiales v7.

## Bloqueadores

Ninguno.

## Siguiente acción exacta

Sincronizar `main` con `agent-router sync` en el siguiente sistema y abrir la próxima tarea mediante su fase SDD correspondiente.
