# Validación — T1: estructura e instalación

**Veredicto: cumple T1 en el entorno verificado.** V-1, V-2 y V-3 están corregidas. Esta comprobación es una autorrevisión de las correcciones, no una revisión independiente ni una validación de toda la spec.

## Alcance y entorno

Correcciones de T1 sobre `540e3a9`, contenidas en el mismo commit que este informe. Fecha: 2026-08-30. Windows AMD64, Python 3.14.7 y pytest 9.1.1. Se utilizó la instalación editable existente en `.venv`, sin reconstruir el entorno.

Alcance: [T1](tasks.md), según [plan.md](plan.md), [spec.md](spec.md) y la [constitución](../../docs/constitution.md). T2 a T14 siguen pendientes; no se han cambiado los requisitos ni implementado el análisis.

## Evidencia ejecutada

Suite completa desde `projects/filepilot/`, con un directorio temporal nuevo reservado para la comprobación:

```powershell
.\.venv\Scripts\python.exe -B -m pytest -q -rA -p no:cacheprovider --basetemp ../../.sdd-check/t1-fix-1788116393436/suite
```

Resultado: **3 pruebas superadas, ninguna omitida**, en 0,37 s.

Desde una carpeta temporal ajena al producto, se ejecutaron por sus rutas absolutas el intérprete del entorno con `-I -B -m filepilot --help` y `Scripts/filepilot.exe --help`: ambos mostraron ayuda, sin salida de error y con código cero. El módulo importado corresponde al código de este producto. Además, `main([])` mostró ayuda y devolvió cero aun teniendo el proceso una opción inválida en `sys.argv`, comprobando que respeta la lista explícita.

Los metadatos instalados indican versión `0.1.0`, Python `>=3.11`, entrada `filepilot.cli:main` y únicamente `pytest>=8; extra == "dev"` como dependencia. El sistema de construcción está separado de las dependencias de ejecución.

**Ausencia del ejecutable:** en un proceso separado, con `unittest.mock.patch`, se hizo que `sysconfig.get_path("scripts")` apuntara a una ruta temporal inexistente y que `shutil.which` devolviera `None`. Se ejecutó solo `test_orden_instalada_muestra_ayuda` mediante `pytest.main`. La versión previa omitía la prueba y devolvía cero; la corregida produjo **1 fallo y código 1**, con el mensaje que identifica el ejecutable ausente. No se borraron ni alteraron ejecutables reales. Este fallo deliberado confirma la detección de una instalación incompleta; no es un fallo de la suite normal.

## Cumplimiento

| Requisito o criterio | Evidencia | Resultado | Limitación |
| --- | --- | --- | --- |
| T1: comando instalado y ejecución como módulo | Suite y arranque directo desde carpeta temporal | Cumple | Windows / Python 3.14.7; instalación existente |
| T1: prueba de arranque efectiva | 3 pruebas superadas; ausencia simulada produce fallo, no omisión | Cumple | El escenario de ausencia es simulado |
| RNF-1: sin dependencias externas de ejecución | Metadatos instalados y revisión de `pyproject.toml` | Cumple, parcial | Funcionamiento completo sin red pendiente de T13 |
| Constitución: imports y código necesarios | Inspección del cambio y arranque verificado | Cumple | Limitado a T1 |
| T1: sin adelantar el análisis | Paquete sin subcomando ni recorrido | Cumple | T2 a T14 pendientes |
| RNF-2 y versión mínima del plan | Python 3.11, Linux y macOS no ejecutados | No verificado | Pendiente de T12 |

## Incidencias corregidas

| Incidencia | Corrección | Comprobación |
| --- | --- | --- |
| V-1: prueba omitida o ejecutable ajeno | [test_arranque.py](../../tests/test_arranque.py) exige el archivo en el directorio de scripts del intérprete, sin buscar en el PATH ni omitir su ausencia | Arranque real superado y ausencia simulada detectada |
| V-2: lectura redundante de argumentos | [cli.py](../../filepilot/cli.py) pasa `argv` directamente a `parse_args`; retirado el import de `sys` | Ambos arranques y lista explícita verificados |
| V-3: estado anterior a T1 | [tasks.md](tasks.md), [README](../../../../README.md) y [AGENTS.md](../../../../AGENTS.md) reflejan T1 completada y el alcance pendiente | Revisión del diff y de las referencias |

Siguiente tarea: **T2**, todavía sin iniciar. La ayuda provisional sin argumentos y el tratamiento definitivo del uso incorrecto se completarán en esa tarea.
