import pytest
from uuid import uuid4
from fastapi.testclient import TestClient
from src.mcp_server.main import mcp

client = TestClient(mcp)

@pytest.fixture
def factory_and_robot_ids():
    return str(uuid4()), str(uuid4())

def test_server_info():
    response = client.get("/server/info")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "meta" in data
    assert "name" in data["data"]
    assert "version" in data["data"]
    assert "description" in data["data"]
    assert "timestamp" in data["meta"]
    assert "trace_id" in data["meta"]

def test_health_check():
    response = client.get("/health/check")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "meta" in data
    assert data["data"]["status"] == "healthy"
    assert "robots_monitored" in data["data"]
    assert isinstance(data["data"]["robots_monitored"], int)

def test_get_robot_telemetry(factory_and_robot_ids):
    factory_id, robot_id = factory_and_robot_ids
    response = client.get(f"/robots/{factory_id}/{robot_id}")
    assert response.status_code == 200
    data = response.json()
    
    # MCP response structure
    assert "data" in data
    assert "meta" in data
    
    # Metadata
    meta = data["meta"]
    assert meta["factory_id"] == factory_id
    assert meta["robot_id"] == robot_id
    assert "timestamp" in meta
    assert "trace_id" in meta
    
    # Telemetry data
    telemetry = data["data"]
    assert "joint_angles" in telemetry
    assert "end_effector_pose" in telemetry
    assert "gripper_state" in telemetry
    assert "force_torque" in telemetry
    assert "status" in telemetry

def test_update_robot_state_tool(factory_and_robot_ids):
    factory_id, robot_id = factory_and_robot_ids
    # First, GET to initialize
    client.get(f"/robots/{factory_id}/{robot_id}")
    
    # Now call the update_robot_state tool
    tool_payload = {
        "factory_id": factory_id,
        "robot_id": robot_id,
        "status": "misaligned"
    }
    response = client.post("/tools/update_robot_state", json=tool_payload)
    assert response.status_code == 200
    data = response.json()
    
    # MCP tool response structure
    assert "data" in data
    assert "meta" in data
    
    # Metadata
    meta = data["meta"]
    assert meta["factory_id"] == factory_id
    assert meta["robot_id"] == robot_id
    assert meta["update_type"] == "state_update"
    assert "timestamp" in meta
    assert "trace_id" in meta
    
    # Telemetry data
    telemetry = data["data"]
    assert telemetry["status"] == "misaligned"
    
    # Verify the change through a GET request
    response = client.get(f"/robots/{factory_id}/{robot_id}")
    data = response.json()
    telemetry = data["data"]
    assert telemetry["status"] == "misaligned"

def test_update_robot_state_invalid_status(factory_and_robot_ids):
    factory_id, robot_id = factory_and_robot_ids
    # Call the update_robot_state tool with invalid status
    tool_payload = {
        "factory_id": factory_id,
        "robot_id": robot_id,
        "status": "invalid_status" # This is not a valid status
    }
    response = client.post("/tools/update_robot_state", json=tool_payload)
    assert response.status_code == 200  # Still returns 200 as we handle errors internally
    data = response.json()
    
    # Should have an error field
    assert "error" in data
    assert "Invalid status value" in data["error"]
