# Exact experiment records

Updated October 12, 2026. **No detector choices, test cases, prompts, runs, or results have been finalized or produced in this documentation work.** This folder describes how to record them when they exist.

A diagram explains the process. The records here should let someone see exactly what we did and trace each score back to the code, independent answer, and original output.

## Tool slots

These are temporary labels, not tool names.

| Slot | Exact name | Model ID or tool version | Role | Status |
| --- | --- | --- | --- | --- |
| LLM-01 | Not chosen | Not chosen | Detect weaknesses | Not chosen |
| LLM-02 | Not chosen | Not chosen | Detect weaknesses | Not chosen |
| LLM-03 | Not chosen | Not chosen | Detect weaknesses | Not chosen |
| SCANNER-01 | Not chosen | Not chosen | Detect weaknesses | Not chosen |
| SCANNER-02 | Not chosen | Not chosen | Detect weaknesses | Not chosen |
| SCANNER-03 | Not chosen | Not chosen | Detect weaknesses | Not chosen |

## Records to keep

| Record | What to save exactly |
| --- | --- |
| Study setup | Target CWE IDs, included related entries, supported code, source versions, comparison rules, scoring rules, and agreed run conditions. |
| Detector setup | Provider and model ID or scanner name and version, why chosen, available target checks, settings, rule files, and commands. |
| Test case | Actual code files, file paths, case ID, source and permission where relevant, language, product description, code version, and all context provided. |
| Independent answer | Expected presence or absence for each target, exact expected locations, reasoning, supporting references, reviewer, and unresolved limits. |
| LLM request | Exact full messages as sent, including instructions, examples, target list, code, supplied CWE passages, file order, and any retrieval results. |
| Scanner run | Exact invocation, input files, rules and rule versions, configuration, and execution logs. |
| Original output | Unedited LLM response or scanner report, date, run ID, completion status, and errors. |
| Shared output | Converted findings with target, file, location, evidence, uncertainty, and a link to the original output. |
| Grading | Item-by-item matches to the independent answer, full or partial credit, misses, false alarms, grader, and reasons for disputed decisions. |
| Results | Counts, denominators, per-detector accuracy, partial findings, supporting scores, matrices, repeated-run summaries, and nine pairwise comparison pages. |

A general prompt description is not the exact prompt. A score without its scored items is not a complete result. Do not save passwords, API keys, or account tokens in these records.

## Suggested organization when the experiments begin

The names below describe folders to create as needed. They are not claims that the contents already exist.

```text
experiment-records/
  setup/                 study rules and the six detector configurations
  test-cases/            exact code and supplied context, grouped by case ID
  independent-answers/   checked answers, separate from detector inputs
  prompts/               exact prompt versions and request records
  runs/                  one folder per run, with input references and raw output
  grading/               item-level scoring and reviewer decisions
  results/               six detector score summaries and accuracy matrices
  comparisons/           nine LLM-versus-scanner comparison pages
```

Keep independent answers out of input folders or archives supplied to a detector. If an answer changes after review, retain its earlier version and record why it changed and which scores must be recalculated.

Use [templates](templates.md) for the individual records. Link exact files rather than relying on remembered settings or screenshots of selected answers. If retrieval is allowed in detection, keep each query and each returned passage as part of that run's input record.
