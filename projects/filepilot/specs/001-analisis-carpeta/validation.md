# Validación — FilePilot, especificación 001

**Versión integrada: T1 a T5 verificadas en el entorno ejecutado.** T1 a T4 no presentan regresiones. El recorrido integrado es un módulo interno: las exclusiones completas, los fallos por entrada y su integración con el CLI y el informe siguen pendientes.

**Última evaluación: la implementación parcial de T6 a T14 no cumple y no se ha integrado.** Presenta fallos de prioridad de exclusiones y de salida Unicode, detallados al final. Esta evaluación no modifica el resultado ni las casillas de las tareas ya integradas.

## Alcance y entorno

Revisión y ejecución independiente del código de programación, el 2026-08-31: base `130dabf` más `recorrido.py` y `test_recorrido.py`, integrados en `077b0dc`. Se contrastaron constitución, spec, clarificaciones, plan y tareas. El coordinador actualizó y autorrevisó los documentos; el código integrado coincide con la entrega aprobada del puente.

Windows 11 AMD64, **Python 3.11.9 y 3.14.7**, con pytest 9.1.1 en ambos entornos. Python 3.11.9 se instaló mediante el gestor oficial, que verificó la firma del índice de distribución; 3.14.7 se conservó como predeterminada. Se usaron instalaciones editables separadas: `.sdd-check/venvs/filepilot-311/` para 3.11 y `projects/filepilot/.venv/` para 3.14. El worktree tuvo además su propio entorno 3.11, comprobando que importaba su propio paquete. No se cambió la versión mínima del producto.

## Evidencia ejecutada

Desde `projects/filepilot/`:

```powershell
$env:PYTHONIOENCODING = 'utf-8'
..\..\.sdd-check\venvs\filepilot-311\Scripts\python.exe -B -m pytest -q -rs -p no:cacheprovider --basetemp ../../.sdd-check/t5-20260831-integrado311
.\.venv\Scripts\python.exe -B -m pytest -q -rs -p no:cacheprovider --basetemp ../../.sdd-check/t5-20260831-integrado314
```

| Entorno y versión evaluada | Superadas | Omitidas | Tiempo |
| --- | --- | --- | --- |
| Python 3.11.9, T1–T4 antes de T5 | 92 | 4 | 3,33 s |
| Python 3.11.9, entrega T5 en worktree | 106 | 5 | 3,20 s |
| Python 3.11.9, T5 integrada | 106 | 5 | 2,40 s |
| Python 3.14.7, T5 integrada | 106 | 5 | 2,93 s |

Las pruebas de T5 se escribieron antes del módulo: `pytest tests/test_recorrido.py` falló por `ModuleNotFoundError: filepilot.recorrido` en 3.11.9 (0,20 s), con el paquete instalado. Después pasan **14 pruebas de T5** y se omite una por no poder crear un enlace simbólico real. Se comprueban primer nivel y modo recursivo, recuentos sin incluir la raíz, carpetas nunca clasificadas como archivos, categorías y bytes reales, vacío, un árbol de 30 niveles y datos inmutables. La simulación de un enlace a un directorio externo verifica que su contenido no se alcanza; complementa, pero no sustituye, la prueba real omitida.

La inspección confirma una pila iterativa y el cierre de `scandir` por directorio, metadatos sin seguimiento de enlaces y ausencia de aperturas de contenido. Los enlaces detectados se registran como omitidos con motivo `enlace` y detalle vacío. Los demás motivos y su prioridad pertenecen a T6/T7/T10: no se dan por verificados.

El puente utilizó dos envíos de Opus 5 en la misma sesión: esfuerzo `high` para las pruebas y `medium` para implementar el contrato revisado. Se respetaron sus límites. Los encargos, respuestas y aprobación están en `.sdd-check/puente/filepilot-t5-20260831/`, excluidos de Git. Claude programó; el coordinador revisó, ejecutó las pruebas e integró únicamente los dos archivos aprobados.

## Cumplimiento

| Requisito o criterio | Evidencia | Resultado | Limitación |
| --- | --- | --- | --- |
| T1: arranque y dependencias declaradas | Instalaciones separadas, ambas entradas desde carpeta temporal y metadatos | Cumple | Windows, versiones indicadas |
| RF-2 / T2 | Pruebas de argumentos, ayudas y errores con código uno | Cumple | No se exige ayuda íntegramente en español |
| RF-3 / T5 | Archivos del primer nivel o de todos los niveles según el modo | Cumple, parcial | Integración CLI pendiente de T8 |
| RF-4 / T5 | Recuentos encontrados/recorridos y carpetas ausentes de archivos clasificados | Cumple, parcial | Exclusiones de T6 e informe de T8 pendientes |
| RF-11 / T3 | Rutas inexistentes, archivo, vacía y fallos de raíz, incluido bucle simulado | Cumple en el alcance ejecutado | Permisos y bucles reales no verificados |
| RF-14: raíz oculta | Directorio con punto inicial aceptado por T3 | Cumple, parcial | Exclusiones de contenido y atributo Windows pendientes |
| RF-16: raíz simbólica | Tres pruebas omitidas; unión de directorio resuelta | No verificado | La unión no sustituye al enlace simbólico |
| RF-5 / T4 | Mapa completo, mayúsculas, última extensión y desconocidas | Cumple | Regresión en ambas versiones |
| RF-6 / T4 | Grupo independiente para nombres sin extensión | Cumple | Exclusiones pendientes del recorrido |
| RF-7 / T4 | Siete carpetas exactas | Cumple, parcial | Ubicación en la raíz, tabla y tamaños pendientes de T8 |
| RF-9: enlaces encontrados | Prueba controlada y registro por inspección | Cumple, parcial | Enlace real omitido; demás motivos y prioridad pendientes |
| RNF-3: errores de uso y raíz | Regresión de diagnósticos | Cumple, parcial | Avisos por entrada pendientes de T10 |
| RF-10: clasificación y recorrido | Inspección de código sin escritura ni apertura de contenido | Cumple, parcial | Auditoría del análisis integrado pendiente de T11 |
| RNF-2 | Suite T1–T5 en Windows 3.11.9 y 3.14.7 | Cumple, parcial | Linux, macOS y portabilidad del informe pendientes de T12 |
| RNF-1 | Sin dependencias de ejecución ni llamadas de red, por inspección | Cumple, parcial | Comprobación del análisis sin conexiones pendiente de T13 |
| RF-1, RF-8, RF-12, RF-13 y RF-15 | Funcionalidad todavía no implementada | No verificado | T6 a T13 |

## Hallazgos y límites

- **V-7 y V-8, resueltos:** se conserva el tratamiento localizado del `RuntimeError` de resolución y el rechazo de la cadena vacía definido en RF-11. Las regresiones pasan también en 3.11.9; el bucle se sigue inyectando, sin acreditar un enlace real.
- Las cinco omisiones son cuatro pruebas de enlaces simbólicos sin privilegio (`WinError 1314`) y la denegación real mediante `chmod`, no aplicable en Windows. Se mantienen pendientes las verificaciones reales en T12/T13.
- T5 aún no aplica ocultos, la prioridad completa de omisiones ni la recuperación por entrada. Los fallos de E/S del módulo se propagan; su tratamiento corresponde a T6/T10. No se conectó el recorrido al comando ni se implementó el informe. Estos límites no se presentan como requisitos completos.
- La ayuda conserva encabezados automáticos en inglés, fuera del alcance de RNF-3. La salida del informe con caracteres no representables y redirección sigue pendiente de T8/T12; fijar UTF-8 en las pruebas no cambia la política del producto.

Se conserva como evidencia anterior, no repetida aquí: sobre `8d40133`, 40 invocaciones por ambas entradas con cp1252 y UTF-8 y una auditoría aislada de la raíz sin aperturas de contenido ni cambios del árbol (`.sdd-check/t3-review-1788120184382/`); sobre `1ebccc3`, nueve comprobaciones adicionales de errores de raíz y su rechazo temprano de cadena vacía (`.sdd-check/puente/filepilot-t3-t4-20260831/`). El control negativo del ejecutable de T1 se verificó en `27b02d5`. La evidencia de T4 incluye el fallo previo a implementar y sus 60 pruebas en memoria. Ninguna de estas comprobaciones acredita el futuro análisis completo.

**La versión integrada permite iniciar T6.** T12 continúa pendiente: ejecutar la suite de T1 a T5 en Windows 3.11 no equivale a verificar todas las plataformas ni el producto terminado.

## Evaluación parcial de T6 a T14, sin integrar

Revisión independiente del 2026-08-31 sobre la base `077b0dc`, en una copia aislada. La versión evaluada incluye cambios de clasificación, CLI y recorrido, el informe, pruebas y el README del producto. Huella SHA-256 del conjunto de cambios: `5bc2980703454f79b831faf28b451885f36ea1e7f3ce2dbb56984f3891220ba3`. La copia y las comprobaciones adicionales se conservan localmente en `.sdd-check/puente/filepilot-t6-t14-20260831/`; no forman parte del código publicado.

| Comprobación | Python 3.11.9 | Python 3.14.7 |
| --- | --- | --- |
| Suite completa en Windows 11, pytest 9.1.1 | 173 superadas, 8 omitidas; 5,87 s | 173 superadas, 8 omitidas; 6,23 s |
| Siete casos adicionales de fallos y prioridad | 5 superados, 2 fallidos | 5 superados, 2 fallidos |
| Módulo y ejecutable, cuatro combinaciones de opciones, UTF-8 y cp1252 | 8 correctos en UTF-8, 8 fallidos en cp1252 | 8 correctos en UTF-8, 8 fallidos en cp1252 |
| Auditoría independiente en proceso aislado | Sin aperturas de contenido ni conexiones; árbol intacto | Sin aperturas de contenido ni conexiones; árbol intacto |

Las ocho omisiones corresponden a siete pruebas de enlaces simbólicos sin privilegio y una de permisos reales mediante `chmod`, no aplicable en Windows. Las tres pruebas con atributo oculto real de Windows pasan. Linux y macOS no se ejecutaron; las simulaciones no sustituyen esos entornos ni los enlaces reales.

Comandos desde `worktree/projects/filepilot/` de la copia local; para 3.14 se sustituyó `.venv/Scripts/python.exe` por `../../../venv314/Scripts/python.exe` y cada directorio temporal terminó en `314`:

```powershell
$env:PYTHONIOENCODING = 'utf-8'
.venv/Scripts/python.exe -B -m pytest -q -rs -p no:cacheprovider --basetemp ../../../bloque-revision311
.venv/Scripts/python.exe -B -m pytest ../../../test_revision_limites.py -q -p no:cacheprovider --basetemp ../../../limites311
.venv/Scripts/python.exe -B ../../../revision_cli.py
```

`revision_cli.py` establece UTF-8 o cp1252 por subproceso; el ajuste del proceso coordinador no oculta el fallo de codificación. Compara rutas, tamaños y fechas antes y después de cada análisis y registra aperturas y conexiones únicamente durante la llamada al CLI.

Se ejecutaron también los comandos de Windows del README: creación y activación de `.venv`, `pip install .`, ambas entradas de análisis, `pip install -e ".[dev]"` y `pytest`. Esta última ejecución dio 173 superadas y 8 omitidas (5,16 s), con `PYTEST_ADDOPTS` para desactivar la caché y fijar un directorio temporal aislado. Los comandos de Linux/macOS no se ejecutaron. Se retiró exclusivamente el directorio `build/` generado por esta comprobación y se confirmó la misma huella de código.

| Requisito | Evidencia de la copia parcial | Resultado y límite |
| --- | --- | --- |
| RF-1, RF-2 | CLI integrado, ayudas, uso incorrecto y ambas entradas | Cumple en los escenarios ejecutados; salida restringida afectada por V-10 |
| RF-3, RF-4 | Primer nivel, recursión, poda y recuentos de subcarpetas | Cumple en los escenarios ejecutados |
| RF-5, RF-6 | Regresión del mapa completo y grupo sin extensión | Cumple; mapa conservado |
| RF-7, RF-8 | Filas, tamaños, destinos en la raíz y cinco extensiones con desempate | Cumple en UTF-8; emisión afectada por V-10 |
| RF-9 | Motivo único y pruebas adicionales de prioridad con fallos | **Falla: V-9** |
| RF-10 | Instantáneas y auditorías aisladas, incluida comprobación independiente | Cumple en los árboles y modos ejecutados |
| RF-11 | Regresión y fallos de raíz durante la enumeración posterior a validar | Cumple en los casos ejecutados; permisos y bucles reales pendientes |
| RF-12 | Informe vacío y exclusiones, con interacción de código tres | Cumple en los escenarios ejecutados |
| RF-13 | Continuación, causas en español y código tres | Parcial: el motivo incorrecto de V-9 altera el código esperado |
| RF-14, RF-15 | Raíz oculta, opción de inclusión y atributo Windows real o fallido | Parcial: V-9 afecta la prioridad; otras plataformas pendientes |
| RF-16 | Prueba real de raíz simbólica omitida | No verificado; la unión de directorio no la sustituye |
| RNF-1 | Instalación sin dependencias de ejecución, vigilancia de conexiones y revisión | Cumple en los análisis ejecutados |
| RNF-2 | Ambas versiones en Windows, rutas relativas/absolutas y otros alfabetos | **Falla: V-10**; Linux/macOS no verificados |
| RNF-3 | Diagnósticos de uso, raíz y entradas con texto original extranjero | Cumple en los escenarios ejecutados; no corrige el motivo de V-9 |

### Hallazgos abiertos de la copia parcial

- **V-9 — Prioridad de exclusiones ante fallos, prioridad media.** En `filepilot/recorrido.py:128–147`, `is_dir()` puede fallar antes de aplicar la ocultación por nombre. Una entrada `.dato.txt` con permiso denegado al consultar el tipo se registra como `sin_permiso`, aunque RF-9 exige `oculto`. En Windows, un enlace ya reconocido cuyo atributo no puede consultarse también termina como `sin_permiso` en vez de conservar la prioridad de `enlace`. Ambos casos fallan en 3.11 y 3.14. Se deben conservar los motivos superiores conocidos sin romper la excepción de subcarpetas no recursivas de RF-4.
- **V-10 — Fallo al emitir una ruta Unicode, prioridad media.** `filepilot/cli.py:188` imprime el informe sin tratar caracteres no representables. Con una raíz `carpeta-á-Ж-資料` y `PYTHONIOENCODING=cp1252`, ambas entradas y las cuatro combinaciones de opciones terminan con `UnicodeEncodeError` y código uno. Se debe permitir el análisis y emitir una salida segura, sin depender de que las pruebas impongan UTF-8.
- **T14, verificación parcial.** El README existe y sus comandos de Windows se ejecutaron. Los comandos de Linux/macOS siguen sin comprobarse; no se da por satisfecha toda su condición de cierre.

**Veredicto de la copia parcial: no cumple.** No se integra el código ni se marcan T6 a T14 como completadas. La siguiente entrega debe corregir V-9 y V-10, conservar los comportamientos que pasan y repetir la revisión conjunta. La validación completa de plataformas y enlaces reales permanece pendiente.
