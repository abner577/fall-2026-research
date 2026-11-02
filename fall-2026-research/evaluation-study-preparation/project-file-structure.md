# Project file structure reference

Accepted November 2, 2026. This Markdown file is the sole file-structure reference for future chats. It describes the application itself, not the surrounding research repository. The Word export is a personal copy managed by the student outside the repository; do not require, locate, read, or synchronize it when planning or generating code.

## Instructions for future chats

Before planning file locations or generating application code:

1. Read this Markdown file for the agreed paths, filenames, and file responsibilities. No Word reference is required.
2. Read [code-case-design.md](code-case-design.md) for realistic device behavior, weakness examples, version design, and the required vulnerability record. Read [code-test-case-notes.md](code-test-case-notes.md) for planning context and [selected-vulnerabilities.md](../app-idea/selected-vulnerabilities.md) for the ten accepted weakness types.
3. Use only `version-a/` and `version-b/`, with identical internal file and folder structures. The student explicitly rejected a separate baseline folder. Earlier proposals using `case-a/`, `case-b/`, or a baseline folder are superseded. Discussion of protected behavior does not authorize creating a third version.
4. Use the same file responsibilities in both versions. Differences should represent the agreed weakness presences and absences while retaining the same application features. Exact placements and counts remain to be finalized.
5. When implementation exists, compare each version's actual files with this Markdown reference before adding or moving files. If an implementation detail requires a structure change, explain the reason and update this file and affected design notes together.
6. Keep the vulnerability record tied to the exact saved code version, file paths, functions, and line ranges. Update locations when edits move code, preserving the earlier version's evidence. Keep that record outside detector input packages.

The structure is a design reference, not evidence that application files already exist. Reading these references does not itself authorize code generation. The student manages where these application folders sit within the surrounding repository.

## Structure for each version

Replace `version-a/` with `version-b/` for the second version. Everything inside has the same name and purpose.

```text
version-a/
├── README.md                  # Setup and run instructions
├── requirements.txt           # Python dependencies
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
