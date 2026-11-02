# Application constants workbook

Recorded November 2, 2026, including the student's external-file clarification. The student requested a short, maintained Excel reference for the fixed study definitions, suitable for sharing with the professor. The actual workbook is kept in another folder on the student's computer, outside this repository. Its external path is unspecified. Keep its requirements, decisions, and progress in this Markdown document under evaluation preparation. The workbook is documentation, not a configuration file loaded by the application.

## Instructions for future AI agents

References to the "constants Excel sheet," "vulnerability workbook," or "Excel file with V1–V10" mean this externally maintained workbook. This document is the repository's requirements and progress reference; it must remain understandable without the `.xlsx` file. Use the linked selection and version-planning documents for the underlying definitions and examples.

Do not assume the workbook exists at a repository-relative path, search for a personal copy, require access to it for planning, or automatically recreate, move, or synchronize it. If the student asks to edit the actual workbook, use the copy or location they supply. Update these notes with new decisions and clearly distinguish a documented plan from an edit actually made to the external file. Do not assume that its current contents still match the initial export.

## Scope and progress

- **Vulnerabilities — create now:** one row for each selected type, V1–V10, with a simple definition, why it matters, a typical cause, the vulnerability boundary and a safe comparison, and the planned temperature/fan application example. Include planned CWE references and keep the wording short.
- **Version A and Version B test cases — later:** eventually record exactly which types are present and absent, each instance's file, function/operation, line range, saved code revision/hash, explanation, safe comparison, and verification evidence/status. Do not create these tabs now. Planned placement is not a confirmed finding.
- **Explanation content — requirements recorded, tab deferred:** explain where each finding is, what the code does, why it is vulnerable, why it matters, the conditions needed, and what vulnerable versus protected behavior looks like. Include supporting code, a suggested change and setup instructions where needed, guidance sources, and missing context. This follows the existing [report design](../coming-up-w-research-plan/application-workflows.md#saved-uploads-and-findings-reports).

Last known progress: an initial `application-constants.xlsx` export was created on November 2 with only the `Vulnerabilities` tab and all ten V1–V10 entries. Version A, Version B, and explanation tabs were not created. That initial generated export is a delivery artifact, not the maintained repository location. The student manages the personal copy outside this repository; no move or synchronization is claimed by this documentation update.

## Worksheet contents

The first tab, `Vulnerabilities`, has exactly ten type rows, V1 through V10. Its table columns are:

| Column | Expected content |
| --- | --- |
| ID | Stable type ID, V1–V10. |
| Vulnerability / meaning | Selected weakness name and a short, plain-language definition. |
| Why it matters | The practical consequence, in one short explanation. |
| Typical cause | The usual developer mistake or omission. |
| Boundary / safe comparison | What makes it count as this weakness, and what a protected or non-vulnerable example looks like. Identify missing context or undecided thresholds. |
| Planned application example | How the temperature-monitoring/fan-control application represents the weakness, including the planned component or operation. Do not imply an unimplemented example is a confirmed finding. |
| Planned CWE reference | The planned CWE ID and reference URL; confirm the final mapping against the implemented defect. |

Keep the wording simple and concise; this is a quick reference for the student and professor, not an exhaustive security specification. Introductory notes should state the update date and whether examples are planned or verified.

The future Version A and Version B tabs should each distinguish type presence/absence from individual instances. For every present instance, include its type ID, version-specific placement ID, exact source location and revision, behavior, vulnerability explanation, consequence and conditions, comparison/fix, and verification status/evidence. For absent types, record the relevant protection and how it was checked. For missing checks, identify the operation and lines where a check is required. Mark unknown locations or unverified behavior explicitly. The existing plans select eight types for A and three for B, with V7 shared; those are intended selections, not verified final findings or instance counts.

The explanation material should cover vulnerable and protected examples, locations, causes, consequences, suggested changes, sources, and uncertainty. A separate explanation tab is a planned option; its exact name and layout are not yet fixed. Do not add any deferred tabs solely because their requirements appear here.

## Stable type IDs

Use the accepted order in [selected vulnerabilities](../app-idea/selected-vulnerabilities.md#november-2-selection-update). Type IDs apply across the project; version placement IDs such as A-04 and B-01 are separate.

| Type ID | Selected vulnerability | Existing planned placement IDs |
| --- | --- | --- |
| V1 | Hardcoded credentials | A-01 |
| V2 | Weak password requirements | A-02 |
| V3 | Unsafe password storage | A-03 |
| V4 | Unencrypted sensitive communication | B-01 |
| V5 | Secrets exposed in logs or files | A-04 |
| V6 | Missing endpoint authentication | A-05 |
| V7 | Missing endpoint authorization | A-06, B-02 |
| V8 | Predictable generated credentials | A-07 |
| V9 | Disabled certificate verification | A-08 |
| V10 | Insufficient restriction of repeated authentication attempts | B-03 |

## Sources, boundaries, and maintenance

Use the newer [Version A](version-a-planning.md) and [Version B](version-b-planning.md) designs for examples. V3 is an insufficient-cost salted password hash, superseding the older plaintext illustration. V5's selected example is a log disclosure. CWE mappings describe the planned defects and must be checked against the implemented root causes.

Exact functions, routes, line numbers, password rules, hash cost, and attempt-limit parameters remain pending; the workbook does not invent these values. Application examples are planned, not implemented or independently verified findings. This step does not generate application code or a scored answer key.

Keep definitions and boundaries synchronized with design decisions. When implementation exists, add version tabs with exact source locations and evidence, preserve earlier revisions, and document target-absent protections and unresolved concerns. Obtain the independent review required by [code-case-design.md](code-case-design.md#required-vulnerability-record-for-every-code-version) before freezing the scored answer key.

Build note: the required artifact-tool loader was unavailable in this session. The student explicitly approved creating the `.xlsx` with Python's standard library instead. Reopened the saved ZIP/XML package, checked every saved cell against the prepared content, confirmed one sheet and ten unique type IDs, and checked the table/filter and frozen headers. There are no formulas. Reviewed an approximate layout preview using Windows text measurements and verified the text fits; the workbook has not been opened or rendered in Excel itself.
