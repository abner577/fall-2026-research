# Where the results go

Everything below is relative to this `evaluation-study/` folder. The scripts save the output for us and print where they saved it.

## LLMs

Use the scripts in `llms/` with `--model` and the Version A or Version B prompt file. The [LLM README](llms/README.md) has the commands. Running without a prompt just sends the short connection test.

Each API attempt saves one `.json` file:

| Model/provider | Results folder | Example filename |
| --- | --- | --- |
| Mistral | `evaluation-runs/mistral/` | `2026-11-25_large-4.json` |
| Gemini | `evaluation-runs/gemini/` | `2026-11-25_3.6-flash.json` |
| GPT-OSS through Groq | `evaluation-runs/groq/` | `2026-11-25_gpt-oss-120b.json` |

Repeat filenames get ` (1)`, ` (2)`, etc., so earlier attempts stay there. The filename doesn't say Version A or B; check the saved request to see which code was sent.

Open the JSON file in an editor. It contains the model used, the request we sent, HTTP status, any error, and the model's response. An error-free attempt has `error: null`. Setup problems before an API attempt, like a missing key or unreadable prompt file, print an error and may not create a result file.

The answer is under `response`: Mistral saves text or content blocks, Gemini saves a list of parts (answer text is in parts without `thought: true`), and Groq saves the answer in `response.content`, with reasoning separately in `response.reasoning` when returned.

The prompt asks for one section per target, like this:

```text
Vulnerability: [type]
Detected: Yes

Instance 1:
File: [relative path]
Location: [function and line number or range]
Explanation: [why this is vulnerable]
```

It repeats the instance block if there are more locations. If it finds none, the section is just `Vulnerability: [type]` and `Detected: No`.

That's the requested layout; the script saves what the model actually returns. We still check the answer's structure and completeness ourselves.

## Scanners

Run the scanner's runner. The commands are in the [Semgrep guide](scanners/README.md), [CodeQL guide](scanners/codeql/README.md), and [Snyk Code guide](scanners/snyk-code/README.md).

Results go under `evaluation-runs/semgrep/`, `evaluation-runs/codeql/`, or `evaluation-runs/snyk-code/`. Each attempt gets a dated folder with the time and case, such as `2026-11-25_11-30-AM_EST_version-A/`. Repeats get numbered instead of overwritten.

Each attempt folder has two files:

- `findings.txt`: the readable scanner results, including its reported locations and descriptions.
- `run-log.txt`: the command, versions, timing, progress, warnings, errors, and whether the scan completed.

Scanner reports keep each tool's own layout. They aren't automatically turned into the ten-row grading table. Check the log before treating no findings as Missing. Keep failed attempts, leave them out of scoring, and rerun them.

## Grading afterward

Keep the original output. Compare it with the [answer key](answer-key.md), then record Found, Missing, or Partially Found and points separately using the [rubric](scoring-rubric.md). These scripts don't calculate those grades or percentages for us.

The `evaluation-runs/` files are saved locally and ignored by Git, so committing the notes doesn't automatically save the run results to Git.
