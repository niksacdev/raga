from pydantic import BaseModel, ConfigDict, Field
from typing import List, Literal, Optional, Any
from datetime import datetime, timezone
from enum import Enum

class TelemetryModel(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)


class EndEffectorPose(TelemetryModel):
    x: float = Field(..., description="X position in millimeters")
    y: float = Field(..., description="Y position in millimeters")
    z: float = Field(..., description="Z position in millimeters")
    roll: float = Field(..., description="Roll angle in degrees")
    pitch: float = Field(..., description="Pitch angle in degrees")
    yaw: float = Field(..., description="Yaw angle in degrees")

class GripperOpenState(int, Enum):
    CLOSED = 0
    OPEN = 1

class GripperState(TelemetryModel):
    is_open: GripperOpenState = Field(..., description="0 for closed, 1 for open")
    force: float = Field(..., ge=0, description="Force applied by gripper in Newtons")

class ForceTorque(TelemetryModel):
    fx: float = Field(..., description="Force along X axis in Newtons")
    fy: float = Field(..., description="Force along Y axis in Newtons")
    fz: float = Field(..., description="Force along Z axis in Newtons")
    tx: float = Field(..., description="Torque around X axis in Newton-meters")
    ty: float = Field(..., description="Torque around Y axis in Newton-meters")
    tz: float = Field(..., description="Torque around Z axis in Newton-meters")

class TelemetryData(TelemetryModel):
    timestamp: datetime = Field(..., description="Timestamp of telemetry reading (ISO8601)")
    joint_angles: List[float] = Field(..., min_length=6, max_length=6, description="List of joint angles in degrees")
    end_effector_pose: EndEffectorPose
    gripper_state: GripperState
    force_torque: ForceTorque
    status: Literal['ok', 'misaligned', 'error'] = Field('ok', description="Overall status of the robot")

class MCPContext(BaseModel):
    user_id: Optional[str] = Field(None, description="ID of the user or operator")
    session_id: Optional[str] = Field(None, description="Session or request ID")
    factory_id: Optional[str] = Field(None, description="Factory or warehouse identifier")
    robot_id: Optional[str] = Field(None, description="Robot identifier")
    location: Optional[str] = Field(None, description="Physical location or zone")
    extra: Optional[dict] = Field(None, description="Additional context as needed")

class MCPEnvelope(BaseModel):
    schema_version: str = Field("1.0", description="Application envelope version, not MCP wire protocol")
    type: str = Field(..., description="Type of message, e.g., 'telemetry', 'state_update'")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Message timestamp")
    trace_id: Optional[str] = Field(None, description="Optional trace or correlation ID")
    source: Optional[str] = Field("mcp_server", description="Source of the message")
    content: Any = Field(..., description="Payload content, e.g., telemetry or state update data")
    context: Optional[MCPContext] = Field(None, description="Contextual metadata for the message")
