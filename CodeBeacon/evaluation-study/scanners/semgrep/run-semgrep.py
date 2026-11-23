"""Run Semgrep CE and retain exactly two text files per attempt.

Run from any directory: python path/to/run-semgrep.py --case practice
Application scans require --config with an explicit local rule file/directory.
"""

import argparse
import hashlib
import os
from pathlib import Path
import queue
import re
import shlex
import subprocess
import sys
import threading
import time
from datetime import datetime, timedelta, timezone


BASE_DIR = Path(__file__).resolve().parent
STUDY_DIR = BASE_DIR.parent.parent
OUTPUT_DIR = STUDY_DIR / "evaluation-runs" / "semgrep"
EST = timezone(timedelta(hours=-5), "EST")
EXCLUSIONS = (".venv", "__pycache__", ".local", ".git", ".env")
ANSI_ESCAPE = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]")


def now():
    return datetime.now(EST)


def command_text(command):
    # PowerShell display only; execution always uses an argument list, no shell.
    if os.name == "nt":
        return "& " + " ".join("'" + arg.replace("'", "''") + "'" for arg in command)
    return shlex.join(command)


def create_run_folder(case):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    stem = f"{now():%Y-%m-%d_%I-%M-%p}_EST_{case}"
    index = 0
    while True:
        suffix = f" ({index})" if index else ""
        folder = OUTPUT_DIR / (stem + suffix)
        try:
            folder.mkdir()
            return folder
        except FileExistsError:
            index += 1


def write_manifest(log, label, paths, suffixes):
    log.write(f"\n{label} (SHA-256; includes candidates that Semgrep may skip):\n")
    files = set()
    for path in paths:
        candidates = path.rglob("*") if path.is_dir() else (path,)
        for candidate in candidates:
            if (candidate.is_file() and candidate.suffix.lower() in suffixes
                    and not any(part in EXCLUSIONS for part in candidate.parts)):
                files.add(candidate)
    for path in sorted(files):
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        log.write(f"{digest}  {path}\n")
    log.flush()


def stream_scan(command, env, findings, log):
    """Drain both pipes concurrently, saving and displaying their original text."""
    events = queue.Queue()
    process = subprocess.Popen(
        command, cwd=BASE_DIR, env=env, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="replace",
    )

    def read_stream(name, pipe):
        try:
            for line in pipe:
                events.put((name, line))
        finally:
            pipe.close()
            events.put((name, None))

    threads = []
    for name, pipe in (("stdout", process.stdout), ("stderr", process.stderr)):
        thread = threading.Thread(target=read_stream, args=(name, pipe), daemon=True)
        thread.start()
        threads.append(thread)
    try:
        finished = 0
        while finished < 2:
            name, line = events.get()
            if line is None:
                finished += 1
                continue
            line = ANSI_ESCAPE.sub("", line)
            destination = findings if name == "stdout" else log
            terminal = sys.stdout if name == "stdout" else sys.stderr
            destination.write(line)
            destination.flush()
            terminal.write(line)
            terminal.flush()
        return process.wait()
    finally:
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
        for thread in threads:
            thread.join(timeout=5)


def main(argv=None):
    for terminal in (sys.stdout, sys.stderr):
        if hasattr(terminal, "reconfigure"):
            terminal.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", choices=("practice", "version-A", "version-B"),
                        default="practice")
    parser.add_argument("--config", type=Path,
                        help="Local YAML file/directory; relative paths use your current directory.")
    parser.add_argument("--semgrep", type=Path,
                        help="Override the scanner executable path.")
    args = parser.parse_args(argv)
    if args.case != "practice" and args.config is None:
        parser.error("Application scans require --config with your selected local rules.")
    config = (args.config or BASE_DIR / "rules" / "practice.yml").resolve()
    targets = ([BASE_DIR / "practice" / "tls_example.py"] if args.case == "practice"
               else [STUDY_DIR / "app" / args.case / name
                     for name in ("backend", "frontend", "firmware")])
    executable = (args.semgrep or BASE_DIR / ".venv" /
                  ("Scripts/semgrep.exe" if os.name == "nt" else "bin/semgrep")).resolve()
    command = [str(executable), "scan", "--oss-only", "--text", "--strict", "--error",
               "--metrics=off", "--disable-version-check", "--verbose",
               "--config", str(config), "--include", "*.py"]
    for exclusion in EXCLUSIONS:
        command.extend(("--exclude", exclusion))
    command.extend(str(path) for path in targets)
    env = os.environ.copy()
    env.update(PYTHONUTF8="1", PYTHONIOENCODING="utf-8", NO_COLOR="1")
    env.pop("SEMGREP_FORCE_COLOR", None)
    env.pop("FORCE_COLOR", None)
    folder = create_run_folder(args.case)
    print(f"Saving this attempt to: {folder}", flush=True)
    started = now()
    clock_start = time.monotonic()
    scan_exit = None
    runner_exit = 2
    status = "FAILED / NOT STARTED"
    with (folder / "findings.txt").open("w", encoding="utf-8") as findings, \
            (folder / "run-log.txt").open("w", encoding="utf-8") as log:
        log.write(f"Semgrep CE run\nCase: {args.case}\nStart: {started.isoformat()} (EST)\n"
                  f"Working directory: {BASE_DIR}\nPython: {sys.version}\n"
                  f"Executable: {executable}\nRules: {config}\n"
                  f"Targets: {', '.join(map(str, targets))}\n"
                  f"Scope: Python only; excludes {', '.join(EXCLUSIONS)}; "
                  "Semgrep default ignores also apply.\n"
                  "Environment overrides: PYTHONUTF8=1, PYTHONIOENCODING=utf-8, "
                  "NO_COLOR=1; SEMGREP_FORCE_COLOR and FORCE_COLOR unset\n"
                  f"Exact scan command (PowerShell on Windows):\n{command_text(command)}\n")
        try:
            for path in (executable, config, *targets):
                if not path.exists():
                    raise FileNotFoundError(f"Required path does not exist: {path}")
            version_command = [str(executable), "--version"]
            log.write(f"\nVersion command: {command_text(version_command)}\n")
            log.flush()
            version = subprocess.run(
                version_command, cwd=BASE_DIR, env=env, capture_output=True,
                text=True, encoding="utf-8", errors="replace", timeout=30,
            )
            log.write(f"Version stdout:\n{version.stdout}\nVersion stderr:\n{version.stderr}\n"
                      f"Version command exit code: {version.returncode}\n")
            if version.returncode != 0 or not version.stdout.strip():
                raise RuntimeError("Semgrep version check failed; see version diagnostics above.")
            log.write(f"Tool version: {version.stdout.strip()}\n")
            write_manifest(log, "Rules", [config], {".yaml", ".yml"})
            write_manifest(log, "Source candidates before scan", targets, {".py"})
            log.write("\n--- Scanner warnings, errors, and progress (stderr) ---\n")
            log.flush()
            status = "FAILED / INCOMPLETE; any findings are partial"
            scan_exit = stream_scan(command, env, findings, log)
            runner_exit = scan_exit if scan_exit in (0, 1) else 2
            status = {0: "COMPLETED / NO FINDINGS", 1: "COMPLETED / FINDINGS REPORTED"}.get(
                scan_exit, "FAILED / INCOMPLETE; any findings are partial")
        except KeyboardInterrupt:
            status = "INTERRUPTED / INCOMPLETE; any findings are partial"
            runner_exit = 130
            log.write("\nRunner: interrupted by user.\n")
        except Exception as exc:
            log.write(f"\nRunner error: {type(exc).__name__}: {exc}\n")
            print(f"Run failed: {exc}", file=sys.stderr)
        finally:
            log.write(f"\n--- Run outcome ---\nEnd: {now().isoformat()} (EST)\n"
                      f"Duration seconds: {time.monotonic() - clock_start:.2f}\n"
                      f"Status: {status}\nScanner exit code: "
                      f"{scan_exit if scan_exit is not None else 'NOT AVAILABLE (scan not started or interrupted)'}\n"
                      f"Runner exit code: {runner_exit}\n"
                      "An empty findings file is meaningful only when the scan completed.\n")
    print(f"{status}\nResults: {folder}", flush=True)
    return runner_exit


if __name__ == "__main__":
    sys.exit(main())
