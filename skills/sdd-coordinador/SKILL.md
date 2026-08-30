---
name: sdd-coordinador
description: Coordina o retoma un proyecto con Spec-Driven Development (SDD), identifica la fase pendiente y conecta sus entregables. Úsala para iniciar o continuar un flujo SDD; no para imponerlo a trabajos ajenos a este método.
---

# Coordinación SDD

## Entrada y alcance

Lee la petición, las instrucciones del proyecto y sus artefactos existentes. Identifica la raíz del producto y la funcionalidad activa; no confundas un portfolio con sus proyectos ni el último número de spec con una selección del usuario. Si hay varias candidatas, avanza en lo inequívoco y pregunta solo por la selección necesaria.

Conserva las rutas existentes. En un producto nuevo, usa `docs/constitution.md` y `specs/NNN-nombre/`. No crees documentos vacíos para fases futuras. Si solo se pide orientación, responde sin escribir archivos. Si se solicita una fase concreta, completa esa fase y sus preparativos documentales necesarios sin implementar otras.

## Selección de fase

| Situación | Skill | Entregable dentro del producto |
| --- | --- | --- |
| Faltan principios o deben revisarse | `sdd-constitucion` | `docs/constitution.md` |
| Se define una funcionalidad | `sdd-especificacion` | `spec.md` |
| Hay que examinar los requisitos | `sdd-clarificacion` | `clarifications.md` |
| El comportamiento está definido; falta el diseño | `sdd-planificacion` | `plan.md` |
| El diseño necesita unidades ejecutables | `sdd-tareas` | `tasks.md` |
| Hay tareas autorizadas listas | `sdd-implementacion` | Código, pruebas y estado de tareas |
| Se debe demostrar cumplimiento | `sdd-validacion` | `validation.md` |
| Cambia un comportamiento especificado | `sdd-cambio` | `changes.md` y artefactos afectados |

Lee el `SKILL.md` de la fase elegida, disponible en una carpeta hermana de esta skill. Carga solo la fase actual. Si falta, explica la limitación y aplica el flujo documentado con las herramientas disponibles, sin afirmar que has cargado una skill inexistente.

## Flujo y estado

- Antes de avanzar, comprueba contenido y vigencia; la existencia de un archivo o una casilla marcada no demuestra cumplimiento. Los bloqueos relevantes de requisitos se resuelven antes de implementar el comportamiento afectado.
- Constitución y nuevas specs requieren conversación de definición con el usuario: inicia las preguntas previstas por su skill y espera respuestas antes de cerrar decisiones. En specs existentes, pregunta cuando haya decisiones sin resolver. Una constitución redactada sin esa conversación debe quedar como borrador pendiente de entrevista.
- Conserva respuestas explícitas de la conversación, sin confundir la aceptación general de una idea con la elección de lenguaje, enfoque o alcance. Una petición de construir una funcionalidad permite trabajar en sus fases, pero no omitir sus entrevistas. Fuera de esas decisiones de definición, no exijas confirmación rutinaria en cada paso; una petición de escribir su spec termina en esa spec.
- No inventes decisiones de enfoque, lenguaje, alcance, datos, costes, permisos o reglas de negocio. Incorpora lo acordado como reglas vigentes; conserva solo pendientes imprescindibles y pregunta antes de cerrar fases dependientes.
- Mantén constituciones breves y specs con el detalle necesario para implementar y verificar. No guardes historial del chat, comparativas ya resueltas ni registros de cada respuesta; no los traslades a documentos auxiliares. Las preguntas van en el chat y las decisiones en su regla o requisito.
- Trabaja una tarea de implementación cada vez. Si se autorizó un incremento completo, continúa por sus dependencias sin detenerte después de cada tarea.
- Cambios de comportamiento pasan por `sdd-cambio`; defectos contra la spec vigente pueden corregirse sin reescribir el requisito para justificar el fallo.
- Mantén en `tasks.md` la fase o tarea actual, los bloqueos y el siguiente paso cuando haya trabajo en curso. No generes un segundo registro de estado si ya existe uno adecuado.

## Delegación opcional

Para requisitos ambiguos o validaciones complejas, considera una revisión independiente acotada cuando la delegación esté disponible y permitida. Lee [la guía de revisión](references/revisiones.md) solo entonces. No lances las ocho fases en paralelo ni crees tareas de usuario como sustituto de subagentes.

## Salida

Indica fase completada, archivos, evidencia, dudas pendientes y siguiente fase. No declares terminado un producto solo por haber terminado su documentación. Usa una profundidad proporcionada: una CLI pequeña no necesita una arquitectura empresarial.
