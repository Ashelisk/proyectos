"""Construye y verifica los artefactos públicos de FilePilot."""

from __future__ import annotations

import argparse
import hashlib
import os
from pathlib import Path
import re
import stat
import subprocess
import sys
import tarfile
import tempfile
import tomllib
import zipfile


PRODUCT_ROOT = Path(__file__).resolve().parents[1]
REPOSITORY_ROOT = PRODUCT_ROOT.parents[1]
TAG_PATTERN = re.compile(r"v(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)")
PLATFORMS = {"windows": ("windows-x64.zip", "filepilot.exe"),
             "linux": ("linux-x86_64.tar.gz", "filepilot")}
DOCUMENTS = {"README.md", "LICENSE"}


class ReleaseError(RuntimeError):
    """Impide generar o publicar un artefacto que incumple la spec."""


def project_version() -> str:
    metadata = tomllib.loads((PRODUCT_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    version = metadata["project"]["version"]
    source = (PRODUCT_ROOT / "filepilot" / "__init__.py").read_text(encoding="utf-8")
    match = re.search(r'^__version__\s*=\s*["\']([^"\']+)["\']', source, re.MULTILINE)
    if not match or match.group(1) != version:
        raise ReleaseError("La versión del paquete y filepilot.__version__ no coinciden.")
    return version


def validate_tag(tag: str) -> str:
    match = TAG_PATTERN.fullmatch(tag)
    if not match:
        raise ReleaseError("La etiqueta debe seguir el formato vX.Y.Z sin ceros iniciales.")
    version = ".".join(match.groups())
    if version != project_version():
        raise ReleaseError(f"La etiqueta {tag} no coincide con la versión {project_version()}.")
    return version


def artifact_name(platform_name: str, version: str | None = None) -> str:
    try:
        suffix = PLATFORMS[platform_name][0]
    except KeyError as error:
        raise ReleaseError(f"Plataforma no admitida: {platform_name}") from error
    return f"filepilot-v{version or project_version()}-{suffix}"


def allowed_entries(platform_name: str) -> set[str]:
    try:
        executable = PLATFORMS[platform_name][1]
    except KeyError as error:
        raise ReleaseError(f"Plataforma no admitida: {platform_name}") from error
    return DOCUMENTS | {executable}


def package_archive(platform_name: str, executable: Path, output: Path) -> Path:
    if not executable.is_file():
        raise ReleaseError(f"No existe el ejecutable: {executable}")
    output.mkdir(parents=True, exist_ok=True)
    destination = output / artifact_name(platform_name)
    executable_name = PLATFORMS[platform_name][1]
    sources = {
        executable_name: executable,
        "README.md": PRODUCT_ROOT / "README_USUARIO.md",
        "LICENSE": REPOSITORY_ROOT / "LICENSE",
    }
    if platform_name == "windows":
        with zipfile.ZipFile(destination, "w", zipfile.ZIP_DEFLATED) as archive:
            for name, source in sources.items():
                archive.write(source, name)
    else:
        with tarfile.open(destination, "w:gz") as archive:
            for name, source in sources.items():
                info = archive.gettarinfo(str(source), name)
                info.mode = 0o755 if name == executable_name else 0o644
                with source.open("rb") as handle:
                    archive.addfile(info, handle)
    verify_archive(platform_name, destination)
    return destination


def verify_archive(platform_name: str, archive_path: Path) -> None:
    if archive_path.name != artifact_name(platform_name):
        raise ReleaseError(f"Nombre de artefacto incorrecto: {archive_path.name}")
    expected = allowed_entries(platform_name)
    if platform_name == "windows":
        with zipfile.ZipFile(archive_path) as archive:
            actual = set(archive.namelist())
    else:
        with tarfile.open(archive_path, "r:gz") as archive:
            members = archive.getmembers()
            actual = {member.name for member in members if member.isfile()}
            executable = next((member for member in members if member.name == "filepilot"), None)
            if executable is None or not executable.mode & stat.S_IXUSR:
                raise ReleaseError("El ejecutable Linux no conserva permiso de ejecución.")
    if actual != expected:
        raise ReleaseError(f"Contenido no permitido: esperado {sorted(expected)}, recibido {sorted(actual)}")


def verify_wheel(wheel_path: Path) -> None:
    expected_name = f"filepilot-{project_version()}-py3-none-any.whl"
    if wheel_path.name != expected_name:
        raise ReleaseError(f"Nombre de wheel incorrecto: {wheel_path.name}")
    with zipfile.ZipFile(wheel_path) as wheel:
        names = wheel.namelist()
        metadata_names = [name for name in names if name.endswith(".dist-info/METADATA")]
        entry_names = [name for name in names if name.endswith(".dist-info/entry_points.txt")]
        if len(metadata_names) != 1 or len(entry_names) != 1:
            raise ReleaseError("El wheel no contiene metadatos o entradas únicos.")
        metadata = wheel.read(metadata_names[0]).decode("utf-8")
        runtime = [line for line in metadata.splitlines()
                   if line.startswith("Requires-Dist:") and "extra ==" not in line]
        entries = wheel.read(entry_names[0]).decode("utf-8")
        if runtime:
            raise ReleaseError(f"El wheel declara dependencias de ejecución: {runtime}")
        if "filepilot = filepilot.cli:main" not in entries:
            raise ReleaseError("El wheel no declara la orden filepilot.")
        forbidden = ("tests/", "specs/", "tools/", "agent_router", "puente_agentes")
        if any(any(part in name for part in forbidden) for name in names):
            raise ReleaseError("El wheel contiene material ajeno a la aplicación.")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def release_files(directory: Path) -> list[Path]:
    version = project_version()
    expected = [
        directory / artifact_name("linux", version),
        directory / artifact_name("windows", version),
        directory / f"filepilot-{version}-py3-none-any.whl",
    ]
    missing = [path.name for path in expected if not path.is_file()]
    if missing:
        raise ReleaseError(f"Faltan artefactos: {', '.join(missing)}")
    extras = {path.name for path in directory.iterdir() if path.is_file()} - {path.name for path in expected} - {"SHA256SUMS.txt"}
    if extras:
        raise ReleaseError(f"Hay artefactos adicionales: {', '.join(sorted(extras))}")
    return expected


def write_checksums(directory: Path) -> Path:
    destination = directory / "SHA256SUMS.txt"
    lines = [f"{sha256(path)}  {path.name}" for path in sorted(release_files(directory))]
    destination.write_text("\n".join(lines) + "\n", encoding="ascii")
    verify_checksums(directory)
    return destination


def verify_checksums(directory: Path) -> None:
    checksum_path = directory / "SHA256SUMS.txt"
    try:
        lines = checksum_path.read_text(encoding="ascii").splitlines()
    except OSError as error:
        raise ReleaseError(f"No se pueden leer las sumas: {error}") from error
    expected_files = {path.name: path for path in release_files(directory)}
    parsed: dict[str, str] = {}
    for line in lines:
        match = re.fullmatch(r"([0-9a-f]{64})  ([^/\\]+)", line)
        if not match or match.group(2) in parsed:
            raise ReleaseError("SHA256SUMS.txt tiene un formato inválido.")
        parsed[match.group(2)] = match.group(1)
    if set(parsed) != set(expected_files):
        raise ReleaseError("SHA256SUMS.txt no enumera exactamente los tres artefactos.")
    for name, path in expected_files.items():
        if sha256(path) != parsed[name]:
            raise ReleaseError(f"La suma no coincide para {name}.")


def tree_snapshot(root: Path) -> dict[str, tuple[int, int]]:
    return {str(path.relative_to(root)): (path.stat().st_size, path.stat().st_mtime_ns)
            for path in root.rglob("*") if path.is_file()}


def run_executable(executable: Path, arguments: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    environment = os.environ.copy()
    environment.pop("PYTHONHOME", None)
    environment.pop("PYTHONPATH", None)
    environment["PATH"] = ""
    return subprocess.run(
        [str(executable.resolve()), *arguments], cwd=cwd, env=environment,
        text=True, encoding="utf-8", errors="replace", capture_output=True,
        timeout=60, check=False,
    )


def verify_executable(executable: Path) -> None:
    if not executable.is_file():
        raise ReleaseError(f"No existe el ejecutable: {executable}")
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        data = root / "entrada"
        data.mkdir()
        (data / "foto.JPG").write_bytes(b"imagen")
        (data / "notas.txt").write_text("texto", encoding="utf-8")
        before = tree_snapshot(data)
        cases = [(["--help"], 0), ([], 1), (["analizar", str(root / "ausente")], 2),
                 (["analizar", str(data)], 0)]
        for arguments, expected in cases:
            result = run_executable(executable, arguments, root)
            if result.returncode != expected:
                detail = (result.stderr or result.stdout)[-1000:]
                raise ReleaseError(f"Falló la prueba {arguments}: {result.returncode}, {detail}")
        if tree_snapshot(data) != before:
            raise ReleaseError("El ejecutable modificó la carpeta analizada.")


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    commands = result.add_subparsers(dest="command", required=True)
    version = commands.add_parser("validar-version")
    version.add_argument("--tag", required=True)
    package = commands.add_parser("empaquetar")
    package.add_argument("--plataforma", choices=sorted(PLATFORMS), required=True)
    package.add_argument("--ejecutable", type=Path, required=True)
    package.add_argument("--salida", type=Path, required=True)
    archive = commands.add_parser("verificar-archivo")
    archive.add_argument("--plataforma", choices=sorted(PLATFORMS), required=True)
    archive.add_argument("--archivo", type=Path, required=True)
    executable = commands.add_parser("verificar-ejecutable")
    executable.add_argument("--ejecutable", type=Path, required=True)
    wheel = commands.add_parser("verificar-wheel")
    wheel.add_argument("--archivo", type=Path, required=True)
    for name in ("sumas", "verificar-sumas"):
        child = commands.add_parser(name)
        child.add_argument("--directorio", type=Path, required=True)
    return result


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        if args.command == "validar-version":
            value = validate_tag(args.tag)
        elif args.command == "empaquetar":
            value = package_archive(args.plataforma, args.ejecutable, args.salida)
        elif args.command == "verificar-archivo":
            verify_archive(args.plataforma, args.archivo)
            value = args.archivo
        elif args.command == "verificar-ejecutable":
            verify_executable(args.ejecutable)
            value = args.ejecutable
        elif args.command == "verificar-wheel":
            verify_wheel(args.archivo)
            value = args.archivo
        elif args.command == "sumas":
            value = write_checksums(args.directorio)
        else:
            verify_checksums(args.directorio)
            value = args.directorio / "SHA256SUMS.txt"
        print(value)
        return 0
    except (ReleaseError, OSError, subprocess.SubprocessError, zipfile.BadZipFile,
            tarfile.TarError, KeyError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
