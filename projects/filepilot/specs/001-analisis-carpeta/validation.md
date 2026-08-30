# Validación — T1 y T2: arranque e invocación

**Veredicto: no cumple completamente la revisión.** Los criterios explícitos de T2 sobre argumentos, ayuda y códigos de salida funcionan, sin regresiones observadas en T1. Queda V-5: los diagnósticos de uso incorrecto se emiten en inglés, en conflicto con RNF-3.

## Alcance y entorno

Versión revisada: `b9fe2ea`. Fecha: 2026-08-30. Windows AMD64, Python 3.14.7 y pytest 9.1.1. Instalación editable existente en `.venv`, sin reconstruir el entorno. Revisión independiente de T2 según [tasks.md](tasks.md), [plan.md](plan.md), [spec.md](spec.md) y la [constitución](../../docs/constitution.md).

No se han modificado código, pruebas, requisitos ni casillas. La validación de rutas pertenece a T3; el recorrido y el informe siguen pendientes. Que `analizar <ruta>` termine ahora en cero sin informe no se considera un fallo de T2.

## Evidencia ejecutada

Suite completa desde `projects/filepilot/`, con un directorio temporal nuevo:

```powershell
.\.venv\Scripts\python.exe -B -m pytest -q -rA -p no:cacheprovider --basetemp ../../.sdd-check/t2-review-1788118239042/suite
```

Resultado: **10 pruebas superadas, ninguna omitida**, en 1,35 s: las tres de T1 y las siete de T2.

Desde una carpeta temporal ajena al producto se ejecutaron además **24 invocaciones**, doce mediante el ejecutable del entorno y doce mediante su intérprete con `-I -B -m filepilot`:

- Sin subcomando, sin ruta, con opción desconocida, con subcomando desconocido, con argumento sobrante, con `--recursivo` sin ruta y con `--recursivo=si`: código uno, uso en la salida de error y salida estándar vacía.
- Ayuda general y de `analizar`: código cero, ayuda en la salida estándar y salida de error vacía.
- Ruta sola y ruta con ambas opciones, antes o después de ella: argumentos aceptados, código cero y ninguna salida, conforme al alcance provisional de T2.

Los errores comprobados no devuelven el código dos reservado para T3. La prueba de opciones verifica también que ambas están desactivadas por defecto y que se activan al indicarlas.

## Cumplimiento

| Requisito o criterio | Evidencia | Resultado | Limitación |
| --- | --- | --- | --- |
| RF-2: uso incorrecto, salida de error y código uno | Suite y siete casos por cada entrada | Cumple | El idioma del diagnóstico se evalúa aparte |
| RF-3 / RF-14: declaración de opciones | Prueba de argumentos y ejecución directa | Cumple, parcial | Recorrido y exclusiones pendientes |
| T2: ayuda general y del subcomando | Ambas entradas con código cero | Cumple | No implica análisis implementado |
| RNF-3: mensajes de error en español | Diagnósticos de argumentos emitidos en inglés | Falla | V-5 |
| T1: arranque y dependencias declaradas | Tres pruebas anteriores superadas | Cumple | Instalación existente; sin reconstrucción |
| RNF-1: funcionamiento completo sin red | No verificado en este incremento | No verificado | Pendiente de T13 |
| RNF-2 y versión mínima del plan | Python 3.11, Linux y macOS no ejecutados | No verificado | Pendiente de T12 |

## V-5 — Diagnósticos de uso incorrecto en inglés

**Prioridad media.** [cli.py](../../filepilot/cli.py), método `AnalizadorDeOrdenes.error`: imprime directamente el mensaje recibido de `argparse`. Ejemplos reproducidos con la orden instalada:

```text
filepilot analizar
filepilot analizar: error: the following arguments are required: ruta

filepilot analizar . --inexistente
filepilot: error: unrecognized arguments: --inexistente
```

RF-2 queda cubierto en canal y código, pero RNF-3 exige mensajes de error en español. Aunque las tareas concentran la referencia a RNF-3 en T10, esa regla también afecta a los diagnósticos ya emitidos por T2. La prueba actual comprueba el uso y el código, sin verificar el idioma ni el diagnóstico de la causa.

**Corrección:** emitir en español la causa concreta —ruta obligatoria ausente, opción o subcomando desconocido— y verificarla con pruebas de comportamiento, conservando código uno y salida de error. No sustituirla por un mensaje genérico que oculte la causa ni debilitar RNF-3.

## Estado conservado y siguiente paso

V-1 / V-4: la prueba de T1 mantiene la selección exclusiva del ejecutable del entorno virtual; no ha cambiado desde `27b02d5`. Su comprobación negativa de aislamiento sigue siendo la evidencia de aquella versión y no se ha repetido en esta revisión. La instalación real con `--user` continúa sin validarse.

V-2: se conserva `parse_args(argv)`; el import de `sys` añadido en T2 sí es necesario para escribir en `sys.stderr`. V-3: README y tareas reflejan T2 implementada y T3 pendiente.

Resolver V-5 y repetir las pruebas antes de cerrar T2 sin observaciones. No hace falta cambiar la spec ni el plan. T3 no se ha iniciado.
