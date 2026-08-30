# Validación — T1: estructura e instalación

**Veredicto: no cumple completamente la revisión de calidad.** Los criterios de arranque e instalación de T1 funcionan en el entorno verificado; quedan una debilidad de las pruebas, una redundancia respecto a la constitución y documentación de estado desactualizada. No se han modificado el código ni las casillas de tareas.

## Alcance y entorno

Versión revisada: `5d42ab5`. Fecha: 2026-08-30. Windows AMD64, Python 3.14.7 y pytest 9.1.1, utilizando el entorno virtual y la instalación editable existentes. Revisión limitada a [T1](tasks.md), según [plan.md](plan.md), [spec.md](spec.md) y la [constitución](../../docs/constitution.md). No se ha reconstruido el entorno desde cero.

## Evidencia ejecutada

Desde la raíz del producto:

```powershell
.\.venv\Scripts\python.exe -B -m pytest tests/test_arranque.py -q -rA -p no:cacheprovider --basetemp ../../.sdd-check/t1-review-1788114659864/pytest
```

Resultado: **3 pruebas superadas, ninguna omitida**, en 0,35 s. El directorio temporal se creó exclusivamente para esta revisión.

Además, desde una carpeta temporal ajena al producto, se ejecutaron por su ruta absoluta el intérprete de ese entorno con `-I -B -m filepilot --help` y su `Scripts/filepilot.exe --help`: ambos devolvieron ayuda y código cero. Se comprobó que el módulo importado corresponde al producto revisado, sin depender del ejecutable localizado mediante el PATH global.

Los metadatos instalados indican versión `0.1.0`, Python `>=3.11`, entrada `filepilot.cli:main` y únicamente `pytest>=8; extra == "dev"` en las dependencias declaradas. El sistema de construcción está separado de las dependencias de ejecución.

| Requisito o criterio | Evidencia | Resultado | Limitación |
| --- | --- | --- | --- |
| T1: comando instalado y ejecución como módulo | Suite y ejecución directa desde carpeta temporal | Cumple | Windows / Python 3.14.7 |
| T1: prueba de arranque recogida y superada | 3 pruebas superadas | Cumple | La prueba del comando permite omitir un fallo de instalación; V-1 |
| RNF-1: sin dependencias externas de ejecución | Metadatos instalados y revisión de `pyproject.toml` | Cumple, parcial | El funcionamiento completo sin red corresponde a T13 |
| Constitución: imports y código estrictamente necesarios | Inspección de `cli.py` | Falla, menor | Redundancia localizada; V-2 |
| T1: no adelantar el análisis | Inspección del paquete | Cumple | El subcomando y sus errores siguen pendientes de T2 |
| RNF-2: Python 3.11, Linux y macOS | No ejecutado | No verificado | Pendiente de T12; no se ha inventariado todo intérprete del equipo |

## Incidencias

### V-1 — Una instalación sin comando puede dar una suite en verde

**Prioridad media.** [test_arranque.py](../../tests/test_arranque.py), líneas 30–39. Si no encuentra el comando, la prueba lo omite; si hay otro `filepilot` en el PATH global, puede probar una instalación distinta.

Reproducción sin editar archivos: en un proceso separado se sustituyó `shutil.which` por una función que devuelve `None` y se ejecutó con `pytest.main` la prueba `test_orden_instalada_muestra_ayuda`. Resultado: **1 prueba omitida y código 0**. Esto no invalida el arranque comprobado directamente, pero permite que una regresión de instalación pase inadvertida.

Corrección: exigir el comando del entorno bajo prueba y fallar si falta; no sustituirlo por otro del PATH global. Esta ausencia no es una limitación de plataforma admisible en T1.

### V-2 — Lectura manual de argumentos innecesaria

**Prioridad baja.** [cli.py](../../filepilot/cli.py), líneas 4 y 17. `parse_args(argv)` admite `None` para usar los argumentos del proceso; el condicional y el import de `sys` en este módulo resultan innecesarios. Referencia: [ArgumentParser.parse_args](https://docs.python.org/3.11/library/argparse.html#argparse.ArgumentParser.parse_args).

Corrección: pasar `argv` directamente y retirar ese import, conservando el comportamiento actual. No requiere adelantar T2.

### V-3 — El estado documental todavía sitúa el trabajo antes de T1

**Prioridad baja.** [tasks.md](tasks.md), línea 51, sigue señalando T1 como primera tarea ejecutable pese a estar marcada y tener evidencia. El [README general](../../../../README.md) sigue diciendo que no hay código y el apartado de verificación de [AGENTS.md](../../../../AGENTS.md) tampoco refleja los comandos existentes.

Corrección: reflejar T1 implementada con observaciones pendientes y T2 como siguiente tarea funcional. Mantener explícito que todavía no existe análisis de carpetas ni compatibilidad multiplataforma verificada.

## Siguiente paso

Corregir V-1 y V-2, repetir las tres pruebas y verificar que la ausencia del comando produce un fallo de prueba; actualizar el estado de V-3. No es necesario cambiar la spec ni el plan. La respuesta provisional sin argumentos y el código de uso incorrecto pendiente pertenecen a T2; no se consideran una implementación anticipada ni una validación del contrato final.
