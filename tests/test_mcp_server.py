import pytest
from uuid import uuid4
from mcp.client.session import ClientSession
import asyncio

# Mark the test module to use pytest-asyncio
pytestmark = pytest.mark.asyncio

import asyncio
from typing import Optional
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# from dotenv import load_dotenv
# load_dotenv()  # load environment variables from .env

class MCPClient:
    def __init__(self):
        # Initialize session and client objects
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
    # methods will go here
    
@pytest.fixture
async def connect_to_server(self, server_script_path: str):
    
    command = "python" if is_python else "node"
    server_params = StdioServerParameters(
        command="python",
        env=None
    )
    
    stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
    self.stdio, self.write = stdio_transport
    self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))
    
    await self.session.initialize()
    
    # List available tools
    response = await self.session.list_tools()
    tools = response.tools
    print("\nConnected to server with tools:", [tool.name for tool in tools])
    
async def mcp_client():
    """
    Fixture that provides a properly configured MCP client session.
    Creates a single connection per test for efficiency.
    """
    # Use HTTP transport to connect to the server
    async with ClientSession.from_http("http://localhost:6227") as session:
        yield session

@pytest.fixture
def factory_and_robot_ids():
    """Generate unique identifiers for factory and robot for test isolation"""
    return str(uuid4()), str(uuid4())

async def test_server_info(mcp_client):
    """Test the server info resource returns expected metadata"""
    result = await mcp_client.read_resource("server://info")
    assert "data" in result
    assert "meta" in result
    
    # Validate specific fields in the response
    info = result["data"]
    assert "name" in info
    assert "version" in info
    assert "description" in info

async def test_health_check(mcp_client):
    """Test the health check resource returns valid status"""
    result = await mcp_client.read_resource("health://check")
    assert "data" in result
    assert "meta" in result
    
    health = result["data"]
    assert health["status"] == "healthy"
    assert isinstance(health["robots_monitored"], int)

async def test_get_robot_telemetry(mcp_client, factory_and_robot_ids):
    """Test retrieving telemetry data for a specific robot"""
    factory_id, robot_id = factory_and_robot_ids
    result = await mcp_client.read_resource(f"robots://{factory_id}/{robot_id}")
    
    assert "data" in result
    assert "meta" in result
    
    # Validate response structure
    meta = result["meta"]
    assert meta["factory_id"] == factory_id
    assert meta["robot_id"] == robot_id
    assert "timestamp" in meta
    assert "trace_id" in meta
    
    # Validate telemetry data structure
    telemetry = result["data"]
    assert "joint_angles" in telemetry
    assert "end_effector_pose" in telemetry
    assert "gripper_state" in telemetry
    assert "force_torque" in telemetry
    assert "status" in telemetry

async def test_update_robot_state_tool(mcp_client, factory_and_robot_ids):
    """Test updating robot state and verifying the changes"""
    factory_id, robot_id = factory_and_robot_ids
    
    # Initialize robot state (first access creates it)
    await mcp_client.read_resource(f"robots://{factory_id}/{robot_id}")
    
    # Update the robot status
    result = await mcp_client.call_tool(
        "update_robot_state",
        arguments={
            "factory_id": factory_id,
            "robot_id": robot_id,
            "status": "misaligned"
        }
    )
    
    assert "data" in result
    assert "meta" in result
    
    # Verify update in response
    telemetry = result["data"]
    assert telemetry["status"] == "misaligned"
    
    # Verify through a separate read that state was updated
    verify_result = await mcp_client.read_resource(f"robots://{factory_id}/{robot_id}")
    verify_telemetry = verify_result["data"]
    assert verify_telemetry["status"] == "misaligned"

async def test_update_robot_state_invalid_status(mcp_client, factory_and_robot_ids):
    """Test error handling for invalid robot status updates"""
    factory_id, robot_id = factory_and_robot_ids
    
    # Attempt to update with invalid status
    with pytest.raises(Exception) as excinfo:
        await mcp_client.call_tool(
            "update_robot_state",
            arguments={
                "factory_id": factory_id,
                "robot_id": robot_id,
                "status": "invalid_status"  # This is not a valid status
            }
        )
    
    # Verify specific error message
    error_msg = str(excinfo.value)
    assert "Invalid status" in error_msg or "invalid_status" in error_msg
