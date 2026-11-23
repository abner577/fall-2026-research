"""Run local CodeQL with two text outputs; defaults to the independent practice case.

Application cases require --queries pointing to an explicitly selected local suite.
No study query suite is selected by this runner.
"""

import argparse
import csv
import hashlib
import os
from pathlib import Path
import queue
import re
import shlex
import shutil
import subprocess
import sys
import threading
import time
from datetime import datetime, timedelta, timezone


BASE_DIR = Path(__file__).resolve().parent
STUDY_DIR = BASE_DIR.parent.parent
OUTPUT_DIR = STUDY_DIR / "evaluation-runs" / "codeql"
WORK_DIR = BASE_DIR / ".work"
EST = timezone(timedelta(hours=-5), "EST")
EXCLUSIONS = {".venv", "__pycache__", ".local", ".git", ".env"}
ANSI_ESCAPE = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]")


def now():
    return datetime.now(EST)


def command_text(command):
    if os.name == "nt":
        return "& " + " ".join("'" + arg.replace("'", "''") + "'" for arg in command)
    return shlex.join(command)


def create_run_folder(case):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    stem = f"{now():%Y-%m-%d_%I-%M-%p}_EST_{case}"
    index = 0
    while True:
        folder = OUTPUT_DIR / (stem + (f" ({index})" if index else ""))
        try:
            folder.mkdir()
            return folder
        except FileExistsError:
            index += 1


def run_command(command, log, cwd, env):
    """Log both streams concurrently; return exit code and stdout for small lookups."""
    log.write(f"\nWorking directory: {cwd}\nCommand: {command_text(command)}\n")
    log.flush()
    events = queue.Queue()
    stdout = []
    process = subprocess.Popen(command, cwd=cwd, env=env, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, text=True,
                               encoding="utf-8", errors="replace")

    def reader(name, pipe):
        try:
            for line in pipe:
                events.put((name, line))
        finally:
            pipe.close()
            events.put((name, None))

    threads = []
    for name, pipe in (("stdout", process.stdout), ("stderr", process.stderr)):
        thread = threading.Thread(target=reader, args=(name, pipe), daemon=True)
        thread.start()
        threads.append(thread)
    try:
        closed = 0
        while closed < 2:
            name, line = events.get()
            if line is None:
                closed += 1
                continue
            line = ANSI_ESCAPE.sub("", line)
            log.write(line)
            log.flush()
            terminal = sys.stdout if name == "stdout" else sys.stderr
            terminal.write(line)
            terminal.flush()
            if name == "stdout":
                stdout.append(line)
        code = process.wait()
        log.write(f"Command exit code: {code}\n")
        log.flush()
        return code, "".join(stdout)
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


def record_hash(log, path, label):
    log.write(f"{label}: {hashlib.sha256(path.read_bytes()).hexdigest()}  {path}\n")


def stage_sources(case, destination, log):
    """Copy only Python inputs, preserving their relative paths and logging hashes."""
    root = BASE_DIR / "practice" if case == "practice" else STUDY_DIR / "app" / case
    targets = [root] if case == "practice" else [root / name for name in
                                               ("backend", "frontend", "firmware")]
    count = 0
    for target in targets:
        if not target.is_dir():
            raise FileNotFoundError(f"Missing source directory: {target}")
        for current, dirs, names in os.walk(target, followlinks=False):
            dirs[:] = sorted(d for d in dirs if d not in EXCLUSIONS and
                             not (Path(current) / d).is_symlink())
            for name in sorted(names):
                original = Path(current) / name
                if original.suffix.lower() != ".py" or original.is_symlink():
                    continue
                relative = original.relative_to(root)
                copied = destination / relative
                copied.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(original, copied)
                record_hash(log, copied, f"Source snapshot ({original})")
                count += 1
    if not count:
        raise RuntimeError("No Python source files selected; refusing an empty scan.")
    log.write(f"Staged Python file count: {count}\n"
              "This inventory is not proof all files were extracted; review CodeQL diagnostics.\n")
    log.flush()


def render_report(report, findings):
    rows = []
    if report.exists():
        with report.open(encoding="utf-8-sig", newline="") as stream:
            for row in csv.reader(stream):
                if not row:
                    continue
                if len(row) != 9:
                    raise RuntimeError(f"Unexpected CodeQL CSV row: expected 9 fields, got {len(row)}")
                rows.append(row)
                name, description, severity, message, path, line, column, end_line, end_column = row
                text = (f"Finding {len(rows)}: {name}\nSeverity: {severity}\n"
                        f"Location: {path}:{line}:{column or '1'}\n"
                        f"End location: line {end_line or line}, column {end_column or '(unspecified)'}\n"
                        f"Message: {message}\nDescription: {description}\n\n")
                text = ANSI_ESCAPE.sub("", text)
                findings.write(text)
                findings.flush()
                print(text, end="", flush=True)
    return rows


def main(argv=None):
    for terminal in (sys.stdout, sys.stderr):
        if hasattr(terminal, "reconfigure"):
            terminal.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", choices=("practice", "version-A", "version-B"), default="practice")
    parser.add_argument("--queries", type=Path, help="Explicit local .ql/.qls file; relative to your terminal.")
    parser.add_argument("--codeql", type=Path, help="Override CodeQL executable (Windows: codeql.exe).")
    args = parser.parse_args(argv)
    if args.case != "practice" and args.queries is None:
        parser.error("Application scans require --queries; study queries have not been selected.")
    suite = (args.queries or BASE_DIR / "queries" / "practice.qls").resolve()
    if args.codeql:
        executable = args.codeql.resolve()
    elif os.name == "nt":
        executable = Path(os.environ.get("LOCALAPPDATA", "")) / "CodeQL" / "codeql" / "codeql.exe"
    else:
        executable = Path(shutil.which("codeql") or "/missing/codeql")
    executable = executable.resolve()
    folder = create_run_folder(args.case)
    work = WORK_DIR / folder.name
    source = work / "source"
    database = work / "database"
    report = work / "findings.csv"
    started, clock_start = now(), time.monotonic()
    status, runner_exit = "FAILED / NOT STARTED", 2
    scan_exit = None
    report_rendered = False
    print(f"Saving this attempt to: {folder}", flush=True)
    with (folder / "findings.txt").open("w", encoding="utf-8") as findings, \
            (folder / "run-log.txt").open("w", encoding="utf-8") as log:
        log.write(f"CodeQL run\nCase: {args.case}\nStart: {started.isoformat()} (EST)\n"
                  f"Python: {sys.version}\nExecutable: {executable}\nQueries: {suite}\n"
                  f"Working files: {work}\nDatabase: {database}\n"
                  "Scope: Python source snapshot only; application targets backend/frontend/firmware.\n"
                  f"Excluded directories: {', '.join(sorted(EXCLUSIONS))}; symlinks excluded.\n"
                  "SQL, environment files, notes, answer keys, and non-Python inputs are not copied.\n"
                  "CodeQL extractor limits still apply; inspect diagnostics for warnings/omissions.\n"
                  "No source execution, build command, report upload, or automatic query download.\n")
        env = os.environ.copy()
        env.update(NO_COLOR="1", PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
        env.pop("FORCE_COLOR", None)
        try:
            if not executable.is_file():
                raise FileNotFoundError(f"CodeQL executable not found: {executable}; use --codeql to override.")
            if not suite.is_file() or suite.suffix.lower() not in {".ql", ".qls"}:
                raise ValueError(f"Queries must be a local .ql or .qls file: {suite}")
            work.mkdir(parents=True, exist_ok=False)
            source.mkdir()
            record_hash(log, suite, "Query selection SHA-256")
            stage_sources(args.case, source, log)

            def checked(arguments):
                code, output = run_command([str(executable), *arguments], log, source, env)
                if code != 0:
                    raise RuntimeError(f"CodeQL {arguments[0]} failed with exit code {code}.")
                return output

            version = checked(["version"])
            if not version.strip():
                raise RuntimeError("CodeQL version check returned no version.")
            checked(["resolve", "languages"])
            checked(["resolve", "packs"])
            resolved = checked(["resolve", "queries", str(suite), "--format=text"])
            queries = [Path(line.strip()) for line in resolved.splitlines() if line.strip().endswith(".ql")]
            if not queries:
                raise RuntimeError("The selected suite resolved to zero queries.")
            if args.case == "practice" and args.queries is None and len(queries) != 1:
                raise RuntimeError("Default practice suite must resolve to exactly one query.")
            for query in queries:
                record_hash(log, query, "Resolved query SHA-256")
                for parent in query.parents:
                    manifest = parent / "qlpack.yml"
                    if manifest.is_file():
                        log.write(f"Selected query pack manifest: {manifest}\n{manifest.read_text(encoding='utf-8')}\n")
                        record_hash(log, manifest, "Pack manifest SHA-256")
                        break
            checked(["database", "create", str(database), "--language=python", "--build-mode=none",
                     f"--source-root={source}", "--threads=2"])
            status = "FAILED / INCOMPLETE; any findings are partial"
            scan_exit, _ = run_command(
                [str(executable), "database", "analyze", str(database), str(suite),
                 "--format=csv", f"--output={report}", "--threads=2", "--ram=2048"],
                log, source, env)
            report_rendered = True
            rows = render_report(report, findings)
            if scan_exit != 0:
                raise RuntimeError(f"CodeQL analysis failed with exit code {scan_exit}; findings may be partial.")
            if not report.exists():
                raise RuntimeError("Analysis returned success but did not create its report.")
            if args.case == "practice" and args.queries is None:
                if len(rows) != 1 or Path(rows[0][4]).name != "tls_example.py" or rows[0][5] != "5":
                    raise RuntimeError("Practice verification failed: expected exactly one alert at tls_example.py:5.")
                log.write("Practice verification: PASS; unsafe call at line 5 flagged, safe call unflagged.\n")
            runner_exit = 1 if rows else 0
            status = "COMPLETED / FINDINGS REPORTED" if rows else "COMPLETED / NO FINDINGS"
            if not rows:
                findings.write("No findings reported. Review run-log.txt for scope and extraction warnings.\n")
        except KeyboardInterrupt:
            runner_exit, status = 130, "INTERRUPTED / INCOMPLETE; any findings are partial"
            log.write("\nRunner: interrupted by user.\n")
        except Exception as exc:
            status = "FAILED / INCOMPLETE; any findings are partial"
            log.write(f"\nRunner error: {type(exc).__name__}: {exc}\n")
            print(f"Run failed: {exc}", file=sys.stderr)
        finally:
            if report.exists() and not report_rendered:
                try:
                    render_report(report, findings)
                    log.write("Preserved intermediate findings after unsuccessful/interrupted analysis.\n")
                except Exception as exc:
                    log.write(f"Could not interpret partial report: {exc}\n")
                    findings.write("Uninterpreted partial CSV from unsuccessful analysis:\n")
                    findings.write(ANSI_ESCAPE.sub("", report.read_text(encoding="utf-8", errors="replace")))
            # The database remains available for inspection. No extra report copies are retained.
            if report.exists():
                try:
                    report.unlink()
                except OSError as exc:
                    log.write(f"Intermediate CSV cleanup failed: {exc}\n")
                    runner_exit, status = 2, "FAILED / INTERMEDIATE REPORT CLEANUP"
            log.write(f"\n--- Run outcome ---\nEnd: {now().isoformat()} (EST)\n"
                      f"Duration seconds: {time.monotonic() - clock_start:.2f}\nStatus: {status}\n"
                      f"Scanner exit code: {scan_exit if scan_exit is not None else 'NOT AVAILABLE (analysis not completed)'}\n"
                      f"Runner exit code: {runner_exit}\n"
                      "An empty findings file is meaningful only when the scan completed.\n")
    print(f"{status}\nResults: {folder}\nDatabase: {database}", flush=True)
    return runner_exit


if __name__ == "__main__":
    sys.exit(main())
