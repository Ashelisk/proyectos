"""Router seguro y multiplataforma para el relevo de trabajo entre agentes."""

from __future__ import annotations

import argparse
from contextlib import redirect_stdout
from datetime import datetime, timezone
import io
import json
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys


EXPECTED_REMOTE = "github.com/Ashelisk/proyectos"
FINAL_STATES = {"PASS", "FAIL", "BLOCKED", "NEEDS_HUMAN"}
SHARED_FILES = ("AGENTS.md", "PROJECT_CONTEXT.md", "TASK.md", ".agents/state.json")
ACTIVE_ENV = "AGENT_ROUTER_ACTIVE"


class RouterError(RuntimeError):
    """Error controlado que impide continuar con seguridad."""


def run(args: list[str], cwd: Path, *, check: bool = True, input_text: str | None = None,
        environment: dict[str, str] | None = None):
    result = subprocess.run(
        args, cwd=cwd, input=input_text, text=True, encoding="utf-8",
        errors="replace", capture_output=True, timeout=900, env=environment,
    )
    if check and result.returncode:
        detail = (result.stderr or result.stdout).strip()
        raise RouterError(f"Falló {' '.join(args)}: {detail}")
    return result


def git(root: Path, *args: str, check: bool = True) -> str:
    return run(["git", "-C", str(root), *args], root, check=check).stdout.strip()


def git_succeeds(root: Path, *args: str) -> bool:
    return run(["git", "-C", str(root), *args], root, check=False).returncode == 0


def find_root(start: Path | None = None) -> Path:
    location = (start or Path.cwd()).resolve()
    result = run(["git", "-C", str(location), "rev-parse", "--show-toplevel"], location)
    return Path(result.stdout.strip()).resolve()


def os_name() -> str:
    value = platform.system().lower()
    return {"darwin": "macos", "windows": "windows", "linux": "linux"}.get(value, value)


def normalize_remote(url: str) -> str:
    value = url.strip().removesuffix(".git").removesuffix("/")
    value = re.sub(r"^https?://", "", value)
    value = re.sub(r"^ssh://git@", "", value)
    value = re.sub(r"^git@([^:]+):", r"\1/", value)
    return value.casefold()


def ensure_expected_remote(root: Path) -> str:
    remote = git(root, "remote", "get-url", "origin")
    if normalize_remote(remote) != EXPECTED_REMOTE.casefold():
        raise RouterError(f"origin inesperado: {remote}")
    return remote


def branch(root: Path) -> str:
    current = git(root, "branch", "--show-current")
    if not current:
        raise RouterError("HEAD está separado; se requiere intervención humana.")
    return current


def porcelain(root: Path) -> list[str]:
    output = git(root, "status", "--porcelain=v1", "--untracked-files=all")
    return output.splitlines() if output else []


def relation(root: Path, reference: str) -> dict[str, object]:
    exists = git(root, "rev-parse", "--verify", "--quiet", reference, check=False)
    if not exists:
        return {"reference": reference, "ahead": None, "behind": None, "state": "missing"}
    counts = git(root, "rev-list", "--left-right", "--count", f"HEAD...{reference}").split()
    ahead, behind = (int(counts[0]), int(counts[1]))
    state = "diverged" if ahead and behind else "ahead" if ahead else "behind" if behind else "equal"
    return {"reference": reference, "ahead": ahead, "behind": behind, "state": state}


def executable_version(name: str) -> dict[str, object]:
    path = shutil.which(name)
    if not path:
        return {"available": False, "version": None}
    result = subprocess.run(
        [path, "--version"], text=True, encoding="utf-8", errors="replace",
        capture_output=True, timeout=15,
    )
    output = (result.stdout or result.stderr).strip().splitlines()
    return {"available": result.returncode == 0, "version": output[0] if output else "desconocida"}


def test_commands(root: Path, system: str | None = None) -> list[dict[str, object]]:
    current_os = system or os_name()
    python = sys.executable
    commands: list[dict[str, object]] = [
        {"name": "agent-router", "cwd": ".", "argv": [python, "-m", "unittest", "discover", "-s", "tools/agent_router", "-p", "test_router.py", "-v"], "applicable": True},
        {"name": "puente-agentes", "cwd": ".", "argv": [python, "-m", "unittest", "discover", "-s", "tools/puente_agentes", "-p", "test_puente.py", "-v"], "applicable": True},
        {"name": "filepilot", "cwd": "projects/filepilot", "argv": ["<venv-python>", "-m", "pytest", "-q", "-rs"], "setup": "venv --system-site-packages; pip install -e . --no-build-isolation", "applicable": current_os in {"linux", "windows"}},
    ]
    return commands


def snapshot(root: Path) -> dict[str, object]:
    current_branch = branch(root)
    tools = {name: executable_version(name) for name in ("git", "gh", "claude", "codex")}
    tools["python"] = {"available": True, "version": platform.python_version()}
    tools["pytest"] = executable_version("pytest")
    return {
        "platform": os_name(), "root": str(root), "branch": current_branch,
        "head": git(root, "rev-parse", "HEAD"), "origin": ensure_expected_remote(root),
        "clean": not porcelain(root), "changes": porcelain(root),
        "origin_main": relation(root, "origin/main"), "origin_branch": relation(root, f"origin/{current_branch}"),
        "tools": tools, "tests": test_commands(root),
    }


def load_state(root: Path) -> dict[str, object]:
    path = root / ".agents" / "state.json"
    try:
        state = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise RouterError(f"Estado compartido inválido: {error}") from error
    required = {"$schema", "task_id", "active_branch", "last_known_commit", "last_platform", "status", "cycle", "tests", "next_action", "blocked_reason", "updated_at"}
    if set(state) != required or state["status"] not in FINAL_STATES | {"IN_PROGRESS"}:
        raise RouterError("state.json no cumple el formato documentado.")
    if set(state["tests"]) != {"windows", "linux", "macos", "ci"}:
        raise RouterError("state.json no contiene todas las plataformas.")
    if not isinstance(state["cycle"], int) or state["cycle"] < 0:
        raise RouterError("El número de ciclo no es válido.")
    return state


def write_state(root: Path, state: dict[str, object]) -> None:
    state["updated_at"] = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    path = root / ".agents" / "state.json"
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def update_task_board(root: Path, status: str, platform_name: str, summary: str, next_action: str) -> None:
    path = root / "TASK.md"
    text = path.read_text(encoding="utf-8")
    text, state_count = re.subn(r"(?m)^- \*\*Estado:\*\*.*$", f"- **Estado:** `{status}`", text, count=1)
    text, platform_count = re.subn(
        rf"(?m)^- \*\*{re.escape(platform_name.capitalize())}:\*\*.*$",
        f"- **{platform_name.capitalize()}:** `{status}`; {summary}", text, count=1,
    )
    text, next_count = re.subn(
        r"(?s)(## Siguiente acción exacta\n\n).*?(?=\n## |\Z)",
        lambda match: match.group(1) + next_action + "\n", text, count=1,
    )
    if (state_count, platform_count, next_count) != (1, 1, 1):
        raise RouterError("TASK.md no conserva las secciones que actualiza cycle.")
    path.write_text(text, encoding="utf-8")


def print_value(value: object, structured: bool) -> None:
    if structured:
        print(json.dumps(value, ensure_ascii=False, indent=2))
        return
    if isinstance(value, dict):
        for key, item in value.items():
            print(f"{key}: {json.dumps(item, ensure_ascii=False) if isinstance(item, (dict, list)) else item}")
    else:
        print(value)


def command_doctor(root: Path, args) -> int:
    data = snapshot(root)
    problems = []
    if not data["clean"]:
        problems.append("El árbol de trabajo contiene cambios.")
    if data["origin_main"]["state"] == "diverged":
        problems.append("La rama ha divergido de origin/main.")
    if data["origin_branch"]["state"] == "diverged":
        problems.append("La rama ha divergido de su referencia en origin.")
    data["diagnosis"] = "PASS" if not problems else "NEEDS_HUMAN"
    data["problems"] = problems
    print_value(data, args.json)
    return 0 if not problems else 2


def command_status(root: Path, args) -> int:
    print_value({"repository": snapshot(root), "shared_state": load_state(root)}, args.json)
    return 0


def command_sync(root: Path, args) -> int:
    ensure_expected_remote(root)
    if porcelain(root):
        raise RouterError("sync requiere un árbol limpio; no se guardan cambios automáticamente.")
    requested = args.branch or branch(root)
    if args.dry_run:
        print_value({"dry_run": True, "branch": requested, "actions": ["git fetch --prune origin", f"actualizar {requested} solo mediante fast-forward"]}, args.json)
        return 0
    git(root, "fetch", "--prune", "origin")
    current = branch(root)
    local_exists = git_succeeds(root, "show-ref", "--verify", "--quiet", f"refs/heads/{requested}")
    remote_exists = git_succeeds(root, "show-ref", "--verify", "--quiet", f"refs/remotes/origin/{requested}")
    if requested != current:
        if local_exists:
            git(root, "switch", requested)
        elif remote_exists:
            git(root, "switch", "--track", "-c", requested, f"origin/{requested}")
        else:
            raise RouterError(f"La rama {requested} no existe localmente ni en origin.")
    rel = relation(root, f"origin/{requested}")
    if rel["state"] == "diverged" or rel["ahead"]:
        raise RouterError(f"No es seguro sincronizar: relación {rel['state']} con origin/{requested}.")
    if rel["behind"]:
        git(root, "merge", "--ff-only", f"origin/{requested}")
    print_value({"branch": requested, "result": "up-to-date" if not rel["behind"] else "fast-forward", "before": rel}, args.json)
    return 0


def command_test(root: Path, args) -> int:
    results = []
    failed = False
    for item in test_commands(root):
        if not item["applicable"]:
            results.append({"name": item["name"], "status": "NOT_APPLICABLE", "reason": "Plataforma fuera del alcance declarado."})
            continue
        if args.only and item["name"] not in args.only:
            continue
        if args.dry_run:
            results.append({"name": item["name"], "status": "DRY_RUN", "cwd": item["cwd"], "argv": item["argv"]})
            continue
        command = list(item["argv"])
        setup_output = ""
        if item["name"] == "filepilot":
            venv = root / ".agent-local" / "filepilot-test-venv"
            venv_python = venv / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
            if not venv_python.exists():
                setup = run([sys.executable, "-m", "venv", "--system-site-packages", str(venv)], root, check=False)
                if setup.returncode:
                    results.append({"name": item["name"], "status": "BLOCKED", "reason": (setup.stderr or setup.stdout)[-4000:]})
                    failed = True
                    continue
            install = run([str(venv_python), "-m", "pip", "install", "-e", ".", "--no-build-isolation"], root / item["cwd"], check=False)
            setup_output = (install.stdout + install.stderr)[-2000:]
            if install.returncode:
                results.append({"name": item["name"], "status": "BLOCKED", "reason": setup_output})
                failed = True
                continue
            command[0] = str(venv_python)
        result = run(command, root / item["cwd"], check=False)
        status = "PASS" if result.returncode == 0 else "FAIL"
        results.append({"name": item["name"], "status": status, "returncode": result.returncode, "setup": setup_output, "stdout": result.stdout[-4000:], "stderr": result.stderr[-4000:]})
        failed |= result.returncode != 0
    print_value({"platform": os_name(), "results": results}, args.json)
    return 1 if failed else 0


RESULT_SCHEMA = {
    "type": "object", "additionalProperties": False,
    "properties": {
        "status": {"type": "string", "enum": ["PASS", "FAIL", "BLOCKED", "NEEDS_HUMAN"]},
        "summary": {"type": "string"},
        "findings": {"type": "array", "items": {"type": "string"}},
        "tests": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["status", "summary", "findings", "tests"],
}


def adapter_commands(root: Path, schema_path: Path, output_path: Path) -> dict[str, list[str]]:
    claude_schema = json.dumps(RESULT_SCHEMA, separators=(",", ":"))
    return {
        "claude": ["claude", "-p", "--output-format", "json", "--json-schema", claude_schema,
                   "--restricted", "--permission-mode", "dontAsk", "--setting-sources", "",
                   "--strict-mcp-config", "--mcp-config", '{"mcpServers":{}}', "--no-chrome",
                   "--tools", "Read,Grep,Glob,Edit,Write"],
        "codex": ["codex", "exec", "--ephemeral", "--ignore-user-config", "-s", "read-only",
                  "-a", "never", "-C", str(root), "--output-schema", str(schema_path),
                  "-o", str(output_path), "-"],
    }


def validate_agent_result(value: object) -> dict[str, object]:
    if not isinstance(value, dict) or set(value) != {"status", "summary", "findings", "tests"}:
        raise RouterError("El agente no devolvió el objeto estructurado exigido.")
    if value["status"] not in FINAL_STATES or not isinstance(value["summary"], str):
        raise RouterError("El veredicto estructurado del agente no es válido.")
    if not all(isinstance(value[key], list) and all(isinstance(x, str) for x in value[key]) for key in ("findings", "tests")):
        raise RouterError("Los hallazgos o pruebas del agente no son válidos.")
    return value


def invoke_claude(root: Path, command: list[str], prompt: str) -> dict[str, object]:
    result = run(command, root, check=False, input_text=prompt)
    if result.returncode:
        raise RouterError(f"Claude terminó con código {result.returncode}: {(result.stderr or result.stdout)[-1500:]}")
    outer = json.loads(result.stdout)
    return validate_agent_result(outer.get("structured_output"))


def invoke_codex(root: Path, command: list[str], prompt: str, output: Path) -> dict[str, object]:
    result = run(command, root, check=False, input_text=prompt)
    if result.returncode:
        raise RouterError(f"Codex terminó con código {result.returncode}: {(result.stderr or result.stdout)[-1500:]}")
    return validate_agent_result(json.loads(output.read_text(encoding="utf-8")))


def cycle_prompt(root: Path, role: str, corrections: list[str] | None = None) -> str:
    contents = []
    for name in SHARED_FILES:
        contents.append(f"\n--- {name} ---\n{(root / name).read_text(encoding='utf-8')}")
    instruction = (
        "Implementa la tarea activa dentro de su alcance. No uses Git ni ejecutes otros agentes. "
        "Devuelve exclusivamente el resultado estructurado solicitado."
        if role == "claude" else
        "Revisa de forma independiente todos los cambios sin modificarlos. Comprueba requisitos, seguridad, portabilidad y pruebas. "
        "PASS exige cero hallazgos concretos; devuelve exclusivamente el resultado estructurado solicitado."
    )
    if corrections:
        instruction += " Corrige estos hallazgos verificables: " + json.dumps(corrections, ensure_ascii=False)
    return instruction + "\n" + "".join(contents)


def nested_session() -> bool:
    return bool(os.environ.get(ACTIVE_ENV) or os.environ.get("CLAUDECODE") or os.environ.get("CODEX_THREAD_ID"))


def command_cycle(root: Path, args) -> int:
    if args.max_cycles < 1:
        raise RouterError("--max-cycles debe ser positivo.")
    ensure_expected_remote(root)
    state = load_state(root)
    local = root / ".agent-local"
    schema = local / "review.schema.json"
    output = local / "codex-result.json"
    commands = adapter_commands(root, schema, output)
    if args.dry_run:
        print_value({"dry_run": True, "max_cycles": args.max_cycles, "documents": list(SHARED_FILES), "adapters": commands, "structured_schema": RESULT_SCHEMA}, args.json)
        return 0
    if nested_session():
        raise RouterError("cycle no se inicia dentro de otra sesión Claude/Codex; usa --dry-run o una terminal normal.")
    if porcelain(root):
        raise RouterError("cycle requiere un árbol limpio antes de sincronizar.")
    command_sync(root, argparse.Namespace(branch=None, dry_run=False, json=True))
    if branch(root) != state["active_branch"]:
        raise RouterError("La rama actual no coincide con el estado compartido.")
    local.mkdir(parents=True, exist_ok=True)
    schema.write_text(json.dumps(RESULT_SCHEMA, indent=2) + "\n", encoding="utf-8")
    environment_before = os.environ.get(ACTIVE_ENV)
    os.environ[ACTIVE_ENV] = "1"
    corrections: list[str] | None = None
    verdict: dict[str, object] = {"status": "FAIL", "summary": "No se ejecutó ninguna revisión.", "findings": [], "tests": []}
    try:
        for number in range(1, args.max_cycles + 1):
            implementation = invoke_claude(root, commands["claude"], cycle_prompt(root, "claude", corrections))
            (local / f"cycle-{number}-claude.json").write_text(json.dumps(implementation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            if implementation["status"] in {"BLOCKED", "NEEDS_HUMAN"}:
                verdict = implementation
                break
            captured = io.StringIO()
            with redirect_stdout(captured):
                test_code = command_test(root, argparse.Namespace(only=None, dry_run=False, json=True))
            test_payload = json.loads(captured.getvalue())
            (local / f"cycle-{number}-tests.json").write_text(json.dumps(test_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            if test_code:
                failed_tests = [item for item in test_payload["results"] if item["status"] in {"FAIL", "BLOCKED"}]
                concrete = [
                    f"{item['name']} ({item['status']}): " + (item.get("stderr") or item.get("stdout") or item.get("reason") or "sin detalle")[-2000:]
                    for item in failed_tests
                ]
                verdict = {"status": "FAIL", "summary": "Fallaron pruebas automatizadas.", "findings": concrete, "tests": [f"{item['name']}: {item['status']}" for item in test_payload["results"]]}
            else:
                verdict = invoke_codex(root, commands["codex"], cycle_prompt(root, "codex"), output)
                (local / f"cycle-{number}-codex.json").write_text(json.dumps(verdict, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            state["cycle"] += 1
            if verdict["status"] == "PASS":
                break
            if verdict["status"] in {"BLOCKED", "NEEDS_HUMAN"}:
                break
            corrections = list(verdict["findings"])
            if not corrections:
                verdict = {"status": "NEEDS_HUMAN", "summary": "FAIL sin correcciones concretas.", "findings": [], "tests": []}
                break
    finally:
        if environment_before is None:
            os.environ.pop(ACTIVE_ENV, None)
        else:
            os.environ[ACTIVE_ENV] = environment_before
    state["status"] = verdict["status"]
    state["last_platform"] = os_name()
    state["last_known_commit"] = git(root, "rev-parse", "HEAD")
    state["blocked_reason"] = verdict["summary"] if verdict["status"] in {"BLOCKED", "NEEDS_HUMAN"} else None
    state["next_action"] = "Crear checkpoint y subir la rama." if verdict["status"] == "PASS" else verdict["summary"]
    write_state(root, state)
    update_task_board(root, verdict["status"], os_name(), verdict["summary"], state["next_action"])
    print_value({"verdict": verdict, "cycles": state["cycle"]}, args.json)
    return 0 if verdict["status"] == "PASS" else 1


def command_checkpoint(root: Path, args) -> int:
    ensure_expected_remote(root)
    current = branch(root)
    if current == "main":
        raise RouterError("Nunca se crea un checkpoint incompleto directamente en main.")
    unstaged = git(root, "diff", "--name-only").splitlines()
    untracked = git(root, "ls-files", "--others", "--exclude-standard").splitlines()
    if unstaged or untracked:
        raise RouterError("Prepara explícitamente los cambios con git add antes del checkpoint; hay archivos sin preparar.")
    state = load_state(root)
    state.update(active_branch=current, last_known_commit=git(root, "rev-parse", "HEAD"), last_platform=os_name(), status="IN_PROGRESS", next_action=args.next_action, blocked_reason=None)
    write_state(root, state)
    git(root, "add", ".agents/state.json")
    if not git(root, "diff", "--cached", "--name-only"):
        raise RouterError("No hay cambios preparados para el checkpoint.")
    git(root, "commit", "-m", args.message)
    git(root, "push", "-u", "origin", current)
    print_value({"status": "PASS", "branch": current, "commit": git(root, "rev-parse", "HEAD"), "next_action": args.next_action}, args.json)
    return 0


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--repo", type=Path, help="Ubicación dentro del repositorio; por defecto, el directorio actual.")
    commands = result.add_subparsers(dest="command", required=True)
    for name in ("doctor", "status"):
        child = commands.add_parser(name)
        child.add_argument("--json", action="store_true")
    sync = commands.add_parser("sync")
    sync.add_argument("--branch")
    sync.add_argument("--dry-run", action="store_true")
    sync.add_argument("--json", action="store_true")
    test = commands.add_parser("test")
    test.add_argument("--only", action="append", choices=("agent-router", "puente-agentes", "filepilot"))
    test.add_argument("--dry-run", action="store_true")
    test.add_argument("--json", action="store_true")
    cycle = commands.add_parser("cycle")
    cycle.add_argument("--max-cycles", type=int, default=5)
    cycle.add_argument("--dry-run", action="store_true")
    cycle.add_argument("--json", action="store_true")
    checkpoint = commands.add_parser("checkpoint")
    checkpoint.add_argument("--next-action", required=True)
    checkpoint.add_argument("--message", default="chore: guarda checkpoint de agentes")
    checkpoint.add_argument("--json", action="store_true")
    return result


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        root = find_root(args.repo)
        return globals()[f"command_{args.command}"](root, args)
    except (RouterError, OSError, subprocess.SubprocessError, json.JSONDecodeError) as error:
        print(f"NEEDS_HUMAN: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
