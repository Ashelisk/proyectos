# Plan técnico — Análisis e informe de una carpeta

## Enfoque

Aplicación de consola en Python, ejecutable como `filepilot` y como `python -m filepilot`, sin dependencias externas en tiempo de ejecución. El trabajo se divide en cuatro responsabilidades encadenadas: interpretar la invocación, recorrer el sistema de archivos decidiendo qué se examina y qué se omite, clasificar cada archivo y componer el informe. La lógica de clasificación e informe no toca el disco, de modo que puede verificarse sin crear archivos.

Estructura dentro de `projects/filepilot/`:

```
pyproject.toml
filepilot/__init__.py, __main__.py, cli.py, recorrido.py, clasificacion.py, informe.py
tests/
```

Se fija Python 3.11 o superior. Es la versión mantenida más antigua con soporte previsto hasta octubre de 2027, viene de serie en distribuciones vigentes como Debian 12 y se instala sin dificultad en macOS y Windows. Se descarta 3.9 porque su soporte terminó en octubre de 2025 y las versiones actuales de pytest ya exigen 3.10 o superior; se descarta 3.10 porque solo recibe correcciones de seguridad y caduca en octubre de 2026. Ninguna necesidad de compatibilidad heredada justifica mantener una combinación sin soporte. Las pruebas se ejecutan con la misma versión mínima y con la última estable disponible en cada plataforma.

## Componentes

| Componente | Responsabilidad | Requisitos |
| --- | --- | --- |
| `cli.py` | Definir el subcomando `analizar` y sus opciones, resolver la ruta inicial, ordenar las fases, emitir los avisos por entrada fallida y traducir el resultado a código de salida | RF-1, RF-2, RF-3, RF-11, RF-13, RF-14, RF-16 |
| `recorrido.py` | Enumerar entradas, aplicar exclusiones con su prioridad, contar subcarpetas y producir archivos analizables y entradas omitidas | RF-3, RF-4, RF-9, RF-10, RF-13, RF-14, RF-15 |
| `clasificacion.py` | Mapa de extensiones, categoría de cada archivo y carpeta propuesta de cada grupo | RF-5, RF-6, RF-7 |
| `informe.py` | Agregar por grupo, formatear tamaños, tabla, extensiones desconocidas y mensaje de carpeta sin archivos | RF-7, RF-8, RF-12 |

## Datos y contratos

Estructuras internas, todas de solo lectura una vez creadas:

- `ArchivoAnalizado(ruta, categoria, tamano)` — un archivo clasificado.
- `EntradaOmitida(ruta, motivo, detalle)` — `motivo` es uno de `oculto`, `enlace`, `sin_permiso`, `error_lectura`, asignado una sola vez con esa prioridad y usado solo para los recuentos (RF-9). `detalle` conserva la causa concreta tal como la comunicó el sistema —fichero inexistente, permiso denegado, error de entrada/salida— y es el texto que acompaña al aviso; está vacío cuando la omisión es voluntaria, es decir, por ocultación o por enlace.
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

El informe va a la salida estándar; los avisos por elemento fallido y los errores de ruta, a la salida de error, redactados en español e identificando ruta y causa (RNF-3). El recorrido no escribe en ninguna salida: devuelve cada `EntradaOmitida` con su `detalle`, y `cli.py` es el único responsable de emitir un aviso por cada entrada omitida que lo lleve y de decidir el código de salida a partir de los motivos presentes. Así el recuento y el texto comunicado proceden del mismo dato y ninguna causa se reconstruye por suposición. Ningún componente escribe en disco (RF-10) ni abre conexiones de red: la aplicación se limita a la biblioteca estándar y no consulta servicios ni credenciales (RNF-1).

Formato del informe: una fila por grupo con categoría, recuento, tamaño en base 1024 con un decimal y carpeta propuesta; fila de totales; bloque de subcarpetas y omitidos por motivo; y, cuando «otros» tenga archivos, hasta cinco extensiones ordenadas por recuento y alfabéticamente en los empates.

## Decisiones

**Recorrido con `os.scandir` en lugar de `os.walk`.** `scandir` entrega un objeto por entrada con métodos propios para saber si es directorio o enlace sin seguir el destino, y permite decidir entrada por entrada qué se examina, qué se poda y a qué causa se atribuye un fallo (RF-9, RF-13, RF-14). En Windows los metadatos llegan ya con la enumeración; en Unix, `DirEntry.stat()` consulta el sistema la primera vez y guarda el resultado, de modo que no se repite por entrada. `os.walk` también permitiría consultar cada archivo y notificar con `onerror` los fallos de enumeración, pero entrega los directorios ya agrupados en listas, lo que obliga a un tratamiento aparte para podar las carpetas ocultas y complica atribuir el fallo a la entrada concreta. La recursión se implementa con una pila propia sobre `scandir`, sin seguir enlaces.

**Códigos de salida propios frente a los de `argparse`.** `argparse` termina con código 2 ante un uso incorrecto, valor que la spec reserva a los problemas de ruta. Se sobrescribe el método de error del analizador para terminar con código 1 (RF-2) y así mantener el contrato de la tabla anterior.

**Detección de oculto por plataforma.** Nombre que empieza por punto en cualquier sistema y, en Windows, además el bit `FILE_ATTRIBUTE_HIDDEN` de `st_file_attributes`, campo que Python documenta en esa plataforma. La tolerancia se limita a los sistemas donde el atributo no es aplicable: en Windows, si la consulta falla para un elemento, este no se da por visible, sino que se contabiliza como omitido por error de lectura y genera su aviso (RF-15, RF-9, RF-13). Un dato que no se ha podido comprobar nunca se interpreta como ausencia de ocultación.

**Formato de tamaño sin `locale`.** El separador decimal se escribe directamente como coma, en lugar de depender de la configuración regional del sistema, para que la misma carpeta produzca el mismo informe en las tres plataformas y las pruebas sean deterministas (RF-7, RNF-2).

**Resolución de la raíz.** La ruta indicada se resuelve siguiendo enlaces antes de comprobar que es un directorio legible, lo que cubre RF-16 y permite analizar una raíz oculta sin `--incluir-ocultos` (RF-14). Las exclusiones se evalúan solo sobre lo encontrado dentro.

**Pruebas con pytest como herramienta de desarrollo.** Sus carpetas temporales y sus marcas para omitir pruebas por plataforma reducen el código de las pruebas de sistema de archivos. Se declara como dependencia de desarrollo, separada de la aplicación, que no incorpora dependencias. La alternativa, `unittest` de la biblioteca estándar, evitaría incluso esa dependencia a costa de más código repetido en la preparación de cada árbol de prueba.

## Verificación

Sin acceso a disco, sobre datos construidos en memoria: mapa de extensiones y última extensión con mayúsculas (RF-5), grupo sin extensión (RF-6), formato de tamaños y filas del informe (RF-7), límite y empates de extensiones desconocidas (RF-8), prioridad de motivos y coincidencia entre la suma por motivos y el total (RF-9), y mensaje de carpeta sin archivos analizables (RF-12).

Con sistema de archivos real, en carpetas temporales creadas por la propia prueba y eliminadas al terminar: primer nivel y modo recursivo (RF-3), recuento de subcarpetas en ambos modos (RF-4), ocultos y `--incluir-ocultos` (RF-14, RF-15), raíz oculta y raíz enlazada (RF-16), rutas inexistentes y no directorios (RF-11), y los cuatro códigos de salida (RF-1, RF-2, RF-11, RF-12, RF-13).

Comprobación específica de RF-10, en dos partes porque la primera no basta. Una instantánea del árbol —rutas, tamaños y fechas de modificación— antes y después de cada análisis demuestra que nada se ha creado, movido ni borrado, pero no que no se haya leído el contenido: abrir un archivo para leerlo deja esa instantánea intacta. Se añade por eso una prueba que registra las aperturas de archivo durante el análisis mediante un enganche de auditoría del intérprete y exige que ninguna corresponda a una ruta del árbol examinado.

Fallos controlados para RF-13, provocados en la propia prueba en lugar de esperar a que ocurran: se sustituye temporalmente la consulta de metadatos para que una ruta concreta lance un error de fichero inexistente —la desaparición entre la enumeración y la consulta del tamaño— y otra un error de entrada/salida. Cada caso comprueba que el análisis continúa con el resto, que la entrada aparece una sola vez con su motivo, que el aviso de la salida de error contiene su ruta y su causa concreta y que el código de salida es tres, incluida la variante en la que ningún archivo llega a clasificarse (RF-12).

Los datos de prueba se generan siempre dentro de la carpeta temporal de la prueba; ninguna prueba usa rutas del usuario, del repositorio ni del sistema, y ninguna crea archivos fuera de ese árbol.

Verificaciones que dependen del entorno y se marcan como omitidas cuando no puede prepararse el escenario, en lugar de darse por superadas: la creación de enlaces simbólicos en Windows, que necesita el privilegio correspondiente y funciona sin elevación cuando está activo el modo de desarrollador, por lo que la prueba se intenta primero y solo se omite si la creación falla; el atributo oculto de Windows, aplicable solo en esa plataforma; y la denegación de permisos, no reproducible cuando la prueba se ejecuta con privilegios administrativos. Los fallos inyectados del párrafo anterior comprueban el tratamiento del error, no los permisos reales de cada sistema: no sustituyen a estas verificaciones. La validación indicará en qué plataformas se ejecutó cada una.

## Riesgos

- El motivo `sin_permiso` puede quedar sin cobertura automática en algunos entornos; se compensa con una comprobación manual documentada en la validación.
- Una carpeta muy poblada puede producir un informe lento; la spec no fija requisitos de rendimiento y no se optimiza sin una necesidad demostrada.
- Si en Windows la consulta del atributo oculto falla para muchos elementos, el análisis los omitirá por error de lectura y el informe perderá cobertura, aunque nunca dará por visible lo que no ha podido comprobar. El aviso por elemento y el código tres hacen visible esa situación.

## Orden de implementación

1. Esqueleto del paquete, subcomando `analizar` y códigos de salida 1 y 2 con la validación de la ruta (RF-2, RF-11, RF-16).
2. Clasificación: mapa de extensiones, categoría y carpeta propuesta (RF-5, RF-6).
3. Recorrido: primer nivel, modo recursivo, exclusiones con prioridad y recuentos (RF-3, RF-4, RF-9, RF-14, RF-15).
4. Informe: tabla, tamaños, extensiones desconocidas y carpeta sin archivos analizables (RF-7, RF-8, RF-12).
5. Fallos por elemento, avisos con causa y código 3 (RF-13).
6. Comprobación de no modificación e informe de cobertura por plataforma (RF-10, RNF-2).
