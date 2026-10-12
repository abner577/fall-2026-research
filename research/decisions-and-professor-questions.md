# Decisions and questions for the professor

Confirmed decisions come from the student or the meeting. The questions below concern the main comparison and still need answers.

## Confirmed decisions

- Milestone 1 compares detection accuracy to select the methodology for development: methodology 1 is scanner-based; methodology 2 is all-AI detection without a code scanner.
- Better or comparable all-AI results provide the go-ahead for all-AI development within the outlined framework. Better scanner results support selecting the scanner methodology. The comparison criteria remain open.
- Compare three LLMs with three scanners: six detectors and nine LLM-versus-scanner pairings.
- Use shared evaluation cases and a comparable output format.
- Define independent correct answers before grading the detectors.
- Define what Partially Found means before scoring.
- Assign each detector an accuracy score against the independent answers.
- Keep Found, Missing, and Partially Found in the reporting plan, while resolving their exact meanings.
- If development proceeds, both detection approaches lead to an LLM suggestion stage supported by CWE guidance.
- Document the methods step by step and retain exact experiment records.
- Prepare six diagrams, with the app-specific diagram conditional on development, and one results document. Keep only plain-English descriptions in the diagram file.
- Show application-controlled CWE retrieval in the workflow diagrams for now, with a note that agent-controlled retrieval remains open.
- Review results and time with the professor before deciding whether to build the app.

## Questions to resolve before the main comparison

### Which two vulnerability targets should we test?

The current password/credential and communication/data-handling areas each contain several possible weaknesses. We need the professor to confirm or narrow them into specific CWE targets so the LLMs, scanners, and grading all refer to the same things.

This is the priority question to ask before finishing the study design: should we confirm these areas first and build the comparison around their specific checks? We need a limited scope so we can select, configure, or write the scanner checks and ask the LLMs to examine the same weaknesses. The student intends to ask by email. If there is no reply, the initial diagrams and mock-ups will use the proposed areas provisionally, with confirmation still pending. See the [meeting checklist](../meetings/next-meeting-checklist.md#priority-question-confirm-the-scope-before-finishing-the-design).

### Which related weaknesses belong in scope?

CWE entries can be related to other entries. We need to decide which of those relationships matter to this study and where to stop. Otherwise a prompt or scanner could cover a much broader set than intended, and we would not know whether a related finding should count.

### Which IoT component, language, and framework should we use?

Firmware, gateways, backends, and browser interfaces involve different code and security checks. We need a shared software scope that all six detectors can examine so differences in results can be interpreted fairly.

### Which three LLMs and three scanners should we choose?

The exact models and tool versions determine access, cost, language support, and the checks available. We need to know which six detectors will actually be evaluated, including whether coding-focused models belong in the comparison.

### Which scanner checks should we use, and what if a target is unsupported?

A scanner can support a language without having a check for the chosen vulnerability. We need to know which rules to enable and how to handle missing coverage so an unsupported check is not confused with a failure to detect a weakness.

### Where should the code cases come from, and how many do we need?

The source, number, and variety of cases affect what we can conclude. We need cases with the selected vulnerabilities and cases where they are absent, and enough variation to avoid basing the methodology choice on only a few similar examples.

### Who will check the correct answers?

We need independently checked answers stating which vulnerabilities are present and where they occur. Agreement between an LLM and a scanner does not prove correctness. We need to know who checks the code and evidence and how disagreements about the expected answers are resolved.

### What counts as one scored item?

A score could count whole cases, each target checked in a case, or each vulnerability location. These choices produce different totals and accuracy percentages. We need one agreed unit so every detector is scored consistently.

### What do Found, Missing, and Partially Found mean?

We need clear definitions so the same finding receives the same grade across detectors. A weakness absent from the code must be distinguished from one that exists but was missed. We also need to know what makes a detection incomplete rather than fully correct.

### What location and evidence must a finding provide?

Mentioning a security concern may not identify the actual problem in the code. We need rules for correct locations, supporting evidence, wrong CWE labels, duplicate reports, and related findings so grading does not depend on an individual reviewer's interpretation.

### How should partial findings affect the scores?

The project requires an accuracy score and confusion matrices, but partial detections do not automatically fit a correct-or-incorrect answer. We need to decide how they enter the main score and whether a separate partial-credit score is wanted before seeing which detector benefits.

### What should we report alongside accuracy?

A high accuracy percentage can hide missed vulnerabilities, false alarms, or poor location accuracy. We need to know which supporting measures the professor expects so the results explain the detectors' strengths and weaknesses clearly.

### Should detection LLMs receive CWE guidance or retrieval tools?

Giving a model reference text or search tools changes the information available during detection. We need to fix what assistance is allowed so the study evaluates a defined condition and differences between runs have a clear meaning.

### What output format should the detectors use?

The professor discussed making LLM reports resemble scanner reports. We need to clarify whether the LLM should follow each scanner's format or whether all findings should be presented in one shared format. This affects prompts and how results are matched without losing the original meaning.

### How many LLM runs should we repeat, and which settings should stay fixed?

An LLM may produce different findings on repeated requests. We need an agreed repetition and summary procedure so the results reflect that variation and do not simply select the best response.

### How should errors and incomplete runs affect scoring?

Unsupported files, missing context, and failed runs can prevent a detector from completing a case. We need rules for their treatment so excluding failures does not quietly make a detector appear more accurate.

### How should the confusion matrices and nine comparisons be presented?

A matrix against independently checked answers shows accuracy; a table comparing two detectors directly shows agreement. We need to know which visuals the professor expects and how they should appear in the results document so those two meanings remain clear.

### What feedback does the professor have on the requested diagrams and results document?

The requested set is six diagrams and one results document, with the specific app diagram conditional on development. We need to check that their explanations cover the intended research process and the professor's six methods before producing the visuals.
