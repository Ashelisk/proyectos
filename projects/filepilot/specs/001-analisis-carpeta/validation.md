# Validación — T1 a T3: arranque, invocación y raíz

**Veredicto de T3: no cumple.** Los casos ordinarios pasan, pero queda sin tratar el error de resolución documentado para bucles de enlaces en Python 3.11 (V-7). La ruta vacía tiene un comportamiento implementado sin requisito cerrado (V-8). T1 y T2 conservan su validación dentro del alcance ejecutado.

## Alcance y entorno

Revisión independiente de `8d40133`, el 2026-08-30: código, pruebas, [spec](spec.md), [plan](plan.md), [clarificaciones](clarifications.md), [tareas](tasks.md) y [constitución](../../docs/constitution.md). Windows 11 AMD64, Python 3.14.7 y pytest 9.1.1, con la instalación editable existente en `.venv`; no se reconstruyó el entorno. No se han modificado código, pruebas permanentes, requisitos ni plan.

## Evidencia ejecutada

Desde `projects/filepilot/`, usando carpetas temporales nuevas:

```powershell
.\.venv\Scripts\python.exe -B -m pytest -q -rs -p no:cacheprovider --basetemp ../../.sdd-check/t3-review-1788120184382/suite
$env:PYTHONIOENCODING = 'utf-8'
.\.venv\Scripts\python.exe -B -m pytest -q -rs -p no:cacheprovider --basetemp ../../.sdd-check/t3-review-1788120184382/suite-utf8
```

**29 pruebas superadas y 4 omitidas en cada ejecución** (2,80 s y 2,75 s). Tres omisiones por no poder crear enlaces simbólicos (`WinError 1314`) y una porque `chmod` no restringe la lectura en Windows. La prueba de unión de directorio pasa; no sustituye al enlace simbólico de RF-16.

Comprobaciones adicionales con datos desechables:

- **40 invocaciones**: diez escenarios por módulo y por ejecutable del entorno, con salida cp1252 y UTF-8, desde una carpeta ajena al producto. Se capturaron bytes y se decodificaron estrictamente con la codificación indicada. Ruta ausente y archivo como raíz devuelven dos; directorios normales, ocultos por nombre y con caracteres acentuados y cirílicos, mediante rutas relativas y absolutas, devuelven cero; falta de ruta devuelve uno. Las opciones se admiten. No hay informe todavía.
- La cadena vacía devuelve dos y «la ruta indicada está vacía»: evidencia del comportamiento actual, no aprobación del requisito. El caso adicional `notas.txt/sub`, con `notas.txt` como archivo, devuelve dos y «no existe» en este Windows; la prueba inyectada de `NotADirectoryError` no demuestra ese diagnóstico sobre una ruta real de todas las plataformas.
- **Ocho fallos inyectados**: permiso denegado y entrada/salida durante resolución, consulta de metadatos, apertura de la enumeración y primera iteración. A través de `main`, todos devuelven dos, conservan ruta y causa en español y dejan vacía la salida estándar, sin copiar el texto extranjero del sistema.
- **Bucle simulado en proceso separado**: `Path.resolve` lanza el `RuntimeError` documentado para Python 3.11. El proceso termina en uno con traceback en inglés, sin el diagnóstico controlado (V-7).
- **Solo lectura de la validación de raíz**: cero eventos `open` durante `resolver_raiz` y árbol idéntico antes y después en rutas, tamaños y fechas de modificación. Auditoría en proceso aislado, acotada a esa llamada; no acredita el futuro análisis completo.

Los scripts auxiliares `verificar.py`, `comprobar.py` y sus resultados están en `.sdd-check/t3-review-1788120184382/`, excluidos del repositorio.

## Cumplimiento

| Requisito o criterio | Evidencia | Resultado | Limitación |
| --- | --- | --- | --- |
| T1: arranque y dependencias declaradas | Pruebas de las dos entradas y metadatos | Cumple | Instalación existente |
| RF-2 / T2: uso incorrecto | Suite y falta de ruta por ambas entradas | Cumple | Sin regresiones observadas |
| RF-3 / RF-14: declaración de opciones | Pruebas de argumentos e invocaciones | Cumple, parcial | Recorrido pendiente |
| RF-11: raíz inexistente, archivo e ilegible | Casos reales ordinarios y ocho fallos inyectados | Cumple en los casos ejecutados | Permisos reales no verificados |
| RF-14: raíz oculta | Directorio con punto inicial aceptado | Cumple, parcial | Atributo de Windows no ejercitado aquí |
| RF-16: raíz simbólica | Tres pruebas omitidas; unión de directorio resuelta | No verificado | La unión es evidencia complementaria |
| RNF-3 y manejo de errores de raíz | Diagnósticos ordinarios correctos; excepción de V-7 sin tratar | Falla | Bucle simulado, no ejecución de Python 3.11 |
| RF-10: validación de raíz sin abrir contenido ni modificar el árbol | Auditoría y comparación | Cumple, parcial | Análisis completo pendiente de T11 |
| RNF-2: rutas y plataformas | Rutas relativas, absolutas y Unicode en Windows 3.14.7 | No verificado en su totalidad | Python 3.11, Linux y macOS pendientes |
| Captura compartida de pruebas | Suite habitual y con salida UTF-8 | Cumple | No establece una política de salida para el producto |
| RNF-1: funcionamiento completo sin red | No ejecutado | No verificado | T13 |

## Hallazgos abiertos

### V-7 — Error de resolución sin tratar en la versión mínima

**Prioridad media.** [cli.py](../../filepilot/cli.py), bloque de `Path.resolve()` en `resolver_raiz` (líneas 136–139); RNF-3 y versión mínima del plan.

Python 3.11 documenta que un bucle de enlaces produce [`RuntimeError`](https://docs.python.org/3.11/library/pathlib.html#pathlib.Path.resolve). [Python 3.13 cambió ese comportamiento](https://docs.python.org/3.13/library/pathlib.html#pathlib.Path.resolve). El bloque actual solo captura `OSError`, por lo que el error antiguo escapa también de `main`.

Reproducción acotada: sustituir `filepilot.cli.Path.resolve` por una función que lance `RuntimeError("Symlink loop from 'bucle'")` e invocar `main(["analizar", "bucle"])` como salida de un proceso. Resultado observado: código uno y traceback, en lugar de un fallo de raíz controlado con causa en español. Esta simulación demuestra la falta de tratamiento; no equivale a ejecutar un bucle real en Python 3.11.

Corrección requerida: tratar específicamente ese fallo en la resolución, sin capturar indiscriminadamente errores del resto de la aplicación, y añadir una prueba de regresión que compruebe causa en español, ruta, ausencia de traceback y código dos. Mantener pendiente la verificación real de la versión mínima.

### V-8 — Cadena vacía sin decisión recogida en la spec

**Decisión pendiente.** [cli.py](../../filepilot/cli.py), líneas 133–134, y evidencia de T3 en [tasks.md](tasks.md).

`analizar ""` se rechaza con código dos y un mensaje específico. Es una protección razonable para evitar convertir accidentalmente la cadena vacía en el directorio actual, pero RF-2 y RF-11 no fijan expresamente este caso. No corresponde afirmar que no quedan decisiones abiertas ni describir el mensaje como «ruta inexistente».

Antes del cierre, confirmar su clasificación y documentarla en el requisito correspondiente; después alinear su prueba de invocación y el plan. No se ha decidido por suposición ni se ha cambiado la spec para justificar el código.

## Correcciones conservadas y límites

- T1 mantiene la selección exclusiva del ejecutable de su entorno virtual. La comprobación negativa de aislamiento de V-1/V-4 corresponde a `27b02d5`; no se repitió aquí.
- T2 mantiene la traducción de los errores de uso de V-5. V-6 permanece corregido: [conftest.py](../../tests/conftest.py) fija UTF-8 tanto al escribir como al leer la captura; las dos ejecuciones completas pasan.
- La ayuda automática conserva textos en inglés, permitidos por el alcance vigente de RNF-3. La salida del informe con caracteres no representables y redirección sigue pendiente de T8/T12.
- Las omisiones por enlaces y permisos están justificadas y no se presentan como pruebas superadas. No se ha implementado ni verificado el recorrido.

Se ha actualizado este informe y el estado documental, que todavía situaban la validación en T2. **T3 pendiente de V-7 y V-8.** T4 es independiente de estos puntos y sigue sin iniciar; T5 depende del cierre de T3 y de T4.
