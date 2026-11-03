from flask import Blueprint, g

from backend.security import (
    account_required, device_required, json_body, page_limit, public_row, reading_payload,
)
from backend.services import devices

blueprint = Blueprint("readings", __name__, url_prefix="/api/devices")


@blueprint.post("/<device_id>/readings")
@device_required
def submit(device_id: str):
    data = json_body("reading_id", "recorded_at", "temperature_c", "unit", "fan_state")
    row, created = devices.save_reading(device_id, reading_payload(data))
    return {"reading": public_row(row)}, 201 if created else 200


@blueprint.get("/<device_id>/readings")
@account_required
def history(device_id: str):
    devices.owned_device(device_id, g.account["id"])
    return {"readings": [public_row(row) for row in devices.reading_history(device_id, page_limit())]}
