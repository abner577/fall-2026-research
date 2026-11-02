# Room Monitor

A room-temperature dashboard and fan controller built with Python, Flask,
Streamlit, and PostgreSQL. A simulated device sends temperature readings to the
API, receives fan commands, and reports its current state. No physical hardware
is required.

**Status:** Initial setup. Application modules and the database schema are still
being built; the run commands below apply once those files are available.

## Features

- User accounts and device registration.
- Temperature readings and reported fan status on a dashboard.
- Fan controls with device acknowledgment of completed commands.
- A repeatable temperature simulation with configurable timing and cooling.

The Streamlit dashboard and device simulator communicate with the Flask API.
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

Generate the local API certificate and key:

```powershell
New-Item -ItemType Directory -Path .local/tls -Force
openssl req -x509 -newkey rsa:3072 -sha256 -nodes -days 365 -keyout .local/tls/server.key -out .local/tls/server.crt -subj "/CN=localhost" -addext "subjectAltName=DNS:localhost,IP:127.0.0.1" -addext "basicConstraints=critical,CA:TRUE"
```

The default `.env.example` paths use this certificate for the API and both
clients. Keep `.env` and the private key local; both are excluded from Git.

## Run

Open separate PowerShell terminals in the project folder. Start the API:

```powershell
.\.venv\Scripts\python.exe -m backend.main
```

Start the dashboard:

```powershell
.\.venv\Scripts\python.exe -m streamlit run frontend/main.py --server.address=127.0.0.1 --server.port=8501
```

Open <http://127.0.0.1:8501>, create an account, and register a device. Copy its
issued identity and token into `DEVICE_ID` and `DEVICE_TOKEN` in `.env`, then
start the simulator:

```powershell
.\.venv\Scripts\python.exe -m firmware.main
```

The dashboard displays incoming temperatures and fan state. Use its controls to
request a fan change and wait for the device to report the result. Stop each
process with `Ctrl+C`.
