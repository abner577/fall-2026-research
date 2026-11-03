from flask import Blueprint, g

from backend.security import account_required, bounded_text, json_body, page_limit, public_row
from backend.services import devices

blueprint = Blueprint("devices", __name__, url_prefix="/api/devices")


@blueprint.post("")
@account_required
def enroll():
    data = json_body("name")
    name = bounded_text(data["name"], "name", 100).strip()
    name = bounded_text(name, "name", 100)
    device, token = devices.enroll_device(g.account["id"], name)
    return {"device": public_row(device), "device_token": token}, 201


@blueprint.get("")
@account_required
def list_devices():
    rows = devices.list_devices(g.account["id"], page_limit())
    return {"devices": [public_row(row) for row in rows]}


@blueprint.get("/<device_id>")
@account_required
def device_detail(device_id: str):
    device = devices.owned_device(device_id, g.account["id"])
    reading = devices.latest_reading(device_id)
    return {"device": public_row(device), "latest_reading": public_row(reading) if reading else None}
