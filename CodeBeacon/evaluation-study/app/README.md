# IoT study application

This folder holds the controlled versions of the room temperature monitoring
and fan-control application used in the CodeBeacon evaluation study.

- [version-A/](version-A/) contains the first application's source and its
  [project README](version-A/README.md).
- `version-B/` is planned to preserve the same features and internal structure
  with a different set of selected weakness presences and absences. It has not
  been created yet.

This README contains the shared architecture, implementation status, and detailed
development setup. Each version's README is the user-facing project guide.
Design decisions and the vulnerability record are maintained separately in
[evaluation-study-preparation](../../../fall-2026-research/evaluation-study-preparation/)
and must remain outside detector inputs.

All setup and run commands below assume the working directory is `version-A/`.
From this `app/` folder, enter it first:

```powershell
Set-Location version-A
```

## Application overview

This Python application connects a simulated room device to a Flask API,
PostgreSQL storage, and a Streamlit dashboard. Temperature measurements and fan
behavior are simulated; network requests, account handling, storage, and command
delivery will run as ordinary application operations.

## Current implementation status

Version A's root files, five firmware modules, and ten backend modules exist.
The dashboard and database schema remain pending. Six focused backend checks
pass using database doubles; PostgreSQL integration, default-device provisioning,
and independent review remain pending. The current API and database contracts,
source locations, and verification limits are maintained in the
[backend implementation record](../../../fall-2026-research/evaluation-study-preparation/version-a-backend-implementation.md).
The earlier firmware-record link pointed to a missing file; existing firmware
explanations are in
[firmware-version-a.md](../../../fall-2026-research/evaluation-study-preparation/explaining-code-files/firmware-version-a.md).

## Application workflow

1. A user creates an account and registers a room device through the dashboard.
2. Device enrollment returns a device identity and access token for the simulator.
3. The simulator acquires a Celsius reading through its sensor interface and
   sends the reading and current fan state to Flask.
4. Flask processes the request and stores the data in PostgreSQL.
5. Streamlit obtains readings and device status through the API.
6. A user requests a fan change. Flask stores a pending command for the device.
7. The device polls for commands, updates its fan through the actuator interface,
   and acknowledges the result. The dashboard displays the reported state.

The dashboard and simulator communicate with Flask independently. Only Flask
accesses PostgreSQL. The simulator starts with its fan off; sensor randomness
uses a fixed seed for repeatable experiments with the same command sequence and
simulation steps. Network timing is not guaranteed to be deterministic.

## Planned source layout

The four root files, `firmware/`, and `backend/` files exist. Other entries show the agreed layout.

```text
version-A/
|-- README.md
|-- requirements.txt
|-- .env                     # Local settings, ignored by Git
|-- .env.example             # Shareable settings template
|-- firmware/
|   |-- main.py
|   |-- settings.py
|   |-- temperature_sensor.py
|   |-- fan.py
|   `-- api_client.py
|-- backend/
|   |-- main.py
|   |-- settings.py
|   |-- database.py
|   |-- security.py
|   |-- routes/
|   |   |-- accounts.py
|   |   |-- devices.py
|   |   |-- readings.py
|   |   `-- commands.py
|   `-- services/
|       |-- accounts.py
|       `-- devices.py
|-- frontend/
|   |-- main.py
|   |-- api_client.py
|   `-- views/
|       |-- account.py
|       `-- dashboard.py
`-- database/
    `-- schema.sql
```

## Prerequisites and dependencies

- Python 3.14 is the initial development target, matching the current workstation.
- A locally running PostgreSQL server with `psql`, `createuser`, and `createdb`
  available on the command path. Record the actual server version when provisioned.
- OpenSSL on the command path for the local HTTPS certificate setup below.
- Separate terminals for Flask, Streamlit, and the device simulator.

The [requirements file](version-A/requirements.txt) pins direct dependencies: Flask for the
API, Werkzeug for password hashing, ItsDangerous for expiring signed account
tokens, Psycopg 3 for PostgreSQL, Streamlit for the dashboard, Requests for API
clients, and python-dotenv for configuration. PostgreSQL and OpenSSL are separate
system prerequisites. Package installation and application integration have not
yet been verified on this workstation.

Package release references: [Flask](https://pypi.org/project/Flask/3.1.3/),
[Werkzeug](https://pypi.org/project/Werkzeug/3.1.9/),
[ItsDangerous](https://pypi.org/project/itsdangerous/2.2.0/),
[Psycopg](https://pypi.org/project/psycopg/3.3.6/),
[Streamlit](https://pypi.org/project/streamlit/1.66.1/),
[Requests](https://pypi.org/project/requests/2.34.2/), and
[python-dotenv](https://pypi.org/project/python-dotenv/1.2.4/).

## Prepare the Python environment

Run these PowerShell commands from this `version-A` folder:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip check
```

Using the virtual environment's executable avoids requiring shell activation.
This environment is separate from the evaluation study's detector environment.
Before scored evaluation, record the complete installed dependency set alongside
the run evidence; these direct pins alone do not freeze transitive packages.

## Configure local settings

A local `.env` is included in this working folder, with required credentials left
blank. On a new checkout, create it once from the template:

```powershell
Copy-Item -LiteralPath .env.example -Destination .env
```

Do not overwrite a configured `.env`. Generate a new application signing secret
with the command below and paste its output into `APP_SECRET_KEY` in `.env`:

```powershell
.\.venv\Scripts\python.exe -c "import secrets; print(secrets.token_urlsafe(48))"
```

The settings modules must load this version's `.env` by its explicit path, resolve
relative file paths against this folder, and let existing process environment
variables take precedence. They must not search upward into the evaluation
study's `.env`. The backend rejects a missing signing secret or database
password. The simulator uses the bundled `room-monitor-01`
profile when its token is blank; other device identities require an externally
supplied enrollment token. Backend and firmware settings validation are implemented.

| Settings | Meaning |
| --- | --- |
| `BACKEND_HOST`, `BACKEND_PORT`, `BACKEND_DEBUG` | Flask listens on loopback port 8443 with debug disabled. |
| `BACKEND_TLS_CERT_FILE`, `BACKEND_TLS_KEY_FILE` | Local HTTPS certificate and private key paths. |
| `APP_SECRET_KEY`, `ACCOUNT_TOKEN_TTL_SECONDS` | Account token signing secret and lifetime in seconds. Tokens contain identifiers, not passwords or device secrets. |
| `LOG_LEVEL` | Application logging verbosity, initially `INFO`. |
| `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD` | Dedicated local PostgreSQL connection settings. |
| `DB_SSLMODE`, `DB_CONNECT_TIMEOUT_SECONDS` | PostgreSQL TLS mode and connection timeout. Default `require` prevents cleartext fallback; remote deployment needs `verify-full` with a trusted CA. |
| `API_BASE_URL`, `API_CA_BUNDLE` | Flask HTTPS address and certificate trusted by both Python clients. |
| `API_CONNECT_TIMEOUT_SECONDS`, `API_READ_TIMEOUT_SECONDS` | Connection and response timeouts for API requests. |
| `DEVICE_ID`, `DEVICE_TOKEN` | Bundled `room-monitor-01` profile, or both values issued by another device's enrollment. The backend must provision the bundled profile before it can authenticate. |
| `DEVICE_READING_INTERVAL_SECONDS` | Interval between submitted readings. |
| `DEVICE_COMMAND_POLL_INTERVAL_SECONDS` | Interval between command checks, independently of readings. |
| `DEVICE_RECONNECT_DELAY_SECONDS` | Delay after communication failure. Retrying command acknowledgments must preserve the command identity. |
| `FIRMWARE_LOG_FILE` | Rotating firmware log, normally `.local/logs/firmware.log`. |
| `SENSOR_SEED` | Repeatable sensor noise seed; unrelated to secret generation. |
| `SENSOR_START_TEMPERATURE_C`, `SENSOR_AMBIENT_TEMPERATURE_C` | Initial reading and ambient target, in Celsius. |
| `SENSOR_FAN_COOLING_C_PER_SECOND`, `SENSOR_NOISE_STDDEV_C` | Cooling rate while the fan runs and sensor noise standard deviation. |
| `SENSOR_THERMAL_TIME_CONSTANT_SECONDS` | First-order room model time constant, initially 300 seconds. |

## Prepare PostgreSQL

These commands create a dedicated role and database, using an existing local
PostgreSQL administrator called `postgres`. Adjust that administrator name if
your installation differs. Run each command once:

```powershell
createuser --host=127.0.0.1 --port=5432 --username=postgres --pwprompt room_monitor_app
createdb --host=127.0.0.1 --port=5432 --username=postgres --owner=room_monitor_app room_monitor_a
```

The password chosen for `room_monitor_app` goes into `DB_PASSWORD` in `.env`.
The application role should have no superuser or role-creation privileges.
Use loopback password authentication for PostgreSQL. No database has been created
as part of this root-file setup.

After `database/schema.sql` is implemented, initialize the tables as their owner:

```powershell
psql --host=127.0.0.1 --port=5432 --username=room_monitor_app --dbname=room_monitor_a --password --set=ON_ERROR_STOP=1 --file=database/schema.sql
```

The schema is planned to hold accounts, device ownership and credentials,
temperature readings with reported fan state, pending commands and their
acknowledgments, and persisted authentication-attempt data. Exact tables and
columns will be defined when the schema is written.

## Prepare local HTTPS

After OpenSSL is available, create a self-signed localhost certificate. The
private key and certificate are local runtime files; do not commit them.

```powershell
New-Item -ItemType Directory -Path .local/tls -Force
openssl req -x509 -newkey rsa:3072 -sha256 -nodes -days 365 -keyout .local/tls/server.key -out .local/tls/server.crt -subj "/CN=localhost" -addext "subjectAltName=DNS:localhost,IP:127.0.0.1" -addext "basicConstraints=critical,CA:TRUE"
```

The Flask settings point to this certificate/key pair. Both Python clients trust
the certificate through `API_CA_BUNDLE`. Keep those paths aligned when replacing
the certificate. Restrict access to the private key to your local account. The
Flask development server and this certificate setup are for local operation.

## Start the application after the source files exist

The following commands are the intended entry points. **They cannot run until
the corresponding modules and schema are implemented.** In each terminal, start
from this `version-A` folder.

Start Flask first:

```powershell
.\.venv\Scripts\python.exe -m backend.main
```

Start the dashboard in a second terminal:

```powershell
.\.venv\Scripts\python.exe -m streamlit run frontend/main.py --server.address=127.0.0.1 --server.port=8501
```

Open `http://127.0.0.1:8501`, create an account, and enroll a device. This browser
connection stays on loopback; Streamlit's server-side API requests use HTTPS.
Copy the issued identity and token into `.env`, then start the simulator in a
third terminal:

```powershell
.\.venv\Scripts\python.exe -m firmware.main
```

Confirm that readings appear, request a fan change, and wait for the device's
acknowledgment before treating the command as applied. Stop each process with
`Ctrl+C`. End-to-end verification remains pending implementation.

## Local files and study inputs

The parent `evaluation-study/.gitignore` already excludes `.env`, `.venv`, and
Python caches while allowing `.env.example`. Locally generated TLS files belong
under `.local/`; an ignore rule for that directory is maintained in the parent
file. Do not add detector-provider keys, personal passwords, or shared-service
credentials to this application.

Supply source and the placeholder template when preparing detector inputs.
Exclude local `.env`, virtual environments, TLS keys, database contents, runtime
outputs, and external research records. Vulnerability placement notes and the
answer key are maintained outside this application folder. Root setup alone
does not establish a runnable or independently verified evaluation case.
