# Room temperature monitoring and fan control

The API manages accounts, device enrollment, temperature readings, and fan
commands using Flask and PostgreSQL. The backend, device client, and Streamlit
dashboard are implemented. The database schema remains pending in `database/`.

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

## Run the device client

After enrolling a device, set `DEVICE_ID` and `DEVICE_TOKEN` in `.env` to the
issued pair. Both are required; there is no bundled credential. Use
`API_BASE_URL=https://localhost:8444` for reading submission and command
acknowledgment, `DEVICE_COMMAND_POLL_BASE_URL=http://127.0.0.1:8081` for command
polling, and `API_CA_BUNDLE=.local/tls/server.crt` for the trusted certificate.
Keep these addresses aligned with backend ports. Origin addresses cannot include
credentials, paths, query strings, or fragments.

```powershell
.\.venv\Scripts\python.exe -m firmware.main --check-config
.\.venv\Scripts\python.exe -m firmware.main
```

The configuration check validates settings and the certificate file's existence;
it does not contact the API, parse the certificate, or verify device enrollment.
The running client sends readings every five seconds and polls commands every
two seconds by default. It applies the requested fan state before acknowledging
the command. Reading failures preserve the same reading identity and contents;
failed acknowledgments preserve the command identity and pause further polling
until acknowledgment succeeds. Transient errors defer the affected operation
for `DEVICE_RECONNECT_DELAY_SECONDS`, default five seconds. Requests run
sequentially with bounded connect/read timeouts, so a slow operation can delay
the next one. Pending work is held in memory and is lost when the process stops.

HTTPS certificate failures and permanent API rejections stop the client with
exit code 1. Invalid local settings use exit code 2. Logs go to the terminal and
`FIRMWARE_LOG_FILE`, with three rotated backups of up to 1 MB each. Failure logs
contain operation/status details. `Ctrl+C` stops the client and turns the fan
off locally; it does not submit a final reading or command acknowledgment.

An existing device credential can be assigned to an account through:

```powershell
.\.venv\Scripts\python.exe -m flask --app backend.main:create_app provision-device --username YOUR_USERNAME --device-id YOUR_DEVICE_ID --name "Room monitor"
```

The command prompts for the token without displaying it. Database connections
require TLS; use `DB_SSLMODE=verify-full` with trusted CA configuration for a
remote database. Full application startup remains dependent on the database
schema and database setup.

## Run the dashboard

After the database is initialized and the backend is running, open a separate
terminal in this folder:

```powershell
.\.venv\Scripts\python.exe -m streamlit run frontend/main.py --server.address 127.0.0.1 --server.port 8502 --server.headless true --browser.gatherUsageStats false
```

Open `http://127.0.0.1:8502`. Create an account, sign in, and register a device.
Save its issued ID and token before dismissing the credentials panel, then use
them to configure the device client. Select a device to view its latest reading,
temperature history, reported fan state, and command acknowledgments. Fan
requests remain pending until the device acknowledges them; the reported fan
state updates with subsequent readings. The dashboard refreshes device data
every five seconds and includes a manual refresh button. Times are shown in UTC;
readings received more than 30 seconds ago are marked stale.

Account settings allows password changes and keeps the replacement account
token for the current session. Sign out clears the dashboard session and any
undismissed device credentials. Expired or rejected account sessions return to
sign-in. Closing or reloading the browser tab can discard the Streamlit session.

The dashboard uses `API_BASE_URL=https://localhost:8444` and verifies the API
certificate with `API_CA_BUNDLE`; it does not use the device polling address.
It loads `.env` from this project folder, with process environment overrides.
The browser connects to Streamlit locally while Streamlit contacts Flask over
HTTPS. Keep the dashboard bound to loopback for this local setup.
