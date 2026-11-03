There are no vulnerability insertions directly in the frontend. Some frontend buttons call backend operations that contain the weaknesses. The connections are pointed out below

### 1. frontend/main.py (starts the dashboard)
- This is the starting file. It loads the connection settings, shows the sign-in screen, and lets a signed-in user switch between the dashboard and account settings.

### 2. frontend/api_client.py (sends requests to Flask)
- The other frontend files use this file whenever they need something from the server: signing in, registering a device, getting a temperature, etc. It sends the request and turns connections problems int messages the page can display.

### 3. frontend/views/account.py (account forms and login state)
- This file displays registration, sign-in and password-change forms, then sends what the user entered through the API client. It also remembers the login token and clears the saved login when the session expires or the user signs out.

**1. Weakness exposed through this workflow: A-02, weak password changes (lines 86-93)**
The form checks that the passwords were entered and the new entries match. It sends even a short new password to the backend, where the strength rule should be enforced.

### 4. frontend/views/dashboard.py (devices, readings, and fan controls)
This file registers devices and shows their latest temperature, reported fan state, charts, and command history. Every five seconds it asks Flask for updated information; pressing the fan button sends a request that waits for the device to acknowledge it.

**2. Exposed through this workflow: A-06, controlling another user’s device**
- The frontend sends the command in frontend/views/dashboard.py (lines 103-105)
```python
command = client.request_fan(device_id, target)
commands = [command, *commands][:100]
st.success("Fan command queued. Waiting for device acknowledgment.")
```
The server checks that someone is signed in, but never checks that they own the named device. The dropdown normally shows their own devices, but someone can send a request directly using another device’s ID.