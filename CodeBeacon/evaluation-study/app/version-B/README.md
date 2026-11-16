# Room temperature monitoring and fan control

The API manages accounts, device enrollment, temperature readings, and fan
commands using Flask and PostgreSQL. The backend is implemented. The database
schema, dashboard, and device client are pending in their respective folders.

## Setup

Run commands from this folder. Python 3.14, PostgreSQL, and OpenSSL are required.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item -LiteralPath .env.example -Destination .env
```

Create `.env` once; preserve it if already configured. Set `APP_SECRET_KEY` to
a newly generated secret of at least 32 characters and `DB_PASSWORD` to the
password of your dedicated database role. Do not commit `.env` or private keys.
Create the separate `room_monitor_b` database with that role as owner. Backend
queries expect `"user"`, `devices`, `readings`, `requests`, and `login_attempts`.
Database initialization instructions will accompany `database/schema.sql`.

Generate a local API certificate:

```powershell
New-Item -ItemType Directory -Path .local/tls -Force
openssl req -x509 -newkey rsa:3072 -sha256 -nodes -days 365 -keyout .local/tls/server.key -out .local/tls/server.crt -subj "/CN=localhost" -addext "subjectAltName=DNS:localhost,IP:127.0.0.1" -addext "basicConstraints=critical,CA:TRUE"
```

After the database schema is initialized, start the backend:

```powershell
.\.venv\Scripts\python.exe -m backend.main
```

One process starts HTTPS on `127.0.0.1:8444` and command-poll HTTP on
`127.0.0.1:8081`. Both ports are configurable and must differ. All API operations
use HTTPS except `GET /api/devices/<device_id>/commands/pending`, which also
accepts HTTP. Command polling requires the device bearer token on either
listener. Other HTTP requests are rejected without redirecting. Stop both
listeners with `Ctrl+C`. These listeners are for local development.

The API provides account registration, login, account details, password changes,
device enrollment/list/details, reading submission/history, and command
submission/history/polling/acknowledgment. Registration and password changes
require passwords of 15 to 128 characters. Login returns an expiring account
bearer token. Enrollment returns a device ID and a device token; retain both
for device configuration because the token is not retrievable afterward.
Commands stay pending until acknowledged, and reading retries retain their IDs.

An existing device credential can be assigned to an account through:

```powershell
.\.venv\Scripts\python.exe -m flask --app backend.main:create_app provision-device --username YOUR_USERNAME --device-id YOUR_DEVICE_ID --name "Room monitor"
```

The command prompts for the token without displaying it. Database connections
require TLS; use `DB_SSLMODE=verify-full` with trusted CA configuration for a
remote database. Full application startup remains dependent on the remaining
components and database setup.
