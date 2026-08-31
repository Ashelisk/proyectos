# FilePilot

Herramienta de consola que examina una carpeta, clasifica sus archivos por
extensión y muestra la organización que propondría. El análisis es de solo
lectura: no crea, mueve, renombra ni elimina nada, tampoco las carpetas de
destino que propone, y no abre el contenido de los archivos. Funciona en local,
sin cuentas ni servicios externos.

## Requisitos

Python 3.11 o superior. La aplicación no necesita dependencias externas.

## Instalación

Desde `projects/filepilot`, en un entorno virtual:

Windows (PowerShell):

```powershell
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
pip install .
```

Linux y macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install .
```

## Uso

```
filepilot analizar <ruta> [--recursivo] [--incluir-ocultos]
```

Equivale a `python -m filepilot analizar <ruta>` si se prefiere invocar el
módulo. La ruta puede ser relativa o absoluta; si apunta a un enlace simbólico
a un directorio, se analiza su destino.

| Opción | Efecto |
| --- | --- |
| `--recursivo` | Examina también el contenido de las subcarpetas no excluidas. |
| `--incluir-ocultos` | Examina los archivos y carpetas ocultos; las demás exclusiones siguen vigentes. |

Sin `--recursivo` solo se examina el primer nivel de la carpeta. No se
clasifican los elementos ocultos, los enlaces simbólicos, los que no permiten su
lectura ni aquellos cuya lectura falla; cada uno se cuenta una sola vez en el
resumen de omitidos y los fallos se avisan en la salida de error.

Ejemplo de informe:

```
Análisis de «/home/ana/descargas»

Categoría      Archivos    Tamaño  Destino propuesto
Imágenes              3    1,4 MB  /home/ana/descargas/imagenes
Documentos            2   12,0 KB  /home/ana/descargas/documentos
Otros                 4    3,2 KB  /home/ana/descargas/otros
Total                 9    1,4 MB

Extensiones desconocidas: .log (3), .cfg (1)
Subcarpetas: 2 encontradas
Omitidos: 3 (ocultos 2, enlaces 1, sin permiso 0, errores de lectura 0)
```

El informe se escribe en la salida estándar; los errores y los avisos, en la
salida de error. Los tamaños usan la base 1024 con un decimal y coma decimal
fija, independiente de la configuración regional.

Se conserva la codificación de la terminal o de la salida redirigida. Los
caracteres que no pueda representar se muestran como escapes, por ejemplo
`\u0416`, sin interrumpir el análisis. Con una salida UTF-8 se muestran completos.

## Códigos de salida

| Código | Situación |
| --- | --- |
| 0 | Informe emitido sin omisiones por permiso ni por error de lectura. |
| 1 | Uso incorrecto: falta la ruta o se indicó una opción desconocida. |
| 2 | Ruta vacía, inexistente, que no es un directorio o que no puede leerse. |
| 3 | Informe emitido con alguna omisión por permiso o por error de lectura. |

## Pruebas

Con el entorno activado, desde `projects/filepilot`:

```
pip install -e ".[dev]"
pytest
```

Algunas pruebas se omiten cuando el entorno no permite preparar su escenario:
la creación de enlaces simbólicos sin el privilegio correspondiente, el atributo
de oculto de Windows fuera de esa plataforma y la denegación real de permisos.
Las plataformas y versiones en las que se ha ejecutado la suite se registran en
[la validación de la funcionalidad](specs/001-analisis-carpeta/validation.md).

## Alcance

Esta versión analiza e informa. Mover u organizar archivos, resolver conflictos
de nombre, detectar duplicados, configurar reglas de clasificación y producir
salida en JSON quedan fuera de
[la especificación vigente](specs/001-analisis-carpeta/spec.md).
