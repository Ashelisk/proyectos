# Tarea activa

- **Objetivo:** distribuir FilePilot como ejecutable independiente para Windows x64 y Linux x86_64, con wheel, sumas SHA-256 y GitHub Release automática.
- **Rama:** `feat/filepilot-distribucion`
- **Estado:** `IN_PROGRESS` — especificación, clarificación, plan y tareas preparados; comienza T1.
- **Identificador:** `filepilot-distribucion`

## Criterios de aceptación

- La spec 002 conserva el comportamiento de la spec 001 y define cuatro artefactos públicos.
- Los archivos nativos funcionan sin Python y no contienen materiales de desarrollo o SDD.
- La versión, el contenido permitido, las sumas y las pruebas bloquean una publicación inválida o parcial.
- La release usa licencia MIT, permisos mínimos y CI nativa en Windows y Linux.
- La etiqueta `v0.1.0` produce una release verificada con los nombres acordados.

## Pendiente

- Ejecutar T1 a T6 de `projects/filepilot/specs/002-distribucion/tasks.md`.

## Resultados por plataforma

- **Linux:** `PENDING`; falta construir y probar el ejecutable independiente.
- **Windows:** `PENDING`; falta construir y probar el ejecutable independiente.
- **macOS:** `NOT_APPLICABLE`; FilePilot y sus artefactos nativos no incluyen esta plataforma.
- **CI:** `PENDING`; falta validar el workflow de release y el commit candidato.

## Bloqueadores

Ninguno.

## Siguiente acción exacta

Completar T1 y continuar por las dependencias hasta validar los artefactos y la release.
