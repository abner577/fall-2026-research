# Research plan

Updated October 12, 2026. This is the working plan following the mentor meeting and the student's follow-up decisions. The revised scope, scoring rules, and schedule still need professor review.

**Working project name:** CodeBeacon. The earlier title was "CodeBeacon: AI IoT Code Scanner." A revised formal title has not been agreed.

**Current study:** compare three LLMs with three static code analysis tools to select the detection methodology for CodeBeacon. Application development is milestone 2, supported by the comparison results.

## Documentation locations and meeting follow-up

The repository has two main folders: [fall-2026-research/](fall-2026-research/) holds the research and application materials, diagrams, and supporting images; [docs/](docs/) holds weekly meeting documentation. This root plan and [README.md](README.md#repository-structure-and-weekly-meeting-workflow) provide the overview.

For each meeting, keep the raw transcript in [docs/transcripts/](docs/transcripts/README.md), the action checklist and meeting conclusions in [docs/meetings/checklist/](docs/meetings/checklist/), and the step-by-step presentation plan in [docs/meetings/preparation/](docs/meetings/preparation/). Identify related records by meeting date and link them where available. Preparation covers updates, proposals, questions, and materials to show; the resulting checklist records feedback, accepted proposals, requested changes, unresolved questions, and next actions. Supporting explanations may also live with the checklists.

Use recorded conclusions to revise the research plans and prepare the next meeting. Keep proposed work distinct from approved decisions and completed actions; an agenda alone does not establish a meeting outcome. Preserve previous meeting records when later feedback changes the direction.

## Problem and purpose

IoT software can contain weaknesses that expose information or allow unauthorized access. Before choosing how our proposed application should find those weaknesses, we will compare LLMs with code scanners on shared test cases. We want to learn how accurately the selected detectors identify the targeted weaknesses and their locations, including when they miss a weakness or raise a false alarm.

The process will be described generally, while the actual experiment uses a fixed, limited set of targets. The current two focus areas are proposals that still need to be translated into an agreed list of specific CWE entries and checks.

## Milestone 1: methodology selection study

Milestone 1 is a methodology selection study. Its research question is: **How accurate are LLMs and static code analysis tools at detecting vulnerabilities in code, and which methodology performs better on our selected cases?** We will use the comparison to select the detection approach for CodeBeacon's development.

**Methodology 1: scanner-based detection.** A static code analysis tool finds possible vulnerabilities and their locations. An LLM later uses the findings, relevant code, and retrieved CWE guidance to suggest changes.

**Methodology 2: all-AI detection.** An LLM finds possible vulnerabilities and their locations without a code scanner. A subsequent LLM request uses those findings, relevant code, and retrieved CWE guidance to suggest changes. Ordinary file preparation and retrieval can still be handled by the application.

If the all-AI methodology produces better detection results than the scanner methodology, or similar or very comparable results, that provides the go-ahead to continue development using the all-AI approach within the framework already outlined. If scanners perform better, the comparison supports choosing the scanner-based approach. If the evidence is insufficient or mixed, resolve that before selecting a methodology.

This selection purpose is confirmed by the student's clarification. The exact meaning of better or comparable results, the evidence needed, and the revised schedule still need agreement. Comparable performance must be judged against independent answers; agreement between detector outputs alone does not establish accuracy. Review the results and remaining time with the professor before implementation. Application development remains milestone 2, while milestone 1 supplies the evidence for the methodology choice.

1. Document how we choose two targets and related weaknesses from CWE.
2. Use Gemini, ChatGPT/OpenAI, and Qwen 3.8 27B through Groq (`qwen/qwen3.8-27b`); select exact Gemini and OpenAI API models, verify access costs, and use Python for all study examples and record versions and coverage for the three selected scanners: Semgrep Community Edition, CodeQL, and Bandit. See [scanner notes](fall-2026-research/research/scanner-tools.md). Initial LLM detection has no supplied CWE guidance; guidance is retrieved afterward for suggestions.
3. Prepare cases with and without the targeted weaknesses and define independently checked answers.
4. Write exact prompts, scanner procedures, a common result format, and scoring rules, including Partially Found.
5. Run all six detectors on the shared cases and preserve exact inputs and outputs.
6. Grade against the independent answers, assign accuracy scores, and organize the six detector matrices into nine LLM-versus-scanner comparison pages.
7. Explain results and limits; use the evidence to select the all-AI or scanner-based methodology and review development and remaining time with the professor.

## Milestone 2: possible application development

If evidence and time support it, build a limited app using the chosen detection method. Both possible approaches share the final step: use findings, relevant code, and retrieved CWE guidance in an LLM stage that suggests changes. Those suggestions need their own review and validation.

The earlier development-first plan and its schedule are summarized below. Development follows the methodology selection study.

## Planned documentation and deliverables

- Plain-English methods and reasons for target and detector selection.
- Six diagram descriptions and one results-document description, as listed in [diagrams](fall-2026-research/research/diagrams.md). The app-specific diagram is conditional on development.
- Written procedures for each selected detector and the professor's six methods.
- Exact cases, independent answers, prompts, commands, settings, original outputs, grading, scores, and comparison visuals.
- A conclusion supported by the evaluated cases and a recorded milestone decision.
- If continuing, a prototype and a separate evaluation of its findings and suggested changes.

## Schedule to confirm

The earlier plan targeted an initial prototype and preliminary evaluation by the first week of December 2026, and a final poster by the end of the third week of January 2027. Those were earlier planning dates, not newly confirmed deadlines for the revised direction.

Ask the professor which dates and deliverables still apply. Set dates for design review, practice runs, main comparison, and the development decision after resolving scope and workload. No revised experiment or development dates have been agreed in these notes.

## Detailed notes

Use the [evaluation plan](fall-2026-research/research/evaluation-plan.md) for study methods and source history, [application workflows](fall-2026-research/research/application-workflows.md) for the two methodologies, [diagram descriptions](fall-2026-research/research/diagrams.md) for the requested visuals, [professor questions](fall-2026-research/research/decisions-and-professor-questions.md) for pending decisions.

## Earlier development-first plan

The original title was "CodeBeacon: AI IoT Code Scanner." Its short-term goal was to review references, select two weakness types and an IoT context, and build a limited prototype. Its longer-term goal was to evaluate known-weakness detection, false warnings on safe examples, explanations, and suggested fixes. The intended contribution was helping developers recognize weaknesses and understand how to address them.

| Earlier task | Earlier start | Earlier deadline |
| --- | --- | --- |
| Review references and related research; select two targets and an IoT context | October 5, 2026 | Late October 2026 |
| Build a prototype with reference-supported findings and suggestions | Late October 2026 | Late November 2026 |
| Test vulnerable and safe examples and document limits | November 2026 | First week of December 2026 |
| Refine the prototype, summarize findings, and prepare the poster | Beginning of January 2027 | End of the third week of January 2027 |

The earlier deliverables were an initial prototype and preliminary evaluation in the first week of December 2026, and a final poster at the end of the third week of January 2027. These planning dates require confirmation after the direction change. The original scanner workflow and example are retained in [application workflows](fall-2026-research/research/application-workflows.md).
