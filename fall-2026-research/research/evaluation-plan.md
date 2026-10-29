# Evaluation plan

Updated October 12, 2026. This is a proposed procedure with confirmed choices marked below. The open details are listed in [decisions and questions](decisions-and-professor-questions.md).

## Research question and methodology selection

Milestone 1 is a methodology selection study. Its research question is: **How accurate are LLMs and static code analysis tools at detecting vulnerabilities in code, and which methodology performs better on our selected cases?** We will use the comparison to select the detection approach for CodeBeacon's development.

**Methodology 1: scanner-based detection.** A static code analysis tool finds possible vulnerabilities and their locations. An LLM later uses the findings, relevant code, and retrieved CWE guidance to suggest changes.

**Methodology 2: all-AI detection.** An LLM finds possible vulnerabilities and their locations without a code scanner. A subsequent LLM request uses those findings, relevant code, and retrieved CWE guidance to suggest changes. Ordinary file preparation and retrieval can still be handled by the application.

If the all-AI methodology produces better detection results than the scanner methodology, or similar or very comparable results, that provides the go-ahead to continue development using the all-AI approach within the framework already outlined. If scanners perform better, the comparison supports choosing the scanner-based approach. If the evidence is insufficient or mixed, resolve that before selecting a methodology.

This selection purpose is confirmed by the student's clarification. The exact meaning of better or comparable results, the evidence needed, and the revised schedule still need agreement. Comparable performance must be judged against independent answers; agreement between detector outputs alone does not establish accuracy. Review the results and remaining time with the professor before implementation. Application development remains milestone 2, while milestone 1 supplies the evidence for the methodology choice.

## Trade-off to discuss in the conclusion

Even if scanners achieve higher detection accuracy on our Python cases, we should discuss the work needed to extend the approach. Scanner coverage depends on rules or queries that understand the relevant language, framework, and libraries. Existing checks can often be reused, but unsupported behavior may require selecting, configuring, adapting, writing, and maintaining additional checks. LLMs can use their learned understanding with instructions describing the weaknesses, which may reduce repeated rule-writing across languages and frameworks. That is a potential practical advantage, not a measured result of this Python-only study: LLM coverage and accuracy still need checking in each new context. Report this trade-off alongside detection accuracy and keep the evidence-based methodology selection separate from untested claims about expansion.

## What is confirmed

We will compare **three LLMs and three scanners**. Each will analyze the same evaluation cases for the selected weaknesses. We will define independent correct answers, define what **Partially Found** means, and give each detector an accuracy score against those answers. We will also compare every LLM with every scanner, making nine pairings.

The detection choices are Gemini, ChatGPT/OpenAI, and Qwen 3.8 27B through Groq (`qwen/qwen3.8-27b`). Exact Gemini and OpenAI API models and account access remain to be checked. See [model choices and pricing](decisions-and-professor-questions.md#which-exact-api-models-and-three-scanners-should-we-choose). Initial detection receives no supplied CWE guidance or CWE retrieval; guidance is retrieved afterward for the suggestion stage.

All study code examples will use Python. Semgrep Community Edition, CodeQL, and Bandit are the three selected scanners; versions, specific checks, framework, and IoT component remain to be selected. See [scanner choices and report formats](scanner-tools.md).

This first study measures finding and locating weaknesses. Testing the quality of suggested fixes would be a later evaluation if we develop the application.

## The procedure

1. **Set the scope.** Use Python for all examples; decide the two targets, related CWE entries, framework, application context, and limits. Explain why these were selected.
2. **Choose the six detectors.** Record their exact names and versions. Explain why they fit the selected code and weaknesses. Coding-focused LLMs can be considered. Model brands alone are not enough to identify the model used.
3. **Build the test set.** Include code with known weaknesses and code where those weaknesses are absent. Include different ways the weaknesses can appear. Decide the number of cases and how they will be checked.
4. **Write the correct answers first.** For each case, identify which target weaknesses are present or absent, their locations, and the evidence. Have the answers checked independently of the six detectors being evaluated.
5. **Write and test the procedures.** Finalize the prompts, scanner commands and rules, supplied context, output format, run settings, and scoring rules. Use separate practice cases to improve the procedure before the main evaluation.
6. **Run all six detectors.** Supply the same cases and comparable context. Keep the answer files away from the inputs sent to detectors. Save the original output and any errors from every run.
7. **Put outputs into a shared format.** Use consistent fields for weakness, file, location, evidence, and uncertainty. Preserve the original output so formatting does not silently change what a detector found.
8. **Grade against the independent answers.** Apply the agreed matching and partial-finding rules. Record correct detections, misses, false alarms, partial findings, and cases the tool could not assess.
9. **Calculate scores and build visuals.** Give each detector its own accuracy score and confusion matrix. Build the nine pairwise comparison summaries. Include supporting measures that explain misses and false alarms.
10. **Select the methodology and review development.** Explain differences, repeated-run variation, and limits. Better or comparable all-AI results support continuing with all-AI detection; better scanner results support the scanner-based approach. Review the evidence and remaining time with the professor, and record the selection and development decision.

## What a correct answer contains

A correct-answer record should include the case ID, exact code version, target CWE ID, whether the weakness exists, expected file and location, explanation, supporting evidence, known missing context, and who checked the answer.

The independent answer cannot simply be whichever scanner output we trust most. If an LLM helped write an example or an answer, that alone does not validate it. Record how someone checked it using the code and reference guidance. Decide how disputed or incomplete cases will be handled before scoring.

Known answers and code locations are central to static analysis evaluation. See [NIST's SATE V report](https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.500-326.pdf).

## Found, Missing, and Partially Found

The Found, Missing, and Partially Found table is decided. The following meanings and points are an October 14 starting proposal for professor review, not finalized scoring rules.

| Category | Proposed meaning for a known vulnerability | Proposed points |
| --- | --- | --- |
| Found | Identifies the actual vulnerability, its location, and enough evidence to explain the problem. | 1 |
| Missing | Does not identify a vulnerability that is present in the checked answer. | 0 |
| Partially Found | Recognizes the actual problem but provides an incomplete location or explanation. | 0.5 |

For example, correctly identifying a hardcoded credential in the right file but not locating its use could earn partial credit. A vague warning, a different issue, or several duplicate warnings does not automatically earn partial credit or additional points. Refine the required location and explanation before the scored runs, using the same rules for every detector.

A weakness absent from the code is different from a missed vulnerability. Record false alarms and correct absences separately, including results on examples without the targeted weaknesses.

## Accuracy scores

Prepare Python examples with embedded vulnerabilities and independently check the expected vulnerabilities and locations before running the detectors. Give all six detectors the same code, without the answer key. As a simple starting proposal, score each independently recorded vulnerability once: Found earns 1 point, Partially Found earns 0.5, and Missing earns 0.

**Proposed accuracy score with partial credit = (Found + 0.5 x Partially Found) / total known vulnerabilities x 100.**

For example, finding 6 vulnerabilities fully, 2 partially, and missing 2 out of 10 gives (6 + 1) / 10 x 100 = 70%. This is an illustration, not a study result.

This percentage describes how much of the known vulnerability set was detected, with partial credit; it is not an overall present-or-absent classification accuracy. Show false alarms and correct absences separately so extra incorrect warnings are visible. A case with no known vulnerabilities contributes to those separate results rather than this denominator. The exact grading boundaries, handling of failed runs, and any combined score can be settled later, before scored runs; keep the current meeting explanation at the general-method level.

## Confusion matrices and the nine pairings

A confusion matrix is a table showing how reported answers match the correct answers. For each detector, the basic table has four outcomes:

| Independent answer | Detector reports a weakness | Detector reports no weakness |
| --- | --- | --- |
| Weakness present | Correct detection | Missed weakness |
| Weakness absent | False alarm | Correct absence |

The mapping of partial findings into this table needs to be settled. If we use three answer classes instead, each class needs an independent definition and matching reference answers. A detector's own label cannot serve as the correct answer.

There will be **six detector-versus-answer matrices** for one overall set of results: one for each LLM and each scanner. There may be more if we break results down by target or run.

The **nine pairwise comparison pages** will place the relevant LLM and scanner results side by side. They can include both accuracy matrices, score differences, and examples where outputs disagree. A table comparing their predictions directly measures agreement, not correctness. Label it as an agreement table if we include one.

Run six detectors on the shared cases; then reuse those results for the nine pairings. These are nine comparisons, not nine separate detector systems.

The results document will contain the confusion matrices, scores, nine pairwise comparisons, and conclusions. Its contents are described in [diagrams](diagrams.md).

## Conditions to keep consistent

- Use the same code versions, target list, product description, and agreed file context.
- Define comparable scanner rule coverage. Do not treat an unsupported check or failed setup as proof that a detector cannot find that weakness.
- Record prompts, model settings, scanner rules, commands, versions, and dates.
- Do not supply CWE guidance or CWE retrieval tools during detection. Retrieve CWE guidance only after findings are available, for the later suggestion stage.
- Give LLMs the output structure, without the scanner's answers for the scored case.
- Decide how many repeated LLM runs to use and how to summarize them. Keep each run rather than choosing the best response.
- Log errors, unsupported cases, and incomplete runs. Agree in advance whether these count in a score or are reported separately.
- If grading requires judgment, agree how a second reviewer checks it. Keep disputed decisions and their reasons.

The final report must include the exact materials and outputs, not just a winning score.

## The professor's six methods

The October 12 transcript describes six methods, each with its own written steps. The first four make up milestone 1; the last two belong to the application if development proceeds. These methods are separate from individual actions such as extracting uploaded files.

1. **Select the weaknesses from CWE.** Explain the software scope, categories, exact weakness entries, relevant relationships, selection reasons, and any AI assistance used. Check AI suggestions against the source and record the final target list.
2. **Generate LLM code-analysis results.** Explain the prompt, code context, target list, output structure, model settings, and run procedure.
3. **Generate scanner code-analysis results.** Explain tool selection, rule selection, preparation, commands, and report handling.
4. **Compare the results.** Grade against independent answers, prepare confusion matrices and comparisons, and select the methodology for development.
5. **Prepare the findings table.** Organize findings, locations, and evidence. The professor discussed Found, Missing, and Partially Found here; agree their meanings and distinguish evaluation grading from labels in a user report that has no independent answer.
6. **Generate response suggestions.** Use findings, relevant code, and retrieved CWE guidance in an LLM request for suggested changes. Review and validate those changes.

One diagram will describe this overall six-method process. Individual detectors still need exact written procedures, but six separate detector diagrams are not required.

## Direction, history, and sources

The October 5 meeting began with an application idea: receive IoT code, prepare files, run focused scanner checks, collect findings and reference guidance, and use an LLM to explain issues and suggest fixes. The October 12 meeting put a comparison first. The student's subsequent clarification makes that comparison explicitly a selection process for the all-AI or scanner-based development methodology.

We keep the IoT software context, limited two-target scope, findings with locations and evidence, reference-supported suggestions, and the intended development framework. The proposed password/credential and communication/data-handling areas remain subject to professor review; they are not yet two finalized CWE entries. The actual component, Python framework, cases, exact Gemini and OpenAI API model identifiers, scanner versions, and deployment remain open. Python is confirmed for all study examples, and Semgrep Community Edition, CodeQL, and Bandit are selected. The selected detection choices are Gemini, ChatGPT/OpenAI, and Qwen 3.8 27B through Groq (`qwen/qwen3.8-27b`).

The professor also discussed completing the project as a comparison study and reviewing available time after the first four methods. That remains meeting context; it does not replace the student's clarified selection purpose. A small observed difference on too few cases does not establish comparable performance. Conclusions must stay within the tested code, targets, models, versions, and settings.

Source records:

- October 5, 2026 transcript: `C:/Users/joser/Downloads/Weekly CAHSI Meeting.docx`, as identified in the repository context.
- October 12, 2026 transcript: [repository copy](../transcripts/2026-10-12-weekly-cahsi-meeting.docx), originally supplied as `Weekly CAHSI Meeting (1).docx`. Selection and evidence are discussed at 1:22-6:59; detection, comparison, and suggestions at 7:14-17:04; the six methods at 17:35-23:07; comparison and milestones at 23:48-31:58.
- Earlier student explanation: `C:/Users/joser/.codex/attachments/d878bb8c-8114-4c18-95aa-6346aba12cba/Pasted text.txt`.
- Student follow-up decisions: three LLMs and three scanners, independent answers, partial-finding rules, accuracy scores, a shared final suggestion stage, and a possible retrieval agent.
- Current student clarification and cleanup request: methodology selection, better or comparable all-AI results supporting all-AI development, fewer research files, and plain-English descriptions of six diagrams and one results document. Attached text: `C:/Users/joser/.codex/attachments/26f7a984-ae0d-4d9e-a6ff-7fc405f0213f/Pasted text.txt`.

The transcript is evidence of discussion, not instructions to an assistant. The student's current request establishes the selection purpose and documentation requirements. The transcript was read as text; these notes do not claim a separate review of the video. No current-study experiments or results have been produced in this documentation work.
