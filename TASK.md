# Tarea activa

- **Objetivo:** crear un flujo compartido y seguro para continuar el desarrollo entre clones independientes de Windows y Linux mediante GitHub.
- **Rama:** `chore/cross-platform-agent-workflow`
- **Estado:** `PASS` — implementación, validación local y CI multiplataforma completas.
- **Identificador:** `cross-platform-agent-workflow`

## Criterios de aceptación

- Documentación raíz con roles, contexto comprobado, tablero y criterios objetivos.
- Estado compartido pequeño, documentado y validable, separado de datos locales.
- Router y lanzadores que cubren `doctor`, `sync`, `status`, `test`, `cycle` y `checkpoint` sin rutas locales codificadas.
- Adaptadores basados en las interfaces instaladas de Claude Code y Codex, validados sin ejecutar agentes reales durante el bootstrap.
- Pruebas automatizadas multiplataforma y GitHub Actions para Linux, Windows y macOS, respetando las plataformas de cada producto.
- Verificación local, commit y push de esta rama; `main` permanece sin integrar.

## Pendiente

- Ninguno dentro del alcance de esta rama. `main` permanece sin integrar hasta una decisión humana.

## Resultados por plataforma

- **Linux:** `PASS`; router 12/12, puente 21/21, FilePilot con Python 3.11.16 y 3.14.4: 209 superadas/4 omitidas (solo Windows) por versión; CLI recursivo con código cero.
- **Windows:** `PASS`; evidencia local de FilePilot con Python 3.11.9 y 3.14.7, más CI correcta en Python 3.11 y 3.x.
- **macOS:** `PASS`; router y puente correctos en CI con Python 3.11 y 3.x; FilePilot no declara compatibilidad con macOS.
- **CI:** `PASS`; los diez jobs de `Pruebas multiplataforma` terminaron correctamente para `f3c9249` (ejecución 33456113911).

## Bloqueadores

Ninguno.

## Siguiente acción exacta

Solicitar decisión humana antes de integrar la rama en `main`.
