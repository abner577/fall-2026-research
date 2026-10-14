# Possible application workflows

Updated October 12, 2026. These workflows describe the possible development milestone. They do not mean development has started or a detection method has been chosen.

## What both workflows do

A user provides code. The application identifies possible weaknesses and where they are. It then sends the findings, relevant code, and useful CWE guidance to an LLM to request suggested changes. It returns a report for the user to review and validate.

Milestone 1 selects between these two methodologies. Better or comparable all-AI detection results provide the go-ahead to continue development with methodology 2. Better scanner results support methodology 1. The meaning of comparable and the development schedule still need agreement. Detection results do not establish the quality of final suggestions; those need their own checks.

## Methodology 1: scanner-based detection

1. Receive code and a short description of what the software does.
2. Prepare the files and identify the supported code. Keep file names and locations intact.
3. Run the selected scanner with the agreed checks.
4. Collect possible findings, locations, code evidence, and any limits of the scan.
5. Retrieve the relevant CWE entries and guidance for those findings.
6. Ask the LLM what changes would address the findings, using the code and guidance.
7. Return a report with the issue, location, explanation, suggested change, source, and any checks still needed.

The original app workflow used this approach. Python is confirmed for all study examples, and Semgrep Community Edition, CodeQL, and Bandit are selected for the comparison. The scanner used in the eventual application will depend on the comparison and applicable tool terms. See [scanner choices and report formats](scanner-tools.md).

## Methodology 2: LLM detection or all-AI

1. Receive code and a short description of what the software does.
2. Prepare the files and identify the supported code. Ordinary file preparation does not need AI.
3. Ask the detection LLM to identify the agreed weaknesses and related weaknesses, with file locations and evidence. Do not supply CWE guidance or CWE retrieval tools in this first call.
4. Read and check the structure of its findings. Record uncertainty and missing context; a well-formatted answer is not proof that the finding is right.
5. Retrieve the relevant CWE entries and guidance for those findings.
6. Make a subsequent LLM request for suggested changes, using the findings, code, and guidance.
7. Return the same kind of report as in Workflow A.

The detection and suggestion stages could use the same model in separate requests or different models. That choice is pending. An agent that makes retrieval requests may require several LLM calls within the suggestion stage, so this is a sequence of stages rather than a promise of exactly two API calls.

## General workflows and our specific application

A general design can ask about broad vulnerability types, while our experiment and specific app name the selected weaknesses. The detection call has the same purpose, but its instructions and expected answer depend on that scope. Neither version supplies CWE guidance during detection; the application retrieves guidance afterward for suggestions. The two general workflow diagrams describe the scanner-based and all-AI processes. If development proceeds, create one additional diagram for our specific application using the selected methodology and our two fixed targets. In the all-AI version, the detection prompt would name those targets and ask the model to find them in the supplied code. General workflows do not promise complete vulnerability coverage.

Present application-controlled and agent-controlled retrieval as two options for professor review. Diagrams using application-controlled retrieval illustrate the first option, not a selected implementation. [Diagram descriptions](diagrams.md) defines the requested contents in plain English.

## Saved uploads and findings reports

The student described this application design on October 14. After upload, show a "Processing" screen and then a report for that upload. Save the upload record, report, and finding statuses so the dashboard can list previous uploads with their unresolved counts. The storage mechanism is still to be designed; this is planned application behavior, not a completed feature.

Each report lists all detected potential vulnerabilities. Selecting one opens its explanation, why it matters, how the uploaded code causes or exposes it, file and line locations where available, and supporting code. Show uncertainty and unavailable locations explicitly. A separate "Proposed changes" tab or section presents replacement code blocks and instructions for changes spanning files or requiring setup. For example, instructions might describe creating a `.env` file with named settings and changing the relevant code to read them; use placeholders in examples. This is an illustration of the instruction format, not a universal fix. Keep every suggestion linked to its finding; the guidance-backed LLM stage generates the content.

Users can mark findings resolved. Save that status and update the unresolved count on the report and upload dashboard: seven findings become six unresolved when one is marked resolved. Reopening the upload preserves that count. Retain the original findings and distinguish user-confirmed resolution from a later scan of updated code; marking resolved alone does not change the uploaded source or verify a fix. The count describes unresolved reported findings, not a guaranteed total of vulnerabilities remaining in the code. Found/Missing/Partially Found are study grades, not resolution statuses for ordinary uploads.

## The final suggestion stage

This stage uses findings from either the scanner or the first LLM call to generate content for the report UI: explanations of the weaknesses, why they matter, how the supplied code exposes them, locations and evidence, proposed replacement code, and written instructions for other changes. Include the guidance sources used and any missing context. The exact prompt wording, output fields, and suggestion model can be selected later. This stage follows detection and does not change the initial detection comparison.

## Retrieving guidance: application or agent?

**Option 1: Application-controlled retrieval.** The application retrieves relevant CWE definitions and guidance from the planned database before calling the suggestion LLM. The request has three main parts:

1. Findings from the scanner or previous LLM call, with file locations and relevant code.
2. Retrieved CWE information: formal definitions, signs of the weakness, consequences, and available mitigation guidance.
3. Instructions specifying the content and structure needed for the report, including explanations and the proposed-changes section.

**Option 2: Agent-controlled retrieval.** The application sends the findings, relevant code, and required report structure through an API to an agent we create. The agent is an LLM with a lookup/search tool connected to the planned CWE vector database. It chooses which information to request, the application executes those tool calls and returns the passages, and the model uses them to generate the same report content. Searches and follow-up requests may require several LLM calls. The retrieved guidance still enters the model's context; the difference is who chooses what to retrieve and when.

**Choice for professor review:** present both options without treating either as selected. An exact CWE-ID lookup can retrieve a known entry; vector search can retrieve related passages. The database, tools, contents, and update process are planned rather than implemented. Older diagrams using application-controlled retrieval illustrate option 1, not a final decision.

For either option, the LLM applies the guidance to the supplied code; a CWE entry does not necessarily contain a ready-made fix. See [MITRE's CWE-798 entry](https://cwe.mitre.org/data/definitions/798.html) for an example of available guidance. Review the resulting explanations and proposed changes, check their source support, and test changes before use. Retrieving a passage or generating a report does not by itself validate a fix.

## Still open for development

Local versus deployed operation; input format; Python framework (Python is confirmed for the study examples); application or device context; selected detector; models for the two stages; code size and cross-file context; database and retrieval design; how suggested changes will be validated; and whether development fits the remaining schedule.

See [the question list](decisions-and-professor-questions.md) for the decisions to take to the professor, and [diagrams](diagrams.md) for the requested plain-English descriptions.

## Earlier scanner workflow and example

The original workflow was: receive project files, extract a ZIP if used, identify the relevant code, run focused scanner checks, gather findings and surrounding code with reference guidance, ask an LLM to review and explain the possible issues and suggest fixes, and return a report. Ordinary file preparation does not require an LLM. Missing information should be identified, and suggested changes checked before use.

For example, a scanner might find a password written directly into code. The app collects the surrounding code and relevant guidance. The LLM checks how that password is used, explains the possible problem, and suggests moving it out of source code into an appropriate configuration mechanism. This is an illustrative workflow, not a completed test.

ZIP input remains a feasible proposal because it preserves project files and folders. Scanners do not inherently require ZIP uploads, and the first application's input format is still open.
