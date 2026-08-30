# Validación — T1: estructura e instalación

**Veredicto: cumple T1 en el entorno verificado.** La corrección de V-1 / V-4 evita que un ejecutable ajeno sustituya al ausente en el entorno aislado. No quedan hallazgos bloqueantes para T1. Esta revisión no modifica la aplicación, las pruebas ni las casillas de tareas.

## Alcance y entorno

Versión revisada: `27b02d5`. Fecha: 2026-08-30. Windows AMD64, Python 3.14.7 y pytest 9.1.1. Instalación editable existente en `.venv`, sin reconstruir el entorno. Revisión independiente de la corrección de V-1 / V-4; las correcciones anteriores de V-2 y V-3 se conservan.

Alcance: [T1](tasks.md), según [plan.md](plan.md), [spec.md](spec.md) y la [constitución](../../docs/constitution.md). El cambio evaluado afecta a la prueba de arranque, la evidencia de tareas y este informe; no modifica la aplicación ni adelanta T2.

## Evidencia ejecutada

Suite completa desde `projects/filepilot/`, con un directorio temporal nuevo:

```powershell
.\.venv\Scripts\python.exe -B -m pytest -q -rA -p no:cacheprovider --basetemp ../../.sdd-check/t1-final-review-1788117745362/suite
```

Resultado: **3 pruebas superadas, ninguna omitida**, en 0,34 s. Cubren la ayuda por módulo y ejecutable desde carpetas temporales ajenas al producto y la ausencia de dependencias declaradas de ejecución.

Se ejecutó además `test_orden_instalada_muestra_ayuda` mediante `pytest.main` en procesos separados, sustituyendo `sysconfig.get_path`:

| Escenario controlado | Resultado observado | Evaluación |
| --- | --- | --- |
| Entorno aislado; ejecutables propio y de usuario ausentes | 1 fallo, código 1 | Detecta correctamente la instalación incompleta |
| Entorno aislado; propio ausente y ejecutable ajeno en la ruta de usuario | 1 fallo, código 1; solo consulta el directorio del entorno | Falso positivo corregido |
| Simulación de ejecución fuera de un entorno virtual; solo ejecutable de usuario | 1 prueba superada, código 0; consulta ambas rutas | Verifica la selección de rutas, no una instalación real con `--user` |

En los dos primeros casos, el fallo es el resultado esperado de la comprobación negativa, no un fallo de la suite normal. El entorno real cumple `sys.prefix != sys.base_prefix` y tiene `site.ENABLE_USER_SITE = False`. Para el tercer caso se igualó temporalmente `sys.base_prefix` a `sys.prefix`; no se creó otra instalación de Python.

El ejecutable ajeno se generó únicamente dentro de `.sdd-check/t1-final-review-1788117745362/usuario-simulado/`, con el generador de lanzadores de la copia de distlib incluida en pip. Solo imprime `filepilot: ejecutable ajeno de prueba` y termina en cero, sin importar la aplicación. Se comprobó su ejecución real como subproceso. No se alteraron ejecutables instalados ni el directorio de usuario.

## Cumplimiento

| Requisito o criterio | Evidencia | Resultado | Limitación |
| --- | --- | --- | --- |
| T1: ayuda por comando y módulo | Suite: ambos arranques superados | Cumple | Windows / Python 3.14.7; instalación existente |
| T1: exigir el ejecutable del entorno aislado | Ausencia propia detectada incluso con un ejecutable ajeno disponible | Cumple | Escenario controlado con rutas sustituidas |
| RNF-1: dependencias de ejecución | Prueba de metadatos superada | Cumple, parcial | Funcionamiento completo sin red pendiente de T13 |
| Constitución: simplificación de argumentos | `cli.py` conserva `parse_args(argv)`, sin import de `sys` | Cumple | Inspección; aplicación sin cambios |
| RNF-2 y versión mínima del plan | Python 3.11, Linux y macOS no ejecutados | No verificado | Pendiente de T12 |

## Cierre

**V-1 / V-4 resuelto para T1.** [test_arranque.py](../../tests/test_arranque.py) exige el ejecutable del entorno virtual cuando `sys.prefix != sys.base_prefix`, sin consultar el esquema de usuario ni el PATH y sin omitir su ausencia. La alternativa fuera del entorno virtual no acredita la identidad de una distribución instalada con `--user`; esa modalidad no se declara validada.

V-2 y V-3 conservan sus correcciones. El informe identifica la versión y los resultados actuales, sin mezclar la evidencia del fallo anterior con la verificación de la corrección. No es necesario cambiar la spec ni el plan. Siguiente tarea: **T2**, todavía sin iniciar.
