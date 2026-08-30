---
name: sdd-tareas
description: Convierte un plan SDD en tareas pequeñas, ordenadas por dependencia y vinculadas a requisitos y verificaciones. Úsala para preparar o actualizar el backlog de una funcionalidad; no ejecuta tareas ni las marca hechas sin evidencia.
---

# Descomposición en tareas

## Entrada

Lee spec, clarificaciones, plan y tareas existentes. Conserva identificadores, avances y evidencia; una nueva planificación no debe reiniciar el trabajo completado.

## Trabajo

- Crea tareas `T1`, `T2`, etc., con checkbox, propósito, requisitos RF/RNF, dependencias, archivos o áreas previstas y una condición «Hecho cuando» comprobable.
- Divide por resultados pequeños que permitan comprobar progreso. Usa estimaciones aproximadas solo si ayudan; no prometas duraciones exactas ni fracciones artificiales para cumplir un límite de minutos.
- Para comportamiento nuevo, incluye su prueba relevante antes o junto con la implementación en la misma tarea. Una tarea de prueba puede completar su objetivo al demostrar un fallo esperado; distingue esto de una funcionalidad terminada.
- Evita tareas vagas como «hacer backend» o «añadir todos los tests al final». La configuración y documentación también necesitan un resultado verificable, pero no pruebas artificiales para simples cambios de texto.
- Marca tareas bloqueadas y su motivo. Señala trabajo independiente únicamente si no comparte contratos inestables ni archivos cuya edición concurrente pueda entrar en conflicto.
- Comprueba que todos los requisitos en alcance están cubiertos; indica expresamente cualquier exclusión. Añade comprobaciones finales de integración y una demostración proporcional al producto.

## Salida y cierre

Actualiza `tasks.md` junto a la spec. Añade una nota breve con la primera tarea ejecutable, las dependencias y los bloqueos. No marques casillas completadas por haber descrito lo que hay que hacer.

La fase está lista cuando una persona puede tomar la siguiente tarea y saber qué hacer, qué requisito satisface y cómo verificarla. No implementes código a menos que el usuario también haya solicitado esa ejecución.
