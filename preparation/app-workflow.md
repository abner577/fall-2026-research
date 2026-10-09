# Simplified app workflow

1. **The user submits their code.** The app receives the project files.
2. **The app prepares the files.** If the upload is a ZIP, the app extracts it. It identifies the language and the files needed for analysis. This step does not require an LLM.
3. **The app runs focused code checks.** It runs an existing code scanner with selected rules for the two vulnerability types we want to examine.
4. **The app gathers context.** For each possible issue, it collects the scanner result, the relevant code, and supporting guidance from the knowledge base.
5. **The LLM reviews the possible issues.** It uses that information to explain whether an issue appears applicable and suggest a fix. If information is missing, it says what is needed.
6. **The app returns a report.** The user sees where the possible issue is, why it matters, and how they could fix it. Suggested code changes should be checked before use.

## Simple example

A user uploads a project. The scanner finds a password written directly into the code. The app collects the surrounding code and relevant guidance, then passes them to the LLM. The LLM checks how the password is used and explains the possible problem. The report points to the location and suggests moving the password out of the source code and loading it through an appropriate configuration mechanism.

## Would the user upload a ZIP?

A ZIP is a feasible input format and a practical starting choice because it keeps the project's files and folders together. We could require it for the first version to keep uploads simple, but scanners do not inherently require ZIP uploads. Other input options could be added later.
