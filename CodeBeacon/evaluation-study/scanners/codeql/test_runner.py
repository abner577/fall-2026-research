"""Infrastructure checks with simulated CodeQL responses, not study queries."""

import contextlib
import csv
import importlib.util
import io
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location("codeql_runner", Path(__file__).with_name("run-codeql.py"))
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


class RunnerChecks(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.base = self.root / "scanner"
        (self.base / "practice").mkdir(parents=True)
        (self.base / "practice" / "tls_example.py").write_text("# independent fixture\n")
        (self.base / "queries").mkdir()
        self.suite = self.base / "queries" / "practice.qls"
        self.suite.write_text("# simulated selection\n")
        self.query = self.root / "query.ql"
        self.query.write_text("// simulated query\n")
        self.outputs = self.root / "results"
        self.work = self.root / "work"
        for name, value in (("BASE_DIR", self.base), ("OUTPUT_DIR", self.outputs), ("WORK_DIR", self.work)):
            patcher = patch.object(runner, name, value)
            patcher.start()
            self.addCleanup(patcher.stop)

    def simulate(self, rows, fail=None, interrupt=False, custom=True):
        def command(command, log, cwd, env):
            if command[1:] == ["version"]:
                return (2, "") if fail == "version" else (0, "simulated version")
            if command[1:3] == ["resolve", "queries"]:
                return 0, str(self.query) + "\n"
            if command[1:3] == ["database", "analyze"]:
                report = Path(next(arg.split("=", 1)[1] for arg in command if arg.startswith("--output=")))
                with report.open("w", newline="", encoding="utf-8") as stream:
                    csv.writer(stream).writerows(rows)
                if interrupt:
                    raise KeyboardInterrupt
                return (2 if fail == "analysis" else 0), ""
            return 0, "simulated diagnostics\n"
        argv = ["--codeql", sys.executable]
        if custom:
            argv += ["--queries", str(self.suite)]
        with patch.object(runner, "run_command", side_effect=command), \
                contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            code = runner.main(argv)
        folder = next(self.outputs.iterdir())
        self.assertEqual({p.name for p in folder.iterdir()}, {"findings.txt", "run-log.txt"})
        self.assertFalse(list(self.work.rglob("*.csv")))
        return code, (folder / "findings.txt").read_text(encoding="utf-8"), (folder / "run-log.txt").read_text(encoding="utf-8")

    @staticmethod
    def alert():
        return ["TLS check", "Description", "error", "Message", "/tls_example.py", "5", "12", "5", "54"]

    def test_success_with_findings_and_no_findings(self):
        code, findings, log = self.simulate([self.alert()])
        self.assertEqual(code, 1)
        self.assertIn("tls_example.py:5:12", findings)
        self.assertIn("Scanner exit code: 0", log)

    def test_success_without_findings(self):
        code, findings, log = self.simulate([])
        self.assertEqual(code, 0)
        self.assertIn("No findings reported", findings)
        self.assertIn("COMPLETED / NO FINDINGS", log)

    def test_failed_scan_preserves_partial_findings(self):
        code, findings, log = self.simulate([self.alert()], fail="analysis")
        self.assertEqual(code, 2)
        self.assertIn("TLS check", findings)
        self.assertIn("FAILED / INCOMPLETE", log)

    def test_interruption_preserves_partial_findings(self):
        code, findings, log = self.simulate([self.alert()], interrupt=True)
        self.assertEqual(code, 130)
        self.assertIn("TLS check", findings)
        self.assertIn("INTERRUPTED", log)

    def test_failed_version_does_not_claim_empty_success(self):
        code, findings, log = self.simulate([], fail="version")
        self.assertEqual(code, 2)
        self.assertEqual(findings, "")
        self.assertIn("NOT AVAILABLE", log)

    def test_practice_rejects_unexpected_empty_result(self):
        code, _, log = self.simulate([], custom=False)
        self.assertEqual(code, 2)
        self.assertIn("Practice verification failed", log)

    def test_application_requires_explicit_queries(self):
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as raised:
            runner.main(["--case", "version-A"])
        self.assertEqual(raised.exception.code, 2)
        self.assertFalse(self.outputs.exists())

    def test_scope_excludes_credentials_environments_and_sql(self):
        practice = self.base / "practice"
        (practice / ".venv").mkdir()
        (practice / ".venv" / "ignored.py").write_text("# ignored")
        (practice / ".env").write_text("do not copy")
        (practice / "schema.sql").write_text("-- do not copy")
        target = self.root / "snapshot"
        runner.stage_sources("practice", target, io.StringIO())
        self.assertEqual([p.name for p in target.iterdir()], ["tls_example.py"])

    def test_repeat_names_and_fixed_est(self):
        first = runner.create_run_folder("practice")
        second = runner.create_run_folder("practice")
        self.assertNotEqual(first, second)
        self.assertTrue(second.name.endswith(" (1)"))
        self.assertEqual(runner.now().utcoffset().total_seconds(), -18000)

    def test_concurrent_pipe_capture_and_color_removal(self):
        script = "import sys; [(print('\\x1b[31mhello\\x1b[0m'), print('diagnostic'*100, file=sys.stderr)) for _ in range(2000)]"
        log = io.StringIO()
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            code, stdout = runner.run_command([sys.executable, "-c", script], log, self.root, None)
        self.assertEqual(code, 0)
        self.assertEqual(stdout.count("hello"), 2000)
        self.assertNotIn("\x1b", log.getvalue())
        self.assertIn("diagnostic", log.getvalue())


if __name__ == "__main__":
    unittest.main()
