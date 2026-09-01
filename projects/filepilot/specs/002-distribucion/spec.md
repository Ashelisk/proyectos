# Especificación 002 — Distribución para usuarios finales

## Contexto y objetivo

FilePilot debe poder obtenerse desde una versión publicada sin descargar el repositorio ni instalar sus herramientas de desarrollo. La entrega ofrecerá ejecutables independientes para Windows y Linux, además de un paquete para usuarios de Python, sin cambiar el comportamiento definido por la especificación 001.

## Usuarios e historias

Persona que quiere ejecutar FilePilot en un equipo compatible.

- Quiere descargar un archivo correspondiente a su sistema y usar la aplicación sin instalar Python.
- Quiere comprobar la integridad de la descarga antes de ejecutarla.
- Si ya utiliza Python, quiere disponer de un paquete instalable que exponga el mismo comando.

## Requisitos funcionales

### Publicación

- RF-1: Cuando se publique una etiqueta con formato `vX.Y.Z` cuyo valor coincida con la versión declarada en los metadatos del paquete de FilePilot, el proceso de entrega creará automáticamente una GitHub Release asociada a esa etiqueta.
- RF-2: Antes de publicar, el proceso ejecutará las pruebas vigentes y las comprobaciones de los artefactos en sus plataformas correspondientes. Si falla una construcción, una prueba, la coincidencia de versión o una comprobación de contenido, no se publicará la release.
- RF-3: Una etiqueta que no siga `vX.Y.Z` no iniciará una publicación. Si la versión de una etiqueta válida no coincide con la de FilePilot o la release ya existe, el proceso terminará con error sin sustituir la publicación existente.

### Artefactos

- RF-4: Cada release incluirá exactamente `filepilot-vX.Y.Z-windows-x64.zip`, `filepilot-vX.Y.Z-linux-x86_64.tar.gz`, el wheel universal `filepilot-X.Y.Z-py3-none-any.whl` y `SHA256SUMS.txt`, sustituyendo `X.Y.Z` por la versión publicada.
- RF-5: El ZIP y el `tar.gz` contendrán únicamente `filepilot.exe` o `filepilot`, según la plataforma, `README.md` y `LICENSE`. No incluirán el repositorio, el router, skills, specs, planes, tareas, pruebas ni herramientas de desarrollo.
- RF-6: Cada ejecutable independiente funcionará sin una instalación de Python y conservará el comando y los códigos de salida de la especificación 001. Desde una carpeta ajena al repositorio, `--help` y un análisis de ejemplo deberán completarse correctamente.
- RF-7: El wheel será instalable con Python 3.11 o superior, no declarará dependencias de ejecución y proporcionará las entradas `filepilot` y `python -m filepilot` con el mismo comportamiento de la especificación 001.
- RF-8: `SHA256SUMS.txt` contendrá la suma SHA-256 y el nombre exacto de cada uno de los otros tres artefactos. Las sumas deberán verificarse antes de publicar.

### Documentación y licencia

- RF-9: El `README.md` incluido en cada archivo para usuarios explicará los sistemas compatibles, la puesta en marcha, el comando `analizar`, sus opciones y los códigos de salida, sin pasos de desarrollo ni referencias necesarias al flujo SDD.
- RF-10: La distribución y el repositorio incluirán la licencia MIT con `Ashelisk` como titular y 2026 como año de copyright.

## Requisitos no funcionales

- RNF-1: Los ejecutables independientes tendrán como objetivos Windows 10/11 x64 y Linux x86_64. No se afirmará compatibilidad con una plataforma que no se haya ejecutado en la validación de la release.
- RNF-2: Las herramientas de construcción serán dependencias de desarrollo y no alterarán la ausencia de dependencias externas en tiempo de ejecución de FilePilot.
- RNF-3: La publicación utilizará únicamente los permisos necesarios para crear la release y no incorporará credenciales, rutas locales ni datos del entorno de construcción a los artefactos.

## Casos límite

- Etiqueta válida con versión distinta de la aplicación o release existente: RF-3.
- Fallo de una plataforma mientras la otra construye correctamente: RF-2; no se publica una entrega parcial.
- Archivo generado con contenido adicional o nombre incorrecto: RF-2, RF-4 y RF-5.
- Ejecutable que funciona dentro del repositorio pero no desde otra carpeta: RF-6.
- Wheel con dependencias de ejecución o sin alguna entrada: RF-7.

## Fuera de alcance

Publicación en PyPI, instaladores MSI o paquetes nativos de distribuciones Linux, actualizaciones automáticas, firma de código, Windows ARM, Linux ARM y macOS.

## Criterios de finalización

Una etiqueta de prueba correspondiente a la versión de FilePilot debe producir los cuatro artefactos previstos. En Windows y Linux se ejecutarán el ejecutable independiente y el wheel desde carpetas ajenas al repositorio; se comprobarán ayuda, análisis, códigos de salida, contenido permitido de los archivos y sumas SHA-256. La validación registrará la release y los entornos realmente ejecutados.
