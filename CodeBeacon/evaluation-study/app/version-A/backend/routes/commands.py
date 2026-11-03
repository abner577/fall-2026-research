from flask import Blueprint, g

from backend.security import (
    account_required, device_required, fan_state, json_body, page_limit, public_row,
    uuid_value, validate_device_id,
)
from backend.services import devices

blueprint = Blueprint("commands", __name__, url_prefix="/api/devices")


@blueprint.post("/<device_id>/commands")
@account_required
def submit(device_id: str):
    validate_device_id(device_id)
    data = json_body("fan_state")
    command = devices.enqueue_command(device_id, g.account["id"], fan_state(data["fan_state"]))
    return {"command": public_row(command)}, 201


@blueprint.get("/<device_id>/commands")
@account_required
def history(device_id: str):
    devices.owned_device(device_id, g.account["id"])
    return {"commands": [public_row(row) for row in devices.command_history(device_id, page_limit())]}


@blueprint.get("/<device_id>/commands/pending")
def pending(device_id: str):
    command = devices.pending_command(device_id)
    return {"command": public_row(command) if command else None}


@blueprint.post("/<device_id>/commands/<command_id>/ack")
@device_required
def acknowledge(device_id: str, command_id: str):
    identifier = uuid_value(command_id, "command_id")
    data = json_body("fan_state")
    command = devices.acknowledge_command(device_id, identifier, fan_state(data["fan_state"]))
    return {"command": public_row(command)}
