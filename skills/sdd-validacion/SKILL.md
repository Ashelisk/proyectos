---
name: sdd-validacion
description: Verifica una entrega SDD requisito por requisito y produce un informe con evidencia ejecutada, fallos y aspectos no verificados. Úsala para comprobar cumplimiento; no basta con que existan tests ni con revisar casillas marcadas.
---

# Validación de cumplimiento

## Entrada

Lee la versión vigente de spec, constitución, clarificaciones, plan, tareas y código. Identifica el incremento y el entorno exactos. Si no hay código o herramientas ejecutables, todavía puedes revisar la documentación, pero no declarar validado el comportamiento del producto.

## Verificación

1. Recorre cada RF/RNF en alcance, incluidos errores y criterios de finalización. Busca evidencia que observe el requisito completo, no solo pruebas que mencionen su nombre.
2. Ejecuta las comprobaciones pertinentes en un entorno permitido y con datos desechables. Registra comandos, resultados, fecha y contexto suficiente para reproducirlos. No reutilices silenciosamente resultados de una versión anterior.
3. Para cada requisito, asigna `cumple`, `falla` o `no verificado`. Distingue cobertura parcial, inspección estática, evidencia manual y prueba automatizada ejecutada. Las exclusiones deben corresponder al alcance documentado, no servir para ocultar fallos.
4. Comprueba también los riesgos reales: por ejemplo, conservación de archivos, aislamiento de usuarios, carreras de reservas o reintentos móviles. No exijas todas esas categorías a todos los productos.
5. Identifica discrepancias entre código, documentos y evidencia. Devuelve ubicación y escenario reproducible. Una suite en verde no basta si falta un requisito.

## Entregable y veredicto

Escribe `validation.md` junto a la spec, salvo petición de informe solo en conversación. Incluye alcance y versión, entorno, matriz `requisito | evidencia | resultado | limitación`, incidencias y veredicto.

- `Cumple`: todos los requisitos en alcance y criterios de cierre tienen evidencia suficiente de la versión evaluada.
- `No cumple`: existe al menos un incumplimiento demostrado, aunque otras comprobaciones no hayan podido ejecutarse.
- `No concluyente`: no se ha demostrado un fallo, pero falta evidencia necesaria.

En modo revisión no modifiques el producto ni sus criterios para obtener un resultado favorable. Si el usuario también autorizó reparar, registra primero los defectos, corrige dentro de alcance y vuelve a ejecutar las comprobaciones afectadas. Conserva la distinción entre revisión independiente y autorrevisión.
