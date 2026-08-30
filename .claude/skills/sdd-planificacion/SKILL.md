---
name: sdd-planificacion
description: Diseña el plan técnico de una funcionalidad SDD desde su especificación y constitución, con componentes, contratos y estrategia de pruebas. Úsala cuando el comportamiento esté definido; no implementa código ni sustituye la spec.
---

# Planificación técnica

## Entrada

Lee constitución, spec, clarificaciones y código o configuración existentes. Determina qué requisitos siguen sin definición; no diseñes como definitivas las partes dependientes de decisiones bloqueantes.

## Trabajo

1. Elige el diseño más sencillo que cubra los requisitos actuales y respete el proyecto. Si ya existe una arquitectura adecuada, extiéndela.
2. Define componentes, responsabilidades, datos y contratos relevantes: entrada/salida CLI, interfaces HTTP o estados de pantalla según el producto. Conecta cada componente con sus RF/RNF.
3. Justifica decisiones de impacto y una alternativa razonable cuando exista una disyuntiva real. No inventes comparaciones para decisiones triviales ni añadas infraestructura para demostrar complejidad.
4. Incluye errores, persistencia, migraciones o recuperación cuando apliquen. Para cambios con datos existentes, identifica compatibilidad y reversión; no asumas que se pueden borrar datos.
5. Define la estrategia de validación por riesgo: comportamiento puro, integraciones reales, flujos del usuario y verificaciones manuales donde correspondan. Especifica cómo generar datos desechables y qué no se tocará.
6. Verifica documentación primaria cuando una capacidad externa incierta determine el diseño. Diferencia información comprobada de supuestos, e identifica dependencias de coste o acceso sin contratarlas.

## Salida y cierre

Escribe `plan.md` junto a la spec: enfoque, componentes, datos y contratos, decisiones, mapa de RF/RNF, pruebas, riesgos y orden de implementación. Una investigación o prototipo exploratorio solo se ejecuta si entra en la petición; un plan por sí solo no autoriza código de producto.

La fase está completa cuando cada requisito en alcance tiene una vía de implementación y verificación, y las decisiones pendientes están localizadas. No escondas falta de definición detrás de decisiones técnicas.
