# Room Monitor

A room-temperature dashboard and fan controller built with Python, Flask,
Streamlit, and PostgreSQL. The device client sends temperature readings to the
API, receives fan commands, and reports its current state.

**Status:** The device client, Flask backend, and Streamlit dashboard are implemented.
The database schema is pending. Database initialization and device
enrollment are required before the client can exchange data with the API.

## Features

- User accounts and device registration.
- Temperature readings and reported fan status on a dashboard.
- Fan controls with device acknowledgment of completed commands.
- Configurable reading and command-polling intervals.

The Streamlit dashboard and device client communicate with the Flask API.
The backend stores accounts, devices, readings, and commands in PostgreSQL.

## Requirements

- Python 3.14
- PostgreSQL, including the `psql`, `createuser`, and `createdb` commands
- OpenSSL for a local HTTPS certificate

## Setup

Run these commands from the project folder in PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

If `.env` does not already exist, copy `.env.example` to `.env`. Set
`APP_SECRET_KEY` to a newly generated secret:

```powershell
.\.venv\Scripts\python.exe -c "import secrets; print(secrets.token_urlsafe(48))"
```

The backend, firmware, and dashboard read only this project's `.env`, with process environment variables
taking precedence. Relative paths resolve against this project folder regardless
of the terminal's current directory. Keep `.env` local. The firmware does not need
the backend signing secret or database password.

Create the local database and its application user. These commands assume your
PostgreSQL administrator is named `postgres`:

```powershell
createuser --host=127.0.0.1 --username=postgres --pwprompt room_monitor_app
createdb --host=127.0.0.1 --username=postgres --owner=room_monitor_app room_monitor_a
```

Put the chosen application user's password in `DB_PASSWORD` in `.env`. The
remaining database settings are listed in `.env.example`. Once the schema file
is available, create the tables:

```powershell
psql --host=127.0.0.1 --username=room_monitor_app --dbname=room_monitor_a --password --set=ON_ERROR_STOP=1 --file=database/schema.sql
```

`DB_SSLMODE=require` requires PostgreSQL TLS without a cleartext fallback. For a
remote database, configure a trusted CA and hostname validation with `verify-full`.

Generate the local API certificate and key:

```powershell
New-Item -ItemType Directory -Path .local/tls -Force
openssl req -x509 -newkey rsa:3072 -sha256 -nodes -days 365 -keyout .local/tls/server.key -out .local/tls/server.crt -subj "/CN=localhost" -addext "subjectAltName=DNS:localhost,IP:127.0.0.1" -addext "basicConstraints=critical,CA:TRUE"
```

The default `.env.example` paths use this certificate for the API and both
clients. Keep `.env` and the private key local; both are excluded from Git.

## Run the device

The bundled profile uses `DEVICE_ID=room-monitor-01`; the API must provision that
device before use. For another enrolled device, set both `DEVICE_ID` and
`DEVICE_TOKEN` from its enrollment response. Do not pair an issued token with a
different device identity.

Validate settings, then run the device client from this project folder:

```powershell
.\.venv\Scripts\python.exe -m firmware.main --check-config
.\.venv\Scripts\python.exe -m firmware.main
```

The configuration check does not contact the API or validate enrollment. Logs go
to the terminal and `.local/logs/firmware.log`, with three rotated backups of up
to 1 MB each. `FIRMWARE_LOG_FILE` and `LOG_LEVEL` control logging.

Readings are submitted every five seconds and commands polled every two seconds
by default. Connection failures, timeouts, and transient server responses defer
the affected operation for `DEVICE_RECONNECT_DELAY_SECONDS`. A single pending
reading retains its ID, timestamp, temperature, and fan state until accepted.
Command acknowledgments retain their command ID across retries, and polling
pauses until acknowledgment succeeds. Pending work is held in memory and is lost
when the process stops. The API must deduplicate reading IDs and accept repeated
acknowledgments. Permanent API rejections stop the device with exit code 1;
configuration errors use exit code 2.

Reading and polling schedules are independent, but requests run sequentially
with bounded connect/read timeouts. A slow request can delay the next operation.

Press `Ctrl+C` to stop. The fan state returns to off locally; shutdown does
not submit a final reading to the API.

## Run the API

After the database schema is available and initialized, start the HTTPS API:

```powershell
.\.venv\Scripts\python.exe -m backend.main
```

The API provides account registration and login under `/api/accounts`, device
enrollment under `/api/devices`, and device-specific reading and command routes.
Registration accepts a username and a password of 15 to 128 characters. Login
returns an expiring bearer token for account requests. Device enrollment returns
a device ID and a separate device token; save the token when it is issued.

To assign an existing device credential to a registered account, run:

```powershell
.\.venv\Scripts\python.exe -m flask --app backend.main:create_app provision-device --username YOUR_USERNAME --device-id room-monitor-01 --name "Room monitor"
```

Enter the device's existing token at the hidden prompt. The command requires an
existing account and does not replace an already registered device.

## Run the full application after database initialization

Open separate PowerShell terminals in the project folder. Start the API:

```powershell
.\.venv\Scripts\python.exe -m backend.main
```

Start the dashboard:

```powershell
.\.venv\Scripts\python.exe -m streamlit run frontend/main.py --server.address=127.0.0.1 --server.port=8501
```

Open <http://127.0.0.1:8501>, create an account, and register a device. The browser
connection is restricted to this machine's loopback interface; the dashboard's
server-side API calls use HTTPS. Configure the enrolled device as described above
and start its device client:

```powershell
.\.venv\Scripts\python.exe -m firmware.main
```

Save the device ID and token from the registration panel before dismissing it;
the token cannot be retrieved later. The dashboard keeps the issued credential
in the current session until dismissed or signed out.

The dashboard refreshes readings and command history every five seconds while
open. It displays the latest temperature, reported fan state, and up to 100
recent readings and commands. Readings become stale after 30 seconds without an
update. Use the fan controls to queue a request; acknowledgment and the fan state
reported in a reading are displayed separately. Times are shown in UTC.

Account settings let you change your password using your current password.
Expired or revoked sessions require signing in again. Signing out clears the
dashboard session. Stop each process with `Ctrl+C`.
