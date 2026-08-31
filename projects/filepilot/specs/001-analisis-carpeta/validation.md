# Validación — FilePilot, especificación 001

**V-9 y V-10 corregidos y verificados.** El análisis, las exclusiones y el informe están integrados. T1 a T13 cumplen sus condiciones dentro del alcance ejecutado; T14 conserva pendiente la ejecución de sus comandos de Linux.

**Veredicto global: no concluyente.** No quedan defectos demostrados abiertos, pero faltan pruebas en Linux y comprobaciones reales de enlaces simbólicos y permisos. No se declara validada toda la compatibilidad de la spec.

## Alcance y entorno

Validación del 2026-08-31 sobre `deb833a`, con el mismo código y pruebas integrados en `a2ce1fa`. RNF-2 y la constitución fijan Linux y Windows como plataformas objetivo. Se contrastaron spec, clarificaciones, plan y tareas. El bloque recibido fue revisado independientemente; las correcciones posteriores y los documentos fueron autorrevisados. La reducción de plataformas no acredita las comprobaciones aún pendientes.

Windows 11 AMD64, Python **3.11.9 y 3.14.7**, pytest 9.1.1. Instalaciones editables separadas: `.sdd-check/venvs/filepilot-311/` y `projects/filepilot/.venv/`; ambas importan el producto integrado. La versión 3.14 se conserva como predeterminada. No se añadieron dependencias de ejecución ni se modificaron requisitos para hacer pasar las pruebas.

## Evidencia ejecutada

Desde `projects/filepilot/`:

```powershell
$env:PYTHONIOENCODING = 'utf-8'
../../.sdd-check/venvs/filepilot-311/Scripts/python.exe -B -m pytest -q -rs -p no:cacheprovider --basetemp ../../.sdd-check/alcance-linux-windows-311
.venv/Scripts/python.exe -B -m pytest -q -rs -p no:cacheprovider --basetemp ../../.sdd-check/alcance-linux-windows-314
```

| Comprobación | Python 3.11.9 | Python 3.14.7 |
| --- | --- | --- |
| Suite integrada, repetida sobre `deb833a` | **205 superadas, 8 omitidas**; 8,96 s | **205 superadas, 8 omitidas**; 9,79 s |
| Siete casos adicionales de la revisión anterior | 7 superados | 7 superados |
| Módulo y ejecutable, cuatro combinaciones de opciones, UTF-8/cp1252 | 16 invocaciones correctas | 16 invocaciones correctas |
| Auditoría independiente reutilizada sobre la versión corregida | Sin aperturas de contenido ni conexiones; árbol intacto | Sin aperturas de contenido ni conexiones; árbol intacto |

La suite incluye 24 escenarios de salida redirigida: módulo y ejecutable, cuatro combinaciones de opciones y UTF-8/cp1252/ASCII, con una raíz de otros alfabetos. Cada subproceso configura su propia codificación; la captura UTF-8 del coordinador no oculta los fallos. Se comprueban la ruta emitida, el informe y el código cero. Las filas de comprobaciones adicionales conservan la evidencia de la integración anterior; no se repitieron porque el código y las pruebas no cambiaron.

Las comprobaciones adicionales están en `.sdd-check/puente/filepilot-t6-t14-20260831/test_revision_limites.py` y `revision_cli.py`. Se ejecutaron desde la raíz Git con cada intérprete del producto integrado. Sus resultados de CLI se conservan en `.sdd-check/cierre-cli311.json` y `cierre-cli314.json`. Estos archivos temporales no forman parte del paquete publicado; las regresiones permanentes están en `tests/`.

Se verificó también una instalación nueva en `.sdd-check/readme-cierre/projects/filepilot/`: comandos de Windows del README, instalación normal y editable, ambas entradas y `pytest`. La suite dio **205 superadas y 8 omitidas** (17,25 s). `PYTEST_ADDOPTS` únicamente desactivó la caché y fijó el directorio temporal. Los comandos de Linux no se ejecutaron.

La documentación de T14 se revisó e integró conservando los comandos de Windows. La guía de Linux usa entornos separados bajo `.venv/`, cuya exclusión de Git se comprobó, e identifica los comandos todavía no ejecutados. La revisión documental no cierra T14 ni acredita Linux. Código y pruebas permanecen sin cambios respecto a la versión ejecutada.

## Cumplimiento

| Requisito | Evidencia | Resultado | Límite |
| --- | --- | --- | --- |
| RF-1 | Informes completos por módulo y ejecutable | Cumple | Entornos ejecutados |
| RF-2 | Ayudas y errores de uso en `test_cli.py` | Cumple | Los encabezados ingleses de la ayuda no están prohibidos |
| RF-3, RF-4 | Árboles reales, dos modos, recuentos y poda | Cumple | Enlaces reales omitidos |
| RF-5, RF-6 | 46 extensiones, mayúsculas, última extensión y grupo sin extensión | Cumple | Mapa sin cambios |
| RF-7, RF-8 | Tabla, tamaños, destinos planos y cinco extensiones con desempate | Cumple | Salida restrictiva comprobada con escapes |
| RF-9 | Recuentos y prioridad, incluidos fallos de tipo y atributo | Cumple | Enlaces simulados complementan los reales omitidos |
| RF-10 | Instantáneas, ausencia de carpetas propuestas y auditoría `open` aislada | Cumple | Árboles y modos ejecutados |
| RF-11 | Regresión de raíz y fallos durante su enumeración tras validar | Cumple, parcial | Permisos y bucles reales no verificados |
| RF-12 | Tres escenarios vacíos en subproceso y ausencia de archivos con error | Cumple | Conserva cero o tres según los motivos |
| RF-13 | Fallos inyectados, continuación, causa española y código tres | Cumple | No acredita permisos reales |
| RF-14 | Raíz oculta, poda, inclusión y demás exclusiones vigentes | Cumple, parcial | Raíz simbólica real pendiente |
| RF-15 | Tres pruebas con atributo Windows real y fallos controlados | Cumple en Windows | Linux no ejecutado |
| RF-16 | Pruebas reales omitidas; unión de directorio resuelta | No verificado | La unión no sustituye al enlace simbólico |
| RNF-1 | Sin dependencias de ejecución; vigilancia de intentos y eventos de red | Cumple | Análisis ejecutados |
| RNF-2 | Ambas versiones, rutas relativas/absolutas y Unicode | Cumple, parcial | Linux pendiente |
| RNF-3 | Uso, raíz y avisos con errores cuyo texto original está en otro idioma | Cumple | Causas derivadas del tipo y código, no del texto del sistema |

## Correcciones verificadas

- **V-9, cerrado:** los fallos al consultar tipo o atributo ya no reemplazan `oculto` o `enlace` cuando esos motivos son conocidos. Entre fallos, se conserva la prioridad de permisos. Las subcarpetas identificadas en modo no recursivo siguen contando únicamente como encontradas. Las cinco regresiones comprueban también aviso, motivo único y código de salida.
- **V-10, cerrado:** el CLI conserva la codificación de stdout/stderr y usa `backslashreplace` para caracteres no representables. Una ruta como `carpeta-á-Ж-資料` no interrumpe el informe bajo cp1252 ni ASCII; UTF-8 conserva los caracteres originales. El comportamiento técnico está descrito en plan y README.
- Antes de corregir, las pruebas focalizadas dieron **20 fallidas, 22 superadas y 2 omitidas**: cuatro fallos de prioridad y dieciséis de codificación. Tras corregir se ejecutaron ambas suites completas y los mismos casos independientes que detectaron los defectos. Las correcciones no se presentan como una revisión externa de sí mismas.

## Límites y siguiente paso

Las ocho omisiones son **siete pruebas de enlaces simbólicos** sin privilegio (`WinError 1314`) y **una de permisos reales** mediante `chmod`, no aplicable en Windows. Las tres pruebas del atributo oculto real pasan. Los fallos inyectados y la unión de directorio no sustituyen esas comprobaciones.

Para completar la verificación en Linux: ejecutar el análisis y la suite con Python 3.11 y la última estable, usando un usuario sin privilegios para comprobar permisos reales; verificar enlaces y ejecutar los comandos Bash del README para cerrar T14. Registrar versiones, resultados y motivos de omisión. Para cerrar la compatibilidad global también deben verificarse los enlaces simbólicos en un Windows que permita crearlos: una prueba en Linux no acredita ese comportamiento en Windows. No hay más comportamiento de producto por definir ni defectos de V-9/V-10 pendientes de implementación.

## Evidencia anterior conservada

- T1/T2: arranque fuera del proyecto por las dos entradas, metadatos sin dependencias de ejecución y errores de uso; control negativo del ejecutable en `27b02d5`.
- T3: V-7 (bucle `RuntimeError`) y V-8 (ruta vacía) corregidos en `a11e72d`; 32 superadas/4 omitidas antes de T4 y 24/4 en la revisión de raíz con nueve casos adicionales. Sobre `8d40133`, 40 invocaciones con cp1252/UTF-8 y auditoría de raíz sin aperturas ni cambios; sobre `1ebccc3`, nueve comprobaciones adicionales. Recursos en `.sdd-check/t3-review-1788120184382/` y `.sdd-check/puente/filepilot-t3-t4-20260831/`.
- T4/T5: fallos por módulo ausente antes de implementar; 60 pruebas de clasificación y 14/1 de recorrido, incluidos 30 niveles y pila iterativa. `077b0dc`: regresión integrada 106/5 en ambas versiones de Python.
- Evaluación parcial documentada en `dcd9112`: 173/8 por versión, con V-9 y V-10 abiertos. Se conserva la copia original con huella `5bc2980703454f79b831faf28b451885f36ea1e7f3ce2dbb56984f3891220ba3` en `.sdd-check/puente/filepilot-t6-t14-20260831/`. Esa copia no representa la versión corregida actual.
