---
name: sdd-especificacion
description: Entrevista y redacta specs SDD claras y concisas, con requisitos EARS, errores y aceptación suficientes para implementar. Documenta el comportamiento vigente, sin historial del chat ni diseño técnico.
---

# Especificación SDD

## Conversación
- Lee constitución, petición y spec existente. Resuelve primero las decisiones pendientes de la constitución que condicionen la funcionalidad.
- Al iniciar una nueva spec, pregunta al usuario y espera respuestas. En una existente, pregunta cuando el cambio deje decisiones sin resolver; una corrección de redacción no exige reabrirlas.
- Pregunta de forma progresiva por usuarios, flujo principal, alcance y errores relevantes. Presenta alternativas cuando ayuden; no inventes respuestas ni repitas cuestiones ya contestadas.
- Mantén un borrador mientras falten decisiones necesarias. Actualiza su contenido con cada respuesta, sin registrar la entrevista.

## Documento
Escribe o edita `specs/NNN-nombre/spec.md` dentro del producto; conserva rutas e identificadores existentes. Selecciona un identificador libre solo para una funcionalidad nueva.

Incluye únicamente las secciones necesarias:
1. Contexto y objetivo: un párrafo.
2. Usuarios e historias: actores y necesidades concretas.
3. Requisitos funcionales: RF identificados, atómicos y observables en EARS, con resultados de éxito y error.
4. Requisitos no funcionales: solo restricciones aplicables y comprobables; no inventes cifras.
5. Casos límite: referencia el RF que los resuelve en lugar de repetirlo.
6. Fuera de alcance: límites de esta entrega.
7. Criterios de finalización: cómo demostrar cumplimiento.
8. Dudas abiertas: solo cuestiones actuales, eliminadas al resolverlas.

Una spec puede ser más extensa que la constitución: el detalle se justifica si elimina ambigüedad para implementar o verificar. Evita explicar varias veces el mismo comportamiento. Añade escenarios de aceptación separados solo cuando el requisito no baste para entenderlos.

No incluyas historial, respuestas del chat, perfil del usuario, decisiones descartadas ni notas del proceso de redacción. No impongas arquitectura, clases o librerías; conserva los contratos técnicos exigidos y deja el diseño para el plan. Los cambios de comportamiento no deben ocultarse como simples correcciones de texto.

## Cierre
Comprueba coherencia con la constitución, trazabilidad y ausencia de decisiones inventadas. Una spec está lista para clarificación cuando incorpora las respuestas necesarias y se entiende sin el chat. Si falta una respuesta, guarda el borrador y pregunta. No implementes código.
