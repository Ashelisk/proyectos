# Plan técnico — Distribución para usuarios finales

## Enfoque

Una automatización de GitHub Actions construirá cada ejecutable en su sistema de destino, generará el wheel en un trabajo separado y publicará una release solo después de verificar todos los artefactos. PyInstaller creará ejecutables de un solo archivo con su propio intérprete; no es un compilador cruzado, por lo que Windows y Linux usarán runners distintos ([documentación oficial](https://github.com/pyinstaller/pyinstaller)).

El código de análisis no cambia. Las herramientas de entrega quedarán como dependencias opcionales de desarrollo y los archivos publicados se prepararán en directorios temporales con una lista cerrada de contenido.

## Componentes

| Componente | Responsabilidad | Requisitos |
| --- | --- | --- |
| `pyproject.toml` | Declarar la licencia y las herramientas de construcción separadas de la aplicación | RF-7, RF-10, RNF-2 |
| `LICENSE` | Aplicar la licencia MIT al repositorio y acompañar cada ejecutable | RF-5, RF-10 |
| `projects/filepilot/README_USUARIO.md` | Instrucciones destinadas a quien descarga un ejecutable | RF-5, RF-9, RNF-1 |
| `projects/filepilot/tools/release.py` | Validar versión, construir archivos, comprobar contenido y sumas y ejecutar pruebas de humo | RF-1 a RF-9, RNF-3 |
| `projects/filepilot/tools/filepilot_entry.py` | Entrada absoluta y mínima que PyInstaller convierte en ejecutable | RF-6 |
| `.github/workflows/release-filepilot.yml` | Construir en Windows y Linux, generar el wheel, reunir resultados y publicar la release | RF-1 a RF-8, RNF-1 a RNF-3 |
| `projects/filepilot/tests/test_release.py` | Verificar en local las reglas puras de versión, nombres, contenido y sumas | RF-1, RF-3 a RF-5, RF-8 |

## Contratos de entrega

La versión canónica se lee de `project.version` en `pyproject.toml`. `filepilot.__version__` debe coincidir. La etiqueta aporta la misma versión precedida por `v`; cualquier diferencia detiene el flujo antes de construir.

El helper de release ofrecerá operaciones explícitas:

```text
release.py validar-version --tag vX.Y.Z
release.py empaquetar --plataforma windows|linux --ejecutable <ruta> --salida <directorio>
release.py verificar-archivo --plataforma windows|linux --archivo <ruta>
release.py verificar-ejecutable --ejecutable <ruta>
release.py sumas --directorio <ruta>
release.py verificar-sumas --directorio <ruta>
```

`empaquetar` generará un ZIP o `tar.gz` con tres entradas exactas: ejecutable, `README.md` y `LICENSE`. En Linux conservará el permiso de ejecución. `sumas` exigirá los dos archivos nativos y el único wheel con los nombres de RF-4 antes de escribir `SHA256SUMS.txt`.

La prueba de humo ejecutará por ruta absoluta, desde una carpeta temporal ajena al repositorio y con un `PATH` que no aporte Python: `--help`, uso incorrecto, ruta inexistente y análisis de una carpeta desechable. Comparará el árbol antes y después para conservar RF-10 de la spec 001.

## Flujo de CI

1. Una etiqueta `v*.*.*` inicia el workflow; el helper exige el formato numérico estricto y la coincidencia de versión.
2. Dos trabajos, `windows-2022` y `ubuntu-22.04`, instalan las dependencias de desarrollo, ejecutan la suite, construyen con PyInstaller y prueban el ejecutable y su archivo.
3. Un trabajo Linux construye el wheel, comprueba sus metadatos y lo instala sin dependencias en un entorno nuevo para probar ambas entradas.
4. Cada trabajo transfiere solo su artefacto mediante `actions/upload-artifact@v7`. El trabajo final los reúne con `actions/download-artifact@v8`, versiones recomendadas actualmente por sus repositorios oficiales.
5. El trabajo final valida los tres nombres, genera y verifica `SHA256SUMS.txt`, comprueba que la etiqueta no tenga release y crea una release en borrador con los cuatro archivos. Solo la publica después de confirmar la carga completa.

El workflow tendrá `contents: read` por defecto. Únicamente el trabajo que crea la release tendrá `contents: write`; no habrá secretos propios ni publicación en PyPI.

## Decisiones

**PyInstaller frente a Nuitka.** PyInstaller empaqueta el intérprete y permite un ejecutable único sin exigir compiladores adicionales. Nuitka puede producir binarios optimizados, pero añade toolchains y tiempo de compilación sin una necesidad funcional en esta CLI. PyInstaller queda limitado a la dependencia de release y nunca se importa desde FilePilot.

**Construcción nativa frente a compilación cruzada.** PyInstaller declara que no es un compilador cruzado. Usar un runner por plataforma reduce supuestos y permite ejecutar el archivo que realmente se publicará.

**Release en borrador antes de publicar.** Los trabajos de construcción deben haber pasado antes de crearla. El borrador evita exponer una entrega parcial si falla la carga o la última verificación; una release ya existente se rechaza en vez de sobrescribirse.

**Helper en Python estándar.** Centralizar nombres, listas permitidas, sumas y comprobaciones evita duplicar reglas entre Bash y PowerShell. El helper usa solo la biblioteca estándar; PyInstaller y `build` se limitan a sus operaciones de construcción.

## Verificación

- Pruebas puras: formato y coincidencia de versión, nombres de artefactos, allowlist del ZIP y `tar.gz`, permisos Linux, rechazo de entradas adicionales y generación/verificación de sumas.
- Pruebas por plataforma: suite completa de FilePilot, ejecución del binario independiente fuera del repositorio y comprobación de que el árbol analizado no cambia.
- Wheel: inspección de metadatos sin dependencias de ejecución, instalación con `--no-deps` en un entorno nuevo y ejecución como comando y módulo.
- Publicación: una etiqueta válida crea una sola release pública con cuatro archivos; una versión distinta falla antes de publicar. La release real será la evidencia final, no se simulará su existencia.

## Riesgos

- Un ejecutable de PyInstaller puede activar falsos positivos de antivirus; se documentará el SHA-256 y no se afirmará firma de código.
- El binario Linux depende de la familia y antigüedad del sistema usado para construirlo. La documentación identificará Ubuntu 22.04 x86_64 como entorno verificado y no prometerá otras distribuciones sin evidencia.
- La creación de una etiqueta y release es externa e irreversible para el historial publicado. Se realizará solo después de que el commit de entrega esté integrado y toda la CI previa pase.

## Orden de implementación

1. Licencia, documentación para usuarios y metadatos de construcción.
2. Helper de release y sus pruebas puras.
3. Construcción y prueba local del ejecutable Windows y del wheel.
4. Workflow con construcción nativa, verificación, sumas y publicación en borrador.
5. CI de rama, integración, etiqueta `v0.1.0`, release real y validación final en Windows y Linux.
