# Capability roadmap and experiment gates

Status: 2026-09-11. **Phase 1 is partial; no hypothesis has a reported empirical result.** Proposed targets below are acceptance criteria to agree before running experiments, not performance claims.

## Phase 1 — telemetry and deterministic detection (partial)

Completed: synthetic snapshots, MCP resource/tool discovery and calls, local demo, atomic update validation, state bounds and regression tests.

Missing: reference pose and coordinate frames, reproducible labeled time series, monitoring loop, deviation detector, evaluation report, supervisor alerting.

Next gate:

1. Generate seeded normal, noisy, drifting, abrupt-fault and stale-data fixtures with labels independent of the detector; reserve held-out seeds/scenarios.
2. Compare a simple position/orientation detector against these labels. Original target: at least 90% recall above 2 mm / 2°. Proposed accompanying gate: at most 5% false positives on normal samples. Define boundary cases and angular wraparound, sample count and confidence intervals.
3. Check schema round trips, timestamps and stale-data handling. Record per-scenario errors; passing synthetic fixtures is not evidence of real-world calibration accuracy.
4. Add a read-only alert view. No actuator integration is needed to evaluate this phase.

## Phase 2 — diagnostic assistance and operator review (planned)

Build an evidence packet from a snapshot history, alarm history and approved maintenance references. Compare rules alone with the same rules/evidence plus an optional LLM, blind to labels.

Original hypotheses: 15–30% diagnosis accuracy improvement, response within 3 seconds and over 80% operator preference. Before testing, specify whether improvement is relative or percentage points, score with a fixed rubric, define latency percentile, and recruit qualified reviewers. Also measure unsupported/unsafe recommendations, abstention and cost. A prompt alone does not implement approval or a safety boundary.

Add a review UI and durable decision log only with defined retention, redaction, identity and authorization. No cloud telemetry upload by default. Continue only if the assistant improves evidence-grounded decisions without worsening harmful recommendations.

## Phase 3 — distributed coordination / A2A (planned, conditional)

First establish a single-process orchestration baseline. Add A2A only if separate ownership, deployment or long-running tasks justify it. Select a concrete protocol version; test cancellation, duplicate delivery, timeouts, recovery and authorization. Require a demonstrated workflow benefit versus baseline. Messaging alone does not validate diagnostic quality.

## Phase 4 — read-only real telemetry (planned)

With authorized, sanitized data, implement a ROS 2 or vendor adapter and preserve timestamps, units and frames. Evaluate stale/out-of-order data, dropout, schema mapping and end-to-end latency at the equipment's actual sample rate. Hardware control remains outside the current project boundary; it needs a separate engineering and safety review.

## Phase 5 — model adaptation (deferred)

Consider domain tuning only after a lawful, representative dataset and a held-out baseline show that retrieval, rules and general models are insufficient. Record rights, provenance, leakage checks, uncertainty and operator outcomes. Do not train on the current independent random status labels.

## Bounded value-proposition experiment

Proposed next investment: a two-week simulator/replay experiment, one fault family, a deterministic baseline and an operator-facing evidence report. Seek feedback from 3–5 maintenance/integration practitioners before platform expansion. Continue if the workflow exposes a repeated diagnosis bottleneck and improves a predefined decision metric. Stop or reframe if rules alone suffice, usable labeled data is unavailable, or the value depends on unsupported claims about autonomous calibration. See the [market assessment](market_assessment_2026-09.md).
