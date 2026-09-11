# Deployment plan

Status: 2026-09-11. Only local stdio execution is implemented and tested. No container build, Kubernetes/AKS deployment, autoscaling or cloud observability stack is provided.

## Supported now: local subprocess

Run `uv sync --locked`, then `uv run --locked python main.py` from the repository root. The client owns a simulator subprocess and cleans it up on exit. Run `uv run --locked python -m src.mcp_server.genericrobotserver` only under an MCP stdio host; it waits for protocol messages rather than presenting a chat interface. Logs go to stderr.

The optional development container is an editor environment, not a production image. Its setup uses the lockfile and forwards no ports. Its image/features still use mutable tags and include third-party features; review those build inputs before use. The devcontainer build is not part of the Python test coverage.

## Future: read-only pilot

Before sharing a service, design authentication, per-resource authorization, TLS, network isolation, request/rate limits, data minimization and retention. Stdio access currently trusts the process owner. Do not infer that changing transport provides those controls. If an MCP host uses cloud models, explicitly approve and redact the telemetry it can transmit.

Add a persistent audit record and measurable service health only when a pilot requires them. Evaluate a simple process/service before adding orchestration infrastructure.

## Deferred: cloud / Kubernetes

Containers, AKS, horizontal scaling, OpenTelemetry exporters and dashboards remain plans. Multi-process deployment would require deliberate state ownership because the current cache is local and ephemeral. Do not deploy the old hypothetical multi-agent diagram as if those services exist.

Physical robot control is a separate scope, requiring equipment-specific safety controls and qualified engineering. Human confirmation in a chat does not substitute for those controls.
