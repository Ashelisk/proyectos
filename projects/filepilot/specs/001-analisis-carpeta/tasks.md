# Tareas — Análisis e informe de una carpeta

Derivadas de [plan.md](plan.md) y trazadas a los requisitos de [spec.md](spec.md). Cada tarea incluye la prueba del comportamiento que introduce. Las rutas son relativas a `projects/filepilot/`.

## Base

- [ ] **T1 — Estructura del paquete y ejecución.** Crear `pyproject.toml` con Python 3.11 como versión mínima, el punto de entrada `filepilot` y `pytest` como única dependencia de desarrollo, más el paquete `filepilot/` con `__init__.py` y `__main__.py`. Requisitos: RNF-1. Dependencias: ninguna. Hecho cuando: `filepilot` y `python -m filepilot` se ejecutan mostrando el uso, `pytest` se ejecuta sin errores de recolección y la aplicación no declara dependencias de ejecución.

- [ ] **T2 — Subcomando y uso incorrecto.** Definir en `cli.py` el subcomando `analizar` con la ruta obligatoria y las opciones `--recursivo` e `--incluir-ocultos`, y sobrescribir el error del analizador para terminar con código uno. Requisitos: RF-2, RF-3 (declaración de opciones). Dependencias: T1. Archivos: `filepilot/cli.py`, `tests/test_cli.py`. Hecho cuando: sin ruta y con una opción desconocida se escribe el uso en la salida de error y el código es uno; `--help` termina en cero; ningún caso de error usa el código dos de `argparse`.

- [ ] **T3 — Resolución y validación de la raíz.** Resolver la ruta indicada siguiendo enlaces y comprobar que es un directorio legible antes de analizar. Requisitos: RF-11, RF-16, RF-14 (raíz oculta). Dependencias: T2. Archivos: `filepilot/cli.py`, `tests/test_raiz.py`. Hecho cuando: ruta inexistente, ruta que es un archivo y directorio ilegible terminan en código dos con mensajes que distinguen la causa y citan la ruta; una raíz enlazada y una raíz oculta se analizan sin `--incluir-ocultos`; la prueba de enlaces se intenta siempre y solo se omite si el sistema no permite crearlos.

## Análisis

- [ ] **T4 — Clasificación por extensión.** Implementar en `clasificacion.py` el mapa de las seis categorías, la selección de la última extensión sin distinguir mayúsculas, el grupo «sin extensión» y la carpeta propuesta de cada grupo. Requisitos: RF-5, RF-6, RF-7 (nombres de carpeta). Dependencias: T1. Archivos: `filepilot/clasificacion.py`, `tests/test_clasificacion.py`. Hecho cuando: las pruebas en memoria cubren una extensión de cada categoría, `FOTO.JPG`, `copia.tar.gz`, una extensión desconocida y un archivo sin extensión, y las siete carpetas propuestas coinciden con los nombres de RF-7.

- [ ] **T5 — Recorrido y recuento de subcarpetas.** Implementar en `recorrido.py` la enumeración con `os.scandir`, el primer nivel por defecto y el modo recursivo con pila propia sin seguir enlaces, junto con los recuentos de subcarpetas encontradas y recorridas. Requisitos: RF-3, RF-4. Dependencias: T3, T4. Archivos: `filepilot/recorrido.py`, `tests/test_recorrido.py`. Hecho cuando: sobre un árbol temporal de dos niveles, el modo por defecto clasifica solo el primer nivel y el recursivo alcanza los descendientes; ninguna subcarpeta aparece clasificada como archivo y los dos recuentos son correctos en ambos modos.

- [ ] **T6 — Exclusiones y prioridad de motivos.** Aplicar las cuatro exclusiones con su motivo único, podar las carpetas ocultas antes de entrar y habilitar `--incluir-ocultos`. Requisitos: RF-9, RF-14, RF-15 (punto inicial). Dependencias: T5. Archivos: `filepilot/recorrido.py`, `tests/test_exclusiones.py`. Hecho cuando: un enlace llamado `.enlace` se cuenta una sola vez como oculto; la suma por motivos coincide con el total de omitidos; sin `--incluir-ocultos` una carpeta oculta no se enumera y, en modo recursivo, cuenta como encontrada y como una entrada omitida, mientras que en modo no recursivo solo cuenta como encontrada; con la opción, los elementos ocultos se clasifican y las demás exclusiones siguen aplicándose.

- [ ] **T7 — Atributo oculto de Windows.** Consultar `FILE_ATTRIBUTE_HIDDEN` en Windows y tratar su consulta fallida sin dar el elemento por visible. Requisitos: RF-15. Dependencias: T6. Archivos: `filepilot/recorrido.py`, `tests/test_ocultos_windows.py`. Hecho cuando: en Windows un archivo con el atributo y sin punto inicial se omite por oculto; con la consulta forzada a fallar, la entrada se omite por falta de permisos o por error de lectura según la causa, nunca como visible; fuera de Windows la ausencia del atributo no altera el resultado y la prueba específica se marca como omitida indicando la plataforma.

## Informe y fallos

- [ ] **T8 — Composición del informe.** Implementar en `informe.py` la agregación por grupo, el formato de tamaño en base 1024 con un decimal y coma, la tabla con destinos, la fila de totales, el bloque de subcarpetas y omitidos por motivo, y las extensiones desconocidas. Requisitos: RF-1, RF-7, RF-8. Dependencias: T4, T6. Archivos: `filepilot/informe.py`, `tests/test_informe.py`. Hecho cuando: un análisis correcto escribe el informe en la salida estándar y termina en cero; los tamaños no dependen de la configuración regional; con más de cinco extensiones desconocidas se muestran cinco, ordenadas por recuento y alfabéticamente en los empates.

- [ ] **T9 — Sin archivos analizables.** Emitir el mensaje correspondiente con los recuentos de omitidos y subcarpetas cuando el recorrido no clasifique ningún archivo. Requisitos: RF-12. Dependencias: T8. Archivos: `filepilot/informe.py`, `filepilot/cli.py`, `tests/test_informe.py`. Hecho cuando: una carpeta vacía, una que solo contiene subcarpetas sin `--recursivo` y una en la que todo queda excluido de forma voluntaria terminan en cero con el aviso y sus recuentos, sin tabla de categorías.

- [ ] **T10 — Fallos por entrada y código tres.** Conservar el `detalle` en español a partir del tipo y el código del fallo, emitir un aviso por entrada desde `cli.py` y devolver código tres cuando haya omisiones por permiso o por error de lectura. Requisitos: RF-13, RNF-3, RF-12 (interacción). Dependencias: T6, T9. Archivos: `filepilot/recorrido.py`, `filepilot/cli.py`, `tests/test_fallos.py`. Hecho cuando: con fallos inyectados de archivo inexistente, permiso denegado y error de entrada/salida el análisis continúa, cada entrada aparece una sola vez con su motivo, la salida de error contiene ruta y causa en español —incluido un error cuyo texto original está en otro idioma— y el código es tres, también cuando no se clasifica ningún archivo; las omisiones por ocultación o enlace mantienen el código cero.

## Comprobaciones transversales

- [ ] **T11 — Garantía de solo lectura.** Verificar que el análisis no modifica el árbol ni abre el contenido de los archivos. Requisitos: RF-10. Dependencias: T8. Archivos: `tests/test_solo_lectura.py`. Hecho cuando: la comparación de rutas, tamaños y fechas de modificación antes y después es idéntica, y una prueba en proceso aislado con el evento de auditoría `open` registra cero aperturas de archivos del árbol durante el análisis, excluyendo la preparación y la limpieza de los datos.

- [ ] **T12 — Portabilidad y entradas admitidas.** Comprobar rutas relativas y absolutas y nombres con caracteres no ASCII, y dejar constancia de las plataformas y versiones de Python realmente ejecutadas. Requisitos: RNF-2. Dependencias: T8. Archivos: `tests/test_portabilidad.py`. Hecho cuando: las pruebas pasan con ambas formas de ruta y con nombres acentuados y de otros alfabetos; la ejecución registra la plataforma y la versión utilizadas, sin afirmar compatibilidad no ejecutada.

- [ ] **T13 — Integración de extremo a extremo.** Analizar un árbol de ejemplo que combine las seis categorías, archivos sin extensión, subcarpetas, elementos ocultos, un enlace y un fallo inyectado, en los dos modos de recorrido. Requisitos: RF-1 a RF-16. Dependencias: T1 a T12. Archivos: `tests/test_integracion.py`. Hecho cuando: la salida contiene la tabla, los destinos, los recuentos de omitidos por motivo y las extensiones desconocidas esperadas, y se observan los cuatro códigos de salida en sus escenarios.

- [ ] **T14 — Documentación de uso del producto.** Escribir `projects/filepilot/README.md` con la instalación, el comando `analizar`, sus opciones, los cuatro códigos de salida y la orden real para ejecutar las pruebas. Requisitos: ninguno de comportamiento; cubre la exigencia del repositorio de documentar los comandos reales de cada producto. Dependencias: T13. Hecho cuando: cada comando del documento se ha ejecutado tal como aparece y la tabla de códigos coincide con la del plan.

## Cobertura y estado

RF-1 (T8, T13), RF-2 (T2), RF-3 (T5), RF-4 (T5, T6), RF-5 (T4), RF-6 (T4), RF-7 (T4, T8), RF-8 (T8), RF-9 (T6), RF-10 (T11), RF-11 (T3), RF-12 (T9, T10), RF-13 (T10), RF-14 (T3, T6), RF-15 (T6, T7), RF-16 (T3), RNF-1 (T1), RNF-2 (T12), RNF-3 (T10).

Primera tarea ejecutable: T1, sin bloqueos. T4 puede avanzar en paralelo a T2 y T3 porque no comparte archivos con ellas; el resto sigue la cadena de dependencias indicada. No hay tareas bloqueadas: la spec y el plan están cerrados y no queda ninguna decisión pendiente.

Quedan fuera de estas tareas los comportamientos excluidos por la spec: mover u organizar archivos, conflictos de nombre, duplicados, reglas configurables, salida en JSON y deshacer.

Ninguna casilla se marca sin evidencia ejecutada; la validación posterior contrastará cada requisito con resultados reales.
