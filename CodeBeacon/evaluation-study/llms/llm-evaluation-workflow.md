# LLM evaluation workflow

## 1. Open PowerShell in the right folder

```powershell
cd "C:\Users\joser\Downloads\fall-2026-research\CodeBeacon\evaluation-study\llms"
```

The scripts use the existing Python environment in `../.venv/` and load keys from this folder's `.env`: `MISTRAL_API_KEY`, `GEMINI_API_KEY`, and `GROQ_API_KEY`.

The command runs the API script directly. The model reviews code sent as text, so there is no need to start Flask, Streamlit, PostgreSQL, or the device first.

## 2. Check the input

The complete [Version A](llm-detection-prompt-version-A.txt) and [Version B](llm-detection-prompt-version-B.txt) prompts already contain the study context, ten target types, and that version's code, labeled by relative path. Use these same two files for all three models. They are saved snapshots; update them before running if the application code changes. Keep the answer key and scanner results out of the requests.

## 3. Send the requests

For version A, run all LLMs, then all scanners, then complete grading and comparisons. Repeat for version B afterward. The commands below are grouped by provider for reference; execute only the current version. Run these one at a time and check each result before moving on. Each command sends one request for one model and one version.

Mistral, Version A and then Version B:

```powershell
..\.venv\Scripts\python.exe .\mistral-api-test.py --model mistral-large-4 --prompt-file .\llm-detection-prompt-version-A.txt
..\.venv\Scripts\python.exe .\mistral-api-test.py --model mistral-large-4 --prompt-file .\llm-detection-prompt-version-B.txt
```

Gemini, Version A and then Version B:

```powershell
..\.venv\Scripts\python.exe .\gemini-api-test.py --model gemini-3.6-flash --prompt-file .\llm-detection-prompt-version-A.txt
..\.venv\Scripts\python.exe .\gemini-api-test.py --model gemini-3.6-flash --prompt-file .\llm-detection-prompt-version-B.txt
```

GPT-OSS through Groq, Version A and then Version B:

```powershell
..\.venv\Scripts\python.exe .\groq-api-test.py --model openai/gpt-oss-120b --prompt-file .\llm-detection-prompt-version-A.txt
..\.venv\Scripts\python.exe .\groq-api-test.py --model openai/gpt-oss-120b --prompt-file .\llm-detection-prompt-version-B.txt
```

Keep `--model` so the script uses that model without switching to a backup. Keep `--prompt-file` so it sends the full study request; without a supplied prompt it only sends a connection test. These six commands cover one pass through the three models and two versions; they don't set a repetition policy.

## 4. Get the saved results

The terminal displays the answer or error and a `Log saved to:` path. Open that exact JSON file, for example:

```powershell
notepad "..\evaluation-runs\mistral\2026-11-25_03-30-PM_EST_version-A/run-log.json"
```

Replace the example with the path printed for your run. Results go to:

- Mistral: `../evaluation-runs/mistral/`
- Gemini: `../evaluation-runs/gemini/`
- Groq: `../evaluation-runs/groq/`

Each API attempt creates an EST-dated run folder labeled with the version. It contains `run-log.json`, `raw-output.txt`, the blank `results-table.csv` template, and an empty `confusion-matrices/` folder. The JSON retains `model_used`, `request`, `http_status`, `error`, and `response`, plus the case and start time. Repeat folder names are numbered without overwriting earlier runs. See [results notes](../results-notes.md) for the complete layout and commands.

Check that `error` is `null` and that the answer covers all ten targets and is complete. A successful HTTP response alone doesn't establish that. Keep unsuccessful attempts and resolve the error before using a complete result for grading. Don't select a rerun just because it scored better.

## 5. Read the report

The prompt asks for this block for each detected target, repeating the instance block for every location:

```text
Vulnerability: [type we asked it to check]
Detected: Yes

Instance 1:
File: [relative file path]
Location: [function and line number or range]
Explanation: [why the code at this location has this vulnerability]

Instance 2:
File: [relative file path]
Location: [function and line number or range]
Explanation: [why the code at this location has this vulnerability]
```

If it finds none for a type, use only:

```text
Vulnerability: [type we asked it to check]
Detected: No
```

The prompt asks for all ten sections, in target order, without extra text or Markdown fences. `Detected: No` means the model didn't detect that type; we still check whether that's correct. The scripts save what the model returns; they don't enforce this layout.

For Mistral, read `response` (text or content blocks). For Gemini, read the text in `response` parts without `thought: true`. For Groq, read `response.content`; `response.reasoning` is separate when returned. Grade the reported findings, keeping any returned reasoning available as supporting output.

## 6. Grade and compare

Open the [answer-key table](../answer-key.md) and use the workbook when you need the full explanation. Fill the generated `results-table.csv` for each run, keeping the original JSON unchanged. Its fields follow this grading structure:

| Target | Expected answer | Found / Missing / Partially Found | Points | Location and short reason |
| --- | --- | --- | --- | --- |
| V1 | From the answer key | From our review | 1, 0.5, or 0 | Reference the saved finding |

Continue through V10. Follow the [scoring rubric](../scoring-rubric.md): correct presence with all instances and locations earns 1; correct absence earns 1; partial detection earns 0.5; an incorrect result earns 0. Location judgments depend on context. Add the points and calculate `(total / 10) * 100`. Enter the sum in the TOTAL row and the overall percentage in its last column, `final_accuracy_percentage` (for example `85%`). These grades and percentages are manual; the API scripts do not calculate them. Once all six runs for a version are complete and graded, use the shared notebook as described in [results notes](../results-notes.md).

Compare each model's score with the other models and the scanners for the same version. Keep Version A and Version B scores separate. For the final assessment, state which approach performed better on these cases, where it missed or only partly found targets, and any relevant limits. Support that assessment with the scores and examples from the saved findings. Don't treat a higher score on these cases as proof that a tool is always better.

See [results-notes.md](../results-notes.md) for both the LLM and scanner output locations. Local run outputs are ignored by Git, while the comparison notebook is tracked; committing this guide doesn't preserve those outputs in Git.
