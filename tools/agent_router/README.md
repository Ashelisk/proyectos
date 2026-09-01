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
./agent-router cycle --max-cycles 5
./agent-router checkpoint --next-action "Continuar las pruebas en Windows"
```

En PowerShell sustituye `./agent-router` por `./agent-router.ps1`. `doctor` y `status` son completamente de solo lectura. `sync --dry-run` no hace fetch ni cambia referencias; `sync` exige un árbol limpio, valida `origin`, hace `fetch --prune` y solo permite un fast-forward. Con `--branch` recupera una rama remota en el segundo sistema sin usar `main` para trabajo incompleto.

`test` ejecuta las suites detectadas y declara FilePilot no aplicable en macOS. Para probar tanto el módulo como el ejecutable instalado, mantiene un entorno virtual ignorado en `.agent-local/`, usa los paquetes de desarrollo ya presentes e instala el checkout editable con `--no-build-isolation`; no descarga dependencias. CI realiza una instalación editable limpia. `cycle --dry-run` muestra adaptadores, documentos y esquema sin iniciar agentes. Un ciclo real solo se admite desde una terminal que no esté ya dentro de Claude o Codex, exige árbol limpio y limita los intentos. Claude implementa sin shell ni Git; Codex revisa en sandbox de solo lectura. Ambos deben devolver JSON conforme al esquema: un texto libre nunca equivale a `PASS`.

`checkpoint` no prepara cambios de trabajo implícitamente: la persona o coordinador debe revisarlos y ejecutar `git add` primero. El comando actualiza y prepara el estado, crea un commit normal y hace push de la rama actual; rechaza `main`, archivos sin preparar y remotos inesperados.

Datos de sesión, esquemas temporales y resultados estructurados por ciclo viven en `.agent-local/` y no se versionan. El relevo portable queda resumido en `.agents/state.json` y `TASK.md`, que el ciclo actualiza al terminar.
