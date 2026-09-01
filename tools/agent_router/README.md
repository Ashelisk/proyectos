# Agent router

CLI en Python estándar para diagnosticar, sincronizar y relevar una rama entre clones independientes. Siempre se ejecuta desde cualquier ubicación interior del repositorio y descubre la raíz mediante Git.

## Uso

```text
./agent-router doctor --json
./agent-router sync --dry-run
./agent-router sync --branch chore/nombre
./agent-router status --json
./agent-router test
./agent-router cycle --dry-run
./agent-router checkpoint --next-action "Continuar las pruebas en Windows"
```

En PowerShell sustituye `./agent-router` por `./agent-router.ps1`. `doctor` y `status` son completamente de solo lectura. `sync --dry-run` no hace fetch ni cambia referencias; `sync` exige un árbol limpio, valida `origin`, hace `fetch --prune` y solo permite un fast-forward. Con `--branch` recupera una rama remota en el segundo sistema sin usar `main` para trabajo incompleto.

`test` ejecuta las suites detectadas y declara FilePilot no aplicable en macOS. Usa el intérprete de desarrollo con el que se inicia el router; FilePilot y `pytest` deben estar instalados como indica su README. Para que una instalación editable de otro checkout no falsee el resultado, fija `PYTHONPATH` al FilePilot de la rama actual y usa un directorio temporal privado bajo `.agent-local/`. No crea entornos ni descarga dependencias. La salida estructurada permanece en JSON ASCII válido y la CLI configura UTF-8 cuando el terminal lo permite. CI realiza una instalación editable limpia.

`cycle --dry-run` muestra los documentos y controles requeridos sin iniciar agentes. El ciclo real permanece deshabilitado: la programación y revisión usa `tools/puente_agentes/` hasta que el router pueda reutilizar sus rutas editables, modelo y esfuerzo acreditados, rondas, presupuesto, consumo, inspección del diff y aprobación. `cycle` nunca es un atajo para eludir esos límites.

`checkpoint` no prepara cambios de trabajo implícitamente: la persona o coordinador debe revisarlos y ejecutar `git add` primero. El comando actualiza y prepara el estado, crea un commit normal y hace push de la rama actual; rechaza `main`, archivos sin preparar y remotos inesperados.

Datos de sesión, esquemas temporales y resultados estructurados por ciclo viven en `.agent-local/` y no se versionan. El relevo portable queda resumido en `.agents/state.json` y `TASK.md`, que el ciclo actualiza al terminar.
