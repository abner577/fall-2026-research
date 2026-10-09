Use this order: explain how the app would work, then ask about deployment, evaluation projects, system scope, languages, and the security checks.

## Introduce the proposed workflow

Start with: “The idea is to give the app an IoT project and have it identify possible security weaknesses, explain them, and suggest fixes.”

Before walking through the steps, explain the knowledge base: “We will use the security references given to us, starting with CWE. The knowledge base is a searchable collection of selected CWE entries relevant to our security focus areas. It contains the original descriptions, examples, detection guidance, and mitigation guidance where available, along with the source links and versions.”

Explain RAG in plain language: “RAG means retrieval-augmented generation. After the scanner identifies a possible issue, the app searches the knowledge base for relevant CWE information. It retrieves the original passages as written, rather than asking the LLM to recall the reference from memory. We can look up a known CWE identifier directly or search for related descriptions.”

Explain how that information is used: “The app passes the retrieved passages to the LLM alongside the scanner finding and relevant code. The LLM uses those references to assess the possible issue and explain a suitable fix. The knowledge base supplies guidance; it does not scan the code itself or prove that a vulnerability exists. This process does not train a new model.”

Walk through these steps:

- **Upload:** The user submits a ZIP and a short description of what the product does.
- **Prepare:** The app extracts the files and identifies the languages and project components.
- **Scan:** A static analysis tool runs selected checks against the code.
- **Gather context:** The app collects the findings and surrounding code, then retrieves relevant original CWE passages from the knowledge base to include in the LLM's input.
- **Review:** An existing LLM reviews that evidence and generates explanations and suggested fixes.
- **Report:** The user gets possible issues, their locations, supporting evidence, and recommendations.

Explain “static check” here: it examines code without running the application. We select rules or queries that tell the scanner what suspicious behavior to look for.

Explain why we divided the work this way: the scanner provides concrete evidence, the knowledge base provides guidance, and the LLM helps interpret and explain both. Retrieving documents does not train a new model.

Mention that we propose starting with CWE guidance and considering Common Criteria later. Give him room to correct that approach here.

Ask: **“Does this workflow make sense for the proof of concept?”**

## Ask whether others should be able to try the deployed app

Say: “I would like to deploy it to demonstrate the research, but I want to confirm whether that belongs in the project.”

Ask: **“Should this remain a local research prototype, or should other people be able to upload projects and try it?”**

Explain why this matters:

- CodeQL builds a representation of the project and runs selected queries against it.
- Semgrep runs selected code-pattern and data-flow rules.
- CodeQL permits academic research, but its standard terms restrict providing it through a hosted scanning service.
- Semgrep Community Edition with our own rules is the more straightforward starting option for the upload service.

Keep the distinction clear: showing a recorded demo or research results is different from letting visitors upload code for scanning. Keeping the project private does not automatically settle every CodeQL licensing condition.

## Ask what projects we should use for evaluation

Ask: **“What projects should we use to test whether the app works?”**

Offer the options we have discussed: controlled examples, open-source IoT projects, or projects he provides.

Explain why we need this answer early: the evaluation projects will help determine which languages, frameworks, and libraries we actually need to support.

Mention that we need both vulnerable examples and safe examples, so we can check whether the app finds problems without flagging everything.

## Explain the parts of an IoT system, then ask which to prioritize

Introduce the four parts before asking:

- **Browser interface:** The dashboard or page people interact with.
- **Backend services:** Accounts, APIs, data storage, and server-side processing.
- **Gateway applications:** Software that collects, processes, or forwards messages between devices and other systems.
- **Embedded firmware:** Code running directly on the device.

Explain that a project can contain several of these parts, and some systems combine roles.

Ask: **“Which parts should our first version prioritize? All four, or a particular combination?”**

Explain why it matters: broader scope means more languages, libraries, rules, and test cases. Focusing on firmware would give us a different implementation task from focusing on backend APIs.

## Present the language list and confirm the initial support

Once he answers the scope question, show this list:

| System part | Proposed language priorities |
|---|---|
| Browser interface | JavaScript/TypeScript, with HTML/CSS as supporting files |
| Backend services | Python, Java, JavaScript/TypeScript |
| Gateway applications | Python, Java, C++ |
| Embedded firmware | C/C++ first; Python variants where relevant |

Explain that users can upload one mixed-language ZIP. We handle the different languages internally and combine the findings.

Then explain the development cost: each supported language needs suitable rules or queries. Frameworks and connection libraries also matter. Existing checks can help, but scanner support for a language does not automatically mean our app covers every application written in it.

Ask: **“Based on the scope and evaluation projects, which languages and frameworks should we commit to supporting first?”**

## Present the two security focus areas and ask for confirmation

Explain what we chose before asking whether he agrees.

**Password and credential security:**

- Hardcoded credentials.
- Predictable password generation.
- Weak password requirements.
- Unsafe storage of login passwords.

**Insecure communication and data handling:**

- Sensitive information sent without appropriate transport protection.
- Disabled certificate verification.
- Secrets exposed in logs or files.
- Sensitive backend endpoints missing authentication or authorization.

Mention the overlap: endpoint checks also belong to category 3, while password storage overlaps with category 7. We are choosing two practical focus areas, not claiming complete coverage of two OWASP categories.

Explain why we chose them: they can provide evidence in uploaded code, understandable fixes, and examples we can evaluate.

Briefly explain the other eight:

- **Network services:** Actual exposure often requires deployment information.
- **Ecosystem interfaces:** We include selected endpoint checks; full coverage is broader.
- **Secure updates:** Requires update code and knowledge of the update process.
- **Outdated components:** Feasible, but mainly dependency-version matching.
- **Privacy protection:** Often requires information about permitted data use.
- **Device management:** Depends on how deployed devices are maintained.
- **Default settings:** Some are covered by our selected checks; deployment can change them.
- **Physical hardening:** Requires examining the device’s physical protections.

Ask: **“Are these focus areas and checks appropriate, or should we narrow, replace, or change any of them?”**
