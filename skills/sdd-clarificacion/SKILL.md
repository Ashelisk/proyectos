---
name: sdd-clarificacion
description: Revisa una especificación SDD para detectar ambigüedades, contradicciones, casos límite y conflictos con la constitución. Úsala antes del diseño o al revisar requisitos; no sustituye decisiones de negocio ni implementa soluciones.
---

# Clarificación de requisitos

## Entrada

Lee la spec exacta, la constitución y las decisiones previas. Si no se puede identificar una spec, no inventes una auditoría: indica lo que falta. La revisión es documental; no exige disponer de código.

## Revisión

1. Recorre los RF/RNF y sus escenarios. Busca interpretaciones que conduzcan a comportamientos diferentes, conflictos entre requisitos, resultados no observables y actores o estados omitidos.
2. Contrasta permisos, límites y errores con el dominio real. Busca ejemplos concretos que demuestren la ambigüedad; no acumules preguntas hipotéticas sin impacto en esta entrega.
3. Registra cada hallazgo como `CL-1`: requisito y ubicación, tipo, escenario, consecuencia, pregunta y prioridad. Un bloqueo impide decidir correctamente el comportamiento afectado; una mejora de redacción no bloquea todo el proyecto.
4. En modo «revisa», solo detecta. No resuelvas preguntas de producto ni edites la spec para aparentar consistencia. Si se pide además corregir, aplica las decisiones existentes y las correcciones inequívocas; registra aparte las hipótesis reversibles y deja abiertas las decisiones materiales.
5. Al recibir respuestas, registra su fuente, actualiza los requisitos afectados dentro del alcance autorizado y vuelve a comprobar las relaciones. No marques un hallazgo como resuelto solo porque propusiste una respuesta.

## Salida y cierre

Entrega `clarifications.md` junto a la spec con hallazgos abiertos y resueltos, y uno de estos resultados: lista para planificación; lista salvo partes indicadas; necesita decisión. Si solo se pidió una opinión sin archivos, devuelve el informe en la conversación.

Pregunta por la duda de mayor impacto cuando sea necesario, después de completar la revisión útil. La existencia de dudas no bloqueantes permite continuar el trabajo no afectado. No afirmes ausencia de ambigüedades fuera del alcance examinado.
