We are going to use four main tables and one small supporting table:
| Table | What it stores | Main fields |
|---|---|---|
| **`user`** | The people using the application. | `id`, `username`, `password_hash`, `token_version`, `created_at` |
| **`devices`** | Each room device and who owns it. | `id`, `owner_id`, `name`, `token_hash`, `created_at` |
| **`readings`** | Temperature measurements and the fan state reported with each measurement. | `id`, `device_id`, `temperature_c`, `fan_state`, `recorded_at`, `received_at` |
| **`requests`** | Requests to turn a device’s fan on or off, including whether the device confirmed them. | `id`, `device_id`, `requested_by`, `fan_state`, `created_at`, `acknowledged_at` |
| **`login_attempts`** | Small counters used by the existing backend to restrict repeated failed logins. | `bucket`, `failures`, `window_started_at` |

- One account can own several devices, through devices.owner_id
- One device can have many readings and requests, through device_id
- Each request also points to the account that requested it, through requested_by
- login_attempts stands separately because failed logins can involve usernames that do not belong to an account.

1. token_version lets a password change invalidate previous login sesions. Its just a counter like:
| Situation | Database value | Value carried by login token |
|---|---:|---:|
| User signs in | `1` | `1` — accepted |
| User changes password | `2` | Old token still carries `1` — rejected |
| New token issued after the change | `2` | `2` — accepted |

On each authenticated request, the backend compares those 2 numbers. They must match. This means someone holding an old login token loses access after the password changes.

2. token_hash stores a hash of the devices secret token instead of storing the original token
For example:
1. A device receives a secret token such as room-token-123 an illustrative value.
2. The backend calculates its SHA-256 hash and stores that 64-character result in token_hash.
3. When the device sends its token, the backend hashes it again.
4. If the new hash matches the stored hash, the token is accepted.

Hashing is one way.
