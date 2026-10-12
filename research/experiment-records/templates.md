# Experiment record templates

These are blank forms. **TBD** means still to be decided. **Not run** means no result exists. None of the tables below contains project results. Copy a form into a separate record when the item exists; keep this template blank.

## Study setup

- Study version and date: TBD
- Research question: TBD
- Two target names and CWE IDs: TBD
- Included related entries and selection reasons: TBD
- Language, framework, and application context: TBD
- CWE and other reference versions: TBD
- Number and mix of cases: TBD
- What counts as one scored item: TBD
- Rules for full findings, partial findings, absence, and false alarms: TBD
- Location, duplicate, related-finding, and uncertainty rules: TBD
- Accuracy formula, partial-credit rule, and other measures: TBD
- Rules for errors and unsupported items: TBD
- Number of repeated runs and how they are summarized: TBD
- Reviewers and review process: TBD
- Professor review and agreed changes: TBD

## Detector setup: make six records

- Detector slot: TBD
- Exact provider/model ID or scanner name/version: TBD
- Access method and date: TBD
- Why selected: TBD
- Supported language and target checks: TBD
- Settings: TBD
- Prompt version or scanner configuration and rule-file paths: TBD
- Exact command, if applicable: TBD
- CWE guidance or retrieval allowed during detection: TBD
- Known limits: TBD

## Test case: make one record per case

- Case ID: TBD
- Exact code folder and version: TBD
- Source and use conditions, if applicable: TBD
- Language and framework: TBD
- Product description and assumptions supplied to every detector: TBD
- Target checks in scope: TBD
- Included files and file order: TBD
- Any preparation or excluded files and reason: TBD
- Independent-answer record: TBD (keep this reference out of detector inputs)

## Independent answer: define before the scored runs

- Case ID and code version: TBD
- Answer version and date: TBD
- Prepared by and independently checked by: TBD
- How the answer was checked: TBD

| Answer item ID | Target CWE | Present or absent | Expected file and location | Reason and reference | Missing context or dispute |
| --- | --- | --- | --- | --- | --- |
| TBD | TBD | TBD | TBD | TBD | TBD |

If several weakness locations exist, list them and apply the agreed scoring rule. Record absence only within the named target and available context. Include the decision and reason if a reviewer changes an answer.

## Exact prompt or request record

- Prompt version: TBD
- Detector slot and run ID: TBD
- Exact system/developer instructions, if any: TBD
- Exact user message: TBD
- Exact attachments, code files, and order: TBD
- Exact CWE text and source version supplied: TBD
- Output structure requested: TBD
- Examples supplied, if any: TBD
- Tool definitions, if applicable: TBD
- Retrieval requests and returned content, if allowed: TBD

Save the actual messages in a text or structured file and link them here. General and two-target prompts need separate versions if they differ. Do not substitute a summary for the submitted prompt. Do not include the expected answer in a scored request.

## Run record

- Run ID: TBD
- Detector setup record: TBD
- Case ID and code version: TBD
- Run number: TBD
- Date, time, and timezone: TBD
- Exact request or scanner invocation record: TBD
- Input and configuration file paths: TBD
- Original output path: Not run
- Logs and errors: Not run
- Status: Not run
- Shared-format output path: Not run
- Any deviation from the agreed procedure: TBD
- Time or cost, if measured: Not run

## Item-by-item grading

| Run ID | Answer item ID | Detector finding and location | Full, partial, miss, correct absence, or false alarm | Credit under agreed rule | Reason | Reviewer |
| --- | --- | --- | --- | --- | --- | --- |
| Not run | TBD | Not run | Not run | Not run | Not run | TBD |

Also record unmatched warnings, duplicates, out-of-scope warnings, and failed or unsupported items according to the study rules. They should not disappear during output conversion.

## Detector score summary: make six records

- Detector and configuration: TBD
- Cases, runs, and answer version included: Not run
- Scoring-rule version: TBD
- Total planned items: TBD
- Total scored items and any exclusions with reasons: Not run
- Correct detections: Not run
- Missed weaknesses: Not run
- False alarms: Not run
- Correct absences: Not run
- Partial findings and how they entered scoring: Not run
- Errors, unsupported items, and incomplete runs: Not run
- Accuracy calculation, numerator, denominator, and percentage: Not run
- Optional partial-credit score, clearly labeled: Not run
- Location results and other agreed measures: Not run
- Variation across repeated runs: Not run
- Linked grading records: Not run

## Accuracy confusion matrix

Use this only after agreeing how partial findings and failures enter the four outcomes. Record its detector, target scope, answer version, run grouping, and number of scored items.

| Independent answer | Reports weakness | Reports no weakness |
| --- | --- | --- |
| Weakness present | Not run: correct detections | Not run: misses |
| Weakness absent | Not run: false alarms | Not run: correct absences |

## Pairwise comparison: make nine records

- Pair ID: TBD (for example, LLM-01 versus SCANNER-01)
- Shared cases, targets, and run-summary rule: TBD
- LLM score summary and accuracy matrix: Not run
- Scanner score summary and accuracy matrix: Not run
- Difference in accuracy and other agreed measures: Not run
- Which items both got right or both got wrong: Not run
- Items where only one got the right answer: Not run
- Examples of partial findings and disagreement: Not run
- Optional agreement table, labeled as agreement: Not run
- Practical differences or coverage limits: Not run
- Conclusion supported by these cases: Not run

Link the two accuracy matrices. If a prediction-agreement table is included, do not call it accuracy against the independent answer.

## Final decision record

- Meeting date and participants: TBD
- Results reviewed: Not run
- Remaining time and revised schedule: TBD
- Decision: conclude the study, improve the study, or begin development — TBD
- Reason and limits: TBD
- Selected detection method, if developing: TBD
- Next tasks and files to update: TBD
