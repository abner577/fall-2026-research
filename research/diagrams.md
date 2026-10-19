# Diagrams and results document

## General evaluation diagram

**Completed for the next meeting, October 19, 2026:** [Vulnerability Detection Evaluation.png](../diagrams/Vulnerability%20Detection%20Evaluation.png), supplied by the student. Store this and future completed diagram images and visual exports in the root [diagrams/](../diagrams/) folder. The descriptions below remain the planning reference; completion of this visual does not establish approval of the study design or completion of the evaluation.

Show the full workflow of the evaluation study comparing LLMs with static code analysis tools. Start with selecting the vulnerabilities and preparing shared code cases and independently checked answers. Show the LLMs and scanners examining the same code, their results being collected, and the results being graded and compared using accuracy scores and confusion matrices. End with selecting the methodology for application development. Better or comparable all-AI detection results support proceeding with the all-AI approach; better scanner results support the scanner approach.

## Evaluation diagram with a specific example

Show the same evaluation workflow using a concrete example, such as ChatGPT compared with three code scanners. Make the wording specific to that example: the model, scanners, code, and vulnerabilities being compared. Keep the same flow as the general evaluation diagram. This example illustrates one LLM against three scanners within the overall three-LLM-versus-three-scanner study; ChatGPT/OpenAI is now one of the three selected families alongside Gemini and Qwen 3.8 27B through Groq (`qwen/qwen3.8-27b`), while its exact API model remains pending.

## General application workflow: methodology 1, scanner-based

Show the whole application process from the user submitting code to receiving the results. The application prepares the code and sends it to a scanner. The scanner identifies possible vulnerabilities and their locations, and the application collects those findings and the relevant code. It retrieves CWE guidance from the database, combines the findings, code, and guidance into a prompt, and asks an LLM for explanations and suggested changes. The application returns a report for the user to review and validate. This is the general workflow for whichever vulnerability list the application is designed to check.

Present two retrieval options for professor review: the application retrieves CWE guidance before preparing the report-generation prompt, or an LLM agent chooses what guidance to retrieve through a database tool. Both use findings, relevant code, and report instructions. Neither is selected.

## General application workflow: methodology 2, LLM detection or all-AI

**Completed for the next meeting, October 19, 2026:** [General Application Workflow ALL AI.png](../diagrams/General%20Application%20Workflow%20ALL%20AI.png), supplied by the student. This artifact also completes the Method 2 + 6 standalone visual of the two LLM calls in the meeting checklist. It separates the application, LLMs, and CWE vector database, and includes the application-versus-agent retrieval question. It illustrates the proposed post-evaluation all-AI path; it does not establish that this methodology or a retrieval approach has been selected.

Show the whole application process from the user submitting code to receiving the results. The application prepares the code and prompts an LLM to identify vulnerabilities and their locations, without using a code scanner. It collects those findings and the relevant code, retrieves CWE guidance from the database, and makes a subsequent LLM request for explanations and suggested changes. The application returns a report for the user to review and validate. Use the same starting point and final report as the scanner workflow so the two methodologies can be compared clearly.

Show the same two retrieval options for professor review, without selecting either. All-AI refers to using an LLM for detection; the application can still prepare files and retrieve guidance.

## The professor's six-method process

The professor was asking us to explain how the research works, rather than only describe what the finished application would do. By a "method," he meant a part of the research with its own clear steps: what information goes in, what we do with it, and what comes out. For example, saying "we use AI to analyze code" is not enough. We need to explain which code it sees, what we ask it to find, and how it reports its findings.

Show one overall diagram covering the six methods below. The professor worked through the numbering while speaking, so this explanation follows the six-part process he arrived at in the October 12 transcript, especially 17:35-23:07. The independently checked answers and accuracy rules come from our subsequent study decisions.

**Select the vulnerabilities from CWE.** Explain how we decide what the study will look for. CWE is the catalog we use to identify specific weakness types. Describe how we narrow the software scope, choose our two targets, decide which related weaknesses belong in scope, and justify those choices. If AI helps with selection, explain what we ask it and how we check its suggestions against CWE. This method ends with a defined target list that both the LLMs and scanners will use.

**Generate the LLM's code-analysis results.** Explain how we give an LLM the code and ask it to detect the selected vulnerabilities. Describe the code and context supplied, the prompt, the expected finding locations and evidence, and the output format. The professor suggested examining scanner report formats so the LLM can produce results that are easy to compare. This means giving it a reporting structure, while keeping the scanner's answers for the scored code out of the LLM's input. This method ends with the LLM's detection results, before asking for fixes.

**Generate the scanner's code-analysis results.** Explain how we examine the same code with the selected static analysis tools. Describe why each scanner was chosen, which checks it runs, how it is configured, and how its findings are collected. This method ends with scanner results that can be compared with the LLM results. The LLM and scanner analysis are two branches using the shared cases; neither detector's answers should become the other detector's input.

**Compare the results and select the methodology.** Bring those two branches together. Check each detector against the independently checked answers, calculate accuracy, and use confusion matrices to explain correct detections, missed vulnerabilities, false alarms, and correct absences. Compare all three LLMs with all three scanners. This is the end of milestone 1 and the selection point: better or comparable all-AI detection results support continuing with all-AI development, while better scanner results support the scanner methodology. The professor also wanted to review the evidence and available time here before moving further.

**Prepare the findings report with evidence.** If development proceeds, show Processing after upload, followed by a saved report listing detected potential vulnerabilities. A dashboard lists previous uploads and their unresolved counts. Clicking a finding shows its explanation, impact, file/line locations where available, and how the code exposes the issue. Show a separate proposed-changes area for replacement code and written instructions supplied by the suggestion stage. Users can mark findings resolved and reduce the saved unresolved count while retaining original findings; label that as user-marked resolution unless updated code is checked. Found, Missing, and Partially Found are study grades using independent answers, rather than the upload's resolution statuses. Link to [the report design](application-workflows.md#saved-uploads-and-findings-reports). This method organizes findings and their presentation; the next method generates suggestions.

**Generate suggestions using CWE guidance.** Take the findings and relevant code, retrieve applicable CWE guidance, and make an LLM request for explanations and suggested changes. The professor wanted a stated method for recommendations, rather than suggestions based only on an unsupported opinion. Explain how the guidance is selected and how it enters the prompt. The output is a set of suggestions tied to the findings and sources, with checks needed before use. CWE supplies guidance, while the LLM applies it to the code; the suggestions still need review and validation.

The diagram should make the split between the milestones clear: select the targets, generate both kinds of detection results, and compare them first. Then, if development proceeds, use the selected methodology to prepare the findings report and generate suggestions. Each of the six methods has its own steps, but this remains one overall diagram.

## Evaluation results document

Prepare a document containing the actual evaluation results and visuals. Include the six detectors' accuracy scores and confusion matrices, all nine LLM-versus-scanner comparisons, partial findings, missed vulnerabilities, false alarms, and examples that explain differences. Document the cases and conditions behind the results and link the exact experimental records. Explain which methodology the evidence supports selecting and why. This is a results document with visuals inside it, rather than another process diagram.

## Our specific application's workflow, if development proceeds

Create one additional application workflow diagram using whichever methodology the comparison supports selecting. Adapt the corresponding general workflow to our actual application and its two fixed vulnerability targets. Name the selected tools or models and show how the fixed targets change the checks or prompt. If the all-AI approach is selected, the first detection request should say, in effect, "Given these two vulnerabilities, look for them in this code," rather than broadly asking the model to list vulnerabilities. Continue through collecting findings, retrieving CWE guidance, requesting suggested changes, and returning the report. Show application-controlled retrieval and agent-controlled retrieval as two options for professor review; neither is selected.
