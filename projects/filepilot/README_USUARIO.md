# FilePilot

FilePilot analiza una carpeta, clasifica sus archivos por extensión y muestra cómo los organizaría. El análisis es de solo lectura: no crea, mueve, renombra ni elimina archivos y tampoco abre su contenido.

## Sistemas compatibles

- Windows 10 u 11 de 64 bits: `filepilot.exe`.
- Linux x86_64: `filepilot` (verificado en Ubuntu 22.04).

## Puesta en marcha

Descarga el archivo correspondiente a tu sistema desde la release y descomprímelo. Conserva `filepilot`, este documento y `LICENSE` en la misma carpeta.

En Windows PowerShell:

```powershell
.\filepilot.exe --help
.\filepilot.exe analizar "C:\ruta\a\la\carpeta"
```

En Linux:

```bash
chmod +x filepilot
./filepilot --help
./filepilot analizar "/ruta/a/la/carpeta"
```

## Uso

```text
filepilot analizar <ruta> [--recursivo] [--incluir-ocultos]
```

- `--recursivo`: analiza también las subcarpetas no excluidas.
- `--incluir-ocultos`: incluye archivos y carpetas ocultos; las demás exclusiones siguen vigentes.

Los enlaces simbólicos encontrados durante el recorrido, los elementos sin permiso y los errores de lectura se omiten y aparecen en el resumen. La ruta inicial sí puede ser un enlace a un directorio.

## Códigos de salida

| Código | Significado |
| --- | --- |
| 0 | Informe emitido sin omisiones por permisos o errores de lectura. |
| 1 | Uso incorrecto o una opción desconocida. |
| 2 | La ruta está vacía, no existe, no es una carpeta o no puede leerse. |
| 3 | Informe emitido con alguna omisión por permisos o error de lectura. |

## Comprobar la descarga

`SHA256SUMS.txt`, disponible en la misma release, contiene la suma SHA-256 de cada archivo descargable.

Windows PowerShell:

```powershell
Get-FileHash .\filepilot-v0.1.0-windows-x64.zip -Algorithm SHA256
```

Linux:

```bash
sha256sum --check SHA256SUMS.txt
```

El valor calculado debe coincidir exactamente con el publicado.
