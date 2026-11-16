"""Run author checks and record exact Version B source hashes and locations."""

import ast
import hashlib
import importlib.metadata
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1] / "app" / "version-B"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    checks = []
    for name, command in (
        ("compile", [sys.executable, "-m", "compileall", "-q", str(ROOT / "backend")]),
        ("backend-behavior-and-live-listeners", [sys.executable, str(HERE / "test_backend.py")]),
        ("dependency-consistency", [sys.executable, "-m", "pip", "check"]),
    ):
        result = subprocess.run(command, capture_output=True, text=True, timeout=60)
        checks.append({"name": name, "exit_code": result.returncode, "output": result.stdout + result.stderr})
        print(f"{name}: {'PASS' if result.returncode == 0 else 'FAIL'}")
    files = []
    for path in sorted((ROOT / "backend").rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        files.append({
            "path": path.relative_to(ROOT).as_posix(), "sha256": digest(path),
            "functions": [{"name": node.name,
                           "start": min([node.lineno] + [d.lineno for d in node.decorator_list]),
                           "end": node.end_lineno}
                          for node in ast.walk(tree) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))],
        })
    for name in ("README.md", "requirements.txt", ".env.example"):
        files.append({"path": name, "sha256": digest(ROOT / name)})
    record = {
        "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
        "author": "Codex author checks; not independent review",
        "source_root": ROOT.relative_to(HERE.parents[3]).as_posix(),
        "python": sys.version,
        "runtime_note": "Reused Version A local Python environment for checks; no Version B environment installed.",
        "dependencies": {name: importlib.metadata.version(name) for name in ("flask", "werkzeug", "psycopg", "itsdangerous", "python-dotenv", "requests")},
        "files": files,
        "verification_files": [{"path": path.name, "sha256": digest(path)} for path in (HERE / "test_backend.py", Path(__file__))],
        "checks": checks,
        "limitations": [
            "Database operations use doubles; no Version B PostgreSQL execution or concurrency verification.",
            "Live local HTTP and certificate-verified HTTPS requests exercised both listeners; the device credential was sent over HTTP.",
            "No firmware or frontend exists yet; B-01 client-side transmission and full application integration remain pending.",
            "Loopback-only network checks do not establish exposure to a remote network observer.",
            "No independent review, detector evaluation, or Excel workbook update performed.",
        ],
    }
    (HERE / "backend-check-results.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    return int(any(check["exit_code"] for check in checks))


if __name__ == "__main__":
    raise SystemExit(main())
