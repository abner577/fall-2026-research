BEGIN;

CREATE TABLE "user" (
    id UUID PRIMARY KEY,
    username VARCHAR(32) NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    token_version INTEGER NOT NULL DEFAULT 1 CHECK (token_version >= 1),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE devices (
    id VARCHAR(64) PRIMARY KEY,
    owner_id UUID NOT NULL REFERENCES "user" (id),
    name VARCHAR(100) NOT NULL,
    token_hash VARCHAR(64) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE readings (
    id UUID NOT NULL,
    device_id VARCHAR(64) NOT NULL REFERENCES devices (id),
    temperature_c DOUBLE PRECISION NOT NULL CHECK (temperature_c BETWEEN -40 AND 85),
    fan_state TEXT NOT NULL CHECK (fan_state IN ('on', 'off')),
    recorded_at TIMESTAMPTZ NOT NULL,
    received_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (device_id, id)
);

CREATE TABLE requests (
    id UUID PRIMARY KEY,
    device_id VARCHAR(64) NOT NULL REFERENCES devices (id),
    requested_by UUID NOT NULL REFERENCES "user" (id),
    fan_state TEXT NOT NULL CHECK (fan_state IN ('on', 'off')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    acknowledged_at TIMESTAMPTZ
);

CREATE TABLE login_attempts (
    bucket INTEGER PRIMARY KEY CHECK (bucket BETWEEN 0 AND 4095),
    failures INTEGER NOT NULL DEFAULT 0 CHECK (failures >= 0),
    window_started_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX devices_owner_history_idx ON devices (owner_id, created_at DESC, id DESC);
CREATE INDEX readings_device_history_idx ON readings (device_id, recorded_at DESC, id DESC);
CREATE INDEX requests_device_history_idx ON requests (device_id, created_at DESC, id DESC);

COMMIT;
