# Evaluation runs and comparisons

For version A, run all three LLMs first, then all three scanners. Keep every attempt. Manually grade the successful, complete runs, then make all the matrices. Finish documenting version A before repeating the process for version B.

## Where each run goes

Everything below is relative to `evaluation-study/`:

```text
evaluation-runs/
  comparison-notebook.ipynb
  requirements.txt
  gemini/
    2026-11-25_03-30-PM_EST_version-A/
      run-log.json
      raw-output.txt
      results-table.csv
      confusion-matrices/
  groq/                         # Same LLM run structure
  mistral/                      # Same LLM run structure
  semgrep/
    2026-11-25_04-00-PM_EST_version-A/
      run-log.txt
      findings.txt
      results-table.csv
      confusion-matrices/
  codeql/                       # Same scanner structure, plus raw-output.csv
  snyk-code/                    # Same scanner structure as Semgrep
```

Every attempt gets a new folder. Its name uses the start date and time in fixed EST (UTC-05:00 all year), followed by `version-A`, `version-B`, or `practice`. Repeated names get ` (1)`, ` (2)`, and so on. Earlier results are never overwritten. Existing historical files stay where they are.

The LLM scripts automatically save the existing request, response, model, status, and error information in `run-log.json`, with the case and start time. They also write the original answer text to `raw-output.txt`, without rewriting or grading it. Returned reasoning or structured content remains in the JSON log. If no answer arrives, the raw-output file stays empty; check the log.

Scanners automatically save readable findings in `findings.txt` and execution details, commands, versions, warnings, errors, and outcome in `run-log.txt`. CodeQL also retains its original CSV report as `raw-output.csv` when analysis produces one, including partial reports.

Every runner creates `results-table.csv` and an empty `confusion-matrices/` folder. It does not grade results or generate matrices during a run. Setup errors before an attempt starts, such as a missing API key or unreadable prompt, may not create a run folder. Preserve failed attempts, but do not grade them or use them in comparisons.

## Fill in the results table manually

The CSV is a blank grading template: column headers, rows V1 through V10, and a TOTAL row. No results or scores are prefilled.

| Column | What to enter |
| --- | --- |
| `target_id` | Already filled with V1-V10 and TOTAL; keep these identifiers. |
| `expected_answer` | Found or Missing from [answer-key.md](answer-key.md) for this version. |
| `result` | Found, Missing, or Partially Found, after reviewing the original output. |
| `reported_locations` | The locations reported by the tool, or a reference to the saved finding. |
| `explanation` | A short explanation, including the reason for partial credit or a mismatch. |
| `points` | 1, 0.5, or 0 under the [scoring rubric](scoring-rubric.md). Enter the sum in the TOTAL row. |
| `final_accuracy_percentage` | The last column. Enter the overall percentage only in the TOTAL row, for example `85%`. Leave this column blank for V1-V10. |

Calculate the final accuracy as `(TOTAL points / 10) * 100`. Seven full-credit targets and three partial-credit targets give 8.5 points and **85%**. This is the agreed rubric score, including correct absences and partial credit. It is separate from exact label agreement in a matrix. CSV files do not calculate this automatically; enter the grades, total, and percentage manually.

## Commands to check the outputs

Open PowerShell in the study folder:

```powershell
Set-Location "C:/Users/joser/Downloads/fall-2026-research/CodeBeacon/evaluation-study"
```

To test the LLM output layout with short connection requests, run these individually. Each sends an actual API request and creates a `practice` folder:

```powershell
.\.venv\Scripts\python.exe .\llms\gemini-api-test.py --model gemini-3.6-flash --case practice
.\.venv\Scripts\python.exe .\llms\groq-api-test.py --model openai/gpt-oss-120b --case practice
.\.venv\Scripts\python.exe .\llms\mistral-api-test.py --model mistral-large-4 --case practice
```

Test the scanners on their separate practice examples:

```powershell
.\.venv\Scripts\python.exe .\scanners\semgrep\run-semgrep.py --case practice
.\.venv\Scripts\python.exe .\scanners\codeql\run-codeql.py --case practice
.\.venv\Scripts\python.exe .\scanners\snyk-code\run-snyk-code.py --case practice
```

The existing API keys, scanner installations, and Snyk authentication must be available. These commands do not start the application. Scanner exit code 1 means a completed scan reported findings; it is not a runner failure. Check the final outcome in the log.

For the actual version A runs, use the prepared prompts and study scanner checks:

```powershell
.\.venv\Scripts\python.exe .\llms\gemini-api-test.py --model gemini-3.6-flash --case version-A --prompt-file .\llms\llm-detection-prompt-version-A.txt
.\.venv\Scripts\python.exe .\llms\groq-api-test.py --model openai/gpt-oss-120b --case version-A --prompt-file .\llms\llm-detection-prompt-version-A.txt
.\.venv\Scripts\python.exe .\llms\mistral-api-test.py --model mistral-large-4 --case version-A --prompt-file .\llms\llm-detection-prompt-version-A.txt
.\.venv\Scripts\python.exe .\scanners\semgrep\run-semgrep.py --case version-A --config .\scanners\semgrep\rules\study.yml
.\.venv\Scripts\python.exe .\scanners\codeql\run-codeql.py --case version-A --queries .\scanners\codeql\queries\study.qls
.\.venv\Scripts\python.exe .\scanners\snyk-code\run-snyk-code.py --case version-A
```

After finishing version A and its comparisons, repeat these six commands with every `version-A` replaced by `version-B`, including the LLM prompt filenames. The LLM scripts can infer the version from the standard prompt filename; an explicit conflicting `--case` is rejected. Custom study prompt files need an explicit `--case`; otherwise they are labeled practice.

Each command prints its exact results path. Open that folder and check the files shown in the layout above. The table should contain only the template, and the matrix folder should be empty. The raw answer/findings and log should contain the actual run output.

## Make the confusion matrices afterward

Install the notebook dependencies once if needed, then open the notebook from `evaluation-runs/`:

```powershell
.\.venv\Scripts\python.exe -m pip install -r .\evaluation-runs\requirements.txt
Set-Location .\evaluation-runs
..\.venv\Scripts\python.exe -m jupyterlab comparison-notebook.ipynb
```

Set `CASE` to `version-A` and paste one successful run folder name for each of the six tools into `RUNS`. Finish all six results tables first. Run the notebook cells in order. It checks the version, completion status, target IDs, labels, and manual totals before writing any images. Review completeness and evidence yourself before selecting a run.

The notebook uses pandas, Matplotlib, and Seaborn to compare the same ten targets with the categories Found, Missing, and Partially Found:

- Six detector-versus-answer-key matrices: answer key on rows, detector on columns.
- Nine LLM-versus-scanner matrices: scanner on rows, LLM on columns. These show agreement, not accuracy against the answer key.

Each run receives four matrix images in its own `confusion-matrices/` folder: one against the answer key and three against the other detector group. Each image also has a CSV containing the counts. An LLM-scanner comparison is generated once and saved in both participating run folders with the same orientation. Titles record the run names used. The notebook places these files automatically; review the images afterward. Repeating the same selection replaces its generated matrices, while leaving original outputs and grading tables intact.

Repeat for version B only after finishing version A. Run outputs remain local and ignored by Git; the comparison notebook and its requirements file are tracked. Shared runner code lives in `support/run_outputs.py`.
