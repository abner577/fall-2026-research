# LLM study files

This folder holds the three API scripts, their shared logging helper and requirements, the [detection prompt](llm-detection-prompt.txt), and the [evaluation workflow](llm-evaluation-workflow.md). The existing API keys are in this folder's `.env`, which is excluded from Git.

The existing Python environment stays one folder up. From this folder, check a script without sending a request:

```powershell
../.venv/Scripts/python.exe mistral-api-test.py --help
```

Use `gemini-api-test.py` or `groq-api-test.py` for the other providers. Running a script without arguments sends the short connection-test prompt.

For a detection call, first copy the detection prompt into a separate `prepared-request.txt` and replace the project-file placeholders with the actual relative paths and complete file contents for one version. Then run:

```powershell
../.venv/Scripts/python.exe mistral-api-test.py --model mistral-large-4 --prompt-file prepared-request.txt
```

Use `--model` to select the study model without automatic fallbacks. Logs still go to `../evaluation-runs/mistral/`, `../evaluation-runs/gemini/`, or `../evaluation-runs/groq/`.
