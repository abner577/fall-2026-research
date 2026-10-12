# Decisions and questions for the professor

Updated October 12, 2026. **Confirmed** means stated by the student or agreed in the meeting. **Proposed** means an idea to review. **Open** means no answer has been agreed. Update the status and record the answer when a decision is made.

## Confirmed decisions

- The first milestone is a comparison study; app development is a possible second milestone.
- Compare three LLMs with three scanners: six detectors and nine LLM-versus-scanner pairings.
- Use shared evaluation cases and a comparable output format.
- Define independent correct answers before grading the detectors.
- Define what Partially Found means before scoring.
- Assign each detector an accuracy score against the independent answers.
- Keep Found, Missing, and Partially Found in the reporting plan, while resolving their exact meanings.
- If development proceeds, both detection approaches lead to an LLM suggestion stage supported by CWE guidance.
- Document the methods step by step, with general and specific diagrams and exact experiment records.
- Review results and time with the professor before deciding whether to build the app.

## Questions to resolve before the main comparison

All entries below are **Open**. The last column gives a proposed starting point where we have one; it is not an agreed answer.

| ID | Question to take to the professor | Why we need an answer | Proposed starting point |
| --- | --- | --- | --- |
| Q01 | Which two specific weakness targets should we test? Should the current two focus areas be narrowed or replaced? | Our notes currently describe broad areas with several checks. | Review the existing focus-area notes and choose a small fixed CWE list. |
| Q02 | Which related weaknesses belong in scope, and how far should we follow CWE relationships? | We need a clear boundary for prompts, rules, and grading. | Record allowed entries and relationship reasons; do not include every linked entry automatically. |
| Q03 | Which IoT software component, language, and framework should the study use first? | All six detectors need suitable inputs and coverage. | Use a manageable shared scope; choose the actual language after reviewing tools. |
| Q04 | Which three LLMs and three scanners should we choose? Should we include coding-focused models? | Names, access, cost, and coverage affect feasibility. | Select exact models and tool versions, not only brands. |
| Q05 | How should we choose scanner rules and handle a tool that lacks a target check? | Otherwise a comparison may mainly measure missing rule coverage. | Record supported checks and decide how unsupported items enter the results. |
| Q06 | Where should test cases come from, and how many do we need? | A few examples may not support a useful claim. | Mix varied vulnerable cases with cases where the target weakness is absent. |
| Q07 | Who will check the independent answers, and how do we settle disagreements? | Detector agreement is not proof of correctness. | Review code and references independently; use a second reviewer for disputed answers. |
| Q08 | What is one scored item: a case, a case checked for one CWE, or each weakness location? | The accuracy denominator and matching rules depend on this. | Start with one case checked for one target weakness, plus a separate location measure. |
| Q09 | What exactly qualifies as Found, Missing, and Partially Found? | We need consistent grading and must separate absence from a miss. | Use the proposed definitions in the evaluation plan as a discussion draft. |
| Q10 | What location and evidence are required? How do we grade wrong labels, duplicate reports, and related findings? | Correctness involves more than mentioning a security issue. | Agree matching rules before evaluating the main cases. |
| Q11 | How should partial findings affect accuracy and confusion matrices? Do we also want a partial-credit score? | We cannot choose credit after seeing which tool benefits. | Consider strict main accuracy plus separate partial counts. |
| Q12 | Which additional measures should we report for misses, false alarms, and correct locations? | One accuracy number can hide important differences. | Report detection of real weaknesses and false warnings alongside accuracy. |
| Q13 | Should detection LLMs receive CWE text or be allowed to retrieve it? | Extra guidance and searches change the experimental condition. | Fix one condition for the first comparison; label extra conditions separately. |
| Q14 | Should we use one common output format or a format matching each scanner? | The meeting discussed scanner formats; comparability still needs a clear rule. | Save original outputs and convert to one shared format. |
| Q15 | How many LLM runs should we repeat, and which settings should stay fixed? | Results may change between runs. | Log every run and summarize variation rather than keeping only the best answer. |
| Q16 | How should errors, unsupported files, incomplete context, and failed runs affect scores? | Excluding failures without a rule can make results misleading. | Set a written rule and show these counts separately. |
| Q17 | Does the professor want nine agreement matrices, side-by-side accuracy matrices, or both? | Pairwise agreement and accuracy answer different questions. | Six matrices against independent answers, organized into nine pairwise pages. |
| Q18 | Are these draft diagrams the right level of detail? Which six method diagrams should be separate? | We need a design the professor can review before running the study. | Review the full diagram checklist, then finalize it. |

## Questions for the milestone decision

These are also **Open**. Discuss the criteria before the results where possible, then make the final decision after the study.

| ID | Question | What the answer will decide |
| --- | --- | --- |
| Q19 | What would count as enough evidence and a meaningful performance difference? | Whether the comparison supports a clear claim or needs more cases. |
| Q20 | If results are similar, what performance and practical requirements would justify choosing a detector? | How accuracy, false alarms, coverage, cost, and speed affect a development choice. |
| Q21 | When will we review results, and how much time must remain to build and evaluate an app? | Whether to stop with the study, extend it, or begin development. |
| Q22 | Which earlier deadlines and deliverables still apply after this change? | The revised schedule and whether a prototype remains an expected deliverable. |

## Questions for later app development

These are **Open**, but most do not have to block the initial comparison.

| ID | Question | What we currently know |
| --- | --- | --- |
| Q23 | Should the app run locally or be deployed, and what input format should it accept? | Both were previously unresolved; ZIP input is only a proposal. |
| Q24 | Which detector will the app use, and will detection and suggestions use the same model? | Decide using evaluation evidence and practical requirements. |
| Q25 | How will we store CWE material and retrieve it: direct lookup, vector search, or an agent? | An agent is possible; application-controlled retrieval is a proposed simpler start. |
| Q26 | Which code context does the suggestion model need, and how should large or incomplete projects be handled? | Findings need relevant code; the exact selection procedure is not designed. |
| Q27 | How will we check suggested code changes and measure whether they address the weakness? | Suggestions need review and validation; detection accuracy does not establish fix quality. |
| Q28 | What roles should OWASP and Common Criteria have in the revised scope? | CWE supports weakness selection and guidance; the role of other references remains open. |
| Q29 | Which application or project will we use to evaluate the finished prototype? | Study cases can help, but a development test project has not been chosen. |

## Record an answer

For each resolved question, add:

- Question ID:
- Decision and practical reason:
- Decided by and date:
- Any conditions or limits:
- Files or diagrams that need updating:

Keep unanswered questions visible. Do not mark a proposed starting point as confirmed without an actual decision.
