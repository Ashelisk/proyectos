# Tarea activa

- **Objetivo:** distribuir FilePilot como ejecutable independiente para Windows x64 y Linux x86_64, con wheel, sumas SHA-256 y GitHub Release automática.
- **Rama:** `feat/filepilot-distribucion`
- **Estado:** `IN_PROGRESS` — T1 a T5 completadas; falta publicar y validar `v0.1.0`.
- **Identificador:** `filepilot-distribucion`

## Criterios de aceptación

- La spec 002 conserva el comportamiento de la spec 001 y define cuatro artefactos públicos.
- Los archivos nativos funcionan sin Python y no contienen materiales de desarrollo o SDD.
- La versión, el contenido permitido, las sumas y las pruebas bloquean una publicación inválida o parcial.
- La release usa licencia MIT, permisos mínimos y CI nativa en Windows y Linux.
- La etiqueta `v0.1.0` produce una release verificada con los nombres acordados.

## Pendiente

- Ejecutar T6 de `projects/filepilot/specs/002-distribucion/tasks.md`.

## Resultados por plataforma

- **Linux:** `PASS`; suite, ejecutable independiente y `tar.gz` verificados en Ubuntu 22.04 con Python 3.11.
- **Windows:** `PASS`; ejecutable independiente, ZIP y wheel verificados localmente y en Windows Server 2022 con Python 3.11.
- **macOS:** `PASS`; router y puente verificados en dos versiones de Python; los artefactos de FilePilot no aplican.
- **CI:** `PASS`; las ejecuciones 33507223769 y 33507223770 completaron las tres construcciones y los diez trabajos transversales; la publicación se omitió en la rama.

## Bloqueadores

Ninguno.

## Siguiente acción exacta

Integrar el pull request 1 y crear la etiqueta `v0.1.0` para validar la release pública.
