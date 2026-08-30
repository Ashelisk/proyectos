# Validación — T1: estructura e instalación

**Veredicto: cumple T1 en el entorno verificado.** El hallazgo V-1 / V-4 detectado sobre `d7248bc` está corregido: en un entorno aislado la prueba exige el ejecutable de ese entorno y rechaza cualquier otro. La aplicación no ha cambiado.

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
| T1: comprobar el ejecutable del entorno aislado | Con el ejecutable propio ausente y uno ajeno en la ruta de usuario, la prueba falla | Cumple | Escenario controlado con rutas sustituidas |
| RNF-1: dependencias de ejecución | Prueba de metadatos superada | Cumple, parcial | Funcionamiento completo sin red pendiente de T13 |
| Constitución: simplificación de argumentos | `cli.py` conserva `parse_args(argv)`, sin import de `sys` | Cumple | Inspección; aplicación sin cambios |
| RNF-2 y versión mínima del plan | Python 3.11, Linux y macOS no ejecutados | No verificado | Pendiente de T12 |

## Hallazgo corregido — V-1 / V-4

**Prioridad media · resuelto.** La versión anterior de [test_arranque.py](../../tests/test_arranque.py) añadía siempre el esquema de usuario y aceptaba el primer ejecutable existente. Evitar el PATH global no bastaba: esa segunda ruta tampoco pertenece al entorno bajo prueba, y pip no admite instalaciones `--user` dentro de un entorno virtual con el aislamiento predeterminado ([documentación de pip](https://pip.pypa.io/en/stable/user_guide/#user-installs)).

**Corrección:** la prueba distingue ahora ambas situaciones mediante `sys.prefix != sys.base_prefix`. Dentro de un entorno aislado exige el ejecutable de ese entorno y no consulta ninguna otra ruta; fuera de él admite además el esquema de usuario, donde `pip install --user` deja la orden. En ningún caso se consulta el PATH ni se omite la prueba.

Escenarios ejecutados tras la corrección, sustituyendo `sysconfig.get_path` en procesos separados:

| Escenario controlado | Resultado observado | Evaluación |
| --- | --- | --- |
| Suite completa en el entorno real | 3 pruebas superadas, ninguna omitida | Correcto |
| Ambas rutas de ejecutables inexistentes | 1 fallo, código 1 | Correcto |
| En entorno aislado: propio ausente y copia real del lanzador en la ruta de usuario | 1 fallo, código 1 | Falso positivo cerrado |
| Fuera de un entorno aislado: solo el ejecutable del esquema de usuario | 1 prueba superada, código 0 | Correcto; `--user` sigue siendo válido donde procede |

La copia del lanzador se creó únicamente en un directorio temporal del sistema, fuera del repositorio y del directorio de usuario real; no se alteró ningún ejecutable instalado.

V-2 y V-3 conservan sus correcciones. No es necesario cambiar la spec ni el plan. Siguiente tarea: **T2**, todavía sin iniciar.
