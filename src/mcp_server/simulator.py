from abc import ABC, abstractmethod
from .models import TelemetryData, EndEffectorPose, GripperState, ForceTorque, GripperOpenState
from datetime import datetime
import random

class TelemetryProvider(ABC):
    @abstractmethod
    def get_telemetry(self) -> TelemetryData:
        pass

class SimulatorTelemetryProvider(TelemetryProvider):
    def __init__(self, num_joints: int = 6):
        self.num_joints = num_joints

    def get_telemetry(self) -> TelemetryData:
        # Simulate joint angles (degrees)
        joint_angles = [random.uniform(-180, 180) for _ in range(self.num_joints)]
        # Simulate end effector pose
        pose = EndEffectorPose(
            x=random.uniform(400, 600),
            y=random.uniform(-100, 100),
            z=random.uniform(800, 1200),
            roll=random.uniform(-180, 180),
            pitch=random.uniform(-90, 90),
            yaw=random.uniform(-180, 180)
        )
        # Simulate gripper state
        gripper = GripperState(
            is_open=random.choice([GripperOpenState.OPEN, GripperOpenState.CLOSED]),
            force=random.uniform(0, 100)
        )
        # Simulate force/torque
        force_torque = ForceTorque(
            fx=random.gauss(0, 2),
            fy=random.gauss(0, 2),
            fz=random.gauss(0, 2),
            tx=random.gauss(0, 0.5),
            ty=random.gauss(0, 0.5),
            tz=random.gauss(0, 0.5)
        )
        # Simulate status
        status = random.choices(['ok', 'misaligned', 'error'], weights=[0.9, 0.08, 0.02])[0]
        return TelemetryData(
            timestamp=datetime.utcnow(),
            joint_angles=joint_angles,
            end_effector_pose=pose,
            gripper_state=gripper,
            force_torque=force_torque,
            status=status
        )
