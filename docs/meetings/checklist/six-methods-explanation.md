# Six methods: meeting preparation

## Method 1: How we selected the vulnerabilities

We started with the OWASP IoT security categories and chose two areas: password and credential security, and insecure communication and data handling. Within these, we identified checks such as hardcoded credentials, predictable passwords, weak password requirements, unsafe password storage, unprotected sensitive communication, disabled certificate checks, exposed secrets, and missing identity or permission checks on sensitive endpoints. We chose these because they matter to IoT applications and can be examined through code and configuration, making them useful for comparing LLMs and scanners. We will match the checks to specific CWE entries, check any AI suggestions against those entries, and review the final scope with the professor. The result is a limited target list that all six detectors will use, rather than an attempt to cover every IoT security problem.

## Method 2: How the LLMs examine the code

We chose Gemini, ChatGPT/OpenAI, and Groq because Gemini and Groq offer free tiers, and the student already pays for OpenAI access and intends to use that existing access without additional spending. For Groq, we selected Qwen 3.8 27B (`qwen/qwen3.8-27b`) because it supports coding and reasoning, is available on the free plan, and adds a different model family to the comparison. Exact Gemini and OpenAI models remain to be selected. In the full AI workflow, the first call sends the uploaded code and asks the selected model to identify possible vulnerabilities and where they occur, without supplying CWE guidance. For our experiment and specific app, we name the selected weaknesses it should look for; in a general design, we could instead ask about broader types of vulnerabilities. The detection call serves the same purpose, while the instructions and expected answer change with the scope; exact wording and format can come later. Once we receive the findings, the application retrieves relevant CWE guidance from the planned database and sends it, the findings, and relevant code in a second LLM call asking for explanations and proposed changes based on that guidance. The first call produces findings for the detection comparison; the second produces suggestions for review if application development proceeds.

## Method 3: How the scanners examine the code

All study code examples will use **Python**, and we selected **Semgrep Community Edition, CodeQL, and Bandit** as the three scanners. Bandit is free and straightforward to run on Python code. The user uploads code files, and the application prepares them, extracting an archive if needed while keeping file names and locations. We select or write rules for the weaknesses in our scope, then pass the prepared code to each scanner separately. Semgrep checks code against structural patterns; CodeQL first builds a database of the code and runs queries that can follow relationships and data movement; Bandit examines Python code using security checks called plugins. These tools inspect code without running the application itself, although CodeQL setup can require a build for some languages. They report possible matches to the checks, rather than guaranteeing that every vulnerability has been found. In the scanner-based app, we collect those findings and relevant code, retrieve CWE guidance, and ask an LLM to explain the issues and propose changes. Exact rules and versions can come later; see [scanner choices and sources](../research/scanner-tools.md).

The output is a report with individual findings. **Semgrep CE** can return JSON containing the rule identifier (`check_id`), file (`path`), start and end lines and columns, a message explaining the concern, and severity. **CodeQL** can return SARIF, a standard JSON report format, containing a rule identifier, an explanatory message, and the file and location; some queries also return a path showing how data moves through the code. **Bandit** can return JSON containing the check identifier, file, line and line range, code snippet, issue description, severity, and confidence, with CWE information where available. The explanation depends on the rule, and a detailed fix is not guaranteed. We preserve the original reports and errors and collect the available fields in a shared format for comparison; code snippets missing from a report can be read from the original files. [Report fields and short examples](../research/scanner-tools.md#what-a-finding-looks-like) show how these outputs differ.

## Method 4: How we compare the results

We prepare Python code examples with known vulnerabilities and write independently checked answers before running the tools, recording what each vulnerability is and where it appears. All three LLMs and three scanners examine the same examples, and we compare their findings with those answers in a table marked **Found, Missing, or Partially Found**. As a starting proposal, Found means identifying the vulnerability and its location (1 point); Missing means failing to identify a vulnerability that is present (0 points); and Partially Found means recognizing the actual problem but giving an incomplete location or explanation (half a point). For example, correctly identifying a hardcoded credential in the right file but not locating its use could earn partial credit; a vague warning alone would not. We calculate a proposed accuracy score by dividing earned points by the number of known vulnerabilities and multiplying by 100. We also record false alarms and performance on examples without the weaknesses, since finding more issues is only useful when they are real. We compare each detector's table and score to guide the methodology choice, while noting the rule-maintenance trade-off. These definitions and half-credit rules are a proposal we can refine with the professor before the scored runs.

**Completed supporting visual, October 22, 2026:** [GPT vs Semgrep worked-example diagram](../diagrams/Example%20GPT%20vs%20Semgrep%20Diagram.png). It follows one GPT and one scanner through the same code example, illustrative findings, answer-key grading, scores, and grading comparisons. [Example details](comparison-example-details.md) contain the prompt, draft key and scoring conventions. The outputs are invented to explain the method, not experimental evidence.

## Method 5: How findings would be organized for the application

After a user uploads code, the app shows "Processing" and then opens a report for that upload, which is saved in a dashboard alongside previous uploads. The report lists all detected potential vulnerabilities, with a counter of unresolved findings. Clicking a finding shows what it is, why it matters, how the uploaded code exposes the problem, and the relevant files, lines, and code evidence where available; missing details or uncertainty are shown clearly. A separate "Proposed changes" tab or section contains replacement code blocks and plain-English instructions for changes that involve other steps, such as creating a configuration file and updating references in several files. Suggestions stay linked to the finding they address. Users can mark each finding resolved, reducing the saved unresolved count, so an upload with seven open findings shows six after one is marked resolved. The original findings remain available, and the status means "marked resolved by the user" unless a rescan checks the updated code. Found, Missing, and Partially Found remain study grades based on known answers; the user report tracks detected findings and their resolution, without claiming to know every vulnerability in the upload.

## Method 6: How suggestions would be generated

**Option 1: Application-controlled retrieval.** After the previous step, we have the vulnerabilities found by either an earlier LLM call or a code scanner. Our application looks up the CWE information for those vulnerabilities in our planned database. We then send the LLM three main things: the vulnerabilities and the code where they were found, the CWE definitions and guidance, and instructions saying what to write for our report. We are basically saying, "Here are the vulnerabilities we found, here is the information about them and how to deal with them, and here is what we need you to explain and suggest." The LLM gives us the content we need to show in the report, including explanations, suggested code changes, and instructions for changes the user needs to make.

The API prompt could be organized like this; this is an outline, so the exact wording can come later:

```text
[Part 1: The vulnerabilities from the previous step]
Here are the vulnerabilities found by the earlier LLM call or code scanner:
[Insert the findings, file names, lines where available, and relevant code.]

[Part 2: The CWE information our application looked up]
Here are the definitions and guidance for those vulnerabilities:
[Insert what each weakness means, how to recognize it, why it is bad,
and the available guidance for fixing it.]

[Part 3: What we want the LLM to produce for the report]
Use the code and guidance above to prepare the following for each finding:
- Explain the vulnerability, why it matters, and how it appears in this code.
- Show the file and lines where available, with the code that shows the issue.
- In a separate proposed-changes section, give replacement code where useful
  and explain any other steps, such as creating a file or changing other files.
- Name the CWE guidance used and explain anything you cannot determine.
Keep each explanation and proposed change linked to its finding.
```

**Option 2: Agent-controlled retrieval.** We send the vulnerabilities from the previous step, the relevant code, and instructions for what our report needs to an agent we create, through an API. The agent is an LLM with a search tool connected to our planned CWE vector database. Instead of our application choosing the CWE information and putting it all into the first message, the agent decides what it needs to look up and asks the tool to get it. Our application carries out those searches and sends the information back to the LLM. It then uses that information to write the same explanations and proposed changes for the report. This can take several calls. Both options are open for the professor to choose from, and the suggested changes still need review and testing before use.

The message to the agent could look like this:

```text
[Part 1: The vulnerabilities from the previous step]
Here are the findings from the earlier LLM call or code scanner:
[Insert the findings, file names, lines where available, and relevant code.]

[Part 2: Instructions to look up the CWE information]
Use your CWE database search tool to get the definitions and guidance
needed to explain these vulnerabilities and suggest changes.

[Part 3: What we want back for the report]
For each finding, return an explanation, why it matters, how it appears
in this code, and its file and lines where available. Include a separate
proposed-changes section with replacement code and any written steps.
Name the CWE guidance used and explain anything you cannot determine.
[We will define the exact output fields the report needs later.]
```

Preparation sources: [selected focus areas](../app-idea/selected-vulnerabilities.md) and [next meeting checklist](next-meeting-checklist.md). Model choices and access details: [decisions and questions](../research/decisions-and-professor-questions.md).
