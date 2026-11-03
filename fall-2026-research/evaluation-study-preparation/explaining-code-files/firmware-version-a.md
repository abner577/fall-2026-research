- The 3 firmware weaknesses are in 2 files: settings.py contains one, and api_client.py

### 1. firmware/settings.py (lines 11-12)
- This file answers practical questions such as: “Which device am I?”, “What token should I send?”, and “Where is the backend?” It reads the device’s settings and checks that they make sense.

**1. Exposed — A-01: a device credential is written directly into the source.**
```python
DEFAULT_DEVICE_ID = "room-monitor-01"
DEFAULT_DEVICE_TOKEN = "rma_T8u4NXp3bS7nV2cQ6kL9fJ5wE1hZ0dR8"
```

Lines 81-83 select this embedded token when the bundled device has no token supplied in .env

```python
device_token = text("DEVICE_TOKEN")
if not device_token and device_id == DEFAULT_DEVICE_ID:
    device_token = DEFAULT_DEVICE_TOKEN
```

Why it’s a problem: someone who obtains the source can copy the token and pretend to be room-monitor-01. The device ID identifies the device; the token is supposed to prove permission to act as it.

### 2. firmware/api_client.py (line 111)
This file sends temperature readings to the backend, asks whether fan commands are waiting, and confirms when a command has been applied. It attaches the device token to those requests.

**2. Exposed — A-04: failed reading submissions put the device token into logs.**
First, lines 70-73 prepare the request headers:
```python
self._headers = {
    "Authorization": f"Bearer {settings.device_token}",
    "Accept": "application/json",
}
```

Then _post_reading(), lines 117-122, logs those complete headers when the request fails: 
```python
except ApiError as error:
    logger.error(
        "Reading submission failed: reason=%s status=%s headers=%s",
        error.reason, error.status_code, self._headers,
    )
    raise
```

**3. Exposed — A-08: a reading retry switches off server-certificate checking.**
submit_reading(), lines 124–132:
```python
def submit_reading(self, reading: Reading) -> None:
    try:
        self._post_reading(reading, self._session, verify=str(self._settings.api_ca_bundle))
    except ApiError as error:
        if not error.certificate_error:
            raise
        with requests.Session() as retry_session:
            retry_session.trust_env = False
            self._post_reading(reading, retry_session, verify=False)
```

Why it’s a problem: the first attempt checks that the server is trusted. If that check fails, the retry uses verify=False, so an impersonating server could receive the reading and device token.