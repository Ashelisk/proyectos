import argparse
from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

import router


def call(args, cwd):
    return subprocess.run(
        ["git", "-C", str(cwd), *args], check=True, text=True,
        encoding="utf-8", capture_output=True,
    ).stdout.strip()


class RouterTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / "repo"
        self.root.mkdir()
        call(["init", "-b", "main"], self.root)
        call(["config", "user.email", "router@example.invalid"], self.root)
        call(["config", "user.name", "Router Tests"], self.root)
        (self.root / "tracked.txt").write_text("base\n", encoding="utf-8")
        (self.root / ".agents").mkdir()
        self.state = {
            "$schema": "state.schema.json", "task_id": "test-task", "active_branch": "main",
            "verified_commit": None, "last_platform": "linux", "status": "IN_PROGRESS", "cycle": 0,
            "tests": {name: {"status": "PENDING", "command": None, "summary": ""} for name in ("windows", "linux", "macos", "ci")},
            "next_action": "probar", "blocked_reason": None, "updated_at": "2026-09-01T00:00:00Z",
        }
        (self.root / ".agents" / "state.json").write_text(json.dumps(self.state), encoding="utf-8")
        (self.root / "TASK.md").write_text(
            "# Tarea\n\n- **Estado:** `IN_PROGRESS`\n\n## Resultados por plataforma\n\n- **Linux:** pendiente\n- **Windows:** pendiente\n- **Macos:** pendiente\n\n## Siguiente acción exacta\n\nProbar.\n",
            encoding="utf-8",
        )
        call(["add", "."], self.root)
        call(["commit", "-m", "base"], self.root)
        call(["remote", "add", "origin", "https://github.com/Ashelisk/proyectos.git"], self.root)

    def tearDown(self):
        self.temp.cleanup()

    def test_descubre_raiz_y_normaliza_remotos_https_y_ssh(self):
        child = self.root / "nested"
        child.mkdir()
        self.assertEqual(router.find_root(child), self.root.resolve())
        self.assertEqual(router.normalize_remote("git@github.com:Ashelisk/proyectos.git"), router.EXPECTED_REMOTE.casefold())
        self.assertEqual(router.normalize_remote("https://github.com/Ashelisk/proyectos.git"), router.EXPECTED_REMOTE.casefold())

    def test_rechaza_remoto_inesperado_y_head_separado(self):
        call(["remote", "set-url", "origin", "https://github.com/otra/cosa.git"], self.root)
        with self.assertRaises(router.RouterError):
            router.ensure_expected_remote(self.root)
        call(["remote", "set-url", "origin", "https://github.com/Ashelisk/proyectos.git"], self.root)
        call(["checkout", "--detach"], self.root)
        with self.assertRaises(router.RouterError):
            router.branch(self.root)

    def test_estado_detecta_archivos_seguidos_y_no_seguidos(self):
        self.assertEqual(router.porcelain(self.root), [])
        (self.root / "tracked.txt").write_text("cambio\n", encoding="utf-8")
        (self.root / "nuevo.txt").write_text("nuevo\n", encoding="utf-8")
        changes = router.porcelain(self.root)
        self.assertTrue(any("tracked.txt" in line for line in changes))
        self.assertTrue(any("nuevo.txt" in line for line in changes))

    def test_relacion_equal_ahead_behind_y_diverged(self):
        base = call(["rev-parse", "HEAD"], self.root)
        call(["update-ref", "refs/remotes/origin/main", base], self.root)
        self.assertEqual(router.relation(self.root, "origin/main")["state"], "equal")
        (self.root / "tracked.txt").write_text("local\n", encoding="utf-8")
        call(["commit", "-am", "local"], self.root)
        self.assertEqual(router.relation(self.root, "origin/main")["state"], "ahead")
        call(["checkout", "--detach", base], self.root)
        (self.root / "tracked.txt").write_text("remote\n", encoding="utf-8")
        call(["commit", "-am", "remote"], self.root)
        remote = call(["rev-parse", "HEAD"], self.root)
        call(["update-ref", "refs/remotes/origin/main", remote], self.root)
        call(["checkout", "main"], self.root)
        self.assertEqual(router.relation(self.root, "origin/main")["state"], "diverged")

    def test_sync_dry_run_es_read_only_y_rechaza_sucio(self):
        before = call(["show-ref"], self.root)
        args = argparse.Namespace(branch=None, dry_run=True, json=True)
        with redirect_stdout(io.StringIO()):
            self.assertEqual(router.command_sync(self.root, args), 0)
        self.assertEqual(call(["show-ref"], self.root), before)
        (self.root / "nuevo.txt").write_text("x", encoding="utf-8")
        with self.assertRaises(router.RouterError):
            router.command_sync(self.root, args)

    def test_comandos_de_prueba_respetan_plataforma(self):
        linux = {item["name"]: item for item in router.test_commands(self.root, "linux")}
        macos = {item["name"]: item for item in router.test_commands(self.root, "macos")}
        self.assertTrue(linux["filepilot"]["applicable"])
        self.assertFalse(macos["filepilot"]["applicable"])
        self.assertEqual(linux["filepilot"]["cwd"], "projects/filepilot")
        self.assertIn("PYTHONPATH", linux["filepilot"]["setup"])
        self.assertIn("--basetemp=<agent-local>", linux["filepilot"]["argv"])

    def test_entorno_de_desarrollo_apunta_al_checkout_actual(self):
        project = self.root / "projects" / "filepilot"
        project.mkdir(parents=True)
        environment = router.development_environment(project)
        self.assertEqual(environment["PYTHONPATH"], str(project.resolve()))
        with self.assertRaises(router.RouterError):
            router.development_environment(self.root / "ausente")

    def test_version_de_modulo_usa_el_interprete_activo(self):
        result = router.module_version("modulo_router_inexistente")
        self.assertFalse(result["available"])
        self.assertIsNotNone(result["version"])

    def test_json_es_imprimible_en_terminales_sin_unicode_completo(self):
        with redirect_stdout(io.StringIO()) as output:
            router.print_value({"detalle": "fallo \ufffd"}, structured=True)
        self.assertIn(r"\ufffd", output.getvalue())

    def test_estado_estricto_y_escritura_utc(self):
        loaded = router.load_state(self.root)
        router.write_state(self.root, loaded)
        written = json.loads((self.root / ".agents" / "state.json").read_text(encoding="utf-8"))
        self.assertRegex(written["updated_at"], r"Z$")
        written["extra"] = True
        (self.root / ".agents" / "state.json").write_text(json.dumps(written), encoding="utf-8")
        with self.assertRaises(router.RouterError):
            router.load_state(self.root)

    def test_estado_rechaza_resultados_y_ciclos_con_tipo_invalido(self):
        for mutation in ("resultado", "ciclo"):
            invalid = json.loads(json.dumps(self.state))
            if mutation == "resultado":
                invalid["tests"]["linux"]["status"] = "DESCONOCIDO"
            else:
                invalid["cycle"] = True
            (self.root / ".agents" / "state.json").write_text(json.dumps(invalid), encoding="utf-8")
            with self.assertRaises(router.RouterError):
                router.load_state(self.root)

    def test_actualiza_tablero_sin_acumular_historial(self):
        router.update_task_board(self.root, "PASS", "linux", "11 pruebas correctas.", "Revisar CI.")
        text = (self.root / "TASK.md").read_text(encoding="utf-8")
        self.assertIn("- **Estado:** `PASS`", text)
        self.assertIn("- **Linux:** `PASS`; 11 pruebas correctas.", text)
        self.assertTrue(text.rstrip().endswith("Revisar CI."))

    def test_estado_ambiguo_no_es_pass(self):
        invalid = json.loads(json.dumps(self.state))
        invalid["status"] = "PASS porque parece correcto"
        (self.root / ".agents" / "state.json").write_text(json.dumps(invalid), encoding="utf-8")
        with self.assertRaises(router.RouterError):
            router.load_state(self.root)

    def test_dry_run_del_ciclo_no_invoca_agentes(self):
        args = argparse.Namespace(max_cycles=3, dry_run=True, json=True)
        with redirect_stdout(io.StringIO()) as output:
            self.assertEqual(router.command_cycle(self.root, args), 0)
        data = json.loads(output.getvalue())
        self.assertFalse(data["enabled"])
        self.assertEqual(data["max_cycles_requested"], 3)
        self.assertIn("puente_agentes", data["command"])

    def test_ciclo_real_permanece_deshabilitado(self):
        args = argparse.Namespace(max_cycles=3, dry_run=False, json=True)
        with self.assertRaises(router.RouterError):
            router.command_cycle(self.root, args)

    def test_checkpoint_rechaza_main_sin_modificar_estado(self):
        before = (self.root / ".agents" / "state.json").read_bytes()
        args = argparse.Namespace(next_action="otro sistema", message="checkpoint", json=True)
        with self.assertRaises(router.RouterError):
            router.command_checkpoint(self.root, args)
        self.assertEqual((self.root / ".agents" / "state.json").read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
