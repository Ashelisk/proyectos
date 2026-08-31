# Plan técnico — Análisis e informe de una carpeta

## Enfoque

Aplicación de consola en Python, ejecutable como `filepilot` y como `python -m filepilot`, sin dependencias externas en tiempo de ejecución. El trabajo se divide en cuatro responsabilidades encadenadas: interpretar la invocación, recorrer el sistema de archivos decidiendo qué se examina y qué se omite, clasificar cada archivo y componer el informe. La lógica de clasificación e informe no toca el disco, de modo que puede verificarse sin crear archivos.

Estructura dentro de `projects/filepilot/`:

```
pyproject.toml
filepilot/__init__.py, __main__.py, cli.py, recorrido.py, clasificacion.py, informe.py
tests/
```

Python 3.11 o superior permite una base compatible con pytest y con soporte de seguridad previsto hasta octubre de 2027 para la versión mínima ([ciclo de soporte](https://devguide.python.org/versions/)). Las pruebas se ejecutarán con la versión mínima y con la última estable disponible en cada plataforma; la validación identificará las versiones realmente utilizadas.

## Componentes

| Componente | Responsabilidad | Requisitos |
| --- | --- | --- |
| `cli.py` | Definir el subcomando `analizar` y sus opciones, resolver la ruta inicial, ordenar las fases, emitir los avisos por entrada fallida y traducir el resultado a código de salida | RF-1, RF-2, RF-3, RF-11, RF-13, RF-14, RF-16 |
| `recorrido.py` | Enumerar entradas, aplicar exclusiones con su prioridad, contar subcarpetas y producir archivos analizables y entradas omitidas | RF-3, RF-4, RF-9, RF-10, RF-13, RF-14, RF-15 |
| `clasificacion.py` | Mapa de extensiones, categoría de cada archivo y carpeta propuesta de cada grupo | RF-5, RF-6, RF-7 |
| `informe.py` | Agregar por grupo, formatear tamaños, tabla, extensiones desconocidas y mensaje de carpeta sin archivos | RF-7, RF-8, RF-12 |

## Datos y contratos

`clasificar(nombre: str) -> Categoria` recibe un nombre de archivo, sin consultar el sistema de archivos. `Categoria` enumera los siete grupos; su propiedad `carpeta` devuelve el nombre de destino de RF-7. La exclusión de ocultos pertenece al recorrido, no a la clasificación.

Estructuras internas, todas de solo lectura una vez creadas:

- `ArchivoAnalizado(ruta, categoria, tamano)` — un archivo clasificado.
- `EntradaOmitida(ruta, motivo, detalle)` — `motivo` es uno de `oculto`, `enlace`, `sin_permiso`, `error_lectura`, asignado una sola vez con esa prioridad y usado para los recuentos y el código de salida (RF-9, RF-13). `detalle` expresa en español la causa real a partir del tipo y código del fallo, sin copiar mensajes dependientes del idioma del sistema ni inventar una causa desconocida. Está vacío para las omisiones por ocultación o enlace.
- `ResultadoRecorrido(archivos, omitidas, subcarpetas_encontradas, subcarpetas_recorridas)`.

Contrato de línea de órdenes:

```
filepilot analizar <ruta> [--recursivo] [--incluir-ocultos]
```

| Código | Situación | Requisito |
| --- | --- | --- |
| 0 | Informe emitido sin omisiones por permiso ni por error de lectura | RF-1, RF-12 |
| 1 | Uso incorrecto: falta la ruta u opción desconocida | RF-2 |
| 2 | Ruta vacía, inexistente, no directorio o fallo al resolver o leer la raíz | RF-11 |
| 3 | Informe emitido con omisiones por permiso o por error de lectura | RF-13 |

El informe va a la salida estándar; los avisos por elemento fallido y los errores de ruta, a la salida de error, redactados en español e identificando ruta y causa (RNF-3). El recorrido no escribe en ninguna salida: devuelve cada `EntradaOmitida` con su `detalle`, y `cli.py` es el único responsable de emitir un aviso por cada entrada omitida que lo lleve y de decidir el código de salida a partir de los motivos presentes. Así el recuento y el texto comunicado proceden del mismo dato y ninguna causa se reconstruye por suposición. Ningún componente escribe en disco (RF-10) ni abre conexiones de red: la aplicación se limita a la biblioteca estándar y no consulta servicios ni credenciales (RNF-1).

Formato del informe: una fila por grupo con categoría, recuento, tamaño en base 1024 con un decimal y carpeta propuesta; fila de totales; bloque de subcarpetas y omitidos por motivo; y, cuando «otros» tenga archivos, hasta cinco extensiones ordenadas por recuento y alfabéticamente en los empates.

## Decisiones

**Recorrido con `os.scandir` en lugar de `os.walk`.** `scandir` entrega un objeto por entrada con métodos propios para saber si es directorio o enlace sin seguir el destino, y permite decidir entrada por entrada qué se examina, qué se poda y a qué causa se atribuye un fallo (RF-9, RF-13, RF-14). En Windows los metadatos llegan ya con la enumeración; en Unix, `DirEntry.stat()` consulta el sistema la primera vez y guarda el resultado, de modo que no se repite por entrada. `os.walk` también permitiría consultar cada archivo y notificar con `onerror` los fallos de enumeración, pero entrega los directorios ya agrupados en listas, lo que obliga a un tratamiento aparte para podar las carpetas ocultas y complica atribuir el fallo a la entrada concreta. La recursión se implementa con una pila propia sobre `scandir`, sin seguir enlaces.

**Códigos de salida propios frente a los de `argparse`.** `argparse` termina con código 2 ante un uso incorrecto, valor que la spec reserva a los problemas de ruta. Se sobrescribe el método de error del analizador para terminar con código 1 (RF-2) y así mantener el contrato de la tabla anterior.

**Detección de oculto por plataforma.** Nombre que empieza por punto en cualquier sistema y, en Windows, además el bit `FILE_ATTRIBUTE_HIDDEN` de `st_file_attributes`. Su ausencia solo se tolera fuera de Windows. Si la consulta falla en Windows, se respeta la prioridad de RF-9: `sin_permiso` cuando esa sea la causa y `error_lectura` para los demás fallos, con su aviso (RF-15, RF-13). Un atributo no comprobado no se interpreta como ausencia de ocultación; las exclusiones se aplican dentro del alcance de RF-4 y RF-14.

**Formato de tamaño sin `locale`.** El separador decimal se escribe directamente como coma, en lugar de depender de la configuración regional del sistema, para que la misma carpeta produzca el mismo informe en las tres plataformas y las pruebas sean deterministas (RF-7, RNF-2).

**Resolución de la raíz.** Una cadena vacía se rechaza antes de resolverla, sin convertirla en el directorio actual. Las demás rutas se resuelven siguiendo enlaces antes de comprobar que son un directorio legible, lo que cubre RF-16 y permite analizar una raíz oculta sin `--incluir-ocultos` (RF-14). Los fallos de resolución o lectura, incluidos los bucles de enlaces, terminan en código dos con ruta y causa en español (RF-11). Las exclusiones se evalúan solo sobre lo encontrado dentro.

**Pruebas con pytest como herramienta de desarrollo.** Sus carpetas temporales y sus marcas para omitir pruebas por plataforma reducen el código de las pruebas de sistema de archivos. Se declara como dependencia de desarrollo, separada de la aplicación, que no incorpora dependencias. La alternativa, `unittest` de la biblioteca estándar, evitaría incluso esa dependencia a costa de más código repetido en la preparación de cada árbol de prueba.

## Verificación

Sin acceso a disco, sobre datos construidos en memoria: mapa de extensiones y última extensión con mayúsculas (RF-5), grupo sin extensión (RF-6), formato de tamaños y filas del informe (RF-7), límite y empates de extensiones desconocidas (RF-8), prioridad de motivos y coincidencia entre la suma por motivos y el total (RF-9), y mensaje de carpeta sin archivos analizables (RF-12).

Con sistema de archivos real, en carpetas temporales creadas por la propia prueba y eliminadas al terminar: primer nivel y modo recursivo (RF-3), recuento de subcarpetas en ambos modos (RF-4), ocultos y `--incluir-ocultos` (RF-14, RF-15), raíz oculta y raíz enlazada (RF-16), rutas relativas y absolutas y nombres no ASCII (RNF-2), rutas inexistentes y no directorios (RF-11), y los cuatro códigos de salida (RF-1, RF-2, RF-11, RF-12, RF-13).

RF-10 se comprobará comparando el árbol —rutas, tamaños y fechas de modificación— antes y después del análisis y registrando las aperturas de contenido mediante el [evento de auditoría `open`](https://docs.python.org/3.11/library/audit_events.html). La prueba se ejecutará en un proceso aislado y exigirá que el análisis no abra el contenido de ningún archivo del árbol. El registro se limitará al análisis, excluyendo la preparación y limpieza de los datos de prueba.

Fallos controlados para RF-13: se sustituye temporalmente la consulta de metadatos para provocar errores de archivo inexistente, permisos y entrada/salida. Se comprobarán continuación, motivo único, aviso con ruta y causa en español y código tres, incluso sin archivos clasificados (RF-12). Se incluirán un error cuyo texto original esté en otro idioma (RNF-3) y fallos de consulta del atributo oculto de Windows (RF-15).

Los datos de prueba se generan siempre dentro de la carpeta temporal de la prueba; ninguna prueba usa rutas del usuario, del repositorio ni del sistema, y ninguna crea archivos fuera de ese árbol.

Verificaciones que dependen del entorno y se marcan como omitidas cuando no puede prepararse el escenario, en lugar de darse por superadas: la creación de enlaces simbólicos en Windows, que necesita el privilegio correspondiente y funciona sin elevación cuando está activo el modo de desarrollador, por lo que la prueba se intenta primero y solo se omite si la creación falla; el atributo oculto de Windows, aplicable solo en esa plataforma; y la denegación de permisos, no reproducible cuando la prueba se ejecuta con privilegios administrativos. Los fallos inyectados del párrafo anterior comprueban el tratamiento del error, no los permisos reales de cada sistema: no sustituyen a estas verificaciones. La validación indicará en qué plataformas se ejecutó cada una.

## Riesgos

- La comprobación de permisos reales puede quedar sin cobertura automática en algunos entornos; se complementará con una comprobación manual documentada en la validación, sin confundirla con los fallos simulados.
- Una carpeta muy poblada puede producir un informe lento; la spec no fija requisitos de rendimiento y no se optimiza sin una necesidad demostrada.
- Si en Windows falla la consulta del atributo oculto, el informe perderá cobertura sobre esas entradas. Las omisiones conservarán el motivo real según RF-9; los avisos y el código tres señalarán esos fallos.

## Orden de implementación

1. Esqueleto del paquete, subcomando `analizar` y códigos de salida 1 y 2 con la validación de la ruta (RF-2, RF-11, RF-16).
2. Clasificación: mapa de extensiones, categoría y carpeta propuesta (RF-5, RF-6).
3. Recorrido: primer nivel, modo recursivo, exclusiones con prioridad y recuentos (RF-3, RF-4, RF-9, RF-14, RF-15).
4. Informe: tabla, tamaños, extensiones desconocidas y carpeta sin archivos analizables (RF-7, RF-8, RF-12).
5. Fallos por elemento, avisos con causa y código 3 (RF-13).
6. Comprobación de no modificación e informe de cobertura por plataforma (RF-10, RNF-2).
