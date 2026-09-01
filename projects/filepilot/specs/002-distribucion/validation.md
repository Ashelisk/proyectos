# Validación — Distribución para usuarios finales

## Alcance y entorno

- Versión: `v0.1.0`, etiqueta sobre `42b9c715e004585077e141fa9b26040c6028ff4c`.
- Automatización vigente: `248ad0df6f81172e949e37b81d1b174fb2914e80`.
- Release pública: [FilePilot v0.1.0](https://github.com/Ashelisk/proyectos/releases/tag/v0.1.0), identificador `380594264`.
- Ejecución final: GitHub Actions `33521838398`, Python 3.11, Windows Server 2022 y Ubuntu 22.04.
- Comprobación local final: Windows 11, Python 3.14.7; 212 pruebas superadas y 8 omitidas por capacidades del proceso, incluidas las 7 pruebas específicas de distribución.

## Matriz

| Requisito | Evidencia | Resultado | Limitación |
| --- | --- | --- | --- |
| RF-1 | La etiqueta inició la ejecución `33508358775`; el flujo corregido completó la publicación asociada a `v0.1.0` en `33521838398`. | Cumple | La primera ejecución dejó un borrador por un defecto al consultarlo; se eliminó, se corrigió el flujo y el reintento construyó de nuevo la misma etiqueta. |
| RF-2 | Windows, Linux, wheel y publicación terminaron correctamente en `33521838398`. La ejecución fallida inicial no hizo pública una entrega parcial. | Cumple | Ninguna. |
| RF-3 | `test_version_etiqueta_y_nombres` rechaza formato y versión incorrectos; el workflow consulta también borradores antes de crear una release. | Cumple | La protección frente a una release existente se verificó por prueba e inspección del flujo. |
| RF-4 | La API de GitHub devuelve exactamente cuatro assets propios: ZIP, `tar.gz`, wheel y `SHA256SUMS.txt`. | Cumple | GitHub muestra además dos enlaces automáticos al código fuente; no forman parte de la colección de assets de la release. |
| RF-5 | Los helpers verificaron en ambos sistemas que cada archivo nativo contiene solo ejecutable, `README.md` y `LICENSE`; las pruebas rechazan contenido adicional. | Cumple | Ninguna. |
| RF-6 | Los trabajos nativos ejecutaron ayuda, uso incorrecto, ruta inválida y análisis con `PATH` vacío, desde una carpeta temporal, y compararon el árbol antes y después. | Cumple | Windows 10 se cubre como objetivo compatible del binario construido en Windows Server 2022; no se ejecutó una máquina Windows 10 separada. |
| RF-7 | El wheel se instaló con `--no-deps` en un entorno limpio con Python 3.11 y ejecutó `filepilot` y `python -m filepilot`; sus metadatos no declaran dependencias de ejecución. | Cumple | Ninguna. |
| RF-8 | El flujo generó y verificó tres sumas antes de publicar; GitHub registró un digest SHA-256 para cada archivo cargado. | Cumple | El repositorio es privado; la comprobación externa se apoya en la ejecución autenticada y los digests de la API. |
| RF-9 | `README_USUARIO.md`, empaquetado como `README.md`, documenta plataformas, puesta en marcha, opciones y códigos sin instrucciones de desarrollo. | Cumple | Ninguna. |
| RF-10 | `LICENSE` contiene MIT, `Ashelisk` y 2026; el mismo archivo se incluye en ambos paquetes nativos. | Cumple | Ninguna. |
| RNF-1 | Construcción y ejecución nativas correctas en Windows x64 y Linux x86_64. | Cumple | macOS y ARM permanecen fuera de alcance. |
| RNF-2 | `dependencies = []`; `build` y `pyinstaller` están únicamente en el extra `release`; wheel sin dependencias de ejecución. | Cumple | Ninguna. |
| RNF-3 | Permiso global `contents: read` y `contents: write` solo en publicación; allowlist de archivos y ausencia de credenciales o configuración privada en los paquetes. | Cumple | Los ejecutables incorporan el intérprete de Python como parte de su funcionamiento independiente. |

## Incidencias

La primera publicación creó correctamente el borrador y sus cuatro archivos, pero intentó consultarlo mediante un endpoint que solo resolvía la release una vez publicada. El fallo quedó registrado sin publicación parcial. El pull request 2 cambió la verificación para usar el identificador del borrador y añadió una prueba de regresión. La ejecución final reconstruyó los tres artefactos, verificó el borrador y lo publicó.

## Veredicto

**Cumple.** Todos los requisitos de la spec 002 tienen evidencia suficiente. Las limitaciones declaradas no amplían las plataformas compatibles ni ocultan fallos pendientes.
