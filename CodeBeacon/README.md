# CodeBeacon: research execution and application

`CodeBeacon/` is the working root for carrying out the research. The repository has two main folders: this folder for execution and [fall-2026-research/](../fall-2026-research/) for the planning and meeting record. The repository-level [README](../README.md) and [research plan](../research-plan.md) provide overall context.

`CodeBeacon/` has two main subfolders:

| Folder | Purpose |
| --- | --- |
| [evaluation-study/](evaluation-study/) | Everything used to prepare and execute the evaluation study, including its code, documents, prompts, configurations, logs, evidence, analyses, and results. |
| [app/](app/) | The optional CodeBeacon application and its code, documentation, assets, and architecture, if the idea proceeds and there is time to develop it. |

Put the evaluation study's actual materials under `evaluation-study/`: the coherent IoT test project and its controlled versions, vulnerability placement explanations, independently reviewed answer keys, exact prompts and revisions, scanner configurations and commands, run settings, complete raw responses and reports, errors, screenshots, images, verification evidence, grading, scores, comparisons, and conclusions from the experiments. Keep answer keys and injection notes separate from the project inputs given to detectors.

Use `evaluation-study/` for the working study designs and revisions to earlier evaluation proposals. If application development proceeds, its code, configuration, tests, documentation, architecture, and related assets belong in `app/`. The evaluation project is study material; it is distinct from the optional CodeBeacon application being developed later.

The earlier planning notes, proposal diagrams, architecture discussions, and supporting images remain under [fall-2026-research/](../fall-2026-research/). Consult [the planning notes](../fall-2026-research/coming-up-w-research-plan/evaluation-plan.md) and [meeting records](../fall-2026-research/docs/) for their rationale and status. Weekly transcripts, preparation, checklists, and meeting conclusions continue to belong in `fall-2026-research/docs/`, including future meetings. Experimental conclusions and run evidence belong in `evaluation-study/`.

AI assistants should read the planning and meeting context before acting, then save study execution work under `CodeBeacon/evaluation-study/` and optional application development work under `CodeBeacon/app/`. Preserve exact inputs, code versions, prompts and revisions, complete outputs, errors, commands, configurations, settings, versions, dates, and reasons for changes. Keep raw evidence separate from normalized results and retain practice and unsuccessful runs. Record why and where each vulnerability was inserted and how and by whom it was verified. Do not present a proposed design, illustrative output, or unchecked answer key as a completed experiment or validated result.

The three selected scanners are Semgrep Community Edition, CodeQL, and Snyk Code, using Snyk's free plan only. The comparison remains the first milestone; application development depends on the findings and available time. This README establishes where work belongs; detailed subfolders can be chosen as the study is implemented, and no experiment, codebase, or completed implementation is implied by this guide.

The three selected detection model families are Mistral Large 4 (`mistral-large-4`), Gemini, and Qwen 3.8 27B through Groq (`qwen/qwen3.8-27b`). Mistral replaces OpenAI as of October 29, 2026. The Mistral request script uses `ministral-14b-2512` and `ministral-8b-2512` as verified backups; these are alternatives within one detector branch, not additional study detectors. Select the exact Gemini model and verify Gemini/Groq access before scored runs.

The Mistral script and Python requirements now live in `evaluation-study/`. Run its commands from that folder; `.env` and `.venv` also belong there. The script saves request logs to `evaluation-study/evaluation-runs/mistral/`. Keep preparation/practice outputs distinct from scored study outputs within the evaluation-study folder.
