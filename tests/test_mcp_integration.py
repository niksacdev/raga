import json

import pytest
from anyio import fail_after

from src.mcp_client.client import RAGAMCPClient


@pytest.mark.asyncio
async def test_stdio_protocol_roundtrip():
    with fail_after(30):
        async with RAGAMCPClient.connect() as client:
            info = await client.get_server_info()
            assert info["meta"]["simulation"] is True
            assert info["data"]["hardware_connected"] is False
            resources = await client.session.list_resources()
            assert {str(r.uri) for r in resources.resources} == {"server://info", "health://check", "index://"}
            templates = await client.session.list_resource_templates()
            assert templates.resourceTemplates[0].uriTemplate == "robots://{factory_id}/{robot_id}"
            tools = await client.session.list_tools()
            assert {t.name for t in tools.tools} == {"update_robot_state", "list_available_robots"}
            before = await client.get_robot_telemetry("demo", "arm")
            after = await client.update_robot_state("demo", "arm", end_effector_pose={"x": 555})
            assert after["data"]["end_effector_pose"]["x"] == 555
            assert after["data"]["end_effector_pose"]["y"] == before["data"]["end_effector_pose"]["y"]
            with pytest.raises(ValueError):
                await client.update_robot_state("demo", "arm", status="bad", end_effector_pose={"x": 777})
            assert (await client.get_robot_telemetry("demo", "arm"))["data"] == after["data"]
            assert (await client.list_robots())["data"]["robots"] == {"demo": ["arm"]}
            health = await client.read_resource("health://check")
            assert 0 <= health["data"]["uptime_seconds"] < 30
            assert "memory_usage_mb" not in health["data"]
            assert "SIMULATION ONLY" in json.dumps(await client.get_calibration_prompt())
        # A new subprocess has no persisted snapshots.
        async with RAGAMCPClient.connect() as client:
            assert (await client.list_robots())["meta"]["total_count"] == 0
