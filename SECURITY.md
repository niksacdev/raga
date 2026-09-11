# Security and privacy

RAGA is an experimental **local, synthetic-data simulator**. It is not a robot controller, multi-tenant service or production safety system.

## Supported boundary

- Use the documented stdio entry point. It opens no network listener. Access is trusted to the local process owner; there is no application authentication.
- All robot state is synthetic and stored in process memory. The update tool has no human approval gate and never actuates hardware.
- Factory/robot IDs do not isolate users. Any client attached to a process can read/list/update its snapshots.
- An external MCP host may forward resources, tools and prompts to its model provider. Do not supply customer telemetry, real site identifiers, credentials or personal information without an approved data-handling design.
- The calibration prompt is a simulation exercise. Physical calibration requires equipment-specific procedures and qualified engineering.

## Development

Use `uv sync --locked` and review dependency changes. No package installation occurs during application import. `uv run --locked pip-audit` checks installed packages against published advisories; repeat it because findings change. CI runs tests and dependency audits, and Dependabot proposes updates. The devcontainer uses mutable image/feature tags, including third-party features; review them before building.

Keep `.env*`, private keys and operational datasets out of Git. Ignore rules are guardrails, not a secret scanner. Git history, forks and caches can retain deleted information. If a credential is exposed, revoke/rotate it first; deleting it in a PR does not revoke it. Choose a GitHub noreply commit email if you do not want a work/personal email attached to future public commits.

## Reporting

Do not post secrets, sensitive telemetry or exploitable details in public issues. Use GitHub's private “Report a vulnerability” option on this repository's Security page **if enabled**; otherwise contact the maintainer through an existing private channel and request a private reporting route. This document does not assert that private reporting or secret protection has been enabled.

See [the dated review](docs/security_review_2026-09.md) for scope, fixed issues and remaining limitations. No production support or security certification is implied.
