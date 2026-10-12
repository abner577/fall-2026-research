# Checklist before the next mentor meeting

The aim is to bring a complete proposed design for milestone 1: compare three LLMs with three code scanners, measure how accurately they find the selected vulnerabilities, and use the results to choose the methodology for development. Bring recommendations with reasons so the professor can review and correct them. Proposed choices are not final decisions yet.

## What the professor asked to see

In the October 12 meeting, the professor asked for clear steps explaining each of his six methods, reasons for choosing the tools, and a design showing how the comparison works. Near the end, he explicitly said that showing the designs at the next meeting would be useful: he could give feedback before we carry out the comparison. He also allowed more time if needed. This checklist therefore focuses on preparing the design for review.

The detailed study proposals below also reflect our follow-up decisions: three LLMs and three scanners, independently checked answers, partial-finding rules, and an accuracy score for each detector. These details should not all be attributed to the professor's original request.

## Explain the six methods

For each method, write the steps in plain English: what information we start with, what we do, what we produce, and why. Give the first four methods the most detail because they make up milestone 1. Explain the last two as planned application work if development proceeds.

- [ ] **Explain how we select the vulnerabilities.** Propose the two specific weaknesses from CWE, the catalog of weakness types, and explain why they fit the project. Identify any related weaknesses we will include and where the scope ends. Explain the selection process, including how any AI assistance would be checked. The current two broad focus areas need to be narrowed into specific targets.

- [ ] **Explain how the LLMs examine the code.** Describe what code and background information each model receives, what it is asked to find, and what its answer must contain. Explain whether it receives CWE guidance. Describe the purpose and expected shape of the request; the final wording of every prompt can come later.

- [ ] **Explain how the scanners examine the code.** Describe the selected tools, the checks they will run, the files they will examine, and how we collect their findings. Explain why each tool is suitable. Identify any setup or missing-check problems that could prevent a fair comparison.

- [ ] **Explain how we compare the results.** Describe how we check findings against independently verified answers, assign scores, and compare each LLM with each scanner. Explain how the results support selecting all-AI detection or scanner-based detection. Better or comparable all-AI results support continuing with the all-AI approach; better scanner results support the scanner approach.

- [ ] **Explain how findings would be organized for the application.** Describe how a report would show the issue, location, code evidence, and any uncertainty. Explain how Found, Missing, and Partially Found would be used and distinguish study grades from what we can honestly report about an ordinary user upload.

- [ ] **Explain how suggestions would be generated.** Describe how the application would combine findings, relevant code, and retrieved CWE guidance in a later LLM request for suggested changes. Use application-controlled retrieval in the design for now, with a note that an agent remains an open option. Explain how the suggestions would be reviewed before use.

## Prepare the two diagrams for this meeting

- [ ] **Make one diagram of the professor's six-method process.** Show all six methods and how they connect. LLM analysis and scanner analysis should examine the shared cases separately and come together at the comparison. Mark that comparison as the end of milestone 1 and the methodology selection point. Show findings reporting and suggestions as later work if development proceeds.

- [ ] **Make a general diagram of the evaluation process.** Show choosing the targets and tools, preparing shared code cases and checked answers, running the six detectors, collecting their results, grading them, calculating scores, comparing the results, and selecting the methodology. Keep the checked answers separate from the code supplied to the detectors. A general diagram is enough for this meeting; the model-specific example and other application diagrams can follow later.

Use the explanations in [diagrams.md](../research/diagrams.md) to guide what these diagrams contain. The two diagrams serve different purposes: one explains the overall research methods, while the other explains the comparison study in more detail.

## Propose the study choices

- [ ] **Choose the software scope.** Propose which part of an IoT system we will examine, its language and framework, and how much code each case contains. Explain why the scope is manageable and suitable for all six detectors.

- [ ] **Propose three exact LLMs.** Give the actual model names and versions or identifiers, rather than only company or product names. Explain why each belongs in the comparison, including whether a model intended for coding is useful. Check that we can access the models and afford the planned runs.

- [ ] **Propose three exact scanners.** Give the tool names and versions and explain their selection. Check that they support the chosen code and can examine the targeted weaknesses. State which checks we intend to use and whether existing checks are enough or custom work would be needed.

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

- [ ] **Bring the written six-method explanation, the two diagrams, and the proposed study choices and scoring rules.** Be ready to explain the reasons for the choices and ask the professor to correct or confirm them. Include a realistic estimate of the work and time needed after design review.

The goal for this meeting is an agreed study design. Final prompt wording, final commands, completed comparison results, and a working application can follow the design review. If an example output is useful, label it as an illustration rather than a study result.

## Transcript references

Source: [October 12 meeting transcript](../transcripts/2026-10-12-weekly-cahsi-meeting.docx), October 12, 2026. The transcript supports this checklist as a record of discussion; the student's current request sets the preparation scope.

- **17:35-23:07:** explain the six methods, their steps, tool-selection reasons, the comparison, findings table, and suggestions.
- **23:19-23:48:** explain the research design explicitly and identify what claims the comparison could support.
- **25:08-27:46:** compare multiple LLMs with multiple scanners and consider coding-focused models. The three-versus-three count is our subsequent choice.
- **30:00-31:58:** focus on the comparison first, then review the evidence and available time before extending the work.
- **32:21-32:39:** showing the designs at the next meeting is acceptable; the professor can give feedback before we proceed with the comparison. More preparation time was also offered.
