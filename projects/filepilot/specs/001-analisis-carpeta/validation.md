# Validación — T1: estructura e instalación

**Veredicto: no cumple la revisión del cambio `d7248bc`.** El arranque actual funciona, pero la prueba puede aprobar una instalación cuyo ejecutable falta en el entorno evaluado. V-1 queda reabierta y V-4 no puede considerarse resuelta. No se han modificado código, pruebas ni casillas de tareas durante esta revisión.

## Alcance y entorno

Versión revisada: `d7248bc`, comparada con `b347b40`. Fecha: 2026-08-30. Windows AMD64, Python 3.14.7 y pytest 9.1.1. Instalación editable existente en `.venv`, sin reconstruir el entorno. Comprobación independiente del cambio de V-4; las correcciones anteriores de V-1 a V-3 proceden de una autorrevisión.

Alcance: [T1](tasks.md), según [plan.md](plan.md), [spec.md](spec.md) y la [constitución](../../docs/constitution.md). El cambio solo afecta a la prueba de arranque y este informe; no modifica la aplicación ni adelanta T2.

## Evidencia ejecutada

Suite completa desde `projects/filepilot/`, con un directorio temporal nuevo:

```powershell
.\.venv\Scripts\python.exe -B -m pytest -q -rA -p no:cacheprovider --basetemp ../../.sdd-check/t1-claude-review-1788117291822/suite
```

Resultado: **3 pruebas superadas, ninguna omitida**, en 0,35 s. Cubren la ayuda por módulo y ejecutable desde carpetas temporales ajenas al producto y la ausencia de dependencias declaradas de ejecución.

Para comprobar el aislamiento, se sustituyó `sysconfig.get_path` en procesos separados y se ejecutó únicamente `test_orden_instalada_muestra_ayuda` con `pytest.main`:

| Escenario controlado | Resultado observado | Evaluación |
| --- | --- | --- |
| Ambas rutas de ejecutables inexistentes | 1 fallo, código 1 | Correcto; confirma la comprobación descrita para V-4 |
| Ejecutable del entorno ausente; ejecutable ajeno en la ruta de usuario | 1 prueba superada, código 0 | Falso positivo |
| Mismo escenario con la prueba de `b347b40` | 1 fallo, código 1 | La versión anterior detecta la ausencia |

El ejecutable ajeno se generó únicamente dentro de `.sdd-check/t1-claude-review-1788117291822/usuario-simulado/`, utilizando el generador de lanzadores de la copia de distlib incluida en pip. Su única acción era imprimir `filepilot: ejecutable ajeno de prueba` y terminar en cero; no importaba la aplicación. Se ejecutó realmente como subproceso: no se simuló su resultado. La ruta del entorno se sustituyó por otra inexistente. No se borraron ni alteraron ejecutables reales ni se escribió en el directorio de usuario.

## Cumplimiento

| Requisito o criterio | Evidencia | Resultado | Limitación |
| --- | --- | --- | --- |
| T1: ayuda por comando y módulo | Suite actual: ambos arranques superados | Cumple | Windows / Python 3.14.7; instalación existente |
| T1: comprobar el ejecutable del entorno aislado | Acepta un ejecutable ajeno cuando falta el propio | Falla | Escenario controlado con rutas sustituidas |
| RNF-1: dependencias de ejecución | Prueba de metadatos superada | Cumple, parcial | Funcionamiento completo sin red pendiente de T13 |
| Constitución: simplificación de argumentos | `cli.py` conserva `parse_args(argv)`, sin import de `sys` | Cumple | Inspección; aplicación sin cambios |
| RNF-2 y versión mínima del plan | Python 3.11, Linux y macOS no ejecutados | No verificado | Pendiente de T12 |

## Hallazgo pendiente — V-1 / V-4

**Prioridad media.** [test_arranque.py](../../tests/test_arranque.py), líneas 27–42, añade siempre el esquema de usuario y acepta el primer ejecutable existente. Evitar el PATH global no basta: esa segunda ruta tampoco pertenece necesariamente al entorno bajo prueba.

La instalación con `--user` existe y merece distinguirse de una instalación en un entorno virtual. Sin embargo, T1 exige verificar una instalación aislada. En el entorno ejecutado, `sys.prefix != sys.base_prefix` y `site.ENABLE_USER_SITE` es `False`; la ruta del esquema de usuario apunta fuera de `.venv`. Pip tampoco admite instalaciones `--user` en un entorno virtual con el aislamiento predeterminado ([documentación de pip](https://pip.pypa.io/en/stable/user_guide/#user-installs)).

**Corrección recomendada:** para T1, exigir el ejecutable del entorno aislado, sin recurrir al esquema de usuario. Si se amplía la comprobación a instalaciones `--user`, identificar explícitamente la distribución que se está evaluando y verificar esa modalidad por separado; no aceptarla como sustituto de un ejecutable ausente. El caso «falta el propio y existe uno ajeno» debe producir fallo.

V-2 y V-3 conservan sus correcciones. La evidencia previa sobre arranque no queda invalidada, pero el cierre de V-1 a V-4 era demasiado amplio: comprobar solo que faltan ambos ejecutables no demuestra aislamiento. No es necesario cambiar la spec ni el plan; T2 permanece sin iniciar.
