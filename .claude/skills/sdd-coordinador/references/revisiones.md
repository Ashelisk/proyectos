# Revisiones con subagentes

Una skill contiene el método; un subagente es una ejecución independiente y temporal. Estas instrucciones no registran agentes permanentes ni habilitan herramientas que el entorno no tenga.

## Cuándo delegar

- Clarificación: hay reglas con consecuencias distintas según la interpretación.
- Diseño: una decisión difícil merece contrastar una alternativa concreta.
- Validación: conviene contrastar el comportamiento contra la spec sin depender del razonamiento del implementador.

En proyectos pequeños, realiza la revisión localmente. No delegues si no hay una subtarea autónoma y trabajo útil que el coordinador pueda continuar. Si falta capacidad o autorización, usa revisión local e indica que no fue independiente.

## Encargo mínimo

Entrega al revisor la petición real, la ruta del producto y de la spec, la skill de su fase, los archivos necesarios y los límites de acceso. Por defecto, que lea sin editar y devuelva hallazgos. Para una validación ejecutable, permite únicamente pruebas locales y datos desechables; no servicios de producción ni secretos. No adelantes el veredicto esperado ni soluciones para influir en el resultado.

Solicita por hallazgo: requisito afectado, ubicación, escenario reproducible, consecuencia y evidencia. El revisor debe distinguir un defecto de una preferencia estética, una pregunta de negocio o una comprobación no ejecutada.

## Integración

El coordinador contrasta los hallazgos, elimina duplicados y decide el siguiente paso conforme a la petición. Solo él integra cambios en documentos compartidos. Repite las verificaciones afectadas por las correcciones; no conviertas una opinión del subagente en prueba de que el sistema funciona.
