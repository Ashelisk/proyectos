# Puente de programación y revisión

Herramienta opcional del paquete SDD. Codex coordina y revisa; Claude Code implementa una tarea delimitada. El coordinador envía las observaciones directamente, sin que una persona copie mensajes entre aplicaciones. La conversación de Codex debe estar activa: este script no es un servicio permanente ni ejecuta otro Codex en segundo plano.

## Requisitos

Python 3.11+, Git y Claude Code instalado y autenticado. El puente usa solo la biblioteca estándar. Se ha probado en Windows con Python 3.14.7 y Claude Code 2.1.251; la versión de Claude debe admitir `--restricted` y las opciones empleadas. Las ejecuciones consumen la cuota o facturación del acceso configurado, que debe comprobarse antes de iniciar encargos.

No se crean ni copian claves. Claude se inicia sin `--bare` para conservar su autenticación; `--restricted`, las herramientas explícitas y la configuración MCP vacía restringen el trabajo. Se mantienen las políticas administradas. Las fuentes de configuración de usuario/proyecto se omiten en esta sesión del puente, sin editar sus archivos. Las instrucciones y skills necesarias se leen explícitamente como contexto. [Ejecución programática](https://code.claude.com/docs/en/headless) y [permisos](https://code.claude.com/docs/en/permissions).

## Ciclo del coordinador

1. Confirmar qué tarea está autorizada y leer su constitución, spec, plan, tareas y validación. No reabrir decisiones resueltas ni implementar las pendientes. Comprobar cambios locales: cada copia parte del commit `HEAD`, sin trasladar archivos sin commit.
2. Crear un encargo con identificador único, contexto explícito y rutas editables concretas. Sin `--editar`, el encargo es de solo lectura. Se crea un worktree separado y sin rama en `.sdd-check/puente/<id>/worktree`.
3. Escribir el encargo UTF-8 en el almacenamiento temporal y enviarlo. El puente crea o reanuda exclusivamente la sesión de ese identificador y espera a que termine. No usar la sesión «más reciente» ni la sesión interactiva de otra persona.
4. Revisar el diff y ejecutar las comprobaciones necesarias desde esa copia, en un entorno permitido. Sus dependencias pueden prepararse por el coordinador; no se supone que el entorno editable del checkout original importe el código del worktree. Claude no dispone de shell y debe indicar como pendientes las pruebas que ejecutará el coordinador.
5. Registrar la revisión con la huella devuelta por el envío. Si hay defectos, escribir hallazgos con requisito, ubicación y evidencia, registrar `corregir` y enviar el siguiente encargo sin pedir confirmación rutinaria. Incluir expresamente los hallazgos y resultados: el archivo de revisión no se envía por sí solo.
6. Aceptar una refutación fundamentada del programador cuando proceda. No exigir preferencias estéticas como si fueran requisitos. Repetir las pruebas afectadas; `entregado` significa listo para revisar, nunca aprobado.
7. Detenerse ante una decisión de producto, bloqueo real o límite. Una pregunta del programador fuerza el estado `decision`. No aprobarla ni inventar su respuesta; tras recibir la decisión, actualizar primero la spec en el trabajo correspondiente. Si cambió la base documental del encargo, crear otro con la base vigente.
8. Tras comprobar la entrega, registrar `aprobar`. El coordinador integra únicamente el diff revisado, vuelve a verificar sobre la versión integrada, actualiza `tasks.md`/`validation.md` y hace commit/push conforme a las instrucciones del repositorio. El puente no integra, publica ni inicia la siguiente tarea por su cuenta.

## Comandos

Desde la raíz Git, con un intérprete Python disponible. En este entorno se ha utilizado el siguiente; el puente no depende de FilePilot ni de sus paquetes:

```powershell
$pythonPuente = '.\projects\filepilot\.venv\Scripts\python.exe'
& $pythonPuente -B tools/puente_agentes/puente.py --help
& $pythonPuente -B -m unittest discover -s tools/puente_agentes -p test_puente.py -v
```

Ejemplo de preparación de una tarea ya autorizada; sustituir identificador, tarea y rutas por su alcance real:

```powershell
& $pythonPuente -B tools/puente_agentes/puente.py iniciar filepilot-tarea --tarea 'Implementar la tarea autorizada de FilePilot' --contexto AGENTS.md --contexto skills/sdd-coordinador/SKILL.md --contexto skills/sdd-implementacion/SKILL.md --contexto projects/filepilot/docs/constitution.md --contexto projects/filepilot/specs/001-analisis-carpeta/spec.md --contexto projects/filepilot/specs/001-analisis-carpeta/plan.md --contexto projects/filepilot/specs/001-analisis-carpeta/tasks.md --contexto projects/filepilot/specs/001-analisis-carpeta/validation.md --editar projects/filepilot/filepilot --editar projects/filepilot/tests
& $pythonPuente -B tools/puente_agentes/puente.py enviar filepilot-tarea --mensaje .sdd-check/puente/filepilot-tarea/encargo.txt
& $pythonPuente -B tools/puente_agentes/puente.py estado filepilot-tarea
```

Los archivos de mensaje y evidencia los redacta el coordinador antes de usarlos. Para registrar su revisión:

```powershell
& $pythonPuente -B tools/puente_agentes/puente.py revisar filepilot-tarea --huella HUELLA_DEVUELTA --veredicto corregir --evidencia .sdd-check/puente/filepilot-tarea/hallazgos.txt
```

Veredictos: `corregir`, `consultar`, `aprobar`. La aprobación exige una entrega en revisión y la misma huella que los archivos actuales. El ejemplo de FilePilot no se ha ejecutado como tarea de producto; se han probado los comandos equivalentes sobre encargos desechables, descritos en la [validación](../../specs/000-sdd-toolkit/validation.md).

## Límites y recuperación

El perfil base es **Opus 5 con esfuerzo extra**: `--model claude-opus-5 --effort xhigh` en cada envío y reanudación. Se usa el identificador completo para evitar que cambie con el alias `opus`. La variable de esfuerzo se fija también en el proceso hijo, sin cambiar el entorno global. El CLI comunica los modelos utilizados; si no aparece el solicitado, el puente detiene la entrega en lugar de asumir una sustitución. [Modelo y esfuerzo en Claude Code](https://code.claude.com/docs/en/model-config).

Para tareas menos exigentes se puede reducir el esfuerzo; para las más difíciles, elevarlo a `max`. Solo cambiar de modelo cuando exista una razón técnica adicional y se hayan comprobado su disponibilidad y condiciones de uso. `enviar --modelo IDENTIFICADOR --esfuerzo NIVEL --motivo 'Justificación técnica'` permite ajustes que se conservan dentro del encargo; no es necesario indicar todas las opciones. Cambiar un valor sin motivo se rechaza. Cada tarea nueva vuelve a la base Opus 5 extra.

Al revisar una corrección que siga incumpliendo el requisito, usar `revisar --veredicto corregir --correccion-fallida` con evidencia. **Dos correcciones fallidas consecutivas elevan a `max` el siguiente envío**, salvo ajuste explícito justificado. Una revisión sin esa marca reinicia la cuenta. No contar el rechazo de la entrega inicial ni un fallo de permisos como fallo de corrección. La escalada no concede otro envío: con el límite predeterminado de tres, una entrega inicial y dos correcciones consumen todo el encargo; se comunica el bloqueo y no se amplía el límite automáticamente.

- Por defecto: **3 envíos**, **600 segundos por envío** y **2 USD de presupuesto estimado acumulado**. Se configuran al crear el encargo con `--rondas`, `--segundos` y `--presupuesto-usd`. El CLI recibe el presupuesto restante en cada envío. El cálculo usa las estimaciones de Claude Code: no garantiza una factura máxima ni representa necesariamente el consumo de una suscripción.
- Claude solo tiene herramientas de lectura y edición de archivos. Las reglas `Edit` autorizan tanto Edit como Write en las rutas indicadas; requisitos, instrucciones, secretos y metadatos Git quedan protegidos. No se permiten shell, web, MCP ni otros agentes. Las pruebas y cualquier operación Git pertenecen al coordinador, con sus propios permisos.
- Un único proceso puede operar sobre cada encargo. Los resultados JSON inválidos, errores de autenticación, cambios fuera del alcance y tiempos agotados dejan el encargo detenido. No se reintentan automáticamente ni se interpreta un fallo como aprobación.
- Tras una interrupción forzada puede quedar un archivo `lock` con el PID. Comprobar primero que ese proceso ha terminado y revisar los archivos; nunca retirar el bloqueo mientras sigue trabajando. En estado `error`/`ejecutando` abandonado, conservar la evidencia y crear un encargo nuevo sobre una base conocida después de revisar cualquier cambio parcial.
- Un límite detiene nuevos envíos aunque queden correcciones. El coordinador comunica qué falta y por qué, sin incrementar los límites silenciosamente.
- Estado, mensajes, respuestas y revisiones quedan bajo `.sdd-check/`, excluidos de Git. La sesión de Claude también se conserva en su almacenamiento habitual para poder reanudarla. No introducir secretos en los mensajes. El puente no borra automáticamente copias ni sesiones.
- Los controles del CLI y la inspección del diff no equivalen a una máquina virtual ni garantizan aislamiento frente a cualquier defecto del proveedor. No conceder herramientas generales ni introducir credenciales para resolver un bloqueo.

No es necesario editar las skills ni duplicar sus instrucciones: el [protocolo](protocolo.md) delimita el rol de programación y los documentos del producto siguen siendo la fuente de sus requisitos.
