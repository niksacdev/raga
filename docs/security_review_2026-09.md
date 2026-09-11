# Public repository review — 2026-09-11

Baseline: `b4da453` on `main`. Scope: tracked source/configuration, all fetched branches and tags (10 commits, 41 unique file blobs), implementation/documentation consistency, dependency advisories and selected GitHub security settings. This is a bounded code review, not a penetration test or safety certification. It does not cover deleted/unreachable Git objects, forks, caches, issue attachments, past Actions artifacts or private infrastructure.

## Findings and disposition

| Priority | Finding at baseline | Change / remaining action |
| --- | --- | --- |
| High for reuse | Outdated lockfile: 16 distinct package/advisory pairs across six packages (31 raw audit records include duplicates) | Refresh locked dependencies; remove unused direct FastAPI/Uvicorn dependencies; maintain MCP 1.x with `<2` and a patched minimum. Current local environment: 59 audited packages, no known vulnerabilities reported |
| Medium | Client import caught a nonexistent SDK API import and ran unrestricted `pip install mcp` | Remove import-time installation; use supported SDK `ClientSession` and stdio contexts, explicit locked setup |
| Medium | Server entry point requested `0.0.0.0` with unsupported SDK startup arguments; no auth or tenant isolation existed | Repair as local stdio only. This was unsafe intended configuration, not evidence that the broken entry point actually exposed a listening service |
| Medium | State updated in place before validation; invalid status/gripper could return an error after partial changes; timestamp stayed stale | Validate a merged copy before atomic replacement and timestamp refresh; regression tests preserve existing state and avoid creating records after failed updates |
| Medium | Nested update fields bypassed model validation; cache and identifiers were unbounded | Reject non-finite values, unknown fields, wrong joint counts and invalid gripper values; bound identifiers and cache to 1,000 records |
| Medium for public operation | GitHub secret scanning, push protection, Dependabot security updates and private reporting disabled at inspection | Add SECURITY guidance, dependency audit CI and Dependabot uv/Actions coverage. Maintainer action: enable those repository settings. This PR does not toggle them |
| Low, persistent privacy | A work email is present in historical commit author metadata | Address deliberately not reproduced here. Use a GitHub noreply email for future commits. A PR cannot remove historical exposure; rewriting history would be separate disruptive work and cannot erase copies |
| Low | Exception strings and requested IDs/values could appear in responses/logs | Validation errors no longer echo payloads; application request logging removed. SDK operational logs still exist and real data should not be supplied |
| Misleading capability claims | Claimed streaming, real health metrics and generic physical calibration instructions without implementation/evidence | Identify synthetic cached snapshots, report actual process uptime, remove fabricated memory values, return simulation-only prompt and correct MCP URI index |

Positive findings: no tracked `.env`, private key or customer telemetry dataset was found. A pattern scan across all 41 fetched historical blobs found no matches for private-key blocks, common GitHub/AWS token formats or quoted credential assignments. Manual source/configuration review found no configured model endpoint or credential. These checks can miss uncommon, encoded or context-dependent secrets; they do not establish that no secret has ever existed.

## GitHub controls observed

The repository is public and auto-merge is disabled. The legacy branch-protection endpoint returns “not protected,” but the effective ruleset for `main` includes **pull request**, **non-fast-forward** and **deletion** rules. Thus it would be incorrect to report main as completely unprotected. Required CI checks were not observed in the returned effective rule types; consider making this PR's checks required after they are established.

Secret scanning, non-provider patterns, validity checks, push protection, Dependabot security updates and private vulnerability reporting were disabled. Weekly version-update configuration is distinct from enabling these GitHub security settings. Review and enable the appropriate controls under repository Settings/Security. No settings were changed by this audit.

## Dependency evidence and reproduction

Baseline audit used pinned names/versions extracted from the original lockfile and `pip-audit --no-deps --disable-pip`; this checks declared packages without executing their installation. Six affected packages: click, idna, mcp, pytest, python-dotenv and starlette. Deduplicate on package and advisory ID when comparing counts. Dependency presence is not proof that every vulnerable code path is reachable: several MCP findings concern HTTP/SSE/WebSocket transports absent from the supported stdio entry point.

The MCP findings include [malformed-request handling](https://github.com/modelcontextprotocol/python-sdk/security/advisories/GHSA-3qhf-m339-9g5v), [HTTP session exception handling](https://github.com/modelcontextprotocol/python-sdk/security/advisories/GHSA-j975-95f5-7wqh), [DNS rebinding protection](https://github.com/modelcontextprotocol/python-sdk/security/advisories/GHSA-9h52-p55h-vw2f), [session principal binding](https://github.com/modelcontextprotocol/python-sdk/security/advisories/GHSA-jpw9-pfvf-9f58), and [WebSocket origin checks](https://github.com/modelcontextprotocol/python-sdk/security/advisories/GHSA-vj7q-gjh5-988w). The refreshed lock selects MCP 1.30.0; no vulnerability suppressions were added.

The local package file host was unreachable during setup. A public PyPI mirror was used for download, then all 902 artifact hashes across 64 locked package/version entries were verified against official PyPI JSON metadata. Committed lock URLs point to official PyPI; no mirror configuration is required. The installed environment has fewer packages because the lock also covers other Python/platform combinations.

```bash
uv sync --locked
uv lock --check
uv run --locked pytest -q
uv run --locked python main.py
uv run --locked pip-audit
python -m compileall -q src main.py tests
git diff --check
```

Local Python 3.11 validation: **17 tests passed**, demo completed, compilation and whitespace checks passed, lockfile consistency passed, and the installed-package audit returned no known vulnerabilities. CI adds Python 3.10 and 3.12 runs; consult the PR checks for their actual outcome. This does not test devcontainer builds, network hosting, cloud models or physical hardware.

## Remaining boundary

Stdio trusts the process owner. Any attached client can read/list/update all synthetic records without human approval. Numeric schema validity is not kinematic feasibility. There are no hardware interlocks, calibrated detector, durable audit record, access controls or production deployment. External MCP hosts can transmit data to model providers. Use synthetic data until a specific authorized data-handling and safety design exists.
