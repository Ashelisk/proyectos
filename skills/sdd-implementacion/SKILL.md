---
name: sdd-implementacion
description: Implementa tareas autorizadas de una funcionalidad SDD con pruebas de comportamiento y trazabilidad. Úsala cuando existan requisitos y tareas suficientemente definidos; no convierte una petición documental en permiso para programar.
---

# Implementación guiada por tareas

## Entrada

Lee las instrucciones aplicables, constitución, spec, clarificaciones, plan y tarea seleccionada. Comprueba el estado real del código y las dependencias. Si faltan artefactos esenciales, prepara lo necesario solo dentro del alcance solicitado; no inventes una spec a posteriori para justificar código ya escrito.

## Ciclo de trabajo

1. Selecciona una tarea autorizada y lista. Si el usuario pidió solo `Tn`, no implementes las demás. Si pidió el incremento completo, continúa secuencialmente mientras no existan bloqueos materiales.
2. Para comportamiento nuevo o un defecto, escribe o adapta una prueba que observe el contrato. Ejecútala y comprueba que el fallo inicial se debe al comportamiento pendiente, no a un entorno roto. Para cambios documentales o mecánicos de bajo impacto, utiliza una comprobación adecuada sin pruebas artificiales.
3. Implementa lo necesario para satisfacer el requisito, preservando cambios ajenos. Evita refactorizaciones independientes y nuevas prestaciones que no estén en la spec.
4. Ejecuta las comprobaciones focalizadas y la regresión pertinente. Si una suite amplia no puede ejecutarse, registra el motivo y lo que sí se verificó; no conviertas ese hueco en éxito.
5. Refactoriza dentro del alcance y vuelve a verificar lo afectado. Mantén la relación entre tarea, RF/RNF y evidencia sin exigir nombres rígidos de pruebas.
6. Marca la tarea hecha solo cuando su condición de cierre se cumpla. Registra comando, resultado y límites de la verificación en `tasks.md` o en el registro existente.

## Cambios y límites

Si aparece un requisito nuevo, actualiza primero su spec y evalúa el impacto antes de implementarlo. Si la spec es clara y el código la incumple, corrige el defecto; no debilites requisitos o tests para que pasen.

Usa archivos temporales y datos de prueba para operaciones destructivas. Implementar una capacidad de borrar, enviar o cobrar no autoriza ejecutarla sobre datos reales. No publiques ni despliegues servicios por completar una tarea local sin la autorización correspondiente.

## Salida

Entrega cambios, tareas terminadas, resultados ejecutados y pendientes. No declares toda la spec cumplida basándote en una prueba aislada; esa conclusión requiere validación del incremento.
