# Deployment Evolution Plan

---

## Overview

RAGA deployment is staged for scalable growth from local development clusters to full enterprise-ready cloud deployments.

---

## Phase 1: Local Kubernetes Deployment

- Use Minikube, Kind, or k3d.
- Deploy MCP Server, Operations Coordinator, Agents, Chat UI as separate pods.
- Local A2A communication via Kubernetes Services.

---

## Phase 2: Azure Kubernetes Service (AKS)

- Full cloud-native microservice scaling.
- Horizontal Pod Autoscaling (HPA) for agents.
- Azure Monitor and OpenTelemetry for system observability.

---

## Phase 4: Advanced Observability and AI Agent Services (Stretch)

- Ingest OpenTelemetry traces.
- Setup dashboards tracking:
  - MCP telemetry ingestion rates
  - Pose deviation detection accuracy
  - Cognitive query latencies
- (Optional) Explore Azure AI Agent Service to offload dynamic reasoning orchestration.