# Checklist before the next mentor meeting

The aim is to bring a complete proposed design for milestone 1: compare three LLMs with three code scanners, measure how accurately they find the selected vulnerabilities, and use the results to choose the methodology for development. Bring recommendations with reasons so the professor can review and correct them. Proposed choices are not final decisions yet.

## Priority question: confirm the scope before finishing the design

- [ ] **Ask whether we should start by confirming the two focus areas.** We did not confirm the earlier vulnerability choices with the professor. Explain that milestone 1 compares three LLMs and three scanners on the same limited set of checks, then ask whether password and credential security, and insecure communication and data handling, are suitable starting areas. Briefly describe the weaknesses within each and why we chose them. The scanner checks need to be selected, configured, or written for this scope; the LLMs must be asked to examine the same weaknesses. See the [email draft](scope-email-draft.md).

If there is no reply before we need to prepare, continue the initial diagrams and mock-ups using these areas as a provisional scope, as the student requested. Keep that assumption visible and ask for confirmation at the meeting. No reply is not confirmation that the professor approved the targets. The specific checks and CWE entries still need to be made clear before the main comparison.

## What the professor asked to see

In the October 12 meeting, the professor asked for clear steps explaining each of his six methods, reasons for choosing the tools, and a design showing how the comparison works. Near the end, he explicitly said that showing the designs at the next meeting would be useful: he could give feedback before we carry out the comparison. He also allowed more time if needed. This checklist therefore focuses on preparing the design for review.

The detailed study proposals below also reflect our follow-up decisions: three LLMs and three scanners, independently checked answers, partial-finding rules, and an accuracy score for each detector. These details should not all be attributed to the professor's original request.

## Explain the six methods

Write one short, plain-English paragraph per method, using what we start with, do, produce, and why as a guide rather than separate questions to answer. Use [the written explanation](six-methods-explanation.md). Give the first four methods the most detail because they make up milestone 1. Explain the last two as planned application work if development proceeds.

- [x] **Explain how we select the vulnerabilities.** [Method 1](six-methods-explanation.md#method-1-how-we-selected-the-vulnerabilities) explains the focus areas, selection reasons, and planned CWE mapping. Exact CWE targets still need review.

- [x] **Explain how the LLMs examine the code.** [Method 2](six-methods-explanation.md#method-2-how-the-llms-examine-the-code) explains detection without supplied CWE guidance, the chosen providers, and the later suggestion stage. Exact Gemini/OpenAI models and final prompts remain pending.

- [x] **Explain how the scanners examine the code.** [Method 3](six-methods-explanation.md#method-3-how-the-scanners-examine-the-code) explains the general process and report contents in two paragraphs. Exact checks can come later. [Scanner notes](../research/scanner-tools.md) show report fields and illustrative examples.

- [x] **Explain how we compare the results.** [Method 4](six-methods-explanation.md#method-4-how-we-compare-the-results) describes the decided Found/Missing/Partially Found table, independently checked answers, and proposed 1/0/0.5 scoring against known vulnerabilities. Definitions and exact scoring can be refined before scored runs; record false alarms separately.

- [x] **Explain how findings would be organized for the application.** [Method 5](six-methods-explanation.md#method-5-how-findings-would-be-organized-for-the-application) describes saved upload reports, clickable findings, proposed changes, and a persistent unresolved counter. User-marked resolution is distinct from rescan verification; study grades remain separate. See [the application design](../research/application-workflows.md#saved-uploads-and-findings-reports).

- [x] **Explain how suggestions would be generated.** [Method 6](six-methods-explanation.md#method-6-how-suggestions-would-be-generated) presents application-controlled retrieval and an LLM agent with a CWE database search tool. Both generate the same report content from findings, relevant code, guidance, and report instructions. Present both options to the professor; neither is selected. Exact wording and output fields can come later.

## Prepare one main diagram for this meeting

- [ ] **Make a general diagram of the evaluation process.** Show choosing the targets and tools, preparing shared code cases and checked answers, running the six detectors, collecting their results, grading them, calculating scores, comparing the results, and selecting the methodology. Keep the checked answers separate from the code supplied to the detectors. A general diagram is enough for this meeting; the model-specific example and other application diagrams can follow later.

Use the general evaluation explanation in [diagrams.md](../research/diagrams.md) to guide this diagram. The smaller method visuals below support the written explanations and are separate from this main diagram.

## Prepare standalone visuals for the method explanations

These are reminders to create supporting visuals, not completed artifacts or additional full study diagrams. Prompt wording and output fields can be illustrative rather than final.

- [ ] **Method 2 + 6: Make a diagram of the two LLM calls.** Show the first call receiving the code and a prompt naming the weaknesses to look for, without supplied CWE guidance. Include a suggested prompt structure and an example output structure with findings, files, lines where available, and supporting code. Then show the application using those findings to retrieve CWE information and prepare the second call, with the findings, relevant code, CWE definitions and guidance, and report instructions. Show the expected response: explanations for the report, replacement code, and written steps for other changes. Label application-controlled retrieval as the illustrated option; the agent option remains open. Use [method 2](six-methods-explanation.md#method-2-how-the-llms-examine-the-code) and [method 6's prompt outlines](six-methods-explanation.md#method-6-how-suggestions-would-be-generated).

- [ ] **Method 3: Make a small scanner visual.** Show the prepared Python files and the selected rule files or checks going into a scanner, followed by findings with the rule, file, line, and message. Use Semgrep CE, CodeQL, and Bandit as the selected tools; make clear that CodeQL uses a code database and queries, while Bandit uses check plugins, rather than implying all three load identical rule files. Keep it small and focused on code + checks → scanner → report. Use [the scanner notes](../research/scanner-tools.md).

- [ ] **Method 4: Make a simple comparison example.** Use one small Python scenario with independently checked answers and illustrative results from one LLM and the three scanners. Put their findings side by side, mark Found, Missing, and Partially Found, and show the proposed 1/0/0.5 points and resulting scores. Include false alarms separately if the example has any. Highlight which detector scores highest, or whether there is a tie, for this example only. Label the visual as an illustration, not an experiment result or the overall methodology decision. Use [method 4](six-methods-explanation.md#method-4-how-we-compare-the-results).

## Propose the study choices

- [ ] **Choose the software scope.** Python is confirmed for all study examples. Propose which part of an IoT system we will examine, its Python framework, and how much code each case contains. Explain why the scope is manageable and suitable for all six detectors.

- [ ] **Record exact API models for the three chosen LLM providers: Gemini, ChatGPT/OpenAI, and Groq.** The student chose Gemini and Groq for their free tiers and OpenAI because they already pay for access and intend to avoid additional spending. Anthropic options are excluded because of cost. Qwen 3.8 27B (`qwen/qwen3.8-27b`) is selected for Groq, for its coding and reasoning support, free access within plan limits, and different model family. Record exact Gemini and OpenAI models, and verify API access under the existing OpenAI payment. See [model choices and pricing](../research/decisions-and-professor-questions.md#which-exact-api-models-and-three-scanners-should-we-choose).

- [ ] **Finish the scanner choices and setup.** Semgrep Community Edition, CodeQL, and Bandit are selected, with Python confirmed for all study examples. Reasons and report examples are in [scanner notes](../research/scanner-tools.md). Record versions and confirm target coverage later; exact checks are not needed for the current explanation.

- [ ] **Propose the code cases and their number.** Explain where cases will come from, how many we plan to use, and how we include both vulnerable and non-vulnerable examples. Include different ways the selected weaknesses can appear so the study does more than repeat the same example.

- [ ] **Propose how the correct answers will be checked.** Explain who will review each case, how they will establish whether a target weakness exists and where it is, and how disagreements will be settled. The expected answer must not simply be whichever detector output we trust most.

- [ ] **Propose a comparable reporting format.** Explain what every finding should contain, such as the weakness, file, location, and supporting code evidence. Check example scanner reports so the proposed LLM output is practical to compare. Use their structure as a reference without giving the LLM a scanner's answers for the scored case.

- [ ] **Propose consistent run conditions.** Explain what code and context every detector receives, whether detection LLMs get CWE text or search tools, what settings stay fixed, and how many times we repeat LLM requests. Explain how repeated results will be summarized and how failed or incomplete runs will be handled.

## Propose the grading and comparison rules

- [ ] **Define Found, Missing, and Partially Found.** Give a clear proposed meaning and a small explanatory example for each. Resolve the ambiguity in "Missing": a vulnerability that is absent from the code is different from one that exists but was missed. Explain what earns partial credit, if any, and what counts as a false alarm.

- [ ] **Define what counts as one scored answer.** Decide whether we score each case, each target checked within a case, or each vulnerability location. Explain how multiple findings, wrong locations, wrong weakness names, duplicate warnings, and related weaknesses affect the grade.

- [ ] **Propose an accuracy score for each LLM and scanner.** Explain what counts as correct, what goes into the total, and how partial findings and failures affect the calculation. A simple accuracy score is the number of correct answers divided by the total number scored, multiplied by 100; its use depends on the grading rules we propose. Also explain how we will show missed vulnerabilities, false alarms, and correct locations so one percentage does not hide them.

- [ ] **Explain accuracy and similarity separately.** Accuracy means matching the independently checked answer. Similarity or agreement means an LLM and scanner give matching results; both could still be wrong. If we propose a similarity score, define what makes two findings match and show it separately from accuracy. Do not use matching wording alone as proof that the methods are equally good.

- [ ] **Explain the confusion matrices and nine comparisons.** Describe a confusion matrix as a table counting correct detections, misses, false alarms, and correct absences. Propose one accuracy summary for each of the six detectors, then compare each LLM with each of the three scanners, producing nine pairings. These use the same study results rather than requiring nine separate experiments.

- [ ] **Propose what better or comparable performance means.** Explain how we will decide whether all-AI detection performs well enough to select it for development. Specify how much difference matters and how misses, false alarms, partial findings, and variation between runs affect that judgment. Bring the criteria as a proposal for review before the main experiment.

## Bring a reviewable proposal

- [ ] **Check the design against the remaining study questions.** Use [the professor questions](../research/decisions-and-professor-questions.md) to check for omissions. Bring a proposed answer wherever possible and clearly explain anything we could not resolve, along with what information is needed.

- [ ] **Discuss the coverage trade-off even if scanners score better.** Existing scanner rules can be reused, but new language and framework coverage may need manual rule work; LLMs may reduce that effort. Treat this as a practical consideration, not a conclusion proved by our Python-only cases. See [the evaluation notes](../research/evaluation-plan.md#trade-off-to-discuss-in-the-conclusion).

- [ ] **Bring the written six-method explanation, the main evaluation diagram, the three supporting method visuals, and the proposed study choices and scoring rules.** Be ready to explain the reasons for the choices and ask the professor to correct or confirm them. Include a realistic estimate of the work and time needed after design review.

The goal for this meeting is an agreed study design. Final prompt wording, final commands, completed comparison results, and a working application can follow the design review. If an example output is useful, label it as an illustration rather than a study result.

## Transcript references

Source: [October 12 meeting transcript](../transcripts/2026-10-12-weekly-cahsi-meeting.docx), October 12, 2026. The transcript supports this checklist as a record of discussion; the student's current request sets the preparation scope.

- **17:35-23:07:** explain the six methods, their steps, tool-selection reasons, the comparison, findings table, and suggestions.
- **23:19-23:48:** explain the research design explicitly and identify what claims the comparison could support.
- **25:08-27:46:** compare multiple LLMs with multiple scanners and consider coding-focused models. The three-versus-three count is our subsequent choice.
- **30:00-31:58:** focus on the comparison first, then review the evidence and available time before extending the work.
- **32:21-32:39:** showing the designs at the next meeting is acceptable; the professor can give feedback before we proceed with the comparison. More preparation time was also offered.
