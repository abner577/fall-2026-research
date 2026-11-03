# Project file structure reference

Accepted November 2, 2026. This Markdown file is the sole file-structure reference for future chats. It describes the application itself, not the surrounding research repository. The Word export is a personal copy managed by the student outside the repository; do not require, locate, read, or synchronize it when planning or generating code.

Implementation update, November 2: the student explicitly chose
`CodeBeacon/evaluation-study/app/version-A/` for the first version. Use the exact
capitalized suffixes `version-A/` and `version-B/` going forward; lowercase names
in older notes describe the earlier naming decision. The first implementation step adds
only `README.md`, `requirements.txt`, `.env`, and `.env.example`. The local `.env`
is ignored by Git. Runtime `.venv/` and `.local/` folders are also ignored and
are not application source. The remaining source files are still planned.

Firmware update, November 2: all five `firmware/` files below are implemented in
Version A. Firmware explanations are in
[firmware-version-a.md](explaining-code-files/firmware-version-a.md); the earlier
firmware implementation-record link pointed to a file absent from this checkout.

Backend update, November 2: all ten `backend/` modules below are now implemented
without changing this structure. The schema remains pending.
See the [backend implementation record](version-a-backend-implementation.md) for
the current API/schema contracts, source locations and hashes, focused checks,
and verification limits. Verification files live outside the version package at
`CodeBeacon/evaluation-study/verification/version-a/`.

Frontend update, November 2: all four `frontend/` modules below are implemented
with the agreed responsibilities and filenames. See
[frontend-version-a.md](explaining-code-files/frontend-version-a.md) for the API
client, account flows, dashboard behavior, source hashes, and focused checks.
No Version B files or database schema were created in this step.

Database update, November 2: `version-A/database/schema.sql` now creates the five
accepted tables: `"user"`, `devices`, `readings`, `requests`, and `login_attempts`.
The backend queries use the accepted table names. See the
[database implementation record](database-version-a-implementation.md) for the
schema decisions, current source hashes, PostgreSQL checks, and remaining limits.
This supersedes the schema-pending status above. No Version B was created.

README responsibilities: `CodeBeacon/evaluation-study/app/README.md` explains
the enclosing study application folder, controlled versions, implementation
status, and detailed shared development setup. Each version's `README.md` is a
concise, standalone project guide covering purpose, prerequisites, setup, and
usage. Keep study-specific planning and detector procedures out of those
version-level project guides.

## Instructions for future chats

Before planning file locations or generating application code:

1. Read this Markdown file for the agreed paths, filenames, and file responsibilities. No Word reference is required.
2. Read [code-case-design.md](code-case-design.md) for realistic device behavior, weakness examples, version design, and the required vulnerability record. Read [code-test-case-notes.md](code-test-case-notes.md) for planning context and [selected-vulnerabilities.md](../app-idea/selected-vulnerabilities.md) for the ten accepted weakness types. Read [Version A planning](version-a-planning.md) and [Version B planning](version-b-planning.md) for the selected subsets, intended operations, protected comparisons, and remaining detailed design work.
3. Use only `version-A/` and `version-B/`, with identical internal file and folder structures. The student explicitly rejected a separate baseline folder. Earlier proposals using `case-a/`, `case-b/`, lowercase version names, or a baseline folder are superseded. Discussion of protected behavior does not authorize creating a third version.
4. Use the same file responsibilities in both versions. Differences should represent the agreed weakness presences and absences while retaining the same application features. Version A selects eight weakness types and Version B selects three, each with one intended insertion site per type. Exact endpoint/function placements and verified instance counts remain to be finalized.
5. When implementation exists, compare each version's actual files with this Markdown reference before adding or moving files. If an implementation detail requires a structure change, explain the reason and update this file and affected design notes together.
6. Keep the vulnerability record tied to the exact saved code version, file paths, functions, and line ranges. Update locations when edits move code, preserving the earlier version's evidence. Keep that record outside detector input packages.
7. When the student mentions the constants Excel workbook, read [its requirements and progress](application-constants-progress.md). The actual `.xlsx` is maintained outside this repository in a personal folder; the path is unspecified. Use the Markdown record to understand its V1–V10 overview, deferred version tabs, and explanation requirements. Do not require the external file for planning or assume a generated repository export is the maintained copy.

The structure is a design reference, not evidence that application files already exist. Reading these references does not itself authorize code generation. The student manages where these application folders sit within the surrounding repository.

## Structure for each version

Replace `version-A/` with `version-B/` for the second version. Everything inside has the same name and purpose.

```text
version-A/
├── README.md                  # Project overview, setup, and usage
├── requirements.txt           # Python dependencies
├── .env                       # Local settings; ignored by Git
├── .env.example               # Settings with placeholder values
│
├── firmware/
│   ├── main.py                # Runs the simulated device
│   ├── settings.py            # Device settings
│   ├── temperature_sensor.py  # Gets simulated temperature readings
│   ├── fan.py                 # Changes and reports fan state
│   └── api_client.py          # Communicates with Flask
│
├── backend/
│   ├── main.py                # Starts Flask
│   ├── settings.py            # Backend settings
│   ├── database.py            # Connects to PostgreSQL
│   ├── security.py            # Shared security checks
│   ├── routes/
│   │   ├── accounts.py        # Registration, login, password changes
│   │   ├── devices.py         # Device registration and information
│   │   ├── readings.py        # Receiving and viewing readings
│   │   └── commands.py        # Sending and confirming fan commands
│   └── services/
│       ├── accounts.py        # Account handling and password storage
│       └── devices.py         # Device data and command handling
│
├── frontend/
│   ├── main.py                # Starts Streamlit
│   ├── api_client.py          # Communicates with Flask
│   └── views/
│       ├── account.py         # Login and account settings
│       └── dashboard.py       # Readings, device status, fan controls
│
└── database/
    └── schema.sql             # Creates the PostgreSQL tables
```
