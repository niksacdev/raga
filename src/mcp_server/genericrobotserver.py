from mcp.server.fastmcp import FastMCP
from typing import Dict, Any, List, Optional
from mcp_server.simulator import SimulatorTelemetryProvider
from mcp_server.models import GripperOpenState
import logging
import uuid

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("mcp_server")

# Create an MCP server with version specified
mcp = FastMCP("RAGA Robot Telemetry", version="1.0.0")

# Simulator provider setup
simulator_provider = SimulatorTelemetryProvider(num_joints=6)
robot_states = {}  # {(factory_id, robot_id): TelemetryData}

@mcp.resource("robots://{factory_id}/{robot_id}")
async def get_robot_telemetry(factory_id: str, robot_id: str) -> Dict[str, Any]:
    """Get the current telemetry for a specific robot"""
    logger.info(f"Retrieving telemetry for robot {robot_id} in factory {factory_id}")
    key = (factory_id, robot_id)
    
    if key not in robot_states:
        logger.info(f"Initializing new robot state for {factory_id}/{robot_id}")
        robot_states[key] = simulator_provider.get_telemetry()
    
    telemetry = robot_states[key]
    
    # Format as MCP standard response
    return {
        "data": telemetry.dict(),
        "meta": {
            "factory_id": factory_id,
            "robot_id": robot_id,
            "timestamp": telemetry.timestamp.isoformat(),
            "trace_id": str(uuid.uuid4())
        }
    }

@mcp.tool()
async def update_robot_state(
    factory_id: str, 
    robot_id: str, 
    joint_angles: Optional[List[float]] = None, 
    end_effector_pose: Optional[Dict[str, float]] = None,
    gripper_state: Optional[Dict[str, Any]] = None,
    force_torque: Optional[Dict[str, float]] = None,
    status: Optional[str] = None
) -> Dict[str, Any]:
    """
    Update the state of a specific robot
    
    Args:
        factory_id: The factory identifier
        robot_id: The robot identifier
        joint_angles: Optional list of joint angles in degrees
        end_effector_pose: Optional end effector position (mm) and orientation (degrees)
        gripper_state: Optional gripper state (is_open: 0/1, force: N)
        force_torque: Optional force (N) and torque (Nm) readings
        status: Optional robot status (ok, misaligned, error)
    
    Returns:
        Updated robot telemetry data with metadata
    """
    logger.info(f"Updating robot state for {robot_id} in factory {factory_id}")
    trace_id = str(uuid.uuid4())
    
    try:
        key = (factory_id, robot_id)
        
        if key not in robot_states:
            logger.info(f"Initializing new robot state for {factory_id}/{robot_id}")
            robot_states[key] = simulator_provider.get_telemetry()
        
        current = robot_states[key]
        
        # Handle the update based on provided fields
        if joint_angles is not None:
            logger.debug(f"Updating joint angles: {joint_angles}")
            current.joint_angles = joint_angles
        
        if end_effector_pose is not None:
            for field in ["x", "y", "z", "roll", "pitch", "yaw"]:
                if field in end_effector_pose:
                    setattr(current.end_effector_pose, field, end_effector_pose[field])
        
        if gripper_state is not None:
            if "is_open" in gripper_state:
                current.gripper_state.is_open = GripperOpenState(gripper_state["is_open"])
            if "force" in gripper_state:
                current.gripper_state.force = gripper_state["force"]
        
        if force_torque is not None:
            for field in ["fx", "fy", "fz", "tx", "ty", "tz"]:
                if field in force_torque:
                    setattr(current.force_torque, field, force_torque[field])
        
        if status is not None:
            if status not in ["ok", "misaligned", "error"]:
                logger.warning(f"Received invalid status: {status}")
                raise ValueError(f"Invalid status value. Expected 'ok', 'misaligned', or 'error', got '{status}'")
            current.status = status
        
        robot_states[key] = current
        logger.info(f"Updated robot {robot_id} state successfully")
        
        return {
            "data": current.dict(),
            "meta": {
                "factory_id": factory_id,
                "robot_id": robot_id,
                "update_type": "state_update",
                "timestamp": current.timestamp.isoformat(),
                "trace_id": trace_id
            }
        }
    except Exception as e:
        logger.error(f"Error updating robot state: {str(e)}")
        return {
            "error": str(e),
            "meta": {
                "factory_id": factory_id,
                "robot_id": robot_id,
                "trace_id": trace_id
            }
        }

@mcp.resource("server://info")
async def server_info() -> Dict[str, Any]:
    """Return information about the MCP server"""
    logger.info("Server info requested")
    return {
        "data": {
            "name": "RAGA Robot Telemetry MCP Server",
            "version": "1.0.0",
            "description": "Provides telemetry data for robotic arms in factory environments"
        },
        "meta": {
            "timestamp": simulator_provider.get_telemetry().timestamp.isoformat(),
            "trace_id": str(uuid.uuid4())
        }
    }

# Add a health check resource
@mcp.resource("health://check")
async def health_check() -> Dict[str, Any]:
    """Health check endpoint"""
    logger.info("Health check requested")
    return {
        "data": {
            "status": "healthy",
            "robots_monitored": len(robot_states)
        },
        "meta": {
            "timestamp": simulator_provider.get_telemetry().timestamp.isoformat(),
            "trace_id": str(uuid.uuid4())
        }
    }

if __name__ == "__main__":
    logger.info("Starting MCP server on port 6227")
    mcp.run()
    # mcp.run(transport="stdio")