# System Capability Evolution

---

## Overview

RAGA evolves in controlled phases, each tied to validating core hypotheses about telemetry ingestion, cognitive augmentation, and multi-agent coordination.

---

## Phase 1: MCP Telemetry + Single Agent

- Deploy MCP Server.
- Launch Health Monitoring Agent.
- Validate telemetry ingestion and pose deviation detection.
- Confirm human-in-the-loop alerting via CLI Chat UI.

---

## Phase 2: Cognitive Augmentation

- Integrate Azure AI Foundry models.
- Enable Health Monitoring and Calibration Manager Agents to use LLMs selectively.
- Validate improvement in diagnosis quality and plan generation speed.

---

## Phase 3: Agent-to-Agent (A2A) Dynamic Collaboration

- Implement A2A messaging contracts.
- Health Monitoring Agent triggers Calibration Manager autonomously.
- Validate dynamic task delegation and collaborative workflows.

---

## Phase 4: Real Robotic Telemetry Integration

- Replace synthetic MCP telemetry with ROS2 topic ingestion.
- Handle real-world noise, packet loss, and telemetry delay.
- Measure ingestion throughput and agent reactivity.

---

## Phase 5: Fine-Tuned LLM Reasoning

- Train domain-specific calibration LLMs using simulation + real-world operational data.
- Replace generic GPT models for Robotics-specific cognition.
- Validate improved action plan precision and operator satisfaction scores.