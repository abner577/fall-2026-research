## Choosing between Semgrep and CodeQL
- Both these tools work in the same way: you give them source files and a set of checks; they return location where those checks find suspicious code. They understand programming langauge structure rather than merely search for words. More advanced cchecks can trace where data comes from and where it goes.

### Semgrep vs CodeQL

| | Semgrep Community Edition | CodeQL |
|---|---|---|
| Basic approach | Matches code patterns and supports some data flow analysis | Builds a database representing the code, then runs queries against it |
| Selecting checks | Rule files or existing rulesets | Individual queries or query suites |
| Custom checks | Usually straightforward YAML rules | Queries written in CodeQL’s query language |
| Main advantage for us | Easy starting point for explicit unsafe settings and credential patterns | Useful for tracing behavior through a larger project |
| Main limitation | Community Edition limits analysis across file boundaries | More preparation and a steeper learning curve |

### A practical example of Semgrep
Suppose the uploaded project contains device.py:
```python

import requests

def send_reading(reading):
    return requests.post(
        "https://api.example.com/readings",
        json={"reading": reading},
        verify=False,
    )

```

- The suspicious part here is verify=False: The connect uses HTTPS but explicitly disables server vertification. We could write this simple check in selected-rules.yaml:

```yaml
rules:
  - id: disabled-certificate-verification
    languages: [python]
    severity: WARNING
    message: Server certificate verification is disabled.
    pattern: requests.$METHOD(..., verify=False, ...)
```

Then we would run a command like:
```powershell
semgrep scan --config selected-rules.yaml --json --output findings.json submitted-project/
```

The parameters mean:
- --config: which rules to run.
submitted-project/: the extracted project to examine.
--json: return structured results.
--output: save those results to a file.

- The app would then read findings.json. 

---

### A practical example of CodeQL
- CodeQL first extracts a structured representation of the project. It records information about functions, expressions, calls, and data flow. Its queries the ask questions about that representation. Database creation may look something like:
```powershell
 codeql database create project-db --language=python --source-root=submitted-project --build-mode=none 
```
- Where project-db is the new analysis database, we select python as the language, source-root represents the project folder.

- Additionally, CodeQL already has default queries for some language, we can select those default queries from the Python query package. We would still need to develop our own custom queries for the specific things that we want to check though.

---

## Project scope and language support

### The Languages

The languages we plan to support depend on which parts of an IoT system we will scan. This scope applies whether we choose Semgrep or CodeQL. The final selection is pending our mentor's answer; we are not committing to support every language below in the first version.

| Part of the IoT system | Planned language priorities |
| --- | --- |
| Browser interface | JavaScript and TypeScript, with HTML and CSS as supporting project files |
| Backend services | Python, Java, and JavaScript/TypeScript for Node.js applications |
| Gateway or edge application | Python, Java, and C++ |
| Embedded device firmware | C and C++ first; Python variants where relevant |

The backend provides services such as accounts, storage, and APIs. A gateway collects, processes, or forwards messages between devices and other systems. Embedded firmware runs on the device itself. A project may contain several of these parts.

Java and Python are both relevant for backend and gateway software. C++ is relevant for gateways and can also be used in backends. For embedded firmware, C and C++ are our main priorities. Other languages exist, but we will keep the first version focused.

The question for our mentor is: **Are we primarily scanning device firmware, gateway software, backend services, browser interfaces, or a combination?** Once that is decided, we will choose the languages and specific frameworks or libraries needed for our evaluation projects.

A user can upload a mixed-language project in one ZIP. The app will run the appropriate checks for each supported language and combine the findings. We will distinguish files accepted as project context from files that receive security checks; accepting HTML and CSS does not mean providing the same coverage as JavaScript or backend code.

Each supported language needs suitable rules or queries and tested coverage for our chosen weaknesses. Support for a language in the scanner does not automatically mean our app covers every framework written in that language.