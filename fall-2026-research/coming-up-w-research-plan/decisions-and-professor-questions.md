# Decisions and questions for the professor

This file is part of the planning record in `fall-2026-research/`. Carry out the study, save raw evidence and explanations, maintain working designs and architecture, and place any future application code under [CodeBeacon/](../../CodeBeacon/README.md); meeting records remain in `fall-2026-research/docs/`.

Confirmed decisions come from the student or the meeting. The questions below concern the main comparison and still need answers.

## Confirmed decisions

- Milestone 1 compares detection accuracy to select the methodology for development: methodology 1 is scanner-based; methodology 2 is all-AI detection without a code scanner.
- Better or comparable all-AI results provide the go-ahead for all-AI development within the outlined framework. Better scanner results support selecting the scanner methodology. The comparison criteria remain open.
- Compare three LLMs with three scanners: six detectors and nine LLM-versus-scanner pairings.
- October 14 student choice: use Gemini, ChatGPT/OpenAI, and Groq as the three LLM providers. The Groq model is now Qwen 3.8 27B (`qwen/qwen3.8-27b`); exact Gemini and OpenAI API models remain to be selected.
- The first LLM call detects weaknesses without supplied CWE guidance or CWE retrieval. After detection, the application retrieves CWE guidance for a separate suggestion call.
- Current scope and scanner choices, updated October 29: all study code examples use Python; the three scanners are Semgrep Community Edition, CodeQL, and Snyk Code. Exact versions and rules remain pending. See [scanner choices and report formats](scanner-tools.md).
- Use a coherent Python IoT application with controlled versions containing or lacking the selected weaknesses. Every detector receives the same version and agreed context, without the answer key or injection notes.
- October 26: the two broad focus areas were accepted; individual weaknesses, CWE entries, injection count, and checks remain to be defined and reviewed.
- Record why each weakness and placement was chosen, the exact code change and location, verification evidence, reviewer, and outcome. Obtain independent review before scored runs; the professor offered to help and potentially involve experts.
- The student now selects Snyk Code on its free plan to replace Bandit; the three scanners are Semgrep CE, CodeQL, and Snyk Code. No additional spending is authorized. See [scanner notes](scanner-tools.md#snyk-code-free-plan).
- Use a comparable output format and preserve original findings.
- Define independent correct answers before grading the detectors.
- Define what Partially Found means before scoring. October 14 starting proposal: the actual problem is recognized but its location or explanation is incomplete; award 0.5 points, versus 1 for Found and 0 for Missing. Review before scored runs.
- Assign each detector an accuracy score against the independent answers.
- Keep Found, Missing, and Partially Found in the reporting plan, while resolving their exact meanings.
- If development proceeds, both detection approaches lead to an LLM suggestion stage supported by CWE guidance.
- October 14 application design: Processing screen, saved uploads dashboard, per-upload findings report with clickable explanations and locations, and a separate proposed-changes area with code replacements and written instructions. Users can mark findings resolved; saved unresolved counts decrease while original findings remain available. A user-marked resolution is not a verified fix. See [saved uploads and reports](application-workflows.md#saved-uploads-and-findings-reports).
- Document methods step by step. AI assistants must save exact prompts and revisions, full responses, scanner reports/errors, code versions, commands, configurations, settings, and dates for all runs, including unsuccessful ones. Keep raw evidence separate from normalized results and explain revisions.
- Prepare six diagrams, with the app-specific diagram conditional on development, and one results document. Keep only plain-English descriptions in the diagram file.
- October 14 suggestion-stage options: present application-controlled CWE retrieval and an LLM agent with a CWE vector-database search tool to the professor. Neither option is selected. Both use findings and relevant code and produce the content and structure required by the report UI. See [retrieval options](application-workflows.md#retrieving-guidance-application-or-agent).
- Review results and time with the professor before deciding whether to build the app.
- Discuss the effort of extending scanner rules across languages and frameworks even if scanners score better. LLMs may reduce manual rule-writing; this is a practical consideration to discuss, not a benefit established by the Python-only results. See [the conclusion trade-off](evaluation-plan.md#trade-off-to-discuss-in-the-conclusion).

## Questions to resolve before the main comparison

### Which specific weaknesses within the two focus areas should we test?

The professor accepted password/credential and communication/data-handling as broad focus areas on October 26, after clarifying that each contains multiple weaknesses. Define and review the specific CWE targets so the LLMs, scanners, and grading refer to the same things.

Acceptance of the broad areas is resolved. Next, choose and justify specific weaknesses, their realistic placements, and the scanner checks, and review the answer key. See the [follow-up checklist](../docs/meetings/checklist/11-1-checklist.md).

### Which related weaknesses belong in scope?

CWE entries can be related to other entries. We need to decide which of those relationships matter to this study and where to stop. Otherwise a prompt or scanner could cover a much broader set than intended, and we would not know whether a related finding should count.

### Which IoT component and Python framework should we use?

Python is confirmed as the baseline language for all study examples. The coherent IoT application, framework or libraries, and project size remain to be selected. APIs and a database are possible connected features, not required architecture. Use controlled project versions rather than unrelated vulnerable snippets. Use a shared scope that all six detectors can examine so differences in results can be interpreted fairly. This language choice does not establish a need to execute the examples; the comparison still concerns static code analysis.

### Which exact API models and three scanners should we choose?

The student selected Gemini, ChatGPT/OpenAI, and Groq on October 14 because Gemini and Groq offer free tiers and the student already pays for OpenAI access, intending to use that existing access without additional spending, and excluded Claude, Claude Code, and other Anthropic options because of cost. For Groq, the student selected Qwen 3.8 27B (`qwen/qwen3.8-27b`). Groq hosts the model; Qwen is the model family. Select exact Gemini and OpenAI API models, check account access and the cost of the planned runs, and record scanner versions. Semgrep Community Edition, CodeQL, and Snyk Code are selected for the Python examples. This does not select the model for the later suggestion stage.

Access rationale: use the [Gemini free tier](https://ai.google.dev/gemini-api/docs/pricing), the [Groq free plan](https://console.groq.com/docs/rate-limits), and the student's existing paid OpenAI access. The plan is to avoid additional spending. For API runs, verify whether that existing payment includes usable API credits; a ChatGPT subscription alone does not cover API usage. [OpenAI API usage has its own pricing](https://developers.openai.com/api/docs/pricing). Exact Gemini and OpenAI models still need recording.

**Selected Groq model:** Qwen 3.8 27B, API identifier `qwen/qwen3.8-27b`, accepted by the student on October 14. We chose it for its coding and reasoning support, free-plan availability, and a model family distinct from Gemini and OpenAI. This is a reason to evaluate it, not evidence of vulnerability-detection accuracy. See [Groq model documentation](https://console.groq.com/docs/model/qwen/qwen3.8-27b). The [published free-plan limits](https://console.groq.com/docs/rate-limits), checked October 14, list 30 requests per minute, 1,000 requests per day, 8,000 tokens per minute, and 200,000 tokens per day; confirm account limits before runs. Updated October 14, 2026.

### Which scanner checks should we use, and what if a target is unsupported?

A scanner can support a language without having a check for the chosen vulnerability. We need to know which rules to enable and how to handle missing coverage so an unsupported check is not confused with a failure to detect a weakness.

### Where should the code cases come from, and how many do we need?

Choose, adapt, or build a coherent IoT project; the professor's example illustrates the intended coherence but is not required. Preserve a baseline intended to lack the selected weaknesses and controlled vulnerable versions. Review target presences and absences, justify each placement, and retain the code changes and verification evidence. Decide the number and variety of versions and vulnerability instances; no fixed count was agreed.

### Who will check the correct answers?

We need independently checked answers stating which vulnerabilities are present and where they occur. Agreement between an LLM and a scanner does not prove correctness. We need to know who checks the code and evidence and how disagreements about the expected answers are resolved.

### What counts as one scored item?

A score could count whole cases, each target checked in a case, or each vulnerability location. These choices produce different totals and accuracy percentages. We need one agreed unit so every detector is scored consistently.

### What do Found, Missing, and Partially Found mean?

We need clear definitions so the same finding receives the same grade across detectors. A weakness absent from the code must be distinguished from one that exists but was missed. We also need to know what makes a detection incomplete rather than fully correct.

### What location and evidence must a finding provide?

Mentioning a security concern may not identify the actual problem in the code. We need rules for correct locations, supporting evidence, wrong CWE labels, duplicate reports, and related findings so grading does not depend on an individual reviewer's interpretation.

### How should partial findings affect the scores?

The starting proposal is 1 point for Found, 0.5 for Partially Found, and 0 for Missing, divided by the number of known vulnerabilities and expressed as a percentage. Refine and review this proposal before scored runs. Record false alarms separately, and decide how partial detections enter the confusion matrices; a half-credit detection score is different from present-or-absent classification accuracy.

### What should we report alongside accuracy?

A high accuracy percentage can hide missed vulnerabilities, false alarms, or poor location accuracy. We need to know which supporting measures the professor expects so the results explain the detectors' strengths and weaknesses clearly.

### Detection context: decided October 14

The first LLM call receives the code and the selected weakness targets, without supplied CWE guidance or CWE retrieval tools. After receiving its findings, the application retrieves CWE guidance from the planned database for the separate suggestion call. Keep this condition consistent across the three detection models. Exact prompt wording and output format can be settled later.

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
