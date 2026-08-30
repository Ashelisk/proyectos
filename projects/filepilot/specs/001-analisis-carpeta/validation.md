# Validación — T1 y T2: arranque e invocación

**Veredicto: cumple T1 y T2 en el entorno verificado.** V-5 está corregida: los errores de uso comprobados mantienen causa en español y código uno. También se corrigió V-6, una discrepancia de codificación al capturar la salida en las pruebas.

## Alcance y entorno

Aplicación de `e6dfbd0`, con las correcciones de pruebas incluidas en el mismo commit que este informe. Fecha: 2026-08-30. Windows AMD64, Python 3.14.7 y pytest 9.1.1. Instalación editable existente en `.venv`, sin reconstruirla. Revisión independiente de la traducción de errores y autorrevisión del ajuste de captura de las pruebas.

Se contrastaron [tasks.md](tasks.md), [plan.md](plan.md), [spec.md](spec.md) y la [constitución](../../docs/constitution.md). No se modificaron la aplicación, los requisitos ni el plan. T3 y el análisis de carpetas siguen pendientes.

## Evidencia ejecutada

Desde `projects/filepilot/`, con directorios temporales nuevos:

```powershell
.\.venv\Scripts\python.exe -B -m pytest -q -rA -p no:cacheprovider --basetemp ../../.sdd-check/t2-close-1788118805179/normal-despues
$env:PYTHONIOENCODING = 'utf-8'
.\.venv\Scripts\python.exe -B -m pytest -q -p no:cacheprovider --basetemp ../../.sdd-check/t2-close-1788118805179/utf8-despues
```

Resultado: **17 pruebas superadas, ninguna omitida**, en cada ejecución (2,16 s y 2,17 s). La variable se estableció solo para el proceso de comprobación, sin modificar la configuración persistente del equipo.

Además, se ejecutaron **48 invocaciones** desde una carpeta ajena al producto: doce casos por módulo y por comando instalado, con salida cp1252 y UTF-8. La comprobación capturó bytes y los decodificó con la codificación configurada en cada proceso, sin sustituciones:

- Sin subcomando o ruta, opción o subcomando desconocido, argumento sobrante y valor indebido para una opción: causa concreta en español, uso en la salida de error, código uno y salida estándar vacía.
- Ayuda general y del subcomando: código cero, salida de error vacía y opciones visibles.
- Ruta y combinaciones de opciones: código cero sin informe, conforme al alcance provisional de T2.

Una invocación adicional con una opción desconocida en cirílico y salida cp1252 terminó con código uno, sin excepción de escritura. Esta prueba de diagnóstico no demuestra la futura salida de nombres en el informe.

## Cumplimiento

| Requisito o criterio | Evidencia | Resultado | Limitación |
| --- | --- | --- | --- |
| RF-2: uso incorrecto y código uno | Suite y casos directos por ambas entradas | Cumple | No valida los errores de ruta de T3 |
| RF-3 / RF-14: declaración de opciones | Valores por defecto, activación y órdenes válidas | Cumple, parcial | Recorrido y exclusiones pendientes |
| RNF-3: diagnósticos de T2 en español | Causas esperadas y ausencia de frases de error en inglés | Cumple en T2 | Errores de archivos pendientes |
| T1: arranque y dependencias declaradas | Tres pruebas de arranque incluidas en la suite | Cumple | Instalación existente |
| Captura fiable de salida en las pruebas | Suite con entorno habitual y con salida UTF-8 | Cumple | La captura controla su propia codificación |
| RNF-1: funcionamiento completo sin red | No ejecutado | No verificado | Pendiente de T13 |
| RNF-2 y versión mínima del plan | Python 3.11, Linux y macOS no ejecutados | No verificado | Pendiente de T12 |

## Incidencias cerradas

**V-5 — Idioma de los errores.** La traducción cubre las causas ejercitadas en T2, incluida la línea de uso, sin perder el argumento que provoca el error. Los fallos de archivos de tareas posteriores no se consideran verificados.

**V-6 — Codificación de las pruebas.** Antes del ajuste, con `PYTHONIOENCODING=utf-8`, la suite daba 16 pruebas superadas y un fallo: el subproceso escribía «opción» en UTF-8 y la captura lo interpretaba como cp1252. [test_arranque.py](../../tests/test_arranque.py) y [test_cli.py](../../tests/test_cli.py) fijan ahora UTF-8 tanto para el subproceso como para su lectura. No se ha añadido una política de codificación a la aplicación. Ambas ejecuciones completas pasan tras el ajuste.

V-1 / V-4 conservan la selección exclusiva del ejecutable del entorno virtual; la comprobación negativa de aislamiento corresponde a `27b02d5` y no se repitió aquí. Se mantienen la simplificación de argumentos de V-2 y el estado documental de V-3.

## Límites que no bloquean T2

- **Ayuda:** sus encabezados y el texto automático de `--help` siguen en inglés; RNF-3 solo exige español para los errores. Traducirlos no exige necesariamente atributos privados: existen [grupos con títulos configurables y opciones de ayuda públicas](https://docs.python.org/3.11/library/argparse.html#argument-groups). Una exigencia de ayuda íntegramente en español debe incorporarse primero a los requisitos.
- **Informe y caracteres no representables:** T8/T12 deben comprobar nombres no ASCII y salida redirigida, registrando la codificación efectiva. `LANG=C` por sí solo no prueba una salida ASCII: Python puede activar UTF-8 mediante la [configuración de locales](https://docs.python.org/3.11/using/cmdline.html#envvar-PYTHONCOERCECLOCALE). La escritura en una codificación limitada sigue siendo un riesgo pendiente del informe, no una incompatibilidad multiplataforma demostrada.

Siguiente tarea: **T3**, todavía sin iniciar.
