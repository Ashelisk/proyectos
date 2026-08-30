---
name: sdd-constitucion
description: Entrevista al usuario y crea o edita una constitución SDD breve con principios operativos del proyecto. Pregunta por enfoque y lenguajes antes de fijarlos; no documenta la conversación ni implementa código.
---

# Constitución SDD

## Conversación
- Lee las instrucciones del proyecto y su constitución. Al iniciar una creación o revisión de fondo, SIEMPRE pregunta al usuario y espera su respuesta. Si la entrevista ya está en curso, continúa sin repetir decisiones contestadas.
- Conversa sobre enfoque, alcance, calidad y restricciones; pregunta preferiblemente una cuestión cada vez.
- Antes de elegir lenguaje, compara dos o tres opciones adecuadas y explica ventajas y costes. No excluyas una opción porque el usuario no la conozca. Conserva elecciones explícitas previas; una recomendación o aceptación general de la idea no elige el stack.
- Mientras falten decisiones necesarias, mantén el documento como borrador y no avances al trabajo dependiente.

## Documento
Edita `docs/constitution.md` en la raíz del producto, respetando su ubicación existente.
- Escribe solo principios vigentes y verificables: tecnología, simplicidad, modularidad, calidad y límites realmente acordados.
- Para un proyecto pequeño, busca 5–7 principios y aproximadamente 15 líneas. Cada principio debe entenderse sin un apartado adicional de explicación o comprobación.
- Incorpora cada respuesta sustituyendo o precisando la regla correspondiente. El archivo describe cómo construir el producto, no quién dijo qué.
- Excluye transcripciones, historial de conversación o versiones, perfil del usuario, alternativas descartadas, fuentes de cada elección y preguntas ya resueltas. No traslades ese contenido a otro archivo.
- Los comandos, algoritmos, casos límite y evidencias detalladas pertenecen a spec, plan o validación. No conviertas propuestas funcionales en principios aceptados.
- Si falta una decisión, deja como máximo una nota breve de pendientes; formula la pregunta en el chat.
- Al revisar, conserva los identificadores que ya tengan referencias en specs o planes y evita duplicar reglas.

## Cierre
Comprueba que cada frase aporta una instrucción necesaria y que el documento se entiende sin leer el chat. No cierres la constitución sin las respuestas fundamentales. Entrega el archivo y, si corresponde, la siguiente pregunta; no programes.
