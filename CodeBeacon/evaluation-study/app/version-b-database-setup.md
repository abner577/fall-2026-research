# Connect Version B to PostgreSQL through pgAdmin

Use the same PostgreSQL server, existing login, and password you used for
Version A. Create only a separate database named `room_monitor_b`. Do not
create a new login/role, change an existing password, or transfer ownership.
The same existing PostgreSQL login can own both databases while their tables
and records remain separate.

The schema in `version-B/database/schema.sql` is identical to A's. Apply it to
an empty B database. No real database or local `.env` is changed by this guide.

## 1. Open your existing PostgreSQL connection

1. Open pgAdmin, expand **Servers**, and connect to the server you used for A.
2. Use the existing PostgreSQL login and password. If A uses `postgres`, keep
   using `postgres`; do not assume that username if you used something else.
3. Note the server host and port under **Properties > Connection**; commonly
   these are `127.0.0.1` and `5432`.
4. Keep this same connection for database creation and loading the schema.

The PostgreSQL password is the same one used for A's database connection,
not pgAdmin's master password or the dashboard account password. You do not
need to generate or retrieve a new password.

## 2. Create only B's database

1. Right-click **Databases** under that server and choose **Create > Database**.
2. Set **Database** to `room_monitor_b`.
3. Leave **Owner** as the existing login shown by pgAdmin, normally `postgres`.
   Every database has an owner; leaving this field uses an existing role and
   does not create a new owner account. Do not create a role or change the
   ownership of A's database.
4. Keep UTF8 encoding and the normal default template (`template1`); do not
   select A's database as a template.
5. Click **Save**, then refresh **Databases** if necessary.

If `room_monitor_b` already exists, inspect its tables before continuing rather
than deleting or recreating it.

## 3. Check PostgreSQL TLS support

The backend currently requires database TLS. A pgAdmin connection that succeeds
with its default SSL mode does not establish that TLS is enabled.

1. Right-click `room_monitor_b` and open **Query Tool** using your existing
   connection.
2. Run:

   ```sql
   SHOW ssl;
   ```

3. If it returns `on`, proceed to the next step. B will use `DB_SSLMODE=require`.
4. If it returns `off`, enable TLS on the PostgreSQL server before continuing.
   Do not change the app setting to `disable`; the backend rejects that setting.

For a local Windows PostgreSQL installation, the following is the setup path if
you do not already have a PostgreSQL server certificate:

1. As the administrator, locate the actual PostgreSQL files:

   ```sql
   SHOW data_directory;
   SHOW config_file;
   SHOW ssl_cert_file;
   SHOW ssl_key_file;
   ```

2. Preserve any existing PostgreSQL TLS configuration and keys. If certificates
   already exist, configure those rather than overwriting them.
3. If no server certificate/key exists, open an elevated PowerShell terminal
   with OpenSSL available and generate a local certificate in the reported data
   directory. Replace the example path with your actual `data_directory`:

   ```powershell
   $pgDataForBSetup = 'C:\Program Files\PostgreSQL\17\data'
   openssl req -x509 -newkey rsa:3072 -sha256 -nodes -days 365 -keyout "$pgDataForBSetup/server.key" -out "$pgDataForBSetup/server.crt" -subj "/CN=localhost" -addext "subjectAltName=DNS:localhost,IP:127.0.0.1"
   ```

4. In the reported `config_file`, enable `ssl = on` and set `ssl_cert_file` and
   `ssl_key_file` to those files. Relative certificate paths resolve against the
   PostgreSQL data directory. Ensure the Windows account running the PostgreSQL
   service can read the key; keep it private from other accounts.
5. Restart that PostgreSQL service through Windows **Services** at a time when
   stopping A's database connections is acceptable. The service is often named
   `postgresql-x64-17`; use the actual installed service name.
6. Reconnect pgAdmin and run `SHOW ssl;` again; it should return `on`.

This enables encryption on the shared PostgreSQL server, rather than creating a
second server. `require` enforces encryption; `verify-full` additionally verifies
the server identity when a trusted CA is configured. The PostgreSQL server
certificate is separate from the Flask HTTPS certificate in B's `.local/tls/`.

## 4. Load the schema through the existing connection

1. Right-click **room_monitor_b > Query Tool** under the same server connection.
2. Run:

   ```sql
   SELECT current_database(), current_user;
   ```

   Expect `room_monitor_b` and your existing PostgreSQL username (for example,
   `postgres`). Confirm the database name before running the schema.
3. Open `CodeBeacon/evaluation-study/app/version-B/database/schema.sql` with
   Query Tool's **Open File** button, or paste its full contents.
4. Execute the entire file, including `BEGIN` and `COMMIT`, once.
5. Refresh **Schemas > public > Tables**. Expect `user`, `devices`, `readings`,
   `requests`, and `login_attempts`.
6. Confirm the database connection uses TLS:

   ```sql
   SELECT ssl FROM pg_stat_ssl WHERE pid = pg_backend_pid();
   ```

   Expect `true`. If PostgreSQL has TLS enabled but this connection is not using
   it, set the existing saved connection's SSL mode to `require` under
   **Properties > Parameters** (or **SSL**, depending on pgAdmin version), then
   disconnect/reconnect. No additional saved server connection is required.

The script creates tables owned by the existing login executing it. No ownership
transfer is required. It is a one-time initialization script, not a reset or
migration. If a statement fails, run `ROLLBACK;` and inspect the error before
retrying. Do not drop existing tables to clear an error. Quote `"user"` in
hand-written SQL queries.

## 5. Configure B's local environment

Open `CodeBeacon/evaluation-study/app/version-B/.env` in your editor. Preserve
the file if it exists. If missing, copy `.env.example` to `.env` once.

Copy the working `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`,
`DB_SSLMODE`, and timeout values from A's database settings into B's `.env`.
Use the existing username that executed the schema above. Set `DB_NAME` to
`room_monitor_b`. For example, if your existing login is `postgres`:

```dotenv
DB_HOST=127.0.0.1
DB_PORT=5432
DB_NAME=room_monitor_b
DB_USER=postgres
DB_PASSWORD='YOUR_EXISTING_POSTGRESQL_PASSWORD'
DB_SSLMODE=require
DB_CONNECT_TIMEOUT_SECONDS=5
```

Replace the password placeholder locally; do not send your password in chat.
Single quotes help preserve spaces and `#` in dotenv values. If your password
itself contains a quote, use the appropriate dotenv quoting/escaping. Set
`DB_USER` explicitly: the existing template/backend fallback names
`room_monitor_app`, which may differ from your existing login. Use the actual
working username from A (and the schema connection), not the template default.
Keep A's `.env` unchanged. No PostgreSQL password change is needed.

Also set B's `APP_SECRET_KEY` to a new random value of at least 32 characters
if it is blank. This signs account tokens; it is not a PostgreSQL credential.
You can generate one locally with:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Process environment variables override `.env`. If a terminal has an old
`DB_NAME`, `DB_USER`, or other `DB_*` override set, remove/correct that override
in the terminal used to run B. Restart the app after changing settings.

## 6. Verify the connection through B's actual backend

Open PowerShell in `CodeBeacon/evaluation-study/app/version-B`. Use a Python
environment with B's pinned requirements. To create B's own environment, if it
does not already exist:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Then run this read-only check. It uses B's real settings loader and database
connector and does not print passwords:

```powershell
@'
from backend.main import create_app
from backend.database import get_db

app = create_app()
with app.app_context():
    db = get_db()
    print(db.execute("SELECT current_database() AS database, current_user AS role").fetchone())
    print(db.execute("SELECT ssl FROM pg_stat_ssl WHERE pid = pg_backend_pid()").fetchone())
    print(db.execute("SELECT tablename FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename").fetchall())
'@ | .\.venv\Scripts\python.exe -
```

Expect database `room_monitor_b`, your existing PostgreSQL role, `ssl: True`, and
the five table names. Creating the Flask app alone does not prove connectivity;
this check executes actual database queries.

## 7. Start the application

Follow [B's project guide](version-B/README.md) to generate its Flask certificate
if needed, then start the API from B's folder:

```powershell
.\.venv\Scripts\python.exe -m backend.main
```

In a second terminal in that folder:

```powershell
.\.venv\Scripts\python.exe -m streamlit run frontend/main.py --server.address 127.0.0.1 --server.port 8502 --server.headless true --browser.gatherUsageStats false
```

Open `http://127.0.0.1:8502`, create a new application account, and enroll a
device. Set B's `DEVICE_ID` and `DEVICE_TOKEN` to the issued pair, then start the
device client as described in the project guide. A's accounts/devices do not
automatically exist in B's separate database. Application passwords, database
role passwords, and device tokens serve different purposes.

To confirm persistence, reconnect Query Tool to `room_monitor_b` and run:

```sql
SELECT id, username, created_at FROM "user";
SELECT id, name, owner_id FROM devices;
SELECT recorded_at, temperature_c, fan_state
FROM readings ORDER BY recorded_at DESC LIMIT 10;
SELECT fan_state, created_at, acknowledged_at
FROM requests ORDER BY created_at DESC LIMIT 10;
```

These queries deliberately omit password hashes and device credential digests.

## Troubleshooting

| Message | Check |
| --- | --- |
| Connection refused | PostgreSQL service is running and host/port match pgAdmin. |
| Password authentication failed | `DB_USER` and `DB_PASSWORD` match your existing working PostgreSQL login, not pgAdmin's master password or the dashboard password. |
| Database does not exist | Exact database name is `room_monitor_b` on the selected server/port. |
| Server does not support SSL | Complete step 3; changing `.env` alone cannot enable server TLS. |
| No pg_hba.conf entry | Administrator must allow this role/database from the local client address using password authentication (normally `scram-sha-256`); do not switch to `trust` to bypass credentials. |
| Relation does not exist | Schema was loaded into B's database and `public` is in the search path; quote `"user"` in hand-written SQL. |
| Permission denied for schema/table | The schema and app use the same existing login; inspect existing privileges before making changes. |
| API says storage unavailable | Run step 6 to see the underlying connection/configuration failure. |
| API certificate error | Flask's `.local/tls/` certificate and `API_CA_BUNDLE` settings are separate from PostgreSQL TLS. |

Interface details are based on the official [pgAdmin database dialog](https://www.pgadmin.org/docs/pgadmin4/latest/database_dialog.html),
[server dialog](https://www.pgadmin.org/docs/pgadmin4/latest/server_dialog.html),
and [Query Tool](https://www.pgadmin.org/docs/pgadmin4/latest/query_tool.html).
TLS behavior follows [PostgreSQL SSL configuration](https://www.postgresql.org/docs/17/ssl-tcp.html)
and [client SSL modes](https://www.postgresql.org/docs/17/libpq-ssl.html).
