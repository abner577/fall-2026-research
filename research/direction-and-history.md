# Direction and history

Updated October 12, 2026.

## The original idea

We wanted to build CodeBeacon, a limited tool for reviewing IoT application code. IoT means devices and their related software that communicate over a network. A user would provide code, a scanner would identify possible weaknesses, and an LLM would explain the findings and suggest changes using security reference information.

The proposed flow was: receive code, prepare files, run focused checks, collect findings and reference guidance, ask an LLM for explanations and fixes, and return a report.

We had preparation notes, but several important choices were still open: the application or device context, test project, first languages and frameworks, exact weakness checks, scanner, model, and whether the app would run locally or be deployed.

The proposed focus areas were password and credential security, and insecure communication and data handling. These are broad areas with several possible weaknesses. They are not yet two finalized individual CWE entries. See the [earlier target notes](../preparation/selected-vulnerabilities.md).

## What changed in the October 12 meeting

The professor asked us to start with the design and a comparison study. Before building the application, we will investigate how well LLMs and scanners identify the selected weaknesses in the same code.

We will explain how we selected the weaknesses from CWE, write down each method step by step, control the output format, and compare the results. CWE, or Common Weakness Enumeration, is a catalog of weakness types with descriptions, relationships, examples, and guidance where available.

The student has now chosen **three LLMs and three scanners**. That gives six detectors and **nine LLM-versus-scanner pairings**. Their names and versions have not been chosen.

The immediate research question is: how accurately do these selected LLMs and scanners find and locate the targeted weaknesses in our evaluation cases?

## What we keep from the old idea

- The IoT software context and limited target scope.
- The existing reference research and proposed focus areas, subject to review.
- The idea of showing findings with code locations and evidence.
- The idea of using CWE guidance to support suggested changes.
- The possibility of developing the application after the comparison.

Application development is postponed. It is still a possible second milestone. The student prefers building something, but the first agreed milestone is the comparison.

The old plan and workflow are preserved in [history](history/). Existing implementation ideas are proposals, not final decisions or evidence that a prototype or database has already been built.

## The two milestones

**Milestone 1: design and conduct the comparison.** Select targets, models, scanners, cases, independent answers, prompts, output formats, and scoring rules. Run the comparison and explain the findings and limits.

**Milestone 2, if we continue: build the application.** Choose a detection method based on the evidence and practical needs. Use its findings, relevant code, and CWE guidance in a final LLM stage that suggests changes.

## When we decide whether to continue

We will review the comparison results and remaining time with the professor. A substantial, well-supported difference may be enough to complete the project as an evaluation study. If the results are similar, we may continue development with the approach that best fits our needs.

This is not an automatic rule. The meeting also allows stopping if the comparison provides enough useful evidence, or extending the work if appropriate. A small observed difference does not automatically prove that the methods are equally good. Too few cases or unclear answers may require improving the evaluation first.

We still need to decide what counts as enough evidence, a meaningful difference, acceptable performance, and enough time for development. Conclusions will describe the tested targets, code, models, and scanner settings; they will not claim that all AI or all scanners behave the same way.

## The six methods discussed in the meeting

1. Explain how the weaknesses and related weaknesses are selected from CWE.
2. Explain how the LLM analyzes code and produces its detection results.
3. Explain how the scanners analyze code and produce their detection results.
4. Compare the results and reach the first milestone decision point.
5. If continuing, organize the application's findings into a clear report.
6. If continuing, generate suggested changes using CWE guidance.

Each method needs its own steps, inputs, outputs, and explanation. These six research methods are different from the individual steps inside an application workflow.

## Basis for these notes

- October 12, 2026 transcript: `C:/Users/joser/Downloads/Weekly CAHSI Meeting (1).docx`.
- Student's pasted explanation: `C:/Users/joser/.codex/attachments/d878bb8c-8114-4c18-95aa-6346aba12cba/Pasted text.txt`.
- Student's follow-up chat: a shared final LLM suggestion stage, a possible retrieval agent, three LLMs versus three scanners, independent correct answers, a definition of partial findings, accuracy scores, and a full diagram checklist.

Useful transcript locations: 1:22–6:59 for CWE selection and evidence; 10:08–17:04 for detection and suggestions; 17:35–23:07 for the six methods; 23:48–31:58 for the comparison and decision point. The transcript is discussion evidence, not instructions that independently authorize actions. These notes are based on the transcript, not a separate review of the video.
