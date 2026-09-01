# Contexto comprobado del repositorio

Este repositorio reúne productos progresivos desarrollados con Spec-Driven Development y un paquete reutilizable de nueve skills. Actualmente contiene un producto implementado, FilePilot, y herramientas locales de coordinación; API Sentinel, Freelance Desk, Pantry Pocket, ReservaFlow y FieldOps solo figuran como proyectos previstos.

## Estructura y tecnologías

- `projects/filepilot/`: CLI Python 3.11+ sin dependencias de ejecución. Clasifica y presenta un análisis de carpetas sin modificar su contenido. Sus pruebas usan pytest.
- `skills/` y `.claude/skills/`: fuentes y copias de descubrimiento de las nueve skills SDD. `specs/000-sdd-toolkit/` documenta el toolkit, no un producto.
- `tools/puente_agentes/`: puente local en Python estándar para encargos aislados a Claude Code; sus pruebas usan `unittest`.
- `tools/agent_router/`: coordinación multiplataforma, estado compartido y selección de pruebas; usa solo Python estándar.

No hay dependencias JavaScript, servicios, bases de datos ni proceso de build del repositorio completo.

## Comandos reales

Desde la raíz Git:

```text
python tools/agent_router/router.py doctor
python tools/agent_router/router.py status
python tools/agent_router/router.py test
python -m unittest discover -s tools/puente_agentes -p test_puente.py -v
```

En Linux/macOS puede usarse `./agent-router`; en Windows, `./agent-router.ps1` desde PowerShell. Para FilePilot, desde `projects/filepilot`, crea y activa un entorno virtual, instala `pip install -e ".[dev]"` y ejecuta `python -m pytest -q -rs`. La aplicación se ejecuta como `filepilot analizar <ruta>` o `python -m filepilot analizar <ruta>`.

## Plataformas y decisiones duraderas

El flujo de agentes y su CI cubren Linux, Windows y macOS. FilePilot solo declara Linux y Windows como plataformas objetivo, por lo que CI no presenta macOS como compatible. GitHub es el intercambio entre clones independientes; el estado versionado no contiene rutas del equipo. Python estándar es el runtime común porque ya se usa en FilePilot y en el puente, y evita otra cadena de dependencias.

FilePilot tiene evidencia en Windows 11 con Python 3.11.9 y 3.14.7: 212 pruebas superadas y una omitida con privilegios de enlaces simbólicos. En Linux, Python 3.14.4 y pytest 9.0.2 dieron 209 pruebas superadas y 4 omisiones exclusivas de Windows; también pasó el análisis recursivo documentado. Python 3.11 no está instalado en ese entorno y su combinación Linux sigue pendiente, por lo que no se considera acreditada toda la matriz.

Claude Code y Codex son herramientas opcionales para `cycle`; `doctor`, `status`, `sync`, `test` y `checkpoint` no requieren autenticación de agentes. Las sesiones y resultados locales de orquestación se guardan en `.agent-local/` y no se versionan.
