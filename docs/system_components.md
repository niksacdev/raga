# System Components

---

## Overview

RAGA is composed of modular microservices, cognitive model integrations, and human-in-the-loop interfaces, all working together via structured messaging to assist in robotic arm health monitoring and calibration workflows.

---

## Chat UI

- **Role**: Interface for Factory Operator to monitor system actions and confirm critical decisions.
- **Type**: CLI application initially; expandable to web-based interfaces.
- **Functions**:
  - Enable query and interaction with Human Operator
  - Displays action recommendations.
  - Enables Operator to approve or reject agent-proposed actions.

---

## MCP Server (Model Context Protocol Server)

- **Role**: Simulates telemetry streams that represent real-world robotic operations.
- **Emits**: 
  - Joint angles
  - Force/torque readings
  - End effector pose and orientation
- **Protocols**: ROS2-inspired JSON event structures.
- **Deployment**: FastAPI app deployed as a Kubernetes pod.

---

## Operations Coordinator (Planner)

- **Role**: Central orchestrator that receives goals or telemetry-triggered events.
- **Responsibilities**:
  - Decides which agent(s) to activate based on current context.
  - Manages task decomposition and delegation.
  - Selectively triggers cognitive model queries for reasoning support.
- **Future**: May integrate with Semantic Kernel planners for dynamic, learned orchestration.

---

## Health Monitoring Agent

- **Role**: Ingests telemetry, monitors for pose deviations and gripper misalignments.
- **Responsibilities**:
  - Detects misalignments using threshold and pattern-matching logic.
  - Optionally augments diagnosis via Azure Foundry models.
  - Sends structured alerts to the Operations Coordinator.

---

## Calibration Management Agent

- **Role**: Receives alerts about detected issues, plans recalibration actions.
- **Responsibilities**:
  - Evaluates health reports.
  - Proposes multi-step calibration plans.
  - May query Foundry-hosted LLMs for repair action recommendations.
  - Sends action proposals to the human Supervisor via Chat UI.

---

## Azure AI Foundry Cognitive Models

- **Role**: Provides advanced reasoning assistance when agents require help diagnosing complex failures or planning recalibration tasks.
- **Models**:
  - GPT-4
  - Phi-2
  - Fine-tuned Robotics LLMs (future phases).

---

## A2A Messaging (Agent-to-Agent Protocol)

- **Format**: RESTful structured messaging for agent interaction.
- **Design Principles**:
  - Async-first
  - Versioned schemas
  - No direct internal function calls across agents.