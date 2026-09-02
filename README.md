# Portfolio de software

[![Pruebas multiplataforma](https://github.com/Ashelisk/proyectos/actions/workflows/cross-platform.yml/badge.svg)](https://github.com/Ashelisk/proyectos/actions/workflows/cross-platform.yml)
[![Distribución de FilePilot](https://github.com/Ashelisk/proyectos/actions/workflows/release-filepilot.yml/badge.svg)](https://github.com/Ashelisk/proyectos/actions/workflows/release-filepilot.yml)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Licencia MIT](https://img.shields.io/badge/licencia-MIT-2D3748)](LICENSE)

Proyectos de software desarrollados de extremo a extremo: definición del comportamiento, diseño técnico, implementación, pruebas, automatización y distribución. El repositorio reúne aplicaciones CLI, herramientas de desarrollo y un método reutilizable de Spec-Driven Development (SDD).

## Proyecto destacado: FilePilot

**FilePilot** es una aplicación de línea de comandos escrita en Python que analiza una carpeta y propone cómo organizar sus archivos sin modificar, mover, renombrar ni eliminar nada.

- Clasificación por extensión y cálculo de tamaños.
- Análisis del primer nivel o recorrido recursivo.
- Tratamiento explícito de archivos ocultos, enlaces y errores de lectura.
- Funcionamiento local, sin cuentas, servicios externos ni dependencias de ejecución.
- Distribución como ejecutable independiente para Windows y Linux, además de paquete wheel para Python.

**[Descargar FilePilot v0.1.0](https://github.com/Ashelisk/proyectos/releases/tag/v0.1.0)** · [Documentación de uso](projects/filepilot/README.md) · [Código fuente](projects/filepilot/filepilot) · [Pruebas](projects/filepilot/tests) · [Validación](projects/filepilot/specs/001-analisis-carpeta/validation.md)

```text
filepilot analizar <ruta> [--recursivo] [--incluir-ocultos]
```

| Aspecto | Implementación |
| --- | --- |
| Lenguaje | Python 3.11 o superior |
| Dependencias de ejecución | Ninguna; utiliza la biblioteca estándar |
| Plataformas objetivo | Windows x64 y Linux x86_64 |
| Calidad | Pruebas unitarias, de integración, portabilidad y seguridad de lectura |
| Automatización | GitHub Actions para pruebas, construcción y publicación de releases |
| Distribución | Ejecutables nativos, wheel y sumas SHA-256 |

### Evidencia de calidad

- **Windows 11:** 212 pruebas superadas y una omitida por versión con Python 3.11.9 y 3.14.7.
- **Linux:** 209 pruebas superadas y cuatro omisiones exclusivas de Windows por versión con Python 3.11.16 y 3.14.4.
- **Integración continua:** construcción y verificación independiente de los artefactos para Windows y Linux antes de publicar la release.
- **Trazabilidad:** requisitos, diseño, tareas y resultados de validación conservados junto al producto.

## Estructura del repositorio

```text
projects/filepilot/       Aplicación, pruebas, documentación y especificaciones
skills/                   Fuentes de las nueve skills del flujo SDD
tools/agent_router/       Diagnóstico y sincronización entre entornos de trabajo
tools/puente_agentes/     Coordinación local y controlada entre agentes
specs/000-sdd-toolkit/    Especificación y validación del paquete SDD
```

## Forma de trabajo

Los productos se desarrollan con un flujo SDD: constitución, especificación, clarificación, planificación, tareas, implementación y validación. Cada requisito se vincula con comprobaciones ejecutables y evidencia. El método puede aplicarse manualmente o con asistencia de IA; las herramientas de agentes son opcionales.

El paquete incluye nueve skills reutilizables para coordinar y ejecutar las fases del proceso. Las fuentes están en [`skills/`](skills/) y su validación en [`specs/000-sdd-toolkit/`](specs/000-sdd-toolkit/).

## Próximos proyectos

| Proyecto | Tipo | Estado |
| --- | --- | --- |
| FilePilot | CLI de organización segura de archivos | Versión 0.1.0 publicada |
| API Sentinel | CLI de comprobación de APIs | Previsto |
| Freelance Desk | Aplicación web para clientes y presupuestos | Previsto |
| Pantry Pocket | Aplicación móvil de despensa y compra | Previsto |
| ReservaFlow | Aplicación web de reservas | Previsto |
| FieldOps | Aplicación móvil y web para intervenciones | Previsto |

Los detalles y tecnologías de los proyectos previstos se definirán en sus propias especificaciones antes de implementarlos.

## Licencia

El código se distribuye bajo la [licencia MIT](LICENSE).
