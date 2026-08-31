# Validación — T1 a T4: arranque, raíz y clasificación

**Veredicto: T3 y T4 cumplen sus condiciones de cierre en el entorno ejecutado.** V-7 y V-8 están resueltos; T1 y T2 no presentan regresiones. T5 está lista para comenzar, pero no se ha iniciado. El recorrido, el informe y la compatibilidad completa entre plataformas siguen pendientes.

## Alcance y entorno

Revisión y ejecución independiente del código de programación, el 2026-08-31: base `1ebccc3` —que incluye la corrección de T3 en `a11e72d`— más los dos archivos nuevos de T4 incluidos en este commit. Se contrastaron constitución, spec, clarificaciones, plan y tareas. El coordinador actualizó y autorrevisó los documentos; no modificó el código entregado.

Windows 11 AMD64, Python 3.14.7 y pytest 9.1.1. El worktree dispuso de una instalación editable propia, creada con `python -m venv .venv` y `python -m pip install -e ".[dev]"`; se comprobó que importaba su propio paquete. Tras integrar los archivos se repitió la regresión con la instalación del producto.

## Evidencia ejecutada

Desde `projects/filepilot/`:

```powershell
$env:PYTHONIOENCODING = 'utf-8'
.\.venv\Scripts\python.exe -B -m pytest -q -rs -p no:cacheprovider --basetemp ../../.sdd-check/t3-t4-20260831-integrado
```

**92 pruebas superadas y 4 omitidas, en 2,83 segundos.** La misma suite en el worktree dio 92 superadas y 4 omitidas en 3,70 segundos. Son 32 pruebas previas y 60 de clasificación, sin regresiones. Antes de implementar el módulo, `pytest tests/test_clasificacion.py` falló al recolectar por `ModuleNotFoundError: filepilot.clasificacion`: el paquete sí estaba instalado y la funcionalidad faltaba.

Las pruebas de T4 verifican las 46 extensiones enumeradas en RF-5 con expectativas independientes del mapa de implementación, mayúsculas, última extensión, desconocidas, nombres sin extensión y las siete carpetas exactas de RF-7. Cuatro comprobaciones adicionales en memoria verificaron `.gitignore`, `archivo.`, `.FOTO.JPG` y `respaldo.jpg.`; los nombres ocultos no se excluyen dentro del clasificador.

T3 se comprobó también con ocho fallos inyectados —permiso denegado y entrada/salida al resolver, consultar metadatos, abrir la enumeración y leer su primera entrada— y una prueba de que la ruta vacía no llama a resolución ni enumeración. Todos terminaron en dos, sin informe, con causa en español y sin copiar el texto extranjero del sistema. Junto con `tests/test_raiz.py`: **24 superadas y 4 omitidas, en 0,75 segundos**. Reproducción desde el producto del worktree:

```powershell
.\.venv\Scripts\python.exe -B -m pytest -q -rs -p no:cacheprovider tests/test_raiz.py ../../../test_revision_raiz.py --basetemp ../../../t3-verificacion
```

El script adicional, los encargos y las respuestas quedan en `.sdd-check/puente/filepilot-t3-t4-20260831/`, fuera de Git. Se utilizaron dos envíos de Opus 5 en la misma sesión, con esfuerzo `high` para la revisión acotada y `medium` para implementar el mapa y la función ya definidos. Se respetaron los límites del puente; Claude programó y el coordinador ejecutó las pruebas y aprobó la entrega.

## Cumplimiento

| Requisito o criterio | Evidencia | Resultado | Limitación |
| --- | --- | --- | --- |
| T1: arranque y dependencias declaradas | Instalación propia, ambas entradas desde carpeta temporal y metadatos | Cumple | Windows 3.14.7 |
| RF-2 / T2 | Pruebas de argumentos, ayudas y errores con código uno | Cumple | No se exige ayuda íntegramente en español |
| RF-3 / RF-14: opciones | Pruebas del analizador | Cumple, parcial | Recorrido pendiente |
| RF-11 / T3 | Rutas inexistentes, archivo, vacía, fallos de resolución, metadatos y enumeración | Cumple en el alcance ejecutado | Permisos reales no verificados |
| RF-14: raíz oculta | Directorio con punto inicial aceptado | Cumple, parcial | Atributo de Windows pendiente de T7 |
| RF-16: raíz simbólica | Tres pruebas omitidas; unión de directorio resuelta | No verificado | La unión no sustituye al enlace simbólico |
| RF-5 / T4 | Mapa completo, mayúsculas, última extensión y desconocidas | Cumple | Clasificación en memoria |
| RF-6 / T4 | Grupo independiente para nombres sin extensión | Cumple | Exclusiones pendientes del recorrido |
| RF-7 / T4 | Siete carpetas exactas | Cumple, parcial | Ubicación en la raíz, tabla y tamaños pendientes de T8 |
| RNF-3: errores de uso y raíz | Suite y fallos inyectados con texto extranjero | Cumple, parcial | Avisos por entrada pendientes de T10 |
| RF-10: clasificación sin E/S | Inspección: solo importa `Enum`; operaciones sobre cadenas y mapa | Cumple, parcial | Garantía del análisis completo pendiente de T11 |
| RNF-2 | Ejecución en Windows 3.14.7 | No verificado en su totalidad | Python 3.11, Linux y macOS pendientes de T12 |
| RNF-1 | Sin dependencias de ejecución ni red en la clasificación, por inspección | Cumple, parcial | Comprobación del análisis sin conexiones pendiente de T13 |
| RF-1, RF-4, RF-8, RF-9, RF-12, RF-13 y RF-15 | Funcionalidad todavía no implementada | No verificado | T5 a T13 |

## Hallazgos y límites

- **V-7, resuelto:** el `RuntimeError` de resolución se captura de forma localizada y devuelve dos con ruta y causa en español. La regresión inyectada pasa; la prueba equivalente había fallado sobre `8d40133`. También pasa el caso de `ELOOP`. Esto no acredita ejecución real en Python 3.11.
- **V-8, resuelto:** RF-11 define el rechazo de la cadena vacía y el tratamiento de los demás fallos de raíz. El plan refleja ese contrato. Se comprobó que la cadena vacía no analiza el directorio actual.
- Las cuatro omisiones corresponden a tres pruebas de enlaces simbólicos sin privilegio (`WinError 1314`) y a la denegación real mediante `chmod`, no aplicable en Windows. La tarea permite estas omisiones justificadas; RF-16 y los permisos reales quedan pendientes de T12/T13.
- La ayuda conserva encabezados automáticos en inglés, fuera del alcance de RNF-3. La salida del informe con caracteres no representables y redirección sigue pendiente de T8/T12; fijar UTF-8 en las pruebas no cambia la política del producto.

Se conserva como evidencia anterior, no repetida en esta revisión: sobre `8d40133`, 40 invocaciones por ambas entradas con cp1252 y UTF-8 y una auditoría aislada de `resolver_raiz` sin aperturas de contenido ni cambios del árbol. Sus recursos están en `.sdd-check/t3-review-1788120184382/`. El control negativo de aislamiento del ejecutable de T1 se verificó en `27b02d5`; la captura compartida de T2 continúa pasando. Ninguna de estas comprobaciones acredita el futuro análisis completo.

**Sin hallazgos abiertos que bloqueen T5.** Las limitaciones anteriores se mantienen en sus tareas de verificación; no se declaran superadas por cerrar T3 y T4.
