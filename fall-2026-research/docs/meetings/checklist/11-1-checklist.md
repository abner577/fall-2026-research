# Evaluation study preparation checklist: November 1

**Current phase: setup and preparation, before executing the scored evaluation study.** The overall design and tool choices are established; the next major step is to put the resources, code, connections, scanner checks, prompts, answer key, and scoring procedure in place.

This is a rolling checklist starting with the November 1 meeting, following the [October 26 conclusions](../conclusions/10-26-conclusions.md). It is not a promise to finish everything by that meeting. Continue using this same checklist in later meetings, checking off completed work and recording what remains. Work through the sections in order; draft vulnerability records while building the cases, then finalize and independently verify the answer key in section 6.

Carry out the study under [CodeBeacon/evaluation-study/](../../../../CodeBeacon/evaluation-study/). Save all study code, documents, prompts, logs, working designs, and evidence there. `CodeBeacon/app/` is reserved for the optional application if development proceeds and time permits; this checklist and other meeting records remain in `fall-2026-research/docs/`. See the [evaluation plan](../../../coming-up-w-research-plan/evaluation-plan.md) for the agreed design and remaining implementation details.

Check an item only when its deliverable exists and any required verification is complete. Add the completion date and a relative link to the file or evidence beside it. Leave partial work unchecked and add a short progress note or blocker. The items below are pending setup work, not completed experiments.

## 1. Select the exact LLM API models

- [ ] Record the exact API model identifier for the three choices: Mistral Large 4 (`mistral-large-4`), Gemini, and GPT-OSS-120B through Groq (`openai/gpt-oss-120b`). Mistral replaces the earlier direct OpenAI API option; GPT-OSS through Groq replaces Qwen. Record `ministral-14b-2512` and `ministral-8b-2512` as Mistral connection-test backups and `openai/gpt-oss-20b` as the only Groq fallback, not additional detectors. Both GPT-OSS models passed practice requests on October 29; see the [Groq connection-test script](../../../../CodeBeacon/evaluation-study/groq-api-test.py). Select the exact Gemini study model and record the selection reasons and any necessary change.
- [ ] Verify usable API access, available credits or free access, request/token limits, and context limits for each chosen model. Mistral Large 4 and both connection-test backups have passed practice requests; GPT-OSS-120B and GPT-OSS-20B through Groq also passed practice requests on October 29. Gemini study-model verification and complete study allowances still need checking. Fit preparation and planned runs within existing resources, without additional spending.
- [ ] Create a model configuration record containing provider, exact model ID or pinned version where available, endpoint, API/client version, supported generation settings, and date checked. Record whether a model alias can change during the study.

## 2. Set up and test the API connections in files

- [ ] Prepare the Python environment and dependency/version record. Configure credentials outside committed code, with an example configuration containing placeholders and instructions for loading the credentials.
- [ ] Create a runnable connection-test file for each provider, or a shared test script with a separate configuration for each. Document the command needed to test each connection.
- [ ] Send a small practice request to each exact model and confirm authentication, the requested model, a complete response, and usable output capture. Save the test input, response, date, settings, and any errors without saving API secrets.
- [ ] Prepare handling for timeouts, rate limits, retries, and incomplete responses. Log each attempt so a failed request or retry cannot silently become a successful scored run.
- [ ] Establish the study folders and naming convention for configurations, cases, vulnerability records, answer keys, prompts, raw evidence, normalized findings, and scores. Keep answer keys and injection notes outside the code folders supplied to detectors.

## 3. Develop and document the code test cases

- [ ] Choose the coherent Python IoT application's component, framework/libraries, connected features, size, folder structure, and file structure. Document why this scope is manageable and appropriate for the comparison; APIs and a database are options, not requirements.
- [ ] Select the specific weaknesses and CWE entries within the accepted password/credential and communication/data-handling focus areas. Define the boundary for related weaknesses and explain each selection using reference guidance.
- [ ] Decide the number and variety of project versions and vulnerability instances. Include target-present and target-absent cases and different realistic appearances of the selected weaknesses; no fixed count has been agreed.
- [ ] Choose a documentation format and create a vulnerability register under `CodeBeacon/evaluation-study/` (for example, a spreadsheet with links to detailed notes). Give each project version, case, and vulnerability a stable ID, such as `VULN-001`, `VULN-002`, and `VULN-003`.
- [ ] Build or adapt the coherent application and preserve a baseline intended to lack the selected weaknesses. Record its source/provenance, dependencies, setup instructions, and exact code version. Absence of the selected weaknesses does not establish that the whole application is secure.
- [ ] Create controlled vulnerable versions. For each injection, record its ID, case/version, CWE, exact file and function/line range, before/after code change, vulnerable behavior, and why it is a vulnerability and belongs at that location in this application.
- [ ] Record the intended target presences and absences for every case, including controls. Preserve the exact code versions or hashes and differences so the supplied inputs and answer locations remain traceable after edits.
- [ ] Prepare separate practice cases for scanner setup, rule development, prompt refinement, and scoring checks. Keep these distinct from the final scored cases so procedures can be refined before the main comparison.

## 4. Install and verify the three scanners

Use the selected tools: **Semgrep Community Edition, CodeQL, and Snyk Code**. Snyk Code replaces Bandit. See the [scanner notes](../../../coming-up-w-research-plan/scanner-tools.md).

- [ ] Install/configure Semgrep CE, record its version and dependencies, and run an example rule against a practice file. Save the command, rule, original report, and any errors.
- [ ] Install/configure CodeQL, record CLI and query-pack versions, and verify Python database creation and an example query on practice code. Save the commands, configuration, original report, and any errors.
- [ ] Set up Snyk Code access and its CLI, record versions, and test source-code analysis and report export on practice code. Verify actual account limits and report usability using the free plan only; no paid upgrade is authorized.
- [ ] Confirm that each scanner can read the chosen framework and project layout. Document excluded files, analysis limits, and report fields; distinguish a failed scan from a successful scan with no findings.

## 5. Prepare the rules, queries, and scanner commands

- [ ] Map every selected weakness to each scanner's relevant existing checks. Record rule/query IDs, sources, versions, applicable usage terms, and any coverage gaps; language support alone does not establish target coverage.
- [ ] Select, adapt, or write the Semgrep rule files needed for the chosen application and targets. Document what each rule checks and test it on separate target-present and target-absent practice cases.
- [ ] Select, adapt, or write the CodeQL queries and query suite needed for the application and targets. Document what each query checks and test it on separate target-present and target-absent practice cases.
- [ ] Determine which Snyk Code checks and configuration options are available for the targets. Document coverage and limitations rather than assuming it accepts custom rule files like Semgrep or CodeQL.
- [ ] Set a common target scope and a documented treatment of unsupported checks. Identify custom versus built-in checks in reporting; do not use hardcoded answer locations or tune checks against scored-case outputs.
- [ ] Save the exact scanner commands, rule/query files or pinned references, exclusions, configurations, and report-export commands. Make each scanner procedure repeatable from the documented environment.

## 6. Finalize the answer key, scoring, reporting, and prompts

### Independent answer key

- [ ] Turn the vulnerability register into a separate answer key: for each case and target, record presence/absence, vulnerability IDs where present, exact code version, locations, explanation, and supporting evidence. Keep it separate from detector inputs.
- [ ] Verify target presences and absences independently of the evaluated detectors. Record the reviewer, verification method, date, evidence, outcome, and any disagreement; AI-generated cases or answers are not validated merely because an AI produced them.
- [ ] Arrange professor review and any additional independent review needed before scored runs. Resolve disputed or incomplete cases, record the outcome when review occurs, and finalize the answer-key version.

### Scoring and confusion matrices

- [ ] Define the scoring unit and denominators, including how multiple vulnerability locations and target-absent cases are counted. Define a finite set of negative opportunities so true negatives are not based on an arbitrary count of safe lines.
- [ ] Finalize Found, Missing, and Partially Found definitions and matching requirements for weakness, location, and evidence. Specify treatment of related/wrong CWE labels, duplicate warnings, vague findings, false alarms, and out-of-scope findings.
- [ ] Finalize and save the accuracy-score criteria and formulas. Review the proposed 1/0.5/0 partial-credit scheme; label its percentage as detection of known vulnerabilities and report false alarms separately. Decide any additional measures and their undefined/zero-denominator handling.
- [ ] Define exactly how findings become true positives, false positives, false negatives, and true negatives. Decide how partial findings enter the confusion matrices, while retaining their separate grading labels.
- [ ] Prepare templates for six detector-versus-answer confusion matrices and nine LLM-versus-scanner comparisons. Reuse the six detectors' results for the nine pairings; distinguish accuracy against the answer key from agreement between detectors.
- [ ] Specify how failed, unsupported, incomplete, and disputed results affect scores and reporting, and how a second reviewer checks judgment-based grades. Decide how repeated runs will be summarized and what evidence counts as better or comparable performance for methodology selection.

### Common reports and consistent run conditions

- [ ] Prepare the common findings format: run ID, detector/model version, case/code version, weakness/CWE, file, location, explanation/evidence, and uncertainty where available. Preserve original output separately and document each scanner's field mapping without adding findings it did not report.
- [ ] Prepare grading and results templates linking each judgment to the raw finding and answer-key entry, with reasons for partial credit, mismatches, and disagreements. Include scores, confusion matrices, nine comparisons, limitations, and the eventual methodology decision.
- [ ] Define the exact input package and context supplied to all six detectors: identical project versions, selected targets, project description, file inclusion/exclusion, and any file ordering or chunking. Withhold the answer key, injection notes, and other detectors' scored-case outputs.
- [ ] Finalize model settings, context/output limits, repetition count, run ordering, and retry policy. Document unavoidable provider/tool differences, a run schedule within available limits, and how all repetitions will be retained rather than selecting the best result.
- [ ] Prepare the run logging procedure or scripts to save exact supplied files, prompts and revisions, complete responses, scanner reports/errors, commands, configurations/rules, versions, settings, dates, and reasons for revisions. Keep originals separate from normalized findings and scores; retain practice and unsuccessful runs too.

### Exact prompts and call procedures

- [ ] Write and save the exact system/user prompts and code-packaging template for each scored detection call. Use the agreed targets and output structure, without supplied CWE guidance, CWE retrieval, scanner answers, or answer-key hints during detection.
- [ ] Document every planned LLM call: purpose, inputs, exact prompt/version, expected output, and where the response is saved. Identify any multi-step detection procedure in advance and apply comparable conditions across models.
- [ ] Define the boundary for later suggestion-stage calls. If included in the prepared workflow, save their prompts and retrieval inputs separately; CWE guidance is retrieved only after detection. Suggestion quality remains outside this detection-accuracy study, so application-only setup need not delay it.

## 7. Check readiness before executing the scored study

- [ ] Run the complete preparation workflow on separate practice cases: API calls, scanner commands, raw evidence capture, output normalization, answer matching, scoring, and confusion-matrix generation. Manually check the calculated results against the practice answers.
- [ ] Resolve practice-run problems and preserve the revised files, earlier evidence, and reasons for changes. Confirm the full study still fits available API resources and scanner limits without additional spending.
- [ ] Update the evaluation diagram to show the shared IoT project feeding both detector branches, with the independent answer key and injection notes kept separate from detector inputs.
- [ ] Review remaining blockers and complete the required independent answer review. Freeze the code cases, answer key, model/tool configuration, scanner checks, prompts, run procedure, and rubric as a documented study version before scored runs.
- [ ] Record readiness and the next action: execute the six detectors on the finalized shared cases, then grade and compare their results. Starting those scored runs is the next phase after this preparation checklist.

## Progress to carry into the next meeting

Update this short record at each meeting while keeping the checklist above in use.

| Meeting/date | Completed items and evidence | Work in progress | Blockers or decisions needed | Next items in order |
| --- | --- | --- | --- | --- |
| November 1, 2026 | To update | To update | To update | Start with section 1; continue from the first unfinished dependency. |
