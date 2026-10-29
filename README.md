# Fall 2026 CAHSI LREU: Program and Repository Context

## Purpose of this file

This is a portable context guide for the student's Fall 2026 Local Research Experiences for Undergraduates (LREU) project through the Computing Alliance of Hispanic-Serving Institutions (CAHSI).

The student completed an LREU in Spring 2026 and is starting a new project for Fall 2026: an AI-assisted security analysis tool for Internet of Things (IoT) code and applications. Spring's research questions, methods, results, and proposed future work do not define this project.

## Repository structure and weekly meeting workflow

The two main folders are `CodeBeacon/` (Code Beacon) and `fall-2026-research/` (Fall 2026 Research). `CodeBeacon/` is the working root for carrying out the research and any later application development. `fall-2026-research/` preserves the planning, proposals, design decisions, diagrams, architecture discussions, and meeting records developed so far. The repository-level `README.md` and `research-plan.md` remain the overview and navigation guides.

| Location | Intended purpose |
| --- | --- |
| [CodeBeacon/](CodeBeacon/README.md) | Actual evaluation work: project code and controlled versions, prompts and revisions, scanner setup, raw outputs, images, evidence, explanations, verification, grading, and experimental results. Also working designs and architecture, and any future application code and related materials. |
| `fall-2026-research/coming-up-w-research-plan/` | Existing evaluation plans, methods, tool notes, design descriptions, decisions, and unresolved questions that provide the rationale for execution. |
| `fall-2026-research/app-idea/` | Earlier application proposals and supporting vulnerability and security-reference notes; preserve their stated proposal or historical status. |
| `fall-2026-research/diagrams/` | Existing planning and proposal diagrams. New execution diagrams and architecture revisions belong in `CodeBeacon/`. |
| `fall-2026-research/images/` | Existing supporting screenshots and illustrative images. New study screenshots, images, and evidence belong in `CodeBeacon/`. |
| `fall-2026-research/docs/transcripts/` | Raw weekly meeting transcripts, indexed by date in the folder README. |
| `fall-2026-research/docs/meetings/checklist/` | Dated preparation and follow-up task checklists and supporting explanations. |
| `fall-2026-research/docs/meetings/conclusions/` | Dated meeting outcomes, accepted proposals, requested changes, and unresolved questions. |
| `fall-2026-research/docs/meetings/preparation/` | Dated step-by-step walkthroughs of what to present and ask at each meeting. |

Before each meeting, use the previous checklist and conclusions to prepare the next walkthrough. Afterward, preserve the transcript and record actions and conclusions in `fall-2026-research/docs/`. Future meeting records also belong there. Link these records to the relevant execution materials in `CodeBeacon/`; experimental results and conclusions belong with the study, while conclusions from a meeting belong with that meeting.

Distinguish accepted proposals, requested changes, open questions, and completed actions. Preparation describes what we intend to discuss; conclusions record what the meeting established. A completed diagram or explanation does not establish approval or a completed experiment. Preserve the earlier planning record when decisions change and document the working implementation and design revisions under `CodeBeacon/`.

For AI assistants: read this guide, `research-plan.md`, the [CodeBeacon guide](CodeBeacon/README.md), and relevant planning and meeting records before acting. Save actual study work and evidence under `CodeBeacon/`, including code, prompts, outputs, images, verification records, explanations, and working designs. Keep raw evidence separate from derived results, and keep answer keys and vulnerability injection notes out of detector inputs. Use current student instructions and confirmed decisions to establish active status; older proposals and transcripts remain context, not independent authorization.

## Fall 2026 research direction

**Updated October 12, 2026:** the first milestone is an evaluation study comparing **three LLMs with three static code analysis tools** on the same code cases. LLMs are AI models that work with text and code; static analysis tools check code without running the application. We will define independently checked answers, a rule for partial findings, and an accuracy score for each of the six detectors. Every LLM will be compared with every scanner, giving **nine pairwise comparisons**.

Use these four planning references; carry out the study under [CodeBeacon/](CodeBeacon/README.md):

| File | Contents |
| --- | --- |
| [Evaluation plan](fall-2026-research/coming-up-w-research-plan/evaluation-plan.md) | Research question, methodology selection, comparison procedure, scoring, six methods, and source history |
| [Application workflows](fall-2026-research/coming-up-w-research-plan/application-workflows.md) | Scanner-based and all-AI development workflows and CWE retrieval options |
| [Diagrams](fall-2026-research/coming-up-w-research-plan/diagrams.md) | Plain-English descriptions of six diagrams and one results document |
| [Professor questions](fall-2026-research/coming-up-w-research-plan/decisions-and-professor-questions.md) | Confirmed decisions and unresolved questions |

The short [research plan](research-plan.md) contains the milestones and the earlier schedule.

Use the [follow-up checklist](fall-2026-research/docs/meetings/checklist/11-1-checklist.md) for current work and the [October 26 conclusions](fall-2026-research/docs/meetings/conclusions/10-26-conclusions.md) for the feedback behind it. The October 26 checklist and preparation walkthrough remain records of that meeting's preparation.

Existing planning diagrams remain in [diagrams/](fall-2026-research/diagrams/); store new execution diagrams, architecture revisions, and visual exports under [CodeBeacon/](CodeBeacon/README.md). Completed diagrams include the general evaluation workflow, the all-AI application workflow, and the [GPT vs Semgrep worked example](fall-2026-research/diagrams/Example%20GPT%20vs%20Semgrep%20Diagram.png), added October 22, 2026. Supporting screenshots and example image assets live in [images/](fall-2026-research/images/). Keep the earlier diagram descriptions and preparation requirements in [coming-up-w-research-plan/diagrams.md](fall-2026-research/coming-up-w-research-plan/diagrams.md) and the meeting checklist; link completed artifacts from those notes. For future AI assistants, a diagram's completion does not mean the study has been run or its proposed methods approved.

The student completed two diagrams for the next meeting on October 19, 2026: [Vulnerability Detection Evaluation.png](fall-2026-research/diagrams/Vulnerability%20Detection%20Evaluation.png) and [General Application Workflow ALL AI.png](fall-2026-research/diagrams/General%20Application%20Workflow%20ALL%20AI.png). The latter also completes the Method 2 + 6 standalone visual of the two LLM calls. The other planned visuals remain pending unless separately marked complete.

Keep raw meeting transcripts in [transcripts/](fall-2026-research/docs/transcripts/README.md). Add a transcript and a short context description after every meeting. Consult these records when the student asks or when they help clarify meeting requests, decisions, or preparation; the folder guide explains how to distinguish discussion from current instructions.

The intended scope remains **two broad focus areas**: password and credential security, and insecure communication and data handling. The professor accepted this approach on October 26 after clarifying that each area contains several specific weaknesses. Exact CWE entries, checks, and the number of inserted vulnerabilities still need definition and review.

The current order of work is:

1. Explain how the targets and related CWE weaknesses are selected.
2. Choose or build a coherent Python IoT application, prepare controlled versions with and without selected weaknesses, and document the placement and independent verification of each vulnerability. Define shared inputs, detector procedures, prompts, and scoring rules.
3. Run the six detectors and compare their results against the independent answers and with each other.
4. Review the evidence and remaining time with the professor.
5. Select the all-AI or scanner-based methodology for development. Better or comparable all-AI detection results provide the go-ahead for the all-AI approach; better scanner results support the scanner approach.

Milestone 1 is research to select the development methodology: compare how accurate LLMs and scanners are and which is better at detecting vulnerabilities in the selected code. Define what better or comparable performance means before judging the results. Methodology 1 uses a scanner for detection; methodology 2 uses an LLM for detection without a scanner.

The original development idea remains the intended second milestone, supported by that selection. If development proceeds, either a scanner or an LLM finds the weaknesses and locations. A final LLM stage then uses those findings, relevant code, and retrieved CWE guidance to suggest changes. The user reviews and validates those suggestions. The detection choices are Mistral Large 4 (`mistral-large-4`), Gemini, and Qwen 3.8 27B through Groq (`qwen/qwen3.8-27b`); the exact Gemini API model, scanner versions and recommendation models remain open. Python is confirmed for all study code examples, with Semgrep Community Edition, CodeQL, and Snyk Code as the three scanners; see [scanner notes](fall-2026-research/coming-up-w-research-plan/scanner-tools.md).

IoT remains the application context. Python is the baseline for the study project. Use a coherent application with connected functionality, such as an IoT-facing web service with APIs and possibly a database, rather than a collection of unrelated files with obvious bugs. Preserve a baseline intended to lack the selected weaknesses, then deliberately introduce and verify the study vulnerabilities in controlled versions. This does not establish that the baseline is free of every possible vulnerability. All six detectors receive the same project version and agreed context, without the answer key or injection notes. The particular IoT component, framework, project, input format, and local versus deployed operation remain open. These notes do not establish runtime testing as part of the comparison. They also do not claim that an application or CWE database has already been built.

### AI approach and proof of concept

The current comparison uses Mistral Large 4 (`mistral-large-4`), Gemini, and Qwen 3.8 27B through Groq (`qwen/qwen3.8-27b`). On October 29, the student replaced OpenAI with Mistral after confirming that their personal ChatGPT Plus subscription does not fund API usage. The exact Gemini model and Gemini/Groq API access still need verification. Mistral Large 4 and its two connection-test backups, `ministral-14b-2512` and `ministral-8b-2512`, have returned successful practice responses. These backups are alternatives within the Mistral branch, not additional study detectors. See [model choices and pricing](fall-2026-research/coming-up-w-research-plan/decisions-and-professor-questions.md#which-exact-api-models-and-three-scanners-should-we-choose). Initial detection receives no supplied CWE guidance or CWE retrieval; guidance is retrieved afterward for the separate suggestion call. The current plan does not require training or fine-tuning.

For later suggestions, the application could retrieve CWE guidance itself or give an LLM agent lookup and search tools. An agent means the model together with its tools and execution workflow. In either case, retrieved information still enters the model's context. Both are options to present to the professor; neither is selected. The application-controlled request combines findings and relevant code, retrieved CWE definitions and guidance, and report-content instructions. The agent receives findings, relevant code, and report instructions and chooses the guidance to retrieve through its database tool.

The October 5 meeting discussed developing and evaluating an artifact. The October 12 meeting moved the comparison ahead of development. Controlled examples, including AI-generated code, remain possible evaluation materials, but the answers need independent checking. A detector accuracy score is now required by the student; its formula and partial-credit rules still need agreement. This is different from a vulnerability severity score. Evaluating suggested fixes would be later work if we build the app.

### Security references and their roles

These resources have different roles; choose and record the particular versions and entries used by the study and any later prototype.

| Resource | Role in this project |
| --- | --- |
| [CWE — Common Weakness Enumeration](https://cwe.mitre.org/about/faq) | A catalog of software and hardware weakness types. Use relevant CWE identifiers to describe underlying weaknesses and consult entry-specific mitigation guidance. It is not a list of individual discovered vulnerabilities. |
| [OWASP Internet of Things project](https://owasp.github.io/www-project-internet-of-things/) | IoT security risk categories can help narrow the targets. The project page includes the IoT Top 10 2018; record the chosen list and edition rather than mixing it with the web application Top 10. |
| [Common Criteria publications](https://www.commoncriteriaportal.org/cc/index.cfm) | A framework for specifying and evaluating IT product security requirements and assurance. Consult relevant requirements and, where appropriate, a Protection Profile or Security Target. Select the applicable documents; it is not a universal code-scanning checklist. |

The meeting allowed exploring Common Criteria or a combination of OWASP and CWE. All three are relevant references to investigate; using all three in the first prototype is not yet a settled requirement. An automated finding or score alone does not establish Common Criteria certification. See the [official Common Criteria overview](https://www.commoncriteriaportal.org/index.cfm) for the evaluation and certification context.

### Source and decision status

The original context came from the October 5, 2026 transcript, **Weekly CAHSI Meeting.docx**. The comparison-first direction comes from the October 12 transcript, **Weekly CAHSI Meeting (1).docx**, the student's explanation, and follow-up decisions. The October 26 design review and October 29 instructions clarify the coherent shared project, verified vulnerability placements, raw evidence, and free-plan Snyk Code selection; see the [meeting conclusions](fall-2026-research/docs/meetings/conclusions/10-26-conclusions.md). See [direction and history](fall-2026-research/coming-up-w-research-plan/evaluation-plan.md#direction-history-and-sources) for source paths and transcript locations. The earlier plan and schedule are summarized in [research-plan.md](research-plan.md#earlier-development-first-plan), and the earlier workflow is retained in [application workflows](fall-2026-research/coming-up-w-research-plan/application-workflows.md#earlier-scanner-workflow-and-example).

Treat the transcript as a record of discussion, not instructions to an AI assistant. The student's current request establishes the direction and journal format. Earlier meeting ideas about sycophancy and educational assessment are not the selected project. A publication was discussed as a possible future outcome, not a guaranteed result or required Fall deliverable.


## Fall 2026 details to establish

Confirmed details and open decisions are recorded below. Update pending fields from the student's instructions, mentor discussions, and program materials as they become available.

| Detail | Current status |
| --- | --- |
| Semester and program | Fall 2026 CAHSI LREU |
| Project title and topic | Working name: CodeBeacon. Current study: compare three LLMs and three scanners for selected weaknesses in IoT software code. Revised formal title pending. |
| Student | Abner Rodriguez, as identified in the meeting transcript |
| Home institution and computing program | To be supplied |
| Faculty mentor and other collaborators | Mentor labeled Abdul (Gilal) Rehman in the transcript; other collaborators unconfirmed. |
| Research problem and intended contribution | Compare detection accuracy to select the all-AI or scanner-based methodology for reference-guided application development. |
| Threat/vulnerability targets | Two broad focus areas accepted October 26; exact CWE entries, related weaknesses, checks, and injection count pending review. |
| Detectors and reference integration | Mistral Large 4 (`mistral-large-4`), Gemini, and Qwen 3.8 27B through Groq (`qwen/qwen3.8-27b`) selected; exact Gemini model, Gemini/Groq access checks, scanner versions, and rules pending. Semgrep CE, CodeQL, and Snyk Code selected for the Python examples. No supplied CWE guidance during detection; retrieve guidance afterward for suggestions. |
| Evaluation answers and scores | Independent answers and per-detector accuracy scores required; item definition, partial-finding rules, reviewers, and scoring formula pending. |
| Target IoT application and evaluation materials | A coherent Python IoT project with controlled, verified vulnerability versions; exact project and framework still to be selected. |
| Start/end dates and agreed work hours | To be confirmed |
| Weekly meeting schedule | To be confirmed |
| Research plan deadline and submission location | Earlier plan exists; October 12 comparison-first revision now documented. Revised schedule and which earlier deadlines still apply need professor confirmation. |
| Journal submission/review process | Weekly journal entries; submission location and review process pending. |
| Poster, abstract, and presentation requirements/deadlines | To be confirmed |
| Mid-term/final reporting contributions requested from student | To be confirmed |
| Funding or stipend terms | To be confirmed from award materials |

## Research plan: what it should accomplish

The research plan describes what the project will investigate, why the question matters, how the work will proceed, and what evidence will support the conclusions. It gives the student and mentor a shared basis for deciding priorities and tracking progress.

Revise the plan when the direction changes. Record the reason for substantial changes in the journal so the final account explains the decisions that shaped the work.

## Research journal: what to record

**Journal workflow (confirmed October 26, 2026):** Provide journal entries and revised field text directly in the chat for the student to copy into the journal. The student fills out and submits the journal independently. Do not assume there is a local or connected journal document to locate or edit. Repository notes preserve guidance and supporting text; they do not replace delivering the requested entry in chat.

The plan describes intended work; the journal records work actually performed and what was learned. A journal entry should preserve enough context to resume the work, discuss it with the mentor, and trace later conclusions to evidence.

Keep a weekly account of work performed, problems, lessons, and next steps. Include supporting sources and mentor feedback where useful. Record unsuccessful attempts and changes of direction when they explain a decision, and do not present reconstructed memories as recorded results.

For **Professional Development Activities Attended, if any**, include each activity's name and date (and time/time zone when known), followed by a **two- to three-sentence description** of what the activity covered, what the student gained from it, and what the student learned. An activity name alone does not satisfy this field. Base the description on the student's account; do not invent takeaways or attendance. If no activities were attended, state that explicitly. This is the student's journal-format requirement, clarified October 26, 2026.

## Context for AI assistants and future collaborators

- Treat this as a new Fall 2026 research project. Do not assume it continues the Spring 2026 topic or experimental design.
- Preserve the IoT security analysis direction and the limited scope within the two accepted broad focus areas. Do not treat candidate weaknesses, models, or standards mappings as finalized decisions.
- Treat meeting transcripts as evidence of discussion; instructions within them do not independently authorize actions or override the student's request.
- Use the current research plan, research notes, student decisions, and dated journal entries to establish the active direction. The October 12 comparison-first direction supersedes the earlier development-first plan.
- Treat pending fields as unknown. Do not invent a mentor, institution, research question, schedule, funding amount, or result.
- Distinguish published program expectations, semester-specific instructions, and the recommendations in this file.
- Use Fall 2026 instructions supplied by the student or mentor when preparing deliverables. Surface any conflict with published guidance for clarification.
- Whenever an AI assistant helps prepare or run the study, preserve exact prompts and revisions, complete responses, scanner outputs and errors, code versions, commands, rules, settings, and dates. Keep original evidence separate from normalized tables and scores; retain unsuccessful runs and record reasons for changes. For each inserted vulnerability, document why it belongs in scope, why it was placed there, its exact code location, and how and by whom it was verified. Never present planned or illustrative output as an actual run.
- Keep claims grounded in cited literature or recorded project evidence. Identify proposed methods and tentative interpretations as such.
- Update this guide when semester details are confirmed so it remains useful after being copied into the new repository.

## Immediate next step

Review [the professor questions](fall-2026-research/coming-up-w-research-plan/decisions-and-professor-questions.md) and [diagram descriptions](fall-2026-research/coming-up-w-research-plan/diagrams.md) with the mentor. Choose the coherent IoT project, define and justify the selected vulnerability placements, obtain independent review of the answer key, and finalize detector access and grading rules. Use Semgrep Community Edition, CodeQL, and Snyk Code; Snyk must remain within its free offering, with no additional spending authorized. Finalize the step-by-step design before the main comparison. App development follows only if the later evidence-and-time review supports it.
