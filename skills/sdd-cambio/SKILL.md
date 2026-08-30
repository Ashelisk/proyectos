---
name: sdd-cambio
description: Gestiona cambios de comportamiento en SDD actualizando primero la especificación y evaluando impacto en plan, tareas y pruebas. Úsala ante un requisito nuevo o modificado; no para justificar defectos del código debilitando requisitos existentes.
---

# Gestión de cambios

## Entrada

Lee la petición, la spec vigente, constitución, clarificaciones, plan, tareas y evidencias. Distingue un nuevo comportamiento de un defecto respecto al comportamiento ya acordado. Un defecto claro se corrige contra la spec existente.

## Trabajo

1. Identifica intención, alcance y RF/RNF afectados. Si la petición cambia una regla material ambigua, prepara el análisis útil y consulta solo la decisión que falta.
2. Resume el impacto técnico en el chat: requisitos afectados y consecuencias relevantes. No crees un historial de conversación ni un archivo de cambios para cada respuesta o ajuste de redacción. Usa un registro técnico existente solo si el proyecto lo requiere.
3. Actualiza primero `spec.md`. Conserva los identificadores de requisitos que evolucionan; añade identificadores nuevos cuando corresponda y documenta los retirados sin reasignarlos.
4. Revisa conflictos con constitución y otros requisitos. Diferencia lo decidido de lo propuesto; no alteres instrucciones o controles externos como consecuencia automática de cambiar la spec.
5. Actualiza plan y tareas afectados. Si cambia el criterio de una tarea completada, conserva su evidencia histórica y reábrela o crea una tarea adicional. Marca la validación anterior como desactualizada en las partes afectadas.
6. Si se pidió también implementar el cambio, continúa con las tareas listas y vuelve a validar. Si se pidió solo actualizar requisitos o mostrar impacto, termina tras los documentos; un cambio de spec no autoriza por sí mismo código ni migraciones reales.

## Salida y cierre

Entrega el diff o resumen preciso del cambio de requisitos, sus consecuencias y los trabajos pendientes. No anuncies una función nueva como disponible cuando solo se ha especificado.

Para un cambio pequeño, actualiza únicamente las reglas o requisitos afectados. No crees documentos auxiliares, una nueva funcionalidad, una arquitectura nueva o un proceso de aprobación adicional sin necesidad.
