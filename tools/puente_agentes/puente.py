"""Puente local entre un coordinador y Claude Code; sin dependencias externas."""

import argparse
from contextlib import contextmanager
import hashlib
import json
import math
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import uuid


class BridgeError(Exception):
    """Fallo controlado que impide continuar o aprobar una entrega."""


SCHEMA = {
    "type": "object",
    "properties": {
        "estado": {"type": "string", "enum": ["entregado", "requiere_decision", "bloqueado"]},
        "resumen": {"type": "string"},
        **{name: {"type": "array", "items": {"type": "string"}}
           for name in ("cambios", "pruebas", "preguntas")},
    },
    "required": ["estado", "resumen", "cambios", "pruebas", "preguntas"],
    "additionalProperties": False,
}
PROTECTED = {".git", ".claude", ".agents", ".codex", "skills", "specs"}
PROTECTED_FILES = {"AGENTS.md", "CLAUDE.md", "constitution.md"}
ROUNDS = 3
TIMEOUT = 600
BUDGET = 2.0
DEFAULT_MODEL = "claude-opus-5"
DEFAULT_EFFORT = "xhigh"
EFFORTS = ("low", "medium", "high", "xhigh", "max")


def git(repo, *args):
    result = subprocess.run(
        ["git", "-C", str(repo), *args], capture_output=True, timeout=30,
    )
    if result.returncode:
        raise BridgeError(result.stderr.decode("utf-8", errors="replace").strip())
    return result.stdout


def write_json(path, value):
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def run_dir(repo, name):
    if not re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9_-]{0,63}", name):
        raise BridgeError("Identificador inválido: usa letras, números, guion o guion bajo.")
    root = Path(repo).resolve()
    parent = root / ".sdd-check" / "puente"
    if not parent.resolve().is_relative_to(root):
        raise BridgeError("El almacenamiento temporal sale del repositorio.")
    directory = parent / name
    if not directory.resolve().is_relative_to(root):
        raise BridgeError("El encargo sale del repositorio.")
    return directory


def load_run(repo, name):
    directory = run_dir(repo, name)
    state = json.loads((directory / "estado.json").read_text(encoding="utf-8"))
    expected = directory / "worktree"
    if Path(state["repo"]) != Path(repo).resolve() or Path(state["worktree"]) != expected:
        raise BridgeError("Las rutas del estado no corresponden a este encargo.")
    if expected.is_symlink() or expected.resolve() != expected:
        raise BridgeError("La copia de trabajo ha sido redirigida.")
    return directory, state


@contextmanager
def locked(directory):
    try:
        descriptor = os.open(directory / "lock", os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as error:
        raise BridgeError("El encargo está ocupado; no se retira un bloqueo automáticamente.") from error
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(str(os.getpid()))
        yield
    finally:
        (directory / "lock").unlink()


def checked_path(repo, value, edit=False):
    path = Path(value)
    if (not value or path.is_absolute() or ".." in path.parts
            or any(char in value for char in "*?[]()!\n\r") or path == Path(".")):
        raise BridgeError(f"Ruta relativa no válida: {value}")
    target = (repo / path).resolve()
    if not target.is_relative_to(repo) or not target.exists():
        raise BridgeError(f"Ruta ausente o fuera del repositorio: {value}")
    if edit and (any(part in PROTECTED for part in path.parts)
                 or path.name in PROTECTED_FILES or path.name.startswith(".env")):
        raise BridgeError(f"No se permite editar instrucciones, requisitos o secretos: {value}")
    return path.as_posix()


def fingerprint(worktree):
    digest = hashlib.sha256()
    digest.update(git(worktree, "rev-parse", "HEAD"))
    digest.update(git(worktree, "diff", "--binary", "HEAD", "--"))
    for raw in git(worktree, "ls-files", "--others", "--exclude-standard", "-z").split(b"\0"):
        if raw:
            path = worktree / os.fsdecode(raw)
            if path.is_symlink() or not path.resolve().is_relative_to(worktree):
                raise BridgeError("Un archivo nuevo redirige fuera de la copia de trabajo.")
            digest.update(raw + b"\0" + path.read_bytes())
    return digest.hexdigest()


def changed_paths(worktree):
    tracked = git(worktree, "diff", "--name-only", "--no-renames", "-z", "HEAD", "--")
    untracked = git(worktree, "ls-files", "--others", "--exclude-standard", "-z")
    return [os.fsdecode(raw) for raw in (tracked + untracked).split(b"\0") if raw]


def allowed_change(path, edits):
    return any(path == entry["ruta"] or
               (entry["directorio"] and path.startswith(entry["ruta"] + "/")) for entry in edits)


def init_run(repo, name, task, context, edits, rounds=ROUNDS, timeout=TIMEOUT, budget=BUDGET):
    repo = Path(repo).resolve()
    if not task.strip() or rounds < 1 or timeout < 1 or not math.isfinite(budget) or budget <= 0:
        raise BridgeError("Tarea y límites deben tener valores válidos y positivos.")
    if Path(os.fsdecode(git(repo, "rev-parse", "--show-toplevel")).strip()).resolve() != repo:
        raise BridgeError("Indica la raíz del repositorio.")
    contexts = [checked_path(repo, path) for path in context]
    permissions = [{"ruta": checked_path(repo, path, edit=True),
                    "directorio": (repo / path).is_dir()} for path in edits]
    directory = run_dir(repo, name)
    check = subprocess.run(["git", "-C", str(repo), "check-ignore", "-q",
                            ".sdd-check/puente/prueba"], capture_output=True)
    if check.returncode:
        raise BridgeError(".sdd-check/ debe estar excluido de Git antes de crear encargos.")
    if directory.exists():
        raise BridgeError("El identificador ya existe; consulta su estado o usa otro.")
    base = os.fsdecode(git(repo, "rev-parse", "HEAD")).strip()
    # El worktree parte de HEAD: no se trasladan cambios sin commit.
    for path in contexts + [entry["ruta"] for entry in permissions]:
        git(repo, "cat-file", "-e", f"{base}:{path}")
    directory.mkdir(parents=True)
    worktree = directory / "worktree"
    git(repo, "worktree", "add", "--detach", str(worktree), base)
    state = {
        "id": name, "tarea": task, "repo": str(repo), "worktree": str(worktree),
        "base": base, "contexto": contexts, "edicion": permissions,
        "session_id": str(uuid.uuid4()), "envios": 0, "max_envios": rounds,
        "timeout": timeout, "presupuesto_usd": budget, "coste_estimado_usd": 0.0,
        "estado": "listo", "huella": fingerprint(worktree),
        "perfil": {"modelo": DEFAULT_MODEL, "esfuerzo": DEFAULT_EFFORT, "motivo": "Perfil base"},
        "correcciones_fallidas": 0,
    }
    write_json(directory / "estado.json", state)
    return state


def claude_arguments(state):
    args = [
        "claude", "-p", "--output-format", "json", "--json-schema", json.dumps(SCHEMA),
        "--model", state["perfil"]["modelo"], "--effort", state["perfil"]["esfuerzo"],
        "--restricted", "--permission-mode", "dontAsk", "--setting-sources", "",
        "--strict-mcp-config", "--mcp-config", '{"mcpServers":{}}', "--no-chrome",
        "--tools", "Read,Grep,Glob,Edit,Write" if state["edicion"] else "Read,Grep,Glob",
        "--allowedTools", "Read", "Grep", "Glob",
    ]
    args += ["Edit(/" + entry["ruta"] + ("/**" if entry["directorio"] else "") + ")"
             for entry in state["edicion"]]
    deny = ["Read(//**/.env)", "Read(//**/.env.*)", "Read(//**/.git)",
            "Read(//**/.git/**)", "Edit(//**/AGENTS.md)", "Edit(//**/CLAUDE.md)",
            "Edit(//**/constitution.md)", "Edit(//**/specs/**)", "Edit(//**/skills/**)",
            "Edit(//**/.claude/**)", "Edit(//**/.agents/**)", "Edit(//**/.codex/**)"]
    deny += ["Edit(/" + path + ")" for path in state["contexto"]]
    args += ["--disallowedTools", *deny]
    args += ["--max-budget-usd", str(max(0, state["presupuesto_usd"] - state["coste_estimado_usd"]))]
    args += ["--session-id" if state["envios"] == 1 else "--resume", state["session_id"]]
    protocol = Path(__file__).with_name("protocolo.md").read_text(encoding="utf-8")
    args += ["--append-system-prompt", protocol]
    return args


def run_claude(args, cwd, message, timeout):
    executable = shutil.which(args[0])
    if not executable:
        raise BridgeError("Claude Code no está disponible en PATH.")
    args = [executable, *args[1:]]
    environment = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    if "--effort" in args:
        # Esta variable prevalece sobre el flag; se fija solo en el proceso hijo.
        environment["CLAUDE_CODE_EFFORT_LEVEL"] = args[args.index("--effort") + 1]
    process = subprocess.Popen(
        args, cwd=cwd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True, encoding="utf-8", env=environment,
        creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
        start_new_session=os.name != "nt",
    )
    try:
        output, error = process.communicate(message, timeout=timeout)
    except (subprocess.TimeoutExpired, KeyboardInterrupt) as problem:
        # Solo se termina el árbol del proceso creado para este envío.
        if os.name == "nt":
            subprocess.run(["taskkill", "/PID", str(process.pid), "/T", "/F"], capture_output=True)
        else:
            import signal
            os.killpg(process.pid, signal.SIGKILL)
        process.communicate()
        raise BridgeError("Envío interrumpido o tiempo agotado; revisar la copia antes de reintentar.") from problem
    try:
        response = json.loads(output)
    except json.JSONDecodeError as problem:
        if process.returncode:
            raise BridgeError(f"Claude terminó con código {process.returncode}: {(error or output)[-2000:]}") from problem
        raise BridgeError("Claude no devolvió un resultado JSON válido.") from problem
    if isinstance(response, dict):
        # Un error del proceso puede traer un JSON válido con consumo facturable.
        response["_bridge_returncode"] = process.returncode
    elif process.returncode:
        raise BridgeError(f"Claude terminó con código {process.returncode}, sin un resultado válido.")
    return response


def response_cost(response, session_id):
    if not isinstance(response, dict) or response.get("session_id") != session_id:
        raise BridgeError("La respuesta no acredita consumo de esta sesión.")
    cost = response.get("total_cost_usd")
    if isinstance(cost, bool) or not isinstance(cost, (int, float)) or not math.isfinite(cost) or cost < 0:
        raise BridgeError("Falta una estimación válida del consumo.")
    return cost


def validate_response(response, session_id):
    if isinstance(response, dict) and response.get("_bridge_returncode"):
        raise BridgeError(f"Claude terminó con código {response['_bridge_returncode']}: "
                          f"{str(response.get('result', 'Sin entrega válida'))[-1000:]}")
    if (not isinstance(response, dict) or response.get("type") != "result"
            or response.get("subtype") != "success" or response.get("is_error", False)):
        raise BridgeError("La ejecución no produjo una entrega válida.")
    if response.get("session_id") != session_id:
        raise BridgeError("La respuesta pertenece a otra sesión.")
    result = response.get("structured_output")
    if not isinstance(result, dict) or set(result) != set(SCHEMA["required"]):
        raise BridgeError("La respuesta no cumple el esquema del puente.")
    if result["estado"] not in SCHEMA["properties"]["estado"]["enum"] or not isinstance(result["resumen"], str):
        raise BridgeError("Estado o resumen no válidos.")
    for key in ("cambios", "pruebas", "preguntas"):
        if not isinstance(result[key], list) or not all(isinstance(item, str) for item in result[key]):
            raise BridgeError(f"Campo no válido: {key}")
    return result


def send_run(repo, name, message, model=None, effort=None, reason=None):
    directory, _ = load_run(repo, name)
    with locked(directory):
        _, state = load_run(repo, name)
        if state["estado"] not in ("listo", "corregir"):
            raise BridgeError("El encargo necesita revisión o está detenido; no se envía otra orden.")
        if state["envios"] >= state["max_envios"]:
            raise BridgeError("Límite de envíos alcanzado; no se declara terminada la tarea.")
        if state["coste_estimado_usd"] >= state["presupuesto_usd"]:
            raise BridgeError("Presupuesto estimado agotado.")
        if not message.strip():
            raise BridgeError("El encargo no puede estar vacío.")
        worktree = Path(state["worktree"])
        if fingerprint(worktree) != state["huella"]:
            raise BridgeError("La copia cambió fuera del ciclo; revisa el estado antes de continuar.")
        previous = state.get("perfil", {"modelo": DEFAULT_MODEL, "esfuerzo": DEFAULT_EFFORT,
                                        "motivo": "Perfil base"})
        profile = {"modelo": model or previous["modelo"], "esfuerzo": effort or previous["esfuerzo"],
                   "motivo": reason or previous["motivo"]}
        if (model is None and effort is None and state.get("correcciones_fallidas", 0) >= 2
                and profile["esfuerzo"] != "max"):
            profile.update(esfuerzo="max", motivo="Dos correcciones consecutivas verificadas como fallidas")
        elif (((profile["modelo"], profile["esfuerzo"]) != (previous["modelo"], previous["esfuerzo"])
               or (state.get("correcciones_fallidas", 0) >= 2 and profile["esfuerzo"] != "max"))
              and not (reason or "").strip()):
            raise BridgeError("Cambiar el perfil o evitar la escalada requiere un motivo técnico.")
        if not re.fullmatch(r"claude-[a-z0-9-]+", profile["modelo"]) or profile["esfuerzo"] not in EFFORTS:
            raise BridgeError("Indica un modelo Claude con identificador completo y un esfuerzo admitido.")
        state["perfil"] = profile
        state["es_correccion"] = state["estado"] == "corregir"
        state["envios"] += 1
        state["estado"] = "ejecutando"
        state["consumo_verificado"] = False
        write_json(directory / f'perfil-{state["envios"]}.json', profile)
        write_json(directory / "estado.json", state)
        request = ("Tarea autorizada: " + state["tarea"] + "\n"
                   "Lee estas instrucciones y documentos antes de actuar: " +
                   ", ".join(state["contexto"]) + "\n"
                   "Rutas editables: " + json.dumps(state["edicion"], ensure_ascii=False) + "\n"
                   "Mensaje del coordinador:\n" + message)
        (directory / f'envio-{state["envios"]}.txt').write_text(request, encoding="utf-8")
        try:
            response = run_claude(claude_arguments(state), worktree, request, state["timeout"])
            write_json(directory / f'respuesta-{state["envios"]}.json', response)
            state["coste_estimado_usd"] += response_cost(response, state["session_id"])
            state["consumo_verificado"] = True
            result = validate_response(response, state["session_id"])
            state["respuesta"] = result
            usage = response.get("modelUsage", {})
            if not isinstance(usage, dict) or profile["modelo"] not in usage:
                raise BridgeError("El CLI no acredita el modelo solicitado; no se acepta una sustitución silenciosa.")
            state["modelos_reportados"] = sorted(usage)
            if os.fsdecode(git(worktree, "rev-parse", "HEAD")).strip() != state["base"]:
                raise BridgeError("El programador modificó HEAD; se requiere revisión manual.")
            outside = [path for path in changed_paths(worktree) if not allowed_change(path, state["edicion"])]
            if outside:
                raise BridgeError("Cambios fuera del alcance: " + ", ".join(outside))
            state["estado"] = {"entregado": "revision", "requiere_decision": "decision",
                               "bloqueado": "bloqueado"}[result["estado"]]
            if result["preguntas"]:
                state["estado"] = "decision"
            if response.get("permission_denials"):
                state["estado"] = "bloqueado"
                state["aviso"] = "Se denegaron herramientas; no se amplían permisos automáticamente."
            state["huella"] = fingerprint(worktree)
        except (BridgeError, OSError, ValueError, subprocess.SubprocessError) as problem:
            state["estado"] = "error"
            state["error"] = str(problem)
        write_json(directory / "estado.json", state)
        return state


def review_run(repo, name, expected, verdict, notes, failed_correction=False):
    directory, _ = load_run(repo, name)
    with locked(directory):
        _, state = load_run(repo, name)
        if state["estado"] not in ("revision", "decision", "bloqueado"):
            raise BridgeError("No hay una entrega que pueda revisarse.")
        if verdict == "aprobar" and state["estado"] != "revision":
            raise BridgeError("No puede aprobarse una decisión pendiente ni un bloqueo.")
        if not notes.strip() or verdict not in ("aprobar", "corregir", "consultar"):
            raise BridgeError("La revisión necesita un veredicto y evidencia o una pregunta concreta.")
        if expected != state["huella"] or fingerprint(Path(state["worktree"])) != expected:
            raise BridgeError("La revisión no corresponde a la versión actual de los archivos.")
        if failed_correction and (verdict != "corregir" or not state.get("es_correccion")
                                  or state["estado"] != "revision"):
            raise BridgeError("Solo puede marcarse fallida una corrección ya ejecutada, no la entrega inicial.")
        state["correcciones_fallidas"] = state.get("correcciones_fallidas", 0) + 1 if failed_correction else 0
        state["revision"] = {"veredicto": verdict, "evidencia": notes, "huella": expected,
                             "correccion_fallida": failed_correction}
        state["estado"] = {"aprobar": "aprobado", "corregir": "corregir", "consultar": "decision"}[verdict]
        write_json(directory / f'revision-{state["envios"]}.json', state["revision"])
        write_json(directory / "estado.json", state)
        return state


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path.cwd(), help="Raíz Git; por defecto, carpeta actual.")
    commands = parser.add_subparsers(dest="command", required=True)
    create = commands.add_parser("iniciar", help="Crear una tarea aislada; solo lectura por defecto.")
    create.add_argument("id")
    create.add_argument("--tarea", required=True)
    create.add_argument("--contexto", action="append", default=[])
    create.add_argument("--editar", action="append", default=[])
    create.add_argument("--rondas", type=int, default=ROUNDS)
    create.add_argument("--segundos", type=int, default=TIMEOUT)
    create.add_argument("--presupuesto-usd", type=float, default=BUDGET)
    send = commands.add_parser("enviar", help="Enviar un encargo UTF-8 y esperar su resultado.")
    send.add_argument("id")
    send.add_argument("--mensaje", type=Path, required=True)
    send.add_argument("--modelo", help="Identificador completo; cambiarlo requiere --motivo.")
    send.add_argument("--esfuerzo", choices=EFFORTS, help="Cambiar el nivel requiere --motivo.")
    send.add_argument("--motivo", help="Justificación por exigencia de la tarea o correcciones fallidas.")
    review = commands.add_parser("revisar", help="Registrar el veredicto del coordinador.")
    review.add_argument("id")
    review.add_argument("--huella", required=True)
    review.add_argument("--veredicto", choices=("aprobar", "corregir", "consultar"), required=True)
    review.add_argument("--evidencia", type=Path, required=True)
    review.add_argument("--correccion-fallida", action="store_true",
                        help="La corrección ejecutada sigue incumpliendo el requisito; adjuntar evidencia.")
    status = commands.add_parser("estado", help="Consultar una tarea sin ejecutarla.")
    status.add_argument("id")
    options = parser.parse_args()
    try:
        if options.command == "iniciar":
            result = init_run(options.repo, options.id, options.tarea, options.contexto, options.editar,
                              options.rondas, options.segundos, options.presupuesto_usd)
        elif options.command == "enviar":
            result = send_run(options.repo, options.id, options.mensaje.read_text(encoding="utf-8"),
                              options.modelo, options.esfuerzo, options.motivo)
        elif options.command == "revisar":
            result = review_run(options.repo, options.id, options.huella, options.veredicto,
                                options.evidencia.read_text(encoding="utf-8"), options.correccion_fallida)
        else:
            result = load_run(options.repo, options.id)[1]
        print(json.dumps(result, ensure_ascii=True, indent=2))
        return 2 if result["estado"] in ("error", "bloqueado", "decision") else 0
    except (BridgeError, OSError, ValueError, subprocess.SubprocessError) as problem:
        print(f"puente: {problem}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
