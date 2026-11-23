# Run CodeQL

CodeQL is set up for local practice verification. Study-specific queries are not
selected or implemented. The existing practice fixture and suite were retained.

## Simple practice command

Open a normal PowerShell window and run:

```powershell
Set-Location "C:\Users\joser\Downloads\fall-2026-research\CodeBeacon\evaluation-study\scanners\codeql"
python .\run-codeql.py --case practice
$LASTEXITCODE
```

No environment activation, manually created database, terminal variables, or
running application is needed. Built-in paths resolve from the script location.
Python and the installed CodeQL bundle are required. On this machine the runner
uses `%LOCALAPPDATA%\CodeQL\codeql\codeql.exe` (the native executable, not a shell
wrapper). An alternate installation can be supplied with `--codeql`:

```powershell
python .\run-codeql.py --case practice --codeql "C:\path\to\codeql.exe"
```

## What happens

1. A unique run folder is created under `../../evaluation-runs/codeql/`, using
   fixed EST (UTC-05:00), minutes, AM/PM, and numbered repeats without overwrites.
2. Python files are copied into a separate source snapshot under `.work/`.
   Source hashes, scope, and exclusions are recorded in the log.
3. The runner checks CodeQL's version, available packs/languages, and the actual
   queries selected by the suite. It records query hashes and pack information.
4. CodeQL creates a fresh Python database from that snapshot. This is an analysis
   database, unrelated to PostgreSQL. No database server or application is started.
5. The built-in certificate verification query runs against the database.
6. The temporary CSV is converted into readable text in `findings.txt`, displayed
   in the terminal, and removed. Both diagnostic streams go to `run-log.txt`.
7. Default practice verification requires exactly one alert at
   `tls_example.py:5`: `verify=False` is flagged and `verify=True` is unflagged.

| File/folder | Purpose |
| --- | --- |
| `run-codeql.py` | Runs the entire local procedure and saves evidence. |
| `practice/tls_example.py` | Independent unsafe/safe TLS examples, analyzed without executing them. |
| `queries/practice.qls` | Selects only the upstream `py/request-without-cert-validation` query. Not a study suite. |
| `.work/<attempt>/source/` | Exact Python snapshot supplied to CodeQL. |
| `.work/<attempt>/database/` | Database, CodeQL internal logs, and analysis caches for inspection. Rebuilt on every run. |
| `.gitignore` | Keeps `.work/` out of Git. |
| `test_runner.py` | Ten infrastructure checks using simulated scanner responses and a real subprocess stream check. |

The only retained files in each **results** folder are `findings.txt` and
`run-log.txt`. CodeQL database internals are working files outside that folder.
The study's existing `.gitignore` also excludes `evaluation-runs/` from Git.
Keep local run evidence; it is not automatically published with a commit.

## Read the result

The runner prints the results folder and database location. To open the newest
attempt from this CodeQL directory:

```powershell
$latest = Get-ChildItem "..\..\evaluation-runs\codeql" -Directory |
    Sort-Object CreationTimeUtc -Descending |
    Select-Object -First 1

Get-Content (Join-Path $latest.FullName "findings.txt") -Encoding UTF8
Get-Content (Join-Path $latest.FullName "run-log.txt") -Encoding UTF8 -Tail 12
```

Use `notepad` with the same paths to read the full files.

| Runner exit code | Meaning |
| --- | --- |
| `0` | Completed without findings (possible with explicitly supplied queries). |
| `1` | Completed with findings; expected for default practice. |
| `2` | Setup, extraction, analysis, report processing, or practice verification failed. |
| `130` | Interrupted; any findings are partial. |

CodeQL itself normally returns **0** for successful analysis even with findings.
The runner maps this to **1** when findings exist, matching the Semgrep interface.
Each command's real exit code remains in the log. Failed and interrupted attempts
remain available; empty findings after failure do not establish target absence.
The readable report preserves the native alert's name, severity, description,
message, and location. It does not invent CWE or query-ID fields absent from CSV;
the selected query identity and provenance are separately recorded in the log.

## Application cases: prepared interface, pending queries

The runner supports `version-A` and `version-B`, but rejects either without an
explicit `--queries` local `.ql` or `.qls` file. No study suite is provided yet.
After query selection and independent fixture tests, the command shape will be:

```text
python .\run-codeql.py --case version-A --queries <selected-local-suite.qls>
```

Only `.py` files from `backend`, `frontend`, and `firmware` are staged, preserving
relative paths. `.venv`, `__pycache__`, `.local`, `.git`, `.env`, and symlinks are
excluded. SQL, credentials, answer keys, and research notes are not copied.
CodeQL's own extraction/modeling limits still apply: a staged-file inventory
does not prove every file or framework feature was analyzed. Inspect diagnostics
before interpreting a successful command or zero findings as useful evidence.
No application scan or study-query coverage is claimed by this setup.

## Verification record

November 23, 2026: CodeQL CLI **2.27.5**, `codeql/python-queries` **1.9.1**, and
`codeql/python-all` **7.2.10**. The real practice run created its Python database
and returned exactly one alert on the unsafe call at line 5. The safe call was
unflagged. Evidence: `../../evaluation-runs/codeql/2026-11-23_04-46-PM_EST_practice/`.
Ten infrastructure checks pass:

```powershell
python .\test_runner.py
```

The earlier `04-45-PM` restricted-sandbox attempt failed during Python discovery:
`No installed Python found!`. The Windows launcher could not discover registered
Python there. The same runner succeeded outside the sandbox without installing
Python or changing the CodeQL bundle. If this recurs in a restricted terminal,
use normal Windows PowerShell and inspect the failed attempt's log.

CodeQL also emitted a non-fatal warning that the 2 GB analysis limit did not
allow query-loading stage caching; analysis still completed. Practice verification
is not an accuracy score, independent answer-key review, or study readiness.

References: [CodeQL setup](https://docs.github.com/en/code-security/how-tos/find-and-fix-code-vulnerabilities/scan-from-the-command-line/set-up-codeql-cli),
[database creation](https://docs.github.com/en/code-security/reference/code-scanning/codeql/codeql-cli-manual/database-create),
[CSV fields](https://docs.github.com/en/code-security/reference/code-scanning/codeql/codeql-cli/csv-output),
[practice query](https://codeql.github.com/codeql-query-help/python/py-request-without-cert-validation/).
