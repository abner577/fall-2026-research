# Code test case planning notes

October 29, 2026 — Section 3 of the November 1 checklist is in progress.

We are deciding what the application should do and which tools to use before writing code. The first version will be a starting point that we test and improve.

## General direction

- Write the application in Python, using Streamlit for the UI, Flask for the backend APIs, and PostgreSQL for the database.
- The UI will call the Flask APIs, and the backend will handle database access.
- Psycopg 3 (`psycopg`) is the proposed library for connecting Python to PostgreSQL. Confirm that choice before adding it as a dependency.
- Build one connected application with a clear purpose, shared data, and features that work together. It should be substantial but manageable to understand, run, and review. We have not set a file or line count.

## Reference project

Use the professor's [IoT Security Lab app folder](https://github.com/rehmanGilalFIU/CNT4182_IoT_Security_Lab/tree/main/app) as a reference for size, complexity, and connected features. Its Flask app connects features such as authentication, device management, telemetry, and reports. We do not need to copy its code or folder structure.

The repository's folders and individual files are accessible through the GitHub link.

## What we still need to decide

Choose the website's purpose and features next. The current research plan calls for an IoT application, so we should keep that connection unless we decide to change the scope. Once the purpose is clear, decide the database tables, file structure, specific vulnerabilities, where they belong, and how many cases and versions we need. We need to keep in mind that it should be a IoT application not just a generic website so we actually need to think this over instead of just defaulting to this.

For Semgrep CE, CodeQL, and Snyk Code, check which rules cover our chosen frameworks, database library, and vulnerabilities. Python support alone does not mean a scanner can detect everything we want to test.
