"""MCP SDK client for a local RAGA simulator subprocess."""

import asyncio
import json
import sys
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class RAGAMCPClient:
    """Use ``async with RAGAMCPClient.connect() as client`` to own the session."""

    def __init__(self, session: ClientSession):
        self.session = session

    @classmethod
    @asynccontextmanager
    async def connect(cls):
        parameters = StdioServerParameters(
            command=sys.executable,
            args=["-m", "src.mcp_server.genericrobotserver"],
            cwd=str(Path(__file__).resolve().parents[2]),
        )
        async with stdio_client(parameters) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                yield cls(session)

    async def read_resource(self, uri: str) -> dict[str, Any]:
        result = await self.session.read_resource(uri)
        return json.loads(result.contents[0].text)

    async def get_server_info(self) -> dict[str, Any]:
        return await self.read_resource("server://info")

    async def get_robot_telemetry(self, factory_id: str, robot_id: str) -> dict[str, Any]:
        return await self.read_resource(f"robots://{factory_id}/{robot_id}")

    async def call_tool(self, name: str, arguments: dict | None = None) -> dict[str, Any]:
        result = await self.session.call_tool(name, arguments=arguments or {})
        if result.isError:
            raise RuntimeError(f"MCP tool failed: {name}")
        payload = result.structuredContent
        if payload is None:
            payload = json.loads(result.content[0].text)
        if "error" in payload:
            raise ValueError(payload["error"]["message"])
        return payload

    async def update_robot_state(self, factory_id: str, robot_id: str, **updates) -> dict[str, Any]:
        return await self.call_tool("update_robot_state", {
            **updates, "factory_id": factory_id, "robot_id": robot_id,
        })

    async def list_robots(self) -> dict[str, Any]:
        return await self.call_tool("list_available_robots")

    async def get_calibration_prompt(self) -> dict[str, Any]:
        result = await self.session.get_prompt("robot_calibration_instructions")
        return result.model_dump(mode="json")


async def main() -> None:
    async with RAGAMCPClient.connect() as client:
        outputs = {
            "server": await client.get_server_info(),
            "before": await client.get_robot_telemetry("demo_factory", "arm1"),
            "updated": await client.update_robot_state(
                "demo_factory", "arm1", end_effector_pose={"x": 500}),
            "robots": await client.list_robots(),
            "prompt": await client.get_calibration_prompt(),
        }
        print(json.dumps(outputs, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
