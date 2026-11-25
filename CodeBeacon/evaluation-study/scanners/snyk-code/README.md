# Snyk Code runner

The runner prints Snyk Code's readable output and saves exactly `findings.txt`
and `run-log.txt` per attempt, following the [shared scanner contract](../README.md).
It uses Snyk's managed security checks, without a custom rule file. CodeQL already
has its own [runner and commands](../codeql/README.md).

## Install and authenticate once (PowerShell)

```powershell
Set-Location "C:\Users\joser\Downloads\fall-2026-research\CodeBeacon\evaluation-study\scanners\snyk-code"
New-Item -ItemType Directory -Force .\.tools | Out-Null
Invoke-WebRequest -Uri "https://downloads.snyk.io/cli/stable/snyk-win.exe" -OutFile ".\.tools\snyk.exe"
.\.tools\snyk.exe --version
.\.tools\snyk.exe auth
```

Skip downloading if `.tools/snyk.exe` is already installed. Authentication opens
the browser for account login; scan findings remain in the terminal and local
text files. Enable Snyk Code for your Snyk organization if prompted. Use the free
plan only: check the organization's actual remaining Snyk Code test allowance
before practice/application runs. No paid upgrade is authorized. Account access,
quota, and organization enablement require verification in your account; the
runner cannot certify them. Do not put tokens in command lines or tracked files.

This uses the official native Windows binary rather than the npm shell shim.
No PATH edit, Python virtual environment, or additional Python package is needed.
To use another native installation, add `--snyk "C:\path\to\snyk.exe"`.
The runner also searches PATH for `snyk.exe` when its local binary is absent.
For a chosen organization, append `--org "your-org-id-or-slug"` to each command;
otherwise Snyk uses the configured account default. Log the actual organization
choice in the account verification evidence when using that default.

## Practice, then actual application scans

```powershell
python .\run-snyk-code.py --case practice
$LASTEXITCODE
```

Inspect the practice result: `practice/tls_example.py` contains an unsafe
`verify=False` call at line 6 and a safe `verify=True` call at line 10. Expect
the unsafe call to be reported and the safe one unflagged. Review this manually:
the runner reports CLI completion, not an automatic assertion that the fixture
passed. Cloud rule behavior can change; document a missing/unexpected finding
as a verification issue without changing application code or tuning to it.
The fixture is never executed.

Once authentication, quota, and practice findings are verified:

```powershell
python .\run-snyk-code.py --case version-A
$LASTEXITCODE
python .\run-snyk-code.py --case version-B
$LASTEXITCODE
```

These scan the actual repository application code through byte-for-byte Python
snapshots of `evaluation-study/app/version-A` or `version-B`, restricted to
`backend`, `frontend`, and `firmware`, as with CodeQL. They do not scan the whole
research repository. Relative paths and SHA-256 hashes connect findings to the
original files. Snapshots remain under ignored `.work/<attempt>/source/` for
inspection; they are inputs, not extra reports. Do not edit source during a run.

Only `.py` files are copied. `.venv`, `__pycache__`, `.local`, `.git`, `.env`,
and symlinks are excluded; SQL, dependency manifests, research notes, answer keys,
and environment credentials are outside scope. Python literals in selected source
are included. No `.gitignore` or `.snyk` file is copied into the snapshot. Snyk's
own supported-file, size, ignore and analysis limits still apply. File inventory
does not prove every file or framework feature was analyzed. Inspect diagnostics
and the native scan summary, including file counts, before interpreting results.

The underlying command is:

```text
snyk.exe code test <absolute-snapshot-path> --severity-threshold=low [--org=<organization>]
```

It runs all applicable built-in security checks at low severity and above.
There is no `--report`, `monitor`, repository import, or web report command.
Snyk Code still sends selected source to Snyk's cloud analysis service; local
result logging does not make Snyk an offline scanner. Existing organization
policies/ignores may affect results. This runner does not alter them.

## Results and exit codes

```text
evaluation-study/evaluation-runs/snyk-code/
  YYYY-MM-DD_hh-mm-AM_EST_version-A/
    findings.txt
    run-log.txt
```

The terminal prints the exact results folder. Fixed EST (UTC-05:00) applies all
year; repeated names receive `(1)`, `(2)`, etc. Previous attempts are preserved.
The existing repository ignore excludes `evaluation-runs` from Git: files are
saved locally in the repository tree, not automatically committed.

`findings.txt` preserves native readable stdout, including the scanner's summary.
`run-log.txt` records stderr progress/errors, exact command, executable/version,
working directory, source paths/hashes, exclusions, rule-source limits, precise
timestamps, duration, raw scanner exit code, runner exit code, and outcome.
Both streams are drained concurrently and displayed in the terminal. Saved text
is UTF-8 without ANSI colors. No JSON, SARIF, HTML, or extra report is generated.
Failures and partial findings are retained, including errors printed on stdout.

| Runner exit | Meaning |
| --- | --- |
| 0 | CLI completed without findings; inspect scope and omissions. |
| 1 | CLI completed with findings; expected for vulnerable practice code. |
| 2 | Setup/scan failure or unsupported source; results may be partial. |
| 130 | Interrupted; results may be partial. |

Snyk scanner exit 3 (no supported source) maps to runner exit 2. Its raw exit
remains in the log. Empty findings after a failure never mean a clean application.

```powershell
$latest = Get-ChildItem "..\..\evaluation-runs\snyk-code" -Directory |
    Sort-Object CreationTimeUtc -Descending | Select-Object -First 1
Get-Content (Join-Path $latest.FullName "findings.txt") -Encoding UTF8
Get-Content (Join-Path $latest.FullName "run-log.txt") -Encoding UTF8 -Tail 15
```

## Verification and checklist status

November 25, 2026: ten infrastructure checks pass, covering findings/clean/error
statuses, unsupported source, version failure, interruption, byte-preserving
scope selection, empty scope rejection, fixed EST/repeat naming, and real
subprocess Unicode/color/concurrent stream capture. Repeat them with:

```powershell
python .\test_runner.py
```

These are simulated CLI status checks plus a real Python subprocess check,
not evidence that Snyk detects the practice vulnerability. The first real runner
launch retained a missing-CLI failure in
`../../evaluation-runs/snyk-code/2026-11-25_11-52-AM_EST_practice/`.
Authenticated practice scanning subsequently succeeded as recorded below.
Free-account plan/limits remain unverified; leave the checklist item open until
that account check is complete.

The official native CLI was subsequently installed locally at `.tools/snyk.exe`;
its version check succeeds with **1.1309.0**. The next practice attempt,
`../../evaluation-runs/snyk-code/2026-11-25_11-55-AM_EST_practice/`, saved the
version, source hash, and a network-restricted scan failure (scanner/runner exit 2).
Automatic approval review initially rejected a network-enabled retry because
external source upload needed explicit user approval. The user then approved
uploading only the independent TLS practice fixture, and the retry succeeded.

Successful real practice evidence:
`../../evaluation-runs/snyk-code/2026-11-25_11-56-AM_EST_practice/`.
Existing local authentication worked with organization `abner07282005`.
Snyk CLI **1.1309.0** reported exactly one HIGH
`Improper Certificate Validation - SSL Verification Bypass` issue at
`tls_example.py:6`, with no finding on the safe call at line 10, and zero ignored
issues in its summary. Scanner and runner both returned **1** (findings).
Both text outputs were saved and findings appeared in the terminal. No dashboard
publication was requested. No application-version scan was performed; the upload
approval was limited to practice. Successful authentication does not verify that
the organization is on the free plan or establish its remaining allowance.

The logging implementation is complete. No Semgrep-style custom YAML rules or
CodeQL queries are needed for this Snyk Code procedure. Its managed checks do
not establish coverage of all ten study targets. Target-to-check/CWE mapping,
observed rule identifiers and limitations, common scope agreement, independent
answer-key review, and scoring remain checklist work. The CLI version is logged
per run, but it does not pin Snyk's cloud engine or rule revision. Preserve the
native findings and date; do not claim deterministic rule-version reproducibility.

References: [Snyk Code command, reporting and exit codes](https://docs.snyk.io/developer-tools/snyk-cli/commands/code-test),
[CLI installation](https://docs.snyk.io/developer-tools/snyk-cli/install-the-snyk-cli),
[authentication](https://docs.snyk.io/developer-tools/snyk-cli/authenticate-to-use-the-cli),
[Snyk data handling](https://docs.snyk.io/snyk-data-and-governance/how-snyk-handles-your-data),
[Code exclusions](https://docs.snyk.io/scan-fix-and-prevent/prevent/policies/the-.snyk-file).
