"""Router seguro y multiplataforma para el relevo de trabajo entre agentes."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
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


def module_version(name: str) -> dict[str, object]:
    result = subprocess.run(
        [sys.executable, "-m", name, "--version"], text=True, encoding="utf-8",
        errors="replace", capture_output=True, timeout=15,
    )
    output = (result.stdout or result.stderr).strip().splitlines()
    return {"available": result.returncode == 0, "version": output[0] if output else None}


def development_environment(project: Path) -> dict[str, str]:
    """Fuerza que los subprocesos importen el checkout actual de FilePilot."""
    if not project.is_dir():
        raise RouterError(f"No existe el proyecto que debe probarse: {project}")
    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(project.resolve())
    return environment


def test_commands(root: Path, system: str | None = None) -> list[dict[str, object]]:
    current_os = system or os_name()
    python = sys.executable
    commands: list[dict[str, object]] = [
        {"name": "agent-router", "cwd": ".", "argv": [python, "-m", "unittest", "discover", "-s", "tools/agent_router", "-p", "test_router.py", "-v"], "applicable": True},
        {"name": "puente-agentes", "cwd": ".", "argv": [python, "-m", "unittest", "discover", "-s", "tools/puente_agentes", "-p", "test_puente.py", "-v"], "applicable": True},
        {"name": "filepilot", "cwd": "projects/filepilot", "argv": [python, "-m", "pytest", "-q", "-rs", "--basetemp=<agent-local>"], "setup": "intérprete de desarrollo instalado; PYTHONPATH=<checkout>", "applicable": current_os in {"linux", "windows"}},
    ]
    return commands


def snapshot(root: Path) -> dict[str, object]:
    current_branch = branch(root)
    tools = {name: executable_version(name) for name in ("git", "gh", "claude", "codex")}
    tools["python"] = {"available": True, "version": platform.python_version()}
    tools["pytest"] = module_version("pytest")
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
    required = {"$schema", "task_id", "active_branch", "verified_commit", "last_platform", "status", "cycle", "tests", "next_action", "blocked_reason", "updated_at"}
    if set(state) != required or state["$schema"] != "state.schema.json":
        raise RouterError("state.json no cumple el formato documentado.")
    if (not isinstance(state["task_id"], str)
            or not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,63}", state["task_id"])
            or not isinstance(state["active_branch"], str) or not state["active_branch"]
            or (state["verified_commit"] is not None
                and (not isinstance(state["verified_commit"], str)
                     or not re.fullmatch(r"[0-9a-f]{40}", state["verified_commit"])))
            or state["last_platform"] not in {"windows", "linux", "macos", "ci"}
            or state["status"] not in FINAL_STATES | {"IN_PROGRESS"}):
        raise RouterError("state.json contiene identidad, rama, commit, plataforma o estado inválidos.")
    if not isinstance(state["tests"], dict) or set(state["tests"]) != {"windows", "linux", "macos", "ci"}:
        raise RouterError("state.json no contiene todas las plataformas.")
    allowed_test_states = {"PENDING", "PASS", "FAIL", "BLOCKED", "NOT_APPLICABLE"}
    for result in state["tests"].values():
        if (not isinstance(result, dict) or set(result) != {"status", "command", "summary"}
                or result["status"] not in allowed_test_states
                or (result["command"] is not None and not isinstance(result["command"], str))
                or not isinstance(result["summary"], str)):
            raise RouterError("state.json contiene un resultado de plataforma inválido.")
    if isinstance(state["cycle"], bool) or not isinstance(state["cycle"], int) or state["cycle"] < 0:
        raise RouterError("El número de ciclo no es válido.")
    if (not isinstance(state["next_action"], str) or not state["next_action"]
            or (state["blocked_reason"] is not None and not isinstance(state["blocked_reason"], str))
            or not isinstance(state["updated_at"], str)
            or not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z", state["updated_at"])):
        raise RouterError("state.json contiene relevo, bloqueo o fecha inválidos.")
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
        print(json.dumps(value, ensure_ascii=True, indent=2))
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
        environment = None
        if item["name"] == "filepilot":
            environment = development_environment(root / item["cwd"])
            temporary = root / ".agent-local" / f"pytest-filepilot-{os.getpid()}"
            command[-1] = f"--basetemp={temporary}"
        result = run(command, root / item["cwd"], check=False, environment=environment)
        status = "PASS" if result.returncode == 0 else "FAIL"
        results.append({"name": item["name"], "status": status, "returncode": result.returncode, "setup": setup_output, "stdout": result.stdout[-4000:], "stderr": result.stderr[-4000:]})
        failed |= result.returncode != 0
    print_value({"platform": os_name(), "results": results}, args.json)
    return 1 if failed else 0


def command_cycle(root: Path, args) -> int:
    """Describe el ciclo previsto sin iniciar agentes ni conceder escrituras."""
    if args.max_cycles < 1:
        raise RouterError("--max-cycles debe ser positivo.")
    ensure_expected_remote(root)
    load_state(root)
    payload = {
        "dry_run": True,
        "enabled": False,
        "max_cycles_requested": args.max_cycles,
        "documents": list(SHARED_FILES),
        "reason": (
            "El ciclo real permanece deshabilitado hasta reutilizar los controles del puente: "
            "tarea autorizada, rutas editables, modelo y esfuerzo acreditados, rondas, presupuesto, "
            "consumo, revisión del diff y aprobación del coordinador."
        ),
        "command": "tools/puente_agentes/puente.py",
    }
    if not args.dry_run:
        raise RouterError(payload["reason"])
    print_value(payload, args.json)
    return 0


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
    state.update(active_branch=current, last_platform=os_name(), status="IN_PROGRESS",
                 next_action=args.next_action, blocked_reason=None)
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
    cycle.add_argument("--max-cycles", type=int, default=3)
    cycle.add_argument("--dry-run", action="store_true")
    cycle.add_argument("--json", action="store_true")
    checkpoint = commands.add_parser("checkpoint")
    checkpoint.add_argument("--next-action", required=True)
    checkpoint.add_argument("--message", default="chore: guarda checkpoint de agentes")
    checkpoint.add_argument("--json", action="store_true")
    return result


def main(argv: list[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="backslashreplace")
    args = parser().parse_args(argv)
    try:
        root = find_root(args.repo)
        return globals()[f"command_{args.command}"](root, args)
    except (RouterError, OSError, subprocess.SubprocessError, json.JSONDecodeError) as error:
        print(f"NEEDS_HUMAN: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
