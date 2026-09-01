# Tarea activa

- **Objetivo:** distribuir FilePilot como ejecutable independiente para Windows x64 y Linux x86_64, con wheel, sumas SHA-256 y GitHub Release automática.
- **Rama:** `main`
- **Estado:** `PASS` — `v0.1.0` publicada y validada.
- **Identificador:** `filepilot-distribucion`

## Criterios de aceptación

- La spec 002 conserva el comportamiento de la spec 001 y define cuatro artefactos públicos.
- Los archivos nativos funcionan sin Python y no contienen materiales de desarrollo o SDD.
- La versión, el contenido permitido, las sumas y las pruebas bloquean una publicación inválida o parcial.
- La release usa licencia MIT, permisos mínimos y CI nativa en Windows y Linux.
- La etiqueta `v0.1.0` produce una release verificada con los nombres acordados.

## Pendiente

Nada para esta tarea.

## Resultados por plataforma

- **Linux:** `PASS`; suite, ejecutable independiente y `tar.gz` verificados en Ubuntu 22.04 con Python 3.11.
- **Windows:** `PASS`; ejecutable independiente, ZIP y wheel verificados localmente y en Windows Server 2022 con Python 3.11.
- **macOS:** `PASS`; router y puente verificados en dos versiones de Python; los artefactos de FilePilot no aplican.
- **CI:** `PASS`; la ejecución 33521838398 completó Windows, Linux, wheel y publicación. La [release v0.1.0](https://github.com/Ashelisk/proyectos/releases/tag/v0.1.0) contiene los cuatro archivos propios previstos y sus sumas SHA-256.

## Bloqueadores

Ninguno.

## Siguiente acción exacta

Iniciar el siguiente incremento mediante su fase SDD correspondiente.
