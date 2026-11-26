# LLM study files

This folder holds the three API scripts, their shared logging helper and requirements, the [detection prompt](llm-detection-prompt.txt), and the [evaluation workflow](llm-evaluation-workflow.md). The existing API keys are in this folder's `.env`, which is excluded from Git.

The existing Python environment stays one folder up. From this folder, check a script without sending a request:

```powershell
../.venv/Scripts/python.exe mistral-api-test.py --help
```

Use `gemini-api-test.py` or `groq-api-test.py` for the other providers. Running a script without arguments sends the short connection-test prompt.

The complete prompts already include the code: [Version A](llm-detection-prompt-version-A.txt) and [Version B](llm-detection-prompt-version-B.txt). Each includes all Python files, the database schema, requirements, and `.env.example`, ordered by relative file path. Local `.env` files, runtime files, README files, and answer-key notes are left out. These are snapshots; rebuild them if the source code or prompt changes.

For a detection call, run either command from this folder:

```powershell
../.venv/Scripts/python.exe mistral-api-test.py --model mistral-large-4 --prompt-file llm-detection-prompt-version-A.txt
../.venv/Scripts/python.exe mistral-api-test.py --model mistral-large-4 --prompt-file llm-detection-prompt-version-B.txt
```

The scripts read the text file and send its full contents as the user message. Use the same two files with `gemini-api-test.py --model gemini-3.6-flash` or `groq-api-test.py --model openai/gpt-oss-120b`. Use `--model` to select the study model without automatic fallbacks. Logs still go to `../evaluation-runs/mistral/`, `../evaluation-runs/gemini/`, or `../evaluation-runs/groq/`.

Each attempt now gets an EST-dated folder with the case/version in its name, containing `run-log.json`, `raw-output.txt`, the blank `results-table.csv` grading template, and an empty `confusion-matrices/` folder. The standard A/B prompt filenames identify the version automatically; use `--case version-A` or `--case version-B` for custom study prompts. Short connection tests default to `practice`. See [results notes](../results-notes.md) for commands and the manual accuracy column.
