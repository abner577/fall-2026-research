"""Logging/status/scope checks; simulated CLI responses do not verify Snyk detection."""
import contextlib
import importlib.util
import io
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location("snyk_runner", Path(__file__).with_name("run-snyk-code.py"))
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


class RunnerChecks(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.base = self.root / "scanner"
        (self.base / "practice").mkdir(parents=True)
        (self.base / "practice/tls_example.py").write_text("# fixture\n", encoding="utf-8")
        self.outputs = self.root / "results"
        for name, value in (("BASE_DIR", self.base), ("STUDY_DIR", self.root),
                            ("WORK_DIR", self.root / "work"), ("OUTPUT_DIR", self.outputs)):
            p = patch.object(runner, name, value)
            p.start()
            self.addCleanup(p.stop)

    def simulate(self, code, version_ok=True):
        version = subprocess.CompletedProcess([], 0 if version_ok else 2, "test-version\n", "")

        def scan(command, env, findings, log, cwd):
            self.assertEqual(command[1:3], ["code", "test"])
            self.assertNotIn("--report", command)
            self.assertTrue((cwd / "tls_example.py").is_file())
            findings.write("simulated finding\n")
            log.write("simulated progress\n")
            if code == 130:
                raise KeyboardInterrupt
            return code

        with patch.object(runner.subprocess, "run", return_value=version), \
                patch.object(runner, "stream_scan", side_effect=scan), \
                contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            result = runner.main(["--snyk", sys.executable])
        folder = sorted(self.outputs.iterdir(), key=lambda p: p.stat().st_mtime_ns)[-1]
        self.assertEqual({p.name for p in folder.iterdir()}, {"findings.txt", "run-log.txt", "results-table.csv", "confusion-matrices"})
        return result, (folder / "findings.txt").read_text(encoding="utf-8"), (folder / "run-log.txt").read_text(encoding="utf-8")

    def test_findings(self):
        code, findings, log = self.simulate(1)
        self.assertEqual(code, 1)
        self.assertIn("simulated finding", findings)
        self.assertIn("COMPLETED / FINDINGS REPORTED", log)
        self.assertIn("Tool version: test-version", log)

    def test_clean(self):
        code, findings, log = self.simulate(0)
        self.assertEqual(code, 0)
        self.assertIn("No findings reported", findings)
        self.assertIn("COMPLETED / NO FINDINGS", log)

    def test_failure_preserves_partial_findings(self):
        code, findings, log = self.simulate(2)
        self.assertEqual(code, 2)
        self.assertIn("simulated finding", findings)
        self.assertIn("FAILED / INCOMPLETE", log)

    def test_unsupported_is_failure(self):
        code, _, log = self.simulate(3)
        self.assertEqual(code, 2)
        self.assertIn("Scanner exit code: 3", log)
        self.assertIn("No supported source", log)

    def test_version_failure(self):
        code, findings, log = self.simulate(1, version_ok=False)
        self.assertEqual(code, 2)
        self.assertEqual(findings, "")
        self.assertIn("NOT AVAILABLE", log)

    def test_interrupt_preserves_partial_findings(self):
        code, findings, log = self.simulate(130)
        self.assertEqual(code, 130)
        self.assertIn("simulated finding", findings)
        self.assertIn("INTERRUPTED", log)

    def test_scope_and_exact_source_copy(self):
        root = self.root / "app/version-A"
        for name in ("backend", "frontend", "firmware"):
            target = root / name
            (target / ".venv").mkdir(parents=True)
            (target / "source.py").write_bytes(b"# source\r\n")
            (target / ".venv/hidden.py").write_text("# exclude")
            (target / ".env").write_text("SECRET=exclude")
            (target / "notes.md").write_text("exclude")
        destination = self.root / "snapshot"
        log = io.StringIO()
        runner.stage_sources("version-A", destination, log)
        self.assertEqual(len(list(destination.rglob("*.*"))), 3)
        self.assertEqual((destination / "backend/source.py").read_bytes(), b"# source\r\n")
        self.assertIn("SHA-256", log.getvalue())

    def test_empty_input_rejected(self):
        (self.base / "practice/tls_example.py").unlink()
        with self.assertRaisesRegex(RuntimeError, "No Python"):
            runner.stage_sources("practice", self.root / "snapshot", io.StringIO())

    def test_est_repeat_names(self):
        from datetime import datetime
        with patch.object(runner, "now", return_value=datetime(2026, 7, 1, 13, 2, tzinfo=runner.EST)):
            first = runner.create_run_folder("practice")
            second = runner.create_run_folder("practice")
        self.assertEqual(first.name, "2026-07-01_01-02-PM_EST_practice")
        self.assertEqual(second.name, first.name + " (1)")

    def test_real_subprocess_streams_unicode_and_color(self):
        findings, log = io.StringIO(), io.StringIO()
        command = [sys.executable, "-c",
                   "import sys; print('\\x1b[31mfinding café\\x1b[0m'); "
                   "sys.stderr.write('progress\\n' * 3000)"]
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            code = runner.stream_scan(command, {**runner.os.environ, "PYTHONIOENCODING": "utf-8"},
                                      findings, log, cwd=self.root)
        self.assertEqual(code, 0)
        self.assertEqual(findings.getvalue(), "finding café\n")
        self.assertEqual(log.getvalue().count("progress"), 3000)


if __name__ == "__main__":
    unittest.main()
