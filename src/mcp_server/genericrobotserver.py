"""Local, synthetic telemetry over MCP stdio; never controls hardware."""

import logging
import re
import time
import uuid
from datetime import datetime, timezone
from typing import Any

from mcp.server.fastmcp import FastMCP
from pydantic import ValidationError

from src.mcp_server.models import TelemetryData
from src.mcp_server.simulator import SimulatorTelemetryProvider

logger = logging.getLogger(__name__)
mcp = FastMCP(
    "RAGA Robot Telemetry Simulator",
    instructions="Synthetic data only. State updates affect memory, never physical robots.",
)
simulator_provider = SimulatorTelemetryProvider(num_joints=6)
robot_states: dict[tuple[str, str], TelemetryData] = {}
MAX_ROBOTS = 1000
STARTED_AT = time.monotonic()
IDENTIFIER = re.compile(r"[A-Za-z0-9_-]{1,64}")


def create_error_response(error_message: str, error_code: str) -> dict[str, Any]:
    return {"error": {"message": error_message, "code": error_code,
                      "timestamp": datetime.now(timezone.utc).isoformat(),
                      "trace_id": str(uuid.uuid4())}}


def create_success_response(data: Any, meta: dict | None = None) -> dict[str, Any]:
    return {"data": data, "meta": {
        "trace_id": str(uuid.uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "simulation": True, **(meta or {}),
    }}


def validate_key(factory_id: str, robot_id: str) -> tuple[str, str]:
    if not all(IDENTIFIER.fullmatch(value) for value in (factory_id, robot_id)):
        raise ValueError("IDs must contain 1–64 ASCII letters, digits, underscores or hyphens.")
    key = (factory_id, robot_id)
    if key not in robot_states and len(robot_states) >= MAX_ROBOTS:
        raise ValueError("Simulator capacity reached; restart to clear state.")
    return key


@mcp.resource("robots://{factory_id}/{robot_id}")
async def get_robot_telemetry(factory_id: str, robot_id: str) -> dict[str, Any]:
    """Read a cached synthetic snapshot, creating one on first access."""
    try:
        key = validate_key(factory_id, robot_id)
    except ValueError as exc:
        return create_error_response(str(exc), "INVALID_REQUEST")
    if key not in robot_states:
        robot_states[key] = simulator_provider.get_telemetry()
    telemetry = robot_states[key]
    return create_success_response(telemetry.model_dump(mode="json"), {
        "factory_id": factory_id, "robot_id": robot_id,
        "timestamp": telemetry.timestamp.isoformat(),
    })


@mcp.tool()
async def update_robot_state(
    factory_id: str,
    robot_id: str,
    joint_angles: list[float] | None = None,
    end_effector_pose: dict[str, float] | None = None,
    gripper_state: dict[str, Any] | None = None,
    force_torque: dict[str, float] | None = None,
    status: str | None = None,
) -> dict[str, Any]:
    """Atomically edit a synthetic snapshot in memory. No hardware actuation or approval workflow."""
    try:
        key = validate_key(factory_id, robot_id)
    except ValueError as exc:
        return create_error_response(str(exc), "INVALID_REQUEST")
    current = robot_states.get(key)
    candidate = (current or simulator_provider.get_telemetry()).model_dump()
    for field, value in (("joint_angles", joint_angles), ("status", status)):
        if value is not None:
            candidate[field] = value
    for field, patch in (("end_effector_pose", end_effector_pose),
                         ("gripper_state", gripper_state), ("force_torque", force_torque)):
        if patch is not None:
            candidate[field].update(patch)
    candidate["timestamp"] = datetime.now(timezone.utc)
    try:
        updated = TelemetryData.model_validate(candidate)
    except ValidationError:
        # Do not echo request values or commit any part of a rejected update.
        return create_error_response("Invalid telemetry fields or values.", "INVALID_UPDATE")
    robot_states[key] = updated
    return create_success_response(updated.model_dump(mode="json"), {
        "factory_id": factory_id, "robot_id": robot_id,
        "timestamp": updated.timestamp.isoformat(), "update_type": "state_update",
    })


@mcp.tool()
async def list_available_robots() -> dict[str, Any]:
    """List synthetic snapshots in this process; IDs are not access-control boundaries."""
    factories: dict[str, list[str]] = {}
    for factory_id, robot_id in robot_states:
        factories.setdefault(factory_id, []).append(robot_id)
    return create_success_response({"robots": factories}, {
        "total_count": len(robot_states), "factory_count": len(factories),
    })


@mcp.prompt("robot_calibration_instructions")
def get_calibration_prompt() -> str:
    """Simulation exercise only, not a physical robot calibration procedure."""
    return (
        "SIMULATION ONLY: inspect a synthetic telemetry snapshot, describe missing "
        "reference data, and propose a hypothetical comparison. Do not infer alignment "
        "from the random status label. Do not issue hardware commands. Real calibration "
        "requires the manufacturer's procedure and a qualified operator."
    )


@mcp.resource("server://info")
async def server_info() -> dict[str, Any]:
    return create_success_response({
        "name": "RAGA Robot Telemetry Simulator", "version": "0.1.0",
        "capabilities": ["synthetic_snapshots", "in_memory_state_updates"],
        "transport": "stdio", "hardware_connected": False,
    })


@mcp.resource("health://check")
async def health_check() -> dict[str, Any]:
    return create_success_response({
        "status": "healthy", "cached_robots": len(robot_states),
        "uptime_seconds": time.monotonic() - STARTED_AT,
    })


@mcp.resource("index://")
async def root() -> dict[str, Any]:
    return create_success_response({"resources": {
        "server_info": "server://info", "health_check": "health://check",
        "robot_telemetry": "robots://{factory_id}/{robot_id}",
    }})


def main() -> None:
    logging.basicConfig(level=logging.INFO)  # stderr; stdout belongs to MCP
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
