import math

import pytest

from src.mcp_server import genericrobotserver as server
from src.mcp_server.models import TelemetryData
from src.mcp_server.simulator import SimulatorTelemetryProvider


@pytest.fixture(autouse=True)
def clear_state():
    server.robot_states.clear()
    yield
    server.robot_states.clear()


@pytest.mark.asyncio
async def test_snapshot_and_atomic_update():
    original = await server.get_robot_telemetry("factory", "arm")
    assert (await server.get_robot_telemetry("factory", "arm"))["data"] == original["data"]
    result = await server.update_robot_state("factory", "arm", end_effector_pose={"x": 501})
    assert result["data"]["end_effector_pose"]["x"] == 501
    assert result["data"]["end_effector_pose"]["y"] == original["data"]["end_effector_pose"]["y"]
    assert result["data"]["timestamp"] > original["data"]["timestamp"]
    assert (await server.get_robot_telemetry("factory", "arm"))["data"] == result["data"]
    TelemetryData.model_validate(result["data"])


@pytest.mark.asyncio
@pytest.mark.parametrize("patch", [
    {"status": "invalid", "end_effector_pose": {"x": 501}},
    {"gripper_state": {"is_open": 2}, "joint_angles": [1] * 6},
    {"gripper_state": {"force": -1}},
    {"end_effector_pose": {"unknown": 5}},
    {"end_effector_pose": {"x": math.nan}},
    {"force_torque": {"tx": math.inf}},
    {"joint_angles": [0] * 5},
    {"joint_angles": [math.inf] * 6},
])
async def test_rejected_update_never_mutates_or_creates(patch):
    before = (await server.get_robot_telemetry("factory", "arm"))["data"]
    assert "error" in await server.update_robot_state("factory", "arm", **patch)
    assert (await server.get_robot_telemetry("factory", "arm"))["data"] == before
    assert "error" in await server.update_robot_state("factory", "new", **patch)
    assert ("factory", "new") not in server.robot_states


@pytest.mark.asyncio
@pytest.mark.parametrize("identifier", ["", "../private", "a/b", "a\nlog", "a" * 65])
async def test_reject_identifiers(identifier):
    assert "error" in await server.get_robot_telemetry(identifier, "arm")
    assert not server.robot_states


@pytest.mark.asyncio
async def test_capacity_and_existing_updates(monkeypatch):
    monkeypatch.setattr(server, "MAX_ROBOTS", 1)
    await server.get_robot_telemetry("factory", "arm")
    assert "error" in await server.get_robot_telemetry("factory", "new")
    assert "error" in await server.update_robot_state("factory", "new", status="ok")
    assert "data" in await server.update_robot_state("factory", "arm", status="ok")
    assert len(server.robot_states) == 1


def test_generator_schema_and_timezone():
    sample = SimulatorTelemetryProvider().get_telemetry()
    assert len(sample.joint_angles) == 6
    assert sample.timestamp.utcoffset().total_seconds() == 0
    with pytest.raises(ValueError):
        SimulatorTelemetryProvider(7)
