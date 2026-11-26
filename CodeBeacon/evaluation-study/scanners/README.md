# Scanner runners and saved results

Agreed November 23, 2026. This is the implementation guide for future agents
working on Semgrep Community Edition, CodeQL, and Snyk Code. Semgrep and CodeQL
practice runners are implemented and verified. CodeQL now also has a
[study query suite](codeql/queries/study.qls) with five upstream checks and nine
custom queries. Snyk Code now has a [runner and setup guide](snyk-code/README.md);
authenticated practice verification passed November 25; free-account limits remain pending. See
[the CodeQL guide](codeql/README.md) for study/practice commands, independent
fixture verification, database handling, and coverage limits.

For the later Application Constants Excel update, see
[scanner-rules-excel-plan.md](scanner-rules-excel-plan.md). It saves the user's
workflow and requested Semgrep table; no workbook editing is requested yet.

## Shared behavior for all three scanners

Use one runner per scanner and the existing `evaluation-study/evaluation-runs/`
folder, with a subfolder for each scanner. Follow the Semgrep runner's behavior
when adding CodeQL and Snyk Code; tool-specific setup and exit codes will differ.

Each run folder retains these scanner outputs:

| File | Contents |
| --- | --- |
| `findings.txt` | The scanner's readable findings, also displayed in the terminal. |
| `run-log.txt` | Warnings, errors, scan progress, tool version, exact executed command, working directory, targets, rules/queries, exclusions, start/end timestamps, duration, scanner exit code, runner exit code, and outcome. |

Each new run also creates the blank `results-table.csv` manual grading template
and an empty `confusion-matrices/` folder. Its final table column is
`final_accuracy_percentage`, entered manually in the TOTAL row. CodeQL additionally
retains its original report as `raw-output.csv` when one is produced.
This November 25 update supersedes the earlier two-file-only output contract.
Keep historical outputs unchanged and keep working databases outside run folders.
See [results notes](../results-notes.md) for the complete workflow and notebook.

Use readable folder names, for example:

```text
evaluation-runs/semgrep/
  2026-11-23_11-30-AM_EST_practice/
    findings.txt
    run-log.txt
    results-table.csv
    confusion-matrices/
  2026-11-23_11-30-AM_EST_practice (1)/
    findings.txt
    run-log.txt
    results-table.csv
    confusion-matrices/
```

Time is **fixed EST, UTC-05:00, all year**, independent of the computer's timezone.
It does not switch to EDT in summer. Names use hours/minutes and AM/PM, without
seconds or milliseconds. The log uses precise timestamps with the UTC offset.
Number repeat names `(1)`, `(2)`, etc.; never overwrite a previous attempt.

Runners must resolve built-in paths from their own script location, without
depending on terminal variables such as `$run` or `$sg`. Launch tools with an
argument list, without a shell. Preserve failed attempts and partial findings;
an empty file after an error does not mean zero vulnerabilities. Display a final
outcome and the results folder. Capture both output streams concurrently so a
busy scanner cannot block on a full pipe. Write UTF-8 text and remove terminal
color escapes from saved output.

Record actual executable versions every time. Record local rule/query paths
and versions or hashes and source identity where practical. Semgrep records
SHA-256 hashes of local YAML rules and candidate Python files before scanning;
this is a candidate inventory, not proof every file was analyzed. Inspect the
scanner's skipped-file diagnostics. Do not edit source or rules during a run.
Treat tool warnings and omissions as limitations even when the exit code is 0/1.

Keep study configuration separate from run evidence. The intended master
constants reference is an external Word document, described in
[study-constants-document-plan.md](../../../fall-2026-research/evaluation-study-preparation/study-constants-document-plan.md).
Automatic per-run metadata belongs in `run-log.txt` so actual executions remain
traceable. Do not create a second maintained constants registry in the repository.

## Run Semgrep now

Open PowerShell. Enter this folder (the commands below assume this location):

```powershell
Set-Location "C:\Users\joser\Downloads\fall-2026-research\CodeBeacon\evaluation-study\scanners\semgrep"
```

Python must be available, and Semgrep must be installed in this folder's `.venv`.
The runner itself uses only Python's standard library. It uses the scanner
executable in `.venv/Scripts/semgrep.exe` on Windows. There is no environment
activation requirement. If installation is needed, run:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install semgrep
```

Once a version is agreed for the study, use that pinned version when recreating
the environment instead of installing an unpinned latest version.

Run the separate practice case:

```powershell
python .\run-semgrep.py --case practice
$LASTEXITCODE
```

This uses `rules/practice.yml` against `practice/tls_example.py`. Expected:
one finding on `verify=False`, none on `verify=True`, and runner exit code **1**.
This runner deliberately supplies `--error`, unlike the earlier manual tutorial:

| Runner exit code | Meaning |
| --- | --- |
| `0` | Scanner completed without findings. Check progress and skipped-file details. |
| `1` | Scanner completed with findings; this is an expected result, not a crash. |
| `2` | Setup/scan failed or was incomplete; consult the log. |
| `130` | Interrupted by the user; results may be incomplete. |

The log retains the actual scanner exit code separately. When the version check
or path validation fails before scanning, it records that no scan exit code is
available. Command-line argument errors are rejected before a run is created.

The runner displays findings and diagnostics while saving them. Semgrep can
buffer its findings until analysis finishes, so progress may appear first.

## Inspect the scanner output files

The terminal prints the exact results folder. To open the newest attempt:

```powershell
$latest = Get-ChildItem "..\..\evaluation-runs\semgrep" -Directory |
    Sort-Object CreationTimeUtc -Descending |
    Select-Object -First 1

Get-Content (Join-Path $latest.FullName "findings.txt") -Encoding UTF8
Get-Content (Join-Path $latest.FullName "run-log.txt") -Encoding UTF8
```

For a longer log, use `notepad` instead of `Get-Content` with the same path.
To check completion quickly:

```powershell
Get-Content (Join-Path $latest.FullName "run-log.txt") -Encoding UTF8 -Tail 10
```

No transcript or manual copying is needed. A failed launch still creates both
files, provided the results folder itself is writable. Read `run-log.txt` first
if findings are empty.

## Application scans and rule selection

Version A and B require an explicit local configuration. The selected Python
checks are in [semgrep/rules/study.yml](semgrep/rules/study.yml): five unchanged
upstream rules at a pinned commit and eleven custom rules. Each rule's purpose,
CWE, provenance, and important limits are recorded in that YAML file. Preserve
the upstream license notice and review its restrictions before redistribution.
The original `practice.yml` remains the one-rule installation check.

```powershell
python .\run-semgrep.py --case version-A --config .\rules\study.yml
python .\run-semgrep.py --case version-B --config .\rules\study.yml
```

These commands do not establish complete weakness coverage or scored results.
Rules were designed from the general requirements and tested on independent
examples, without using application source or placement notes to choose patterns.
The separate [rule fixtures](semgrep/tests/study.py) include target-present and
target-absent controls for every rule. From the Semgrep folder, repeat validation:

```powershell
.\.venv\Scripts\semgrep.exe scan --validate --oss-only --config .\rules\study.yml --metrics=off --disable-version-check
.\.venv\Scripts\semgrep.exe scan --test --config .\rules\study.yml .\tests\study.py --metrics=off --disable-version-check
```

Sixteen rule tests pass with Semgrep CE 1.186.0. This is local pattern verification,
not an independent answer key or a detector accuracy score. General missing
authorization remains unsupported; authentication and login throttling checks
cover explicit library bypass settings only. Missing custom guards, ownership
checks, or lockouts are coverage gaps. See the YAML header for all ten categories.
Do not revise rules to catch missed application locations.

Relative custom config paths resolve from your terminal's current directory;
built-in paths do not. The runner executes Semgrep from the chosen application's
root with relative `backend`, `frontend`, and `firmware` targets. This avoids an
include-filter issue when scanning directories outside Semgrep's working directory.
Practice runs execute from the Semgrep folder.

The runner analyzes only Python files under the selected version's `backend`,
`frontend`, and `firmware` directories. It excludes `.venv`, `__pycache__`,
`.local`, `.git`, and `.env`. Semgrep's default ignore, size, and timeout rules
still apply and are reported in verbose diagnostics. SQL, README files, runtime
credentials, the answer key, and research notes are outside this Python scope.
Review the common scope with the other scanners before freezing the study.

To use a different installation, supply its executable explicitly:

```powershell
python .\run-semgrep.py --case practice --semgrep "C:\path\to\semgrep.exe"
```

The scan command uses `--oss-only --text --strict --error --metrics=off
--disable-version-check --verbose`, the selected local config, explicit Python
scope/exclusions, and target paths. The exact executable command is saved in the
log in PowerShell syntax on Windows. No account login, source execution,
autofix, or report upload is requested by the runner.

## Verification and remaining work

On November 23 the installed Semgrep distribution was 1.186.0. The practice
runner completed with the expected one finding at line 5 and exit code 1.
The sandbox's version command failed with
`ca_certs_iter_on_anchors: CertOpenSystemStore returned NULL`; the runner retained
the failed attempt, and running outside that sandbox succeeded. A terminal
encoding failure found during implementation was corrected; earlier failed
attempt folders remain as history. If that certificate-store error appears in
another environment, consult the saved diagnostics rather than treating it as
an empty successful scan or disabling TLS verification.

Seven temporary verification checks also passed: concurrent stdout/stderr capture
and Unicode/color handling, success with/without findings, scan failure, version
failure, missing executable, required explicit application configuration, and
EST/repeat-name behavior. These checks used controlled subprocess outputs for
failure/status scenarios; only the separate practice scan above used real Semgrep.

Additional November 23 verification: `study.yml` validates with zero configuration
errors and all sixteen annotated rule tests pass. Saved evidence is in
`../../evaluation-runs/semgrep/2026-11-23_03-23-PM_EST_rule-verification-practice/`.
The unchanged final rules were also used for unscored layout smoke checks in
`2026-11-23_03-27-PM_EST_practice/`, `2026-11-23_03-27-PM_EST_version-A/`, and
`2026-11-23_03-27-PM_EST_version-B/` under the same results directory. Each retains
the two standard text outputs. These checks verify file selection and scanner
execution; no rule changes were made in response to application findings.

Earlier `03-24-PM` application attempts selected zero files due to the runner's
working-directory/include interaction. Preserve those attempts; their empty
findings do not establish target absence. Inspect file counts and omissions even
when the runner says `COMPLETED / NO FINDINGS`. None of these checks establishes
full ten-target coverage, application integration, independent case review, or
readiness for scored runs. CodeQL installation/practice verification is now
complete. The study-query implementation described in the CodeQL guide is a
later November 23 update. Snyk Code logging was implemented November 25; see below.

Future agents should retain the per-run comparison files and EST naming contract when maintaining
study queries and the Snyk Code runner, preserving each
tool's different exit-code meanings and query configuration. Use Snyk's free plan
only. Keep practice and scored attempts
explicitly distinguishable, withhold answer keys/injection notes, and do not
tune detector rules against scored-case outputs. Record rule sources, applicable
usage terms, and coverage gaps when selecting final checks.

Reference: [Semgrep CLI options and exit codes](https://docs.semgrep.dev/cli-reference).

## Run Snyk Code

Follow the [Snyk Code guide](snyk-code/README.md) for installation, account login,
practice verification, exact application commands, and reading local results.
From `scanners/snyk-code`, run `python .\run-snyk-code.py --case practice`, then
use `--case version-A` or `--case version-B` for the actual application sources.
No custom rule argument is needed. Findings and diagnostics appear in the terminal;
scanner output and comparison placeholders are saved under `evaluation-runs/snyk-code/<attempt>/`.
The runner omits `--report`, so it does not request dashboard publication.
Snyk Code still uploads selected source for cloud analysis. Ten infrastructure
checks pass, and the real TLS practice scan reports the expected single finding
with Snyk CLI 1.1309.0. Account plan/limits remain unverified; see the guide's evidence.
