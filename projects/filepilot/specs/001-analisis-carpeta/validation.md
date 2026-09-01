# Validación — FilePilot, especificación 001

**V-9 y V-10 corregidos y verificados.** El análisis, las exclusiones y el informe están integrados. T1 a T14 cumplen sus condiciones y la matriz declarada de Linux y Windows está ejecutada.

**Veredicto global: cumple.** No quedan defectos demostrados abiertos. Los enlaces simbólicos reales pasan en Windows y Linux, los permisos reales pasan en Linux y la versión mínima y la última estable seleccionada están verificadas en ambas plataformas objetivo.

## Alcance y entorno

Validación del 2026-08-31, base de referencia `f0e2e03`, con el mismo código y pruebas integrados en `a2ce1fa`. RNF-2 y la constitución fijan Linux y Windows como plataformas objetivo. Se contrastaron spec, clarificaciones, plan y tareas. El bloque recibido fue revisado independientemente; las correcciones posteriores y los documentos fueron autorrevisados. La ejecución elevada fue manual y sus informes JUnit se revisaron; no se presenta como una ejecución del coordinador. La reducción de plataformas no acredita las comprobaciones aún pendientes.

Windows 11 AMD64, Python **3.11.9 y 3.14.7**, pytest 9.1.1. Instalaciones editables separadas: `.sdd-check/venvs/filepilot-311/` y `projects/filepilot/.venv/`; ambas importan el producto integrado. La versión 3.14 se conserva como predeterminada. No se añadieron dependencias de ejecución ni se modificaron requisitos para hacer pasar las pruebas.

## Evidencia ejecutada

En Linux, el 2026-09-01, Python 3.14.4 y pytest 9.0.2 ejecutaron la suite desde una instalación editable aislada: **209 superadas y 4 omitidas** en 1,61 s. Las omisiones corresponden a tres pruebas del atributo oculto de Windows y una unión de directorio de Windows; las pruebas de permisos mediante `chmod` y enlaces simbólicos reales pasan. La orden instalada `filepilot analizar filepilot --recursivo` terminó con código cero, clasificó 12 archivos y no registró omisiones. No estaba disponible Python 3.11.

Ese mismo día, Python 3.11.16 y pytest 9.1.1 ejecutaron literalmente el bloque Bash del README desde `.venv/linux-311`, como usuario sin privilegios: **209 superadas y 4 omitidas** en 1,46 s. Las cuatro omisiones fueron los mismos casos exclusivos de Windows; las pruebas de permisos mediante `chmod` y enlaces simbólicos reales pasaron. La orden instalada `filepilot analizar filepilot --recursivo` terminó con código cero, clasificó 18 archivos —incluidos bytecodes generados por la suite— y no registró omisiones. Python 3.11 quedó instalado dentro de `.venv/pythons`, sin sustituir el intérprete del sistema.

Desde `projects/filepilot/`:

```powershell
$env:PYTHONIOENCODING = 'utf-8'
../../.sdd-check/venvs/filepilot-311/Scripts/python.exe -B -m pytest -q -rs -p no:cacheprovider --basetemp ../../.sdd-check/alcance-linux-windows-311
.venv/Scripts/python.exe -B -m pytest -q -rs -p no:cacheprovider --basetemp ../../.sdd-check/alcance-linux-windows-314
```

Ejecución manual posterior desde la misma carpeta, en PowerShell como administrador:

```powershell
$env:PYTHONIOENCODING = 'utf-8'
& ../../.sdd-check/venvs/filepilot-311/Scripts/python.exe -B -m pytest -q -rs -p no:cacheprovider --junitxml=../../.sdd-check/windows-admin-311.xml
& .venv/Scripts/python.exe -B -m pytest -q -rs -p no:cacheprovider --junitxml=../../.sdd-check/windows-admin-314.xml
```

| Comprobación | Python 3.11.9 | Python 3.14.7 |
| --- | --- | --- |
| Suite con privilegios para crear enlaces, informes JUnit revisados | **212 superadas, 1 omitida**; 5,300 s | **212 superadas, 1 omitida**; 5,812 s |
| Suite integrada, repetida sobre `deb833a` | **205 superadas, 8 omitidas**; 8,96 s | **205 superadas, 8 omitidas**; 9,79 s |
| Siete casos adicionales de la revisión anterior | 7 superados | 7 superados |
| Módulo y ejecutable, cuatro combinaciones de opciones, UTF-8/cp1252 | 16 invocaciones correctas | 16 invocaciones correctas |
| Auditoría independiente reutilizada sobre la versión corregida | Sin aperturas de contenido ni conexiones; árbol intacto | Sin aperturas de contenido ni conexiones; árbol intacto |

Los informes `.sdd-check/windows-admin-311.xml` y `windows-admin-314.xml`, iniciados a las 19:57:10 y 19:57:16 (+02:00), contienen 213 casos cada uno, cero fallos, cero errores y una omisión. Se comprobó individualmente que pasan los siete casos antes omitidos: enlaces visibles y ocultos, raíz enlazada resuelta y analizada por módulo e integración, enlace roto y exclusión de enlaces durante el recorrido. La única omisión es `test_carpeta_sin_permiso_termina_en_dos`: `chmod no restringe la lectura en Windows`.

La suite incluye 24 escenarios de salida redirigida: módulo y ejecutable, cuatro combinaciones de opciones y UTF-8/cp1252/ASCII, con una raíz de otros alfabetos. Cada subproceso configura su propia codificación; la captura UTF-8 del coordinador no oculta los fallos. Se comprueban la ruta emitida, el informe y el código cero. Las filas de comprobaciones adicionales conservan la evidencia de la integración anterior; no se repitieron porque el código y las pruebas no cambiaron.

Las comprobaciones adicionales están en `.sdd-check/puente/filepilot-t6-t14-20260831/test_revision_limites.py` y `revision_cli.py`. Se ejecutaron desde la raíz Git con cada intérprete del producto integrado. Sus resultados de CLI se conservan en `.sdd-check/cierre-cli311.json` y `cierre-cli314.json`. Estos archivos temporales no forman parte del paquete publicado; las regresiones permanentes están en `tests/`.

Se verificó también una instalación nueva en `.sdd-check/readme-cierre/projects/filepilot/`: comandos de Windows del README, instalación normal y editable, ambas entradas y `pytest`. La suite dio **205 superadas y 8 omitidas** (17,25 s). `PYTEST_ADDOPTS` únicamente desactivó la caché y fijó el directorio temporal. Los comandos de Linux no se ejecutaron.

La documentación de T14 se revisó e integró conservando los comandos de Windows. La guía de Linux usa entornos separados bajo `.venv/`, cuya exclusión de Git se comprobó, e identifica los comandos todavía no ejecutados. La revisión documental no cierra T14 ni acredita Linux. Código y pruebas permanecen sin cambios respecto a la versión ejecutada.

## Cumplimiento

| Requisito | Evidencia | Resultado | Límite |
| --- | --- | --- | --- |
| RF-1 | Informes completos por módulo y ejecutable | Cumple | Entornos ejecutados |
| RF-2 | Ayudas y errores de uso en `test_cli.py` | Cumple | Los encabezados ingleses de la ayuda no están prohibidos |
| RF-3, RF-4 | Árboles reales, dos modos, recuentos y poda | Cumple | Linux y Windows ejecutados |
| RF-5, RF-6 | 46 extensiones, mayúsculas, última extensión y grupo sin extensión | Cumple | Mapa sin cambios |
| RF-7, RF-8 | Tabla, tamaños, destinos planos y cinco extensiones con desempate | Cumple | Salida restrictiva comprobada con escapes |
| RF-9 | Recuentos, prioridad y enlaces visibles/ocultos reales | Cumple | Fallos de metadatos también inyectados |
| RF-10 | Instantáneas, ausencia de carpetas propuestas y auditoría `open` aislada | Cumple | Árboles y modos ejecutados |
| RF-11 | Regresión de raíz, enlace roto real y fallos al enumerar | Cumple | Permisos reales en Linux; bucles con fallos controlados |
| RF-12 | Tres escenarios vacíos en subproceso y ausencia de archivos con error | Cumple | Conserva cero o tres según los motivos |
| RF-13 | Fallos inyectados, continuación, causa española y código tres | Cumple | No acredita permisos reales |
| RF-14 | Raíz oculta, poda, inclusión y raíz simbólica real | Cumple | Linux y Windows ejecutados |
| RF-15 | Tres pruebas con atributo Windows real y fallos controlados | Cumple en Windows | Linux no ejecutado |
| RF-16 | Raíz simbólica real resuelta y analizada por módulo e integración | Cumple | Linux y Windows ejecutados |
| RNF-1 | Sin dependencias de ejecución; vigilancia de intentos y eventos de red | Cumple | Análisis ejecutados |
| RNF-2 | Ambas versiones, rutas relativas/absolutas y Unicode | Cumple | Linux y Windows, versión mínima y última seleccionada |
| RNF-3 | Uso, raíz y avisos con errores cuyo texto original está en otro idioma | Cumple | Causas derivadas del tipo y código, no del texto del sistema |

## Correcciones verificadas

- **V-9, cerrado:** los fallos al consultar tipo o atributo ya no reemplazan `oculto` o `enlace` cuando esos motivos son conocidos. Entre fallos, se conserva la prioridad de permisos. Las subcarpetas identificadas en modo no recursivo siguen contando únicamente como encontradas. Las cinco regresiones comprueban también aviso, motivo único y código de salida.
- **V-10, cerrado:** el CLI conserva la codificación de stdout/stderr y usa `backslashreplace` para caracteres no representables. Una ruta como `carpeta-á-Ж-資料` no interrumpe el informe bajo cp1252 ni ASCII; UTF-8 conserva los caracteres originales. El comportamiento técnico está descrito en plan y README.
- Antes de corregir, las pruebas focalizadas dieron **20 fallidas, 22 superadas y 2 omitidas**: cuatro fallos de prioridad y dieciséis de codificación. Tras corregir se ejecutaron ambas suites completas y los mismos casos independientes que detectaron los defectos. Las correcciones no se presentan como una revisión externa de sí mismas.

## Límites y siguiente paso

La ejecución elevada cierra las siete omisiones de enlaces simbólicos en Windows. Permanece **una omisión de permisos reales mediante `chmod`**, no aplicable en Windows. Las tres pruebas del atributo oculto real también pasan. La evidencia elevada complementa la ejecución sin privilegios; no exige usar FilePilot como administrador ni sustituye las pruebas de permisos en Linux.

La verificación de Linux está completa con Python 3.11.16 y 3.14.4, usando un usuario sin privilegios: pasan los permisos y enlaces reales, y los comandos Bash del README quedan ejecutados. No hay más comportamiento de producto por definir ni defectos de V-9/V-10 pendientes de implementación.

## Evidencia anterior conservada

- T1/T2: arranque fuera del proyecto por las dos entradas, metadatos sin dependencias de ejecución y errores de uso; control negativo del ejecutable en `27b02d5`.
- T3: V-7 (bucle `RuntimeError`) y V-8 (ruta vacía) corregidos en `a11e72d`; 32 superadas/4 omitidas antes de T4 y 24/4 en la revisión de raíz con nueve casos adicionales. Sobre `8d40133`, 40 invocaciones con cp1252/UTF-8 y auditoría de raíz sin aperturas ni cambios; sobre `1ebccc3`, nueve comprobaciones adicionales. Recursos en `.sdd-check/t3-review-1788120184382/` y `.sdd-check/puente/filepilot-t3-t4-20260831/`.
- T4/T5: fallos por módulo ausente antes de implementar; 60 pruebas de clasificación y 14/1 de recorrido, incluidos 30 niveles y pila iterativa. `077b0dc`: regresión integrada 106/5 en ambas versiones de Python.
- Evaluación parcial documentada en `dcd9112`: 173/8 por versión, con V-9 y V-10 abiertos. Se conserva la copia original con huella `5bc2980703454f79b831faf28b451885f36ea1e7f3ce2dbb56984f3891220ba3` en `.sdd-check/puente/filepilot-t6-t14-20260831/`. Esa copia no representa la versión corregida actual.
