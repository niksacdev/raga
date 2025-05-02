from mcp.server.fastmcp import FastMCP
from typing import Dict, Any, List, Optional, Union
from src.mcp_server.simulator import SimulatorTelemetryProvider
from src.mcp_server.models import GripperOpenState
import logging
import uuid
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("mcp_server")

# Create an MCP server with version specified
mcp = FastMCP("RAGA Robot Telemetry", version="1.0.0",
              description="MCP server for robotic arm telemetry and control")

# Simulator provider setup
simulator_provider = SimulatorTelemetryProvider(num_joints=6)
robot_states = {}  # {(factory_id, robot_id): TelemetryData}

# Define common error response structure


def create_error_response(error_message: str, error_code: str = "INTERNAL_ERROR",
                          factory_id: Optional[str] = None,
                          robot_id: Optional[str] = None) -> Dict[str, Any]:
    """Create a standardized error response structure

    Args:
        error_message: Human-readable error description
        error_code: Machine-readable error code
        factory_id: Optional factory identifier involved in the error
        robot_id: Optional robot identifier involved in the error

    Returns:
        Structured error response dictionary
    """
    return {
        "error": {
            "message": error_message,
            "code": error_code,
            "timestamp": datetime.utcnow().isoformat(),
            "trace_id": str(uuid.uuid4()),
            "context": {
                "factory_id": factory_id,
                "robot_id": robot_id
            }
        }
    }

# Define success response structure


def create_success_response(data: Any, meta: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Create a standardized success response structure

    Args:
        data: The response data payload
        meta: Optional metadata about the response

    Returns:
        Structured success response dictionary
    """
    if meta is None:
        meta = {}

    # Ensure trace_id is always present
    if "trace_id" not in meta:
        meta["trace_id"] = str(uuid.uuid4())

    # Ensure timestamp is always present
    if "timestamp" not in meta:
        meta["timestamp"] = datetime.utcnow().isoformat()

    return {
        "data": data,
        "meta": meta
    }

# --- Existing resource endpoints with updated response handling ---


@mcp.resource("robots://{factory_id}/{robot_id}")
async def get_robot_telemetry(factory_id: str, robot_id: str) -> Dict[str, Any]:
    """Get the current telemetry for a specific robot

    Args:
        factory_id: The identifier of the factory where the robot is located
        robot_id: The unique identifier of the target robot

    Returns:
        Current telemetry data for the specified robot
    """
    logger.info(
        f"Retrieving telemetry for robot {robot_id} in factory {factory_id}")

    try:
        key = (factory_id, robot_id)

        if key not in robot_states:
            logger.info(
                f"Initializing new robot state for {factory_id}/{robot_id}")
            robot_states[key] = simulator_provider.get_telemetry()

        telemetry = robot_states[key]

        # Return using standardized response structure
        return create_success_response(
            data=telemetry.dict(),
            meta={
                "factory_id": factory_id,
                "robot_id": robot_id,
                "timestamp": telemetry.timestamp.isoformat(),
                "trace_id": str(uuid.uuid4())
            }
        )
    except Exception as e:
        logger.error(f"Error retrieving robot telemetry: {str(e)}")
        return create_error_response(
            error_message=f"Failed to retrieve telemetry: {str(e)}",
            error_code="TELEMETRY_RETRIEVAL_ERROR",
            factory_id=factory_id,
            robot_id=robot_id
        )

# --- Update tool methods with enhanced error handling ---


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

    This tool allows precise control over robot configuration by updating
    any combination of joint positions, end effector pose, gripper state,
    force/torque readings, or overall status.

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

    Example:
        ```python
        result = await mcp_client.call_tool(
            "update_robot_state", 
            factory_id="factory1", 
            robot_id="robot2",
            end_effector_pose={"x": 450, "y": 0, "z": 1000}
        )
        ```
    """
    logger.info(f"Updating robot state for {robot_id} in factory {factory_id}")
    trace_id = str(uuid.uuid4())

    try:
        key = (factory_id, robot_id)

        if key not in robot_states:
            logger.info(
                f"Initializing new robot state for {factory_id}/{robot_id}")
            robot_states[key] = simulator_provider.get_telemetry()

        current = robot_states[key]

        # Handle the update based on provided fields
        if joint_angles is not None:
            logger.debug(f"Updating joint angles: {joint_angles}")
            current.joint_angles = joint_angles

        if end_effector_pose is not None:
            for field in ["x", "y", "z", "roll", "pitch", "yaw"]:
                if field in end_effector_pose:
                    setattr(current.end_effector_pose,
                            field, end_effector_pose[field])

        if gripper_state is not None:
            if "is_open" in gripper_state:
                current.gripper_state.is_open = GripperOpenState(
                    gripper_state["is_open"])
            if "force" in gripper_state:
                current.gripper_state.force = gripper_state["force"]

        if force_torque is not None:
            for field in ["fx", "fy", "fz", "tx", "ty", "tz"]:
                if field in force_torque:
                    setattr(current.force_torque, field, force_torque[field])

        if status is not None:
            if status not in ["ok", "misaligned", "error"]:
                logger.warning(f"Received invalid status: {status}")
                return create_error_response(
                    error_message=f"Invalid status value. Expected 'ok', 'misaligned', or 'error', got '{status}'",
                    error_code="INVALID_STATUS",
                    factory_id=factory_id,
                    robot_id=robot_id
                )
            current.status = status

        robot_states[key] = current
        logger.info(f"Updated robot {robot_id} state successfully")

        return create_success_response(
            data=current.dict(),
            meta={
                "factory_id": factory_id,
                "robot_id": robot_id,
                "update_type": "state_update",
                "timestamp": current.timestamp.isoformat(),
                "trace_id": trace_id
            }
        )
    except Exception as e:
        logger.error(f"Error updating robot state: {str(e)}")
        return create_error_response(
            error_message=f"Failed to update robot state: {str(e)}",
            error_code="UPDATE_ERROR",
            factory_id=factory_id,
            robot_id=robot_id
        )

# --- Add new capabilities inspired by the article ---


@mcp.tool()
async def list_available_robots() -> Dict[str, Any]:
    """
    List all robots currently available in the system

    Returns:
        Dictionary containing lists of available robots grouped by factory
    """
    logger.info("Listing available robots")

    try:
        # Group robots by factory
        robots_by_factory = {}

        for (factory_id, robot_id) in robot_states.keys():
            if factory_id not in robots_by_factory:
                robots_by_factory[factory_id] = []

            robots_by_factory[factory_id].append(robot_id)

        return create_success_response(
            data={
                "robots": robots_by_factory
            },
            meta={
                "total_count": len(robot_states),
                "factory_count": len(robots_by_factory)
            }
        )
    except Exception as e:
        logger.error(f"Error listing available robots: {str(e)}")
        return create_error_response(
            error_message=f"Failed to list available robots: {str(e)}",
            error_code="LIST_ERROR"
        )

# --- Add example of prompt functionality ---


@mcp.prompt("robot_calibration_instructions")
def get_calibration_prompt() -> Dict[str, Any]:
    """
    Provides standardized instructions for robot calibration procedures

    Returns:
        Structured prompt with calibration instructions
    """
    return {
        "title": "Robot Calibration Procedure",
        "instructions": [
            "1. Ensure the robot is in home position",
            "2. Mark reference points on the workspace",
            "3. Execute the calibration sequence",
            "4. Validate the end effector reaches all reference points",
            "5. Measure and record any deviation"
        ],
        "warning": "Always ensure the robot workspace is clear of obstacles before calibration"
    }

# --- Update the existing endpoints with standardized responses ---


@mcp.resource("server://info")
async def server_info() -> Dict[str, Any]:
    """Return information about the MCP server

    This resource provides metadata about the MCP server capabilities,
    supported features, and current status.

    Returns:
        Server information and metadata
    """
    logger.info("Server info requested")
    return create_success_response(
        data={
            "name": "RAGA Robot Telemetry MCP Server",
            "version": "1.0.0",
            "description": "Provides telemetry data for robotic arms in factory environments",
            "capabilities": [
                "telemetry_streaming",
                "robot_state_updates",
                "calibration_assistance"
            ]
        },
        meta={
            "timestamp": datetime.utcnow().isoformat(),
            "trace_id": str(uuid.uuid4())
        }
    )


@mcp.resource("health://check")
async def health_check() -> Dict[str, Any]:
    """Health check endpoint

    Returns a status report of the MCP server health including active
    robot connections and system metrics.

    Returns:
        Health status information
    """
    logger.info("Health check requested")
    return create_success_response(
        data={
            "status": "healthy",
            "robots_monitored": len(robot_states),
            "uptime_seconds": 3600,  # placeholder value
            "memory_usage_mb": 128,  # placeholder value
        },
        meta={
            "timestamp": datetime.utcnow().isoformat(),
            "trace_id": str(uuid.uuid4())
        }
    )


@mcp.resource("index://")
async def root() -> Dict[str, Any]:
    """Root endpoint that provides basic information and links to other endpoints

    This serves as the entry point for API exploration and discovery.

    Returns:
        Server overview and available endpoints
    """
    logger.info("Root endpoint accessed")
    return create_success_response(
        data={
            "name": "RAGA Robot Telemetry MCP Server",
            "version": "1.0.0",
            "description": "Provides telemetry data for robotic arms in factory environments",
            "endpoints": {
                "server_info": "/server/info",
                "health_check": "/health/check",
                "robot_telemetry": "/robots/{factory_id}/{robot_id}"
            }
        },
        meta={
            "timestamp": datetime.utcnow().isoformat(),
            "trace_id": str(uuid.uuid4())
        }
    )

if __name__ == "__main__":
    logger.info("Starting MCP server on port 8000")
    # Support both HTTP and SSE transport options
    mcp.run(host="0.0.0.0", port=8000, enable_sse=True)
