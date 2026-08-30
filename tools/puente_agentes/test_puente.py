"""Contrato del puente con repositorios desechables y transporte simulado."""

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import puente


class PuenteTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        if Path(self.temp.name).resolve().parent != Path(tempfile.gettempdir()).resolve():
            raise RuntimeError("La carpeta desechable sale de la raíz temporal prevista.")
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name) / "repo"
        self.repo.mkdir()
        self.git("init", "-q")
        self.git("config", "user.email", "prueba@example.invalid")
        self.git("config", "user.name", "Prueba local")
        (self.repo / ".gitignore").write_text(".sdd-check/\n", encoding="utf-8")
        (self.repo / "AGENTS.md").write_text("No modificar requisitos.", encoding="utf-8")
        (self.repo / "src").mkdir()
        (self.repo / "src/app.py").write_text("valor = 1\n", encoding="utf-8")
        self.git("add", ".")
        self.git("commit", "-qm", "Base desechable")

    def git(self, *args):
        return subprocess.check_output(["git", "-C", str(self.repo), *args], text=True).strip()

    def init(self, **kwargs):
        return puente.init_run(self.repo, "caso", "Tarea de prueba", ["AGENTS.md"], [], **kwargs)

    def response(self, args, cwd, message, timeout):
        session = args[args.index("--session-id") + 1] if "--session-id" in args else args[args.index("--resume") + 1]
        return {"type": "result", "subtype": "success", "session_id": session,
                "total_cost_usd": 0.05, "permission_denials": [],
                "modelUsage": {args[args.index("--model") + 1]: {}},
                "structured_output": {"estado": "entregado", "resumen": "Lectura completa",
                                      "cambios": [], "pruebas": [], "preguntas": []}}

    @patch("puente.run_claude")
    def test_aislamiento_continuidad_y_aprobacion(self, transport):
        transport.side_effect = self.response
        initial = self.init()
        self.assertNotEqual(initial["worktree"], str(self.repo))
        first = puente.send_run(self.repo, "caso", "Lee el contexto.")
        self.assertEqual(first["estado"], "revision")
        with self.assertRaises(puente.BridgeError):
            puente.send_run(self.repo, "caso", "No debe adelantarse a la revisión.")
        puente.review_run(self.repo, "caso", first["huella"], "corregir", "Contrastar una segunda vez.")
        second = puente.send_run(self.repo, "caso", "Continúa.")
        self.assertEqual(first["session_id"], second["session_id"])
        self.assertIn("--resume", transport.call_args.args[0])
        result = puente.review_run(self.repo, "caso", second["huella"], "aprobar", "Lectura contrastada.")
        self.assertEqual(result["estado"], "aprobado")
        self.assertEqual((self.repo / "src/app.py").read_text(), "valor = 1\n")
        self.assertEqual(self.git("status", "--porcelain"), "")

    @patch("puente.run_claude")
    def test_la_revision_rechaza_archivos_alterados(self, transport):
        transport.side_effect = self.response
        state = self.init()
        sent = puente.send_run(self.repo, "caso", "Lee.")
        (Path(state["worktree"]) / "src/app.py").write_text("valor = 2\n", encoding="utf-8")
        with self.assertRaises(puente.BridgeError):
            puente.review_run(self.repo, "caso", sent["huella"], "aprobar", "Resultado antiguo.")

    @patch("puente.run_claude")
    def test_cambios_fuera_del_permiso_bloquean(self, transport):
        state = self.init()
        def changed(*args):
            (Path(state["worktree"]) / "src/app.py").write_text("valor = 3\n", encoding="utf-8")
            return self.response(*args)
        transport.side_effect = changed
        result = puente.send_run(self.repo, "caso", "Solo lectura.")
        self.assertEqual(result["estado"], "error")

    @patch("puente.run_claude")
    def test_limite_de_rondas(self, transport):
        transport.side_effect = self.response
        self.init(rounds=1)
        state = puente.send_run(self.repo, "caso", "Lee.")
        puente.review_run(self.repo, "caso", state["huella"], "corregir", "Pendiente.")
        with self.assertRaises(puente.BridgeError):
            puente.send_run(self.repo, "caso", "Segunda ronda.")
        self.assertEqual(transport.call_count, 1)

    @patch("puente.run_claude")
    def test_no_se_aprueba_una_decision_pendiente(self, transport):
        def decision(*args):
            result = self.response(*args)
            result["structured_output"]["estado"] = "requiere_decision"
            result["structured_output"]["preguntas"] = ["Falta una regla."]
            return result
        transport.side_effect = decision
        self.init()
        state = puente.send_run(self.repo, "caso", "Examina.")
        self.assertEqual(state["estado"], "decision")
        with self.assertRaises(puente.BridgeError):
            puente.review_run(self.repo, "caso", state["huella"], "aprobar", "No hay respuesta.")

    @patch("puente.run_claude")
    def test_respuesta_invalida_y_timeout_no_son_entrega(self, transport):
        self.init()
        transport.return_value = {"type": "result", "subtype": "success"}
        self.assertEqual(puente.send_run(self.repo, "caso", "Lee.")["estado"], "error")
        puente.init_run(self.repo, "otro", "Otra tarea", [], [])
        transport.side_effect = puente.BridgeError("Tiempo agotado")
        self.assertEqual(puente.send_run(self.repo, "otro", "Lee.")["estado"], "error")

    @patch("puente.run_claude")
    def test_bloqueo_exclusivo(self, transport):
        state = self.init()
        lock = Path(state["worktree"]).parent / "lock"
        lock.write_text("otro proceso", encoding="utf-8")
        with self.assertRaises(puente.BridgeError):
            puente.send_run(self.repo, "caso", "No debe empezar.")
        transport.assert_not_called()

    def test_rutas_y_nombres_no_escapan_del_repositorio(self):
        for name in ("../fuera", ".", "mal/nombre"):
            with self.assertRaises(puente.BridgeError):
                puente.init_run(self.repo, name, "Prueba", [], [])
        for path in ("../fuera", ".git", "AGENTS.md", "*", "src/../../fuera"):
            with self.assertRaises(puente.BridgeError):
                puente.init_run(self.repo, "ruta", "Prueba", [], [path])

    @patch("puente.run_claude")
    def test_presupuesto_y_herramientas_limitadas(self, transport):
        transport.side_effect = self.response
        puente.init_run(self.repo, "caso", "Prueba", ["AGENTS.md"], ["src"], budget=0.05)
        state = puente.send_run(self.repo, "caso", "Modifica solo src.")
        args = transport.call_args.args[0]
        self.assertIn("--restricted", args)
        self.assertEqual(args[args.index("--permission-mode") + 1], "dontAsk")
        self.assertEqual(args[args.index("--tools") + 1], "Read,Grep,Glob,Edit,Write")
        self.assertIn("Edit(/src/**)", args)
        self.assertNotIn("bypassPermissions", args)
        puente.review_run(self.repo, "caso", state["huella"], "corregir", "Pendiente.")
        with self.assertRaises(puente.BridgeError):
            puente.send_run(self.repo, "caso", "No hay presupuesto.")

    @patch("puente.run_claude")
    def test_identificador_erroneo_y_permisos_denegados(self, transport):
        self.init()
        def wrong(*args):
            result = self.response(*args)
            result["session_id"] = "otra-sesion"
            return result
        transport.side_effect = wrong
        self.assertEqual(puente.send_run(self.repo, "caso", "Lee.")["estado"], "error")
        puente.init_run(self.repo, "denegado", "Prueba", [], [])
        def denied(*args):
            result = self.response(*args)
            result["permission_denials"] = [{"tool_name": "Edit"}]
            return result
        transport.side_effect = denied
        self.assertEqual(puente.send_run(self.repo, "denegado", "Lee.")["estado"], "bloqueado")

    def test_timeout_del_transporte_real(self):
        with self.assertRaisesRegex(puente.BridgeError, "tiempo agotado"):
            puente.run_claude([sys.executable, "-c", "import time; time.sleep(30)"],
                             self.repo, "", 0.1)

    @patch("puente.run_claude")
    def test_opus_extra_explicito_incluso_al_reanudar(self, transport):
        transport.side_effect = self.response
        self.init()
        first = puente.send_run(self.repo, "caso", "Lee.")
        puente.review_run(self.repo, "caso", first["huella"], "corregir", "Amplía la comprobación.")
        second = puente.send_run(self.repo, "caso", "Continúa.")
        for call in transport.call_args_list:
            args = call.args[0]
            self.assertEqual(args[args.index("--model") + 1], "claude-opus-5")
            self.assertEqual(args[args.index("--effort") + 1], "xhigh")
        self.assertEqual(first["session_id"], second["session_id"])

    @patch("puente.run_claude")
    def test_ajuste_requiere_motivo_y_se_conserva(self, transport):
        transport.side_effect = self.response
        self.init()
        with self.assertRaises(puente.BridgeError):
            puente.send_run(self.repo, "caso", "Lee.", effort="medium")
        transport.assert_not_called()
        state = puente.send_run(self.repo, "caso", "Lee.", model="claude-sonnet-5",
                                effort="medium", reason="Lectura mecánica sin cambios de código.")
        self.assertEqual(state["perfil"]["modelo"], "claude-sonnet-5")
        puente.review_run(self.repo, "caso", state["huella"], "corregir", "Comprobación adicional.")
        puente.send_run(self.repo, "caso", "Continúa.")
        args = transport.call_args.args[0]
        self.assertEqual(args[args.index("--effort") + 1], "medium")

    @patch("puente.run_claude")
    def test_dos_correcciones_fallidas_suben_a_max(self, transport):
        transport.side_effect = self.response
        self.init(rounds=4)
        initial = puente.send_run(self.repo, "caso", "Entrega inicial.")
        with self.assertRaises(puente.BridgeError):
            puente.review_run(self.repo, "caso", initial["huella"], "corregir", "No es corrección.", failed_correction=True)
        puente.review_run(self.repo, "caso", initial["huella"], "corregir", "Defecto demostrado.")
        for _ in range(2):
            state = puente.send_run(self.repo, "caso", "Corrige el defecto.")
            self.assertEqual(state["perfil"]["esfuerzo"], "xhigh")
            puente.review_run(self.repo, "caso", state["huella"], "corregir", "Persiste el defecto.", failed_correction=True)
        with self.assertRaisesRegex(puente.BridgeError, "motivo técnico"):
            puente.send_run(self.repo, "caso", "No escales sin justificación.", effort="xhigh")
        self.assertEqual(transport.call_count, 3)
        state = puente.send_run(self.repo, "caso", "Corrige con mayor esfuerzo.")
        self.assertEqual(state["perfil"]["esfuerzo"], "max")
        self.assertEqual(state["max_envios"], 4)
        self.assertEqual(state["presupuesto_usd"], 2.0)

    @patch("puente.run_claude")
    def test_escalada_no_amplia_limites(self, transport):
        transport.side_effect = self.response
        self.init()
        state = puente.send_run(self.repo, "caso", "Entrega.")
        puente.review_run(self.repo, "caso", state["huella"], "corregir", "Defecto.")
        for _ in range(2):
            state = puente.send_run(self.repo, "caso", "Corrige.")
            puente.review_run(self.repo, "caso", state["huella"], "corregir", "Persiste.", failed_correction=True)
        with self.assertRaisesRegex(puente.BridgeError, "Límite de envíos"):
            puente.send_run(self.repo, "caso", "No debe consumir otro envío.")
        self.assertEqual(transport.call_count, 3)

    @patch("puente.run_claude")
    def test_modelo_sustituido_no_se_da_por_validado(self, transport):
        self.init()
        def substituted(*args):
            result = self.response(*args)
            result["modelUsage"] = {"claude-sonnet-5": {}}
            return result
        transport.side_effect = substituted
        self.assertEqual(puente.send_run(self.repo, "caso", "Lee.")["estado"], "error")

    def test_esfuerzo_del_hijo_no_depende_del_entorno_ni_lo_modifica(self):
        code = 'import json, os; print(json.dumps({"effort": os.environ["CLAUDE_CODE_EFFORT_LEVEL"]}))'
        with patch.dict(os.environ, {"CLAUDE_CODE_EFFORT_LEVEL": "low"}):
            result = puente.run_claude([sys.executable, "-c", code, "--effort", "xhigh"],
                                      self.repo, "", 5)
            self.assertEqual(result["effort"], "xhigh")
            self.assertEqual(os.environ["CLAUDE_CODE_EFFORT_LEVEL"], "low")


if __name__ == "__main__":
    unittest.main()
