# Simulation Assumptions and Realism

---

## Overview

The RAGA MCP Server simulates robotic telemetry streams to validate agent ingestion and reasoning workflows before connecting to physical robots. The goal is to minimize the "sim-to-real" gap while keeping sample complexity manageable.

---

## Pose and Gripper Deviation Simulation

- **End Effector Pose Deviation**:  
  Simulated deviation in Tool Center Point (TCP) position and orientation (ΔX, ΔY, ΔZ, ΔRoll, ΔPitch, ΔYaw).

- **Gripper Misalignment**:  
  Errors in gripper positioning and orientation detected through pose deviation analysis.

- **Variation Across Robot Makes**:  
  - Universal Robots (UR): ±0.1mm to 0.5mm tolerance.  
  - KUKA Robots: ±0.05mm for high-precision tasks.  
  - ABB Robots: Tolerances vary based on payload and configuration.

**Note**: Robot-specific noise and tolerance variations are abstracted for simplicity but flagged for future simulation fidelity improvements.

---

## Force/Torque Reading Simulation

- **Force and Torque Drift**:  
  Minor drift introduced into force/torque readings to simulate normal mechanical and sensor deviations.

- **Gaussian Noise Injection**:
  - Force readings: ~±2% random noise.
  - Torque readings: ~±1% random noise.
  - Pose deviation: ~±1mm random jitter.

This mimics real-world sensor inaccuracies.

---

## Telemetry Update Rate

- **Simplification for Phase 1**:  
  MCP Server emits telemetry events every 2–5 seconds to simplify development and monitoring.

- **Real-World Reference**:  
  Robotic telemetry typically operates between 10Hz to 100Hz depending on control precision requirements.

- **Future Work**:  
  Later phases will incorporate higher telemetry update frequencies and buffered ingestion.

---

## Simulated Failure Modes

- **Pose Drift Accumulation**:  
  Gradual increase in pose error simulating mechanical fatigue or environmental impact.

- **Sudden Misalignment Jumps**:  
  Random larger pose shifts simulating fixture slippage, sudden external forces, or sensor shock.

- **Sensor Noise and Dropout**:  
  Gaussian noise is present consistently; future work can simulate occasional packet loss or out-of-order events.
