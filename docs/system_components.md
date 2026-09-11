# System components

Status: 2026-09-11. This is a local simulator with an MCP client, not a deployed multi-agent system.

| Component | Implementation | Boundary |
| --- | --- | --- |
| Telemetry generator | `src/mcp_server/simulator.py` | Random six-joint snapshots; no dynamics or ground truth |
| Data models | `src/mcp_server/models.py` | Finite numeric values, six joints, known fields; schema validity does not mean physically valid pose |
| MCP server | `src/mcp_server/genericrobotserver.py` | Stdio only in the supported entry point; bounded process-local cache |
| MCP client/demo | `src/mcp_client/client.py`, `main.py` | SDK session initialization, resources, tools, prompt, automatic process cleanup |
| Tests | `tests/` | Atomic updates and real subprocess protocol round trip |

## MCP interface

- `server://info`: simulator identity and actual capabilities.
- `health://check`: process uptime and snapshot count; no invented memory/connection metrics.
- `index://`: MCP resource URIs, not HTTP endpoint paths.
- `robots://{factory_id}/{robot_id}`: generate once on first access, then read the cached snapshot.
- `update_robot_state`: validate a merged copy before replacing the snapshot; refresh its UTC timestamp. This edits synthetic data, not hardware.
- `list_available_robots`: list every snapshot in this process. Factory IDs do not provide tenant separation.
- `robot_calibration_instructions`: simulation-only analysis prompt, not manufacturer calibration instructions.

IDs allow 1–64 ASCII letters, digits, underscores and hyphens. There are at most 1,000 snapshots per process; restart to clear them. Unknown nested update fields and non-finite values are rejected. Joint/pose consistency, workspace limits and collision checking are not implemented.

`MCPContext` and `MCPEnvelope` are unused application schema sketches. Their schema version does not describe the MCP wire protocol, which is negotiated by the SDK.

## Proposed components — not implemented

A monitoring agent would compare timestamped, framed telemetry to reference data. A diagnostic assistant would cite evidence and uncertainty. An operator UI would record review decisions. A calibration manager would propose actions only after a separate safety and authorization design. A coordinator/A2A layer would be justified by independently deployed responsibilities, not agent count alone.

There is currently no LLM provider, Azure integration, chat UI, persistent audit record, REST/A2A contract, ROS 2 adapter, robot driver or Kubernetes manifest. See the [roadmap](capability_evolution.md).
