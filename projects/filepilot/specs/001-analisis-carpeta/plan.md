# Plan técnico — Análisis e informe de una carpeta

## Enfoque

Aplicación de consola en Python, ejecutable como `filepilot` y como `python -m filepilot`, sin dependencias externas en tiempo de ejecución. El trabajo se divide en cuatro responsabilidades encadenadas: interpretar la invocación, recorrer el sistema de archivos decidiendo qué se examina y qué se omite, clasificar cada archivo y componer el informe. La lógica de clasificación e informe no toca el disco, de modo que puede verificarse sin crear archivos.

Estructura dentro de `projects/filepilot/`:

```
pyproject.toml
filepilot/__init__.py, __main__.py, cli.py, recorrido.py, clasificacion.py, informe.py
tests/
```

Se fija Python 3.9 o superior: es la versión mínima que ofrece las anotaciones y utilidades usadas y mantiene disponible `st_file_attributes` para el atributo oculto de Windows.

## Componentes

| Componente | Responsabilidad | Requisitos |
| --- | --- | --- |
| `cli.py` | Definir el subcomando `analizar` y sus opciones, resolver la ruta inicial, ordenar las fases y traducir el resultado a código de salida | RF-1, RF-2, RF-3, RF-11, RF-14, RF-16 |
| `recorrido.py` | Enumerar entradas, aplicar exclusiones con su prioridad, contar subcarpetas y producir archivos analizables y entradas omitidas | RF-3, RF-4, RF-9, RF-10, RF-13, RF-14, RF-15 |
| `clasificacion.py` | Mapa de extensiones, categoría de cada archivo y carpeta propuesta de cada grupo | RF-5, RF-6, RF-7 |
| `informe.py` | Agregar por grupo, formatear tamaños, tabla, extensiones desconocidas y mensaje de carpeta sin archivos | RF-7, RF-8, RF-12 |

## Datos y contratos

Estructuras internas, todas de solo lectura una vez creadas:

- `ArchivoAnalizado(ruta, categoria, tamano)` — un archivo clasificado.
- `EntradaOmitida(ruta, motivo)` — `motivo` es uno de `oculto`, `enlace`, `sin_permiso`, `error_lectura`, asignado una sola vez con esa prioridad (RF-9).
- `ResultadoRecorrido(archivos, omitidas, subcarpetas_encontradas, subcarpetas_recorridas)`.

Contrato de línea de órdenes:

```
filepilot analizar <ruta> [--recursivo] [--incluir-ocultos]
```

| Código | Situación | Requisito |
| --- | --- | --- |
| 0 | Informe emitido sin omisiones por permiso ni por error de lectura | RF-1, RF-12 |
| 1 | Uso incorrecto: falta la ruta u opción desconocida | RF-2 |
| 2 | La ruta no existe, no es un directorio o no puede leerse | RF-11 |
| 3 | Informe emitido con omisiones por permiso o por error de lectura | RF-13 |

El informe va a la salida estándar; los avisos por elemento fallido y los errores de ruta, a la salida de error, redactados en español e identificando ruta y causa (RNF-3). Ningún componente escribe en disco (RF-10) ni abre conexiones de red: la aplicación se limita a la biblioteca estándar y no consulta servicios ni credenciales (RNF-1).

Formato del informe: una fila por grupo con categoría, recuento, tamaño en base 1024 con un decimal y carpeta propuesta; fila de totales; bloque de subcarpetas y omitidos por motivo; y, cuando «otros» tenga archivos, hasta cinco extensiones ordenadas por recuento y alfabéticamente en los empates.

## Decisiones

**Recorrido con `os.scandir` en lugar de `os.walk`.** `scandir` entrega cada entrada con su tipo y sus metadatos en la misma consulta, lo que permite decidir por entrada si es enlace, si está oculta y si su tamaño es legible, y atribuir el fallo a su causa real (RF-9, RF-13). `os.walk` agrupa los errores por directorio y no permite ese detalle, y `Path.rglob` no deja podar las carpetas ocultas antes de entrar en ellas (RF-14). La recursión se implementa con una pila propia sobre `scandir`.

**Códigos de salida propios frente a los de `argparse`.** `argparse` termina con código 2 ante un uso incorrecto, valor que la spec reserva a los problemas de ruta. Se sobrescribe el método de error del analizador para terminar con código 1 (RF-2) y así mantener el contrato de la tabla anterior.

**Detección de oculto por plataforma.** Nombre que empieza por punto en cualquier sistema y, en Windows, además el bit `FILE_ATTRIBUTE_HIDDEN` de `st_file_attributes`, consultado de forma tolerante para que su ausencia no rompa el análisis en sistemas que no lo exponen (RF-15).

**Formato de tamaño sin `locale`.** El separador decimal se escribe directamente como coma, en lugar de depender de la configuración regional del sistema, para que la misma carpeta produzca el mismo informe en las tres plataformas y las pruebas sean deterministas (RF-7, RNF-2).

**Resolución de la raíz.** La ruta indicada se resuelve siguiendo enlaces antes de comprobar que es un directorio legible, lo que cubre RF-16 y permite analizar una raíz oculta sin `--incluir-ocultos` (RF-14). Las exclusiones se evalúan solo sobre lo encontrado dentro.

**Pruebas con pytest como herramienta de desarrollo.** Sus carpetas temporales y sus marcas para omitir pruebas por plataforma reducen el código de las pruebas de sistema de archivos. Se declara como dependencia de desarrollo, separada de la aplicación, que no incorpora dependencias. La alternativa, `unittest` de la biblioteca estándar, evitaría incluso esa dependencia a costa de más código repetido en la preparación de cada árbol de prueba.

## Verificación

Sin acceso a disco, sobre datos construidos en memoria: mapa de extensiones y última extensión con mayúsculas (RF-5), grupo sin extensión (RF-6), formato de tamaños y filas del informe (RF-7), límite y empates de extensiones desconocidas (RF-8), prioridad de motivos y coincidencia entre la suma por motivos y el total (RF-9), y mensaje de carpeta sin archivos analizables (RF-12).

Con sistema de archivos real, en carpetas temporales creadas por la propia prueba y eliminadas al terminar: primer nivel y modo recursivo (RF-3), recuento de subcarpetas en ambos modos (RF-4), ocultos y `--incluir-ocultos` (RF-14, RF-15), raíz oculta y raíz enlazada (RF-16), rutas inexistentes y no directorios (RF-11), y los cuatro códigos de salida (RF-1, RF-2, RF-11, RF-12, RF-13).

Comprobación específica de RF-10: se toma una instantánea del árbol de entrada —rutas, tamaños y fechas de modificación— antes y después de cada análisis y se exige que sea idéntica.

Los datos de prueba se generan siempre dentro de la carpeta temporal de la prueba; ninguna prueba usa rutas del usuario, del repositorio ni del sistema, y ninguna crea archivos fuera de ese árbol.

Verificaciones que dependen del entorno y se marcan como omitidas cuando no puede prepararse el escenario, en lugar de darse por superadas: enlaces simbólicos en Windows, que exigen privilegios; el atributo oculto de Windows, aplicable solo allí; y la denegación de permisos, no reproducible cuando la prueba se ejecuta con privilegios administrativos. La validación indicará en qué plataformas se ejecutó cada una.

## Riesgos

- El motivo `sin_permiso` puede quedar sin cobertura automática en algunos entornos; se compensa con una comprobación manual documentada en la validación.
- Una carpeta muy poblada puede producir un informe lento; la spec no fija requisitos de rendimiento y no se optimiza sin una necesidad demostrada.
- El atributo oculto de Windows depende de que la plataforma exponga `st_file_attributes`; la consulta tolerante evita el fallo, pero en un sistema que no lo ofrezca solo se detectará el punto inicial.

## Orden de implementación

1. Esqueleto del paquete, subcomando `analizar` y códigos de salida 1 y 2 con la validación de la ruta (RF-2, RF-11, RF-16).
2. Clasificación: mapa de extensiones, categoría y carpeta propuesta (RF-5, RF-6).
3. Recorrido: primer nivel, modo recursivo, exclusiones con prioridad y recuentos (RF-3, RF-4, RF-9, RF-14, RF-15).
4. Informe: tabla, tamaños, extensiones desconocidas y carpeta sin archivos analizables (RF-7, RF-8, RF-12).
5. Fallos por elemento, avisos con causa y código 3 (RF-13).
6. Comprobación de no modificación e informe de cobertura por plataforma (RF-10, RNF-2).
