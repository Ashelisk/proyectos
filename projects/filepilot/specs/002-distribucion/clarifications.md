# Clarificación — Distribución para usuarios finales

## Revisión

- Los artefactos, plataformas, arquitecturas y canal de publicación están definidos de forma observable.
- La versión de la etiqueta se contrasta con los metadatos del paquete; los nombres externos y el contenido permitido de los archivos quedan fijados en RF-1, RF-4 y RF-5.
- RF-2 y RF-3 impiden releases parciales, sustituciones y publicaciones cuya versión no corresponda.
- RF-6 y RF-7 separan el ejecutable sin Python del wheel para Python 3.11 o superior.
- RNF-1 limita las afirmaciones de compatibilidad a los entornos realmente ejecutados.
- No hay conflicto con la constitución: las herramientas de construcción quedan fuera de las dependencias de ejecución y la validación sigue siendo obligatoria por plataforma.

## Resultado

No quedan decisiones abiertas. La especificación está lista para planificación.
