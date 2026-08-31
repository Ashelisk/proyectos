# Validación — T1 a T5: arranque, raíz, clasificación y recorrido

**Veredicto: T5 cumple sus condiciones de cierre en el entorno ejecutado.** T1 a T4 no presentan regresiones. T6 es la siguiente tarea y no se ha iniciado. El recorrido es un módulo interno: las exclusiones completas, los fallos por entrada y su integración con el CLI y el informe siguen pendientes.

## Alcance y entorno

Revisión y ejecución independiente del código de programación, el 2026-08-31: base `130dabf` más `recorrido.py` y `test_recorrido.py` incluidos en este commit. Se contrastaron constitución, spec, clarificaciones, plan y tareas. El coordinador actualizó y autorrevisó los documentos; el código integrado coincide con la entrega aprobada del puente.

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

**Sin hallazgos abiertos que bloqueen T6.** T12 continúa pendiente: ejecutar la suite actual en Windows 3.11 no equivale a verificar todas las plataformas ni el producto terminado.
