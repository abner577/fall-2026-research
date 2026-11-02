# Code test case planning notes

October 29, 2026 — Section 3 of the November 1 checklist is in progress.

We are deciding what the application should do and which tools to use before writing code. The first version will be a starting point that we test and improve.

## General direction

Before coming up with code, consult the [Markdown file-structure reference](project-file-structure.md) and the [current design decisions](code-case-design.md). The Markdown file is the sole structure reference; no Word document is required. The agreed application versions are `version-A/` and `version-B/`, with the same internal structure and no separate baseline folder. The student placed the first version at `CodeBeacon/evaluation-study/app/version-A/`. Follow the Markdown reference's instructions for checking existing files and updating the structure when it changes.

- Write the application in Python, using Streamlit for the UI, Flask for the backend APIs, and PostgreSQL for the database.
- The UI will call the Flask APIs, and the backend will handle database access.
- Psycopg 3 (`psycopg`) was initially proposed for PostgreSQL. In the November 2 root-file implementation, it is selected with the `binary` extra for local Windows development. Installation and integration remain to be verified.
- Build one connected application with a clear purpose, shared data, and features that work together. It should be substantial but manageable to understand, run, and review. We have not set a file or line count.

## Reference project

Use the professor's [IoT Security Lab app folder](https://github.com/rehmanGilalFIU/CNT4182_IoT_Security_Lab/tree/main/app) as a reference for size, complexity, and connected features. Its Flask app connects features such as authentication, device management, telemetry, and reports. We do not need to copy its code or folder structure.

The repository's folders and individual files are accessible through the GitHub link.

## November 2 update: accepted direction and realism requirements

The student accepted the room temperature monitoring and fan-control direction below, using simulated devices with the existing Python, Streamlit, Flask, and PostgreSQL stack. The [working design record](code-case-design.md) documents the decision and requirements for localized, realistic vulnerabilities and normal sensor/actuator interfaces. It is the current implementation guidance; the earlier open-purpose notes below describe the October 29 planning state.

The next step is to document exact weaknesses and intended placements before generating application code. No code was generated in this documentation step. Readings will be simulated, rather than measured from a physical room sensor.

## What we still need to decide (October 29 planning state)

Choose the website's purpose and features next. The current research plan calls for an IoT application, so we should keep that connection unless we decide to change the scope. Once the purpose is clear, decide the database tables, file structure, specific vulnerabilities, where they belong, and how many cases and versions we need. We need to keep in mind that it should be a IoT application not just a generic website so we actually need to think this over instead of just defaulting to this.

For Semgrep CE, CodeQL, and Snyk Code, check which rules cover our chosen frameworks, database library, and vulnerabilities. Python support alone does not mean a scanner can detect everything we want to test.

---

## How do IoT applications split up code
| Part | Where its code runs | What it does |
|---|---|---|
| Device software, often called firmware | A processor inside the physical device | Reads sensors, controls actuators, and exchanges network messages |
| Backend/API | A local server or cloud server | Authenticates devices and users, processes readings, and handles commands |
| Database | A database server | Stores accounts, devices, readings, and command history |
| Frontend | A phone, browser, or application server, depending on the framework | Shows readings and lets users control devices |

- Firmware is software stored in devide memory and excuted by its processor. So we can really think of it has having 4 big parts:
1. The Firmware so the code in the devide
2. An API that the firmare exchanges messages wit
3. A Database that the API queries that stores information most likely for the frontend app
4. Frontend - Most of the time like a mobile app that gives u information based off ur device like say the Ring camera app right.

## Recommendation:
- A small room temperature monitoring and fan-control system.
Proposed structure:

Python device simulator (Temprature sensor, gives actual readings) <-> Flask API <-> Postgres
Flask APi <-> Streamlit Frontend

Here is how one complete interaction would look like:
1. A python program would represent the device (and the information the device would send). So it would generate a sample temperature and sends that reading to Flask through a network request.
2. Flask authenticates the device, and stores it in Postgres
3. Streamlit requests the readings from Flask and displays them.
4. A user requests "turn on the fan". Flask checks the users permission and records a pending command
5. Simulated device communicates w/ Flask for commands, and changes its simulated fan state.
6. Dashboard displays the reported fan state. 
