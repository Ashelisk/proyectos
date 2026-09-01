"""Spec 002: reglas de los artefactos públicos de FilePilot."""

import importlib.util
from pathlib import Path
import tarfile
import zipfile

import pytest


RUTA_HELPER = Path(__file__).parents[1] / "tools" / "release.py"
SPEC = importlib.util.spec_from_file_location("filepilot_release", RUTA_HELPER)
release = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(release)


def crear_wheel(ruta: Path, dependencia: str = "pytest>=8; extra == 'dev'") -> None:
    metadata = "\n".join(
        [
            "Metadata-Version: 2.4",
            "Name: filepilot",
            f"Version: {release.project_version()}",
            f"Requires-Dist: {dependencia}",
            "",
        ]
    )
    with zipfile.ZipFile(ruta, "w") as wheel:
        wheel.writestr("filepilot/__init__.py", "")
        wheel.writestr("filepilot-0.1.0.dist-info/METADATA", metadata)
        wheel.writestr(
            "filepilot-0.1.0.dist-info/entry_points.txt",
            "[console_scripts]\nfilepilot = filepilot.cli:main\n",
        )


def test_version_etiqueta_y_nombres() -> None:
    assert release.validate_tag("v0.1.0") == "0.1.0"
    assert release.artifact_name("windows") == "filepilot-v0.1.0-windows-x64.zip"
    assert release.artifact_name("linux") == "filepilot-v0.1.0-linux-x86_64.tar.gz"
    for tag in ("0.1.0", "v00.1.0", "v0.1", "v0.2.0"):
        with pytest.raises(release.ReleaseError):
            release.validate_tag(tag)


def test_zip_windows_solo_contiene_la_aplicacion_y_documentos(tmp_path: Path) -> None:
    executable = tmp_path / "filepilot.exe"
    executable.write_bytes(b"ejecutable")
    archive = release.package_archive("windows", executable, tmp_path / "salida")

    with zipfile.ZipFile(archive) as content:
        assert set(content.namelist()) == {"filepilot.exe", "README.md", "LICENSE"}

    with zipfile.ZipFile(archive, "a") as content:
        content.writestr("tasks.md", "no debe publicarse")
    with pytest.raises(release.ReleaseError):
        release.verify_archive("windows", archive)


def test_tar_linux_conserva_contenido_y_permiso_ejecutable(tmp_path: Path) -> None:
    executable = tmp_path / "filepilot"
    executable.write_bytes(b"ejecutable")
    archive = release.package_archive("linux", executable, tmp_path / "salida")

    with tarfile.open(archive, "r:gz") as content:
        members = {member.name: member for member in content.getmembers()}
    assert set(members) == {"filepilot", "README.md", "LICENSE"}
    assert members["filepilot"].mode & 0o100


def test_wheel_admite_extras_y_rechaza_dependencias_de_ejecucion(tmp_path: Path) -> None:
    wheel = tmp_path / "filepilot-0.1.0-py3-none-any.whl"
    crear_wheel(wheel)
    release.verify_wheel(wheel)

    crear_wheel(wheel, "requests>=2")
    with pytest.raises(release.ReleaseError):
        release.verify_wheel(wheel)


def test_sumas_cubren_exactamente_los_tres_artefactos(tmp_path: Path) -> None:
    (tmp_path / release.artifact_name("windows")).write_bytes(b"windows")
    (tmp_path / release.artifact_name("linux")).write_bytes(b"linux")
    wheel = tmp_path / "filepilot-0.1.0-py3-none-any.whl"
    wheel.write_bytes(b"wheel")

    checksum = release.write_checksums(tmp_path)
    assert len(checksum.read_text(encoding="ascii").splitlines()) == 3
    release.verify_checksums(tmp_path)

    wheel.write_bytes(b"modificado")
    with pytest.raises(release.ReleaseError):
        release.verify_checksums(tmp_path)


def test_sumas_rechazan_artefactos_adicionales(tmp_path: Path) -> None:
    (tmp_path / release.artifact_name("windows")).write_bytes(b"windows")
    (tmp_path / release.artifact_name("linux")).write_bytes(b"linux")
    (tmp_path / "filepilot-0.1.0-py3-none-any.whl").write_bytes(b"wheel")
    (tmp_path / "spec.md").write_text("no debe publicarse", encoding="utf-8")

    with pytest.raises(release.ReleaseError):
        release.write_checksums(tmp_path)
