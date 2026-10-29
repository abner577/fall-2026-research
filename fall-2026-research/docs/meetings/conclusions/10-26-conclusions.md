# October 26, 2026: selected conclusions and follow-up

The professor supported the overall comparison design and the two broad focus areas. Exact weaknesses, project, scanner checks, and scoring details still need definition and review. These notes capture the priorities selected by the student for follow-up, rather than every discussion point. Carry out the resulting study work and save evidence, explanations, and working designs under [CodeBeacon/evaluation-study/](../../../../CodeBeacon/evaluation-study/); meeting records remain under `fall-2026-research/docs/`.

## Scanner selection

The professor suggested Snyk without choosing a replacement at the meeting. The student subsequently selected Semgrep Community Edition, CodeQL, and Snyk Code, replacing Bandit. The student will not pay for access. As checked October 29, [Snyk's pricing page](https://snyk.io/plans/) lists a $0 Free plan with Snyk Code, 100 Code tests per month, and five projects. Confirm account limits, relevant checks, and reporting during setup. If the study requires paid access, do not use it. See [scanner notes](../../../coming-up-w-research-plan/scanner-tools.md#snyk-code-free-plan).

## Shared coherent IoT project

Use an actual Python IoT application with connected functionality, such as a small web service with APIs and possibly a database, rather than unrelated files containing obvious demonstration bugs. The particular architecture remains open. The professor's example can illustrate the intended project coherence; using that project is optional.

Preserve a baseline intended to lack the selected weaknesses, then deliberately introduce vulnerabilities into controlled project versions. Verify presences and absences of the selected targets; do not claim the baseline is free of every possible vulnerability. Know exactly where each inserted weakness is and give all six detectors the same version and agreed context, withholding the answer key and injection notes. No required vulnerability count was agreed. The evaluation diagram should explicitly show the common project feeding both branches; the existing image has not yet been revised.

## Reasons and verification

For each weakness, record why it belongs in the selected focus areas, why it is placed in that application path, the exact code change and location, and evidence that the code actually contains it. Document the verification method, reviewer, date, outcome, and unresolved questions. The professor offered to review the code and potentially involve experts; record that review as complete only after it happens. AI-generated code or explanations alone do not establish the answer key.

## Raw evidence

Whenever an AI assistant helps prepare or run the study, preserve exact prompts and revisions, full responses, scanner reports and errors, exact code versions, commands, configurations/rules, model/tool versions, settings, and dates. Keep original evidence separate from normalized findings and scores. Retain practice and unsuccessful runs and explain why prompts, code, or procedures changed. Illustrative outputs remain distinct from actual results.

Source: [October 26 transcript](../../transcripts/10-26-Weekly%20CAHSI%20Meeting.docx), especially 18:20-24:54, 38:52-58:53, and 1:09:47-1:10:47, plus the student's October 29 follow-up instructions. The clean starting version, realistic application examples, and free-only scanner constraint reflect those follow-up instructions. Current actions are in the [follow-up checklist](../checklist/11-1-checklist.md).
