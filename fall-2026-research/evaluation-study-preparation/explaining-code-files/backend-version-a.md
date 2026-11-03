- The basic flow is that a request arrives in a routes/file --> a services/ files does the work --> Postgres stores or returns the information. 

Database update, November 2: the backend now queries `"user"` and `requests`
instead of `accounts` and `commands`. This changes SQL table names only; source
line counts and the function locations described below remain unchanged.
Current source hashes and real PostgreSQL checks are recorded in the
[database implementation record](../database-version-a-implementation.md).

## Protected files

### 1. backend/main.py
- Starts the API and connects all the account, device, reading, and command routes. 

Vulnerabilitiy: Encrypted API Communication (Protected)
- Lines 103–107 load the certificate and key and start the server using HTTPS:

```python
context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.minimum_version = ssl.TLSVersion.TLSv1_2
context.load_cert_chain(settings.tls_cert_file, settings.tls_key_file)
app = create_app(settings)
app.run(host=settings.host, port=settings.port, ssl_context=context, debug=False, use_reloader=False)
```
- This protects passwords and tokens while they travel to the API.

### 2. backend/settings.py
- Collects settings such as the database name, password, server port, and certificate paths. Line 33 reads this version’s .env

Protected: backend secrets come from configuration. Lines 50–55 require a signing secret and database password:

### 3. backend/database.py
- Opens the PostgreSQL connection when a request needs data, reuses it during that request, and closes it afterward.

Protected: the database connection requires encryption. Lines 14–16 pass these settings to PostgreSQL:

### 4. backend/security.py
Contains the shared checks: “Is this account signed in?”, “Does this token belong to this device?”, “Is this reading valid?”, and “Have there been too many failed logins?” Routes must actually call these checks to receive their protection.

### 5. backend/routes/accounts.py
- Receives requests to register, log in, view the signed-in account, or change a password. It reads the submitted information, passes it to the account service, and returns the result.

### 7. backend/routes/devices.py
Receives requests to register a device, list your devices, or show one device’s details and latest reading. Registration returns the new device ID and its token.

### 8. backend/routes/readings.py
Receives temperature updates from the device and returns readings for the dashboard.

---

## Files w/ vulnerabilities

### 6. backend/services/accounts.py
- Creates account records, checks login passwords, and replaces passwords. This file contains two separate planned vulnerabilities.

**1. Exposed — A-03: registration hashes are too cheap to calculate. Lines 12–14:**
```python
def register_account(username: str, password: str) -> dict:
    validate_password_strength(password)
    password_hash = generate_password_hash(password, method="pbkdf2:sha256:1000")
```

Registration checks password length, but stores a hash using only 1,000 iterations. If someone obtains the database hashes, they can test password guesses much faster than against our protected configuration.

**2. Exposed — A-02: password changes skip the strength check. Inside change_password(), lines 43–45:**
```python
if account is None or not check_password_hash(account["password_hash"], current_password):
    raise Unauthorized("Current password is incorrect")
password_hash = generate_password_hash(new_password, method=PASSWORD_HASH_METHOD)
```

After checking the current password, the code immediately hashes the new one. The full function, lines 37–49, never calls validate_password_strength(new_password), so someone can change their password to "a" even though registration rejects it.

### 9. backend/routes/commands.py
Receives fan-change requests, lets the device collect waiting commands, and receives confirmation that a command was applied from the physical device. This file contains two separate planned vulnerabilities.

**3. Exposed — A-05: collecting commands requires no device token. Lines 28–31:**
```python
@blueprint.get("/<device_id>/commands/pending")
def pending(device_id: str):
    command = devices.pending_command(device_id)
    return {"command": public_row(command) if command else None}
```
There is no @device_required check here, and the called service doesn’t authenticate the caller either. Someone knowing a device ID can read its waiting command.

**4. Exposed — A-06: submitting commands doesn’t check ownership. Lines 12–18:**
```python
@blueprint.post("/<device_id>/commands")
@account_required
def submit(device_id: str):
    validate_device_id(device_id)
    data = json_body("fan_state")
    command = devices.enqueue_command(device_id, g.account["id"], fan_state(data["fan_state"]))
    return {"command": public_row(command)}, 201
```

@account_required proves Alice is signed in, but nothing checks whether the device belongs to Alice. She can name Bob’s device and queue a fan command.

### 10. backend/services/devices.py
Does the database work for devices, readings, and commands. It avoids saving identical reading retries twice, returns waiting commands, and records acknowledgments.

**5. Exposed — A-07: generated device tokens are predictable. Lines 27–31:**
```python
def enroll_device(owner_id, name: str) -> tuple[dict, str]:
    device_id = uuid4().hex
    generator = random.Random(device_id)
    token = f"rma_{generator.getrandbits(256):064x}"
    return _insert_device(owner_id, device_id, name, token), token
```

- The device ID starts the random-number sequence. Someone who learns that ID can run the same calculation and recreate the token—it looks random, but can be reproduced.
