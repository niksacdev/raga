# Physical AI and RAGA's value proposition

Assessment date: **2026-09-11**. Sources below were checked on that date. Vendor announcements describe capabilities and availability, not independently verified factory performance or RAGA customer demand.

## Baseline and what changed

Git history places RAGA's initial implementation in April–May 2025, about 16 months ago. The requested seven-month comparison starts around February 2026. Both matter: the original idea predates several major advances, while recent changes further raise the bar for general robotics intelligence.

| Evidence and date | Change relevant to RAGA | Interpretation for this project |
| --- | --- | --- |
| [Gemini Robotics research, March 2025](https://arxiv.org/abs/2503.20020) | Vision-language-action and embodied reasoning already existed at the repo's inception | LLM-connected robotics was not itself a unique proposition even at the original baseline |
| [Intrinsic joins Google, February 25, 2026](https://blog.google/alphabet/intrinsic-joins-google/) | Industrial robotics software is being brought closer to Google's AI and cloud capabilities | Generic orchestration faces better-resourced platform competition; evaluate integration opportunities |
| [NVIDIA open models, March 16, 2026](https://nvidianews.nvidia.com/news/nvidia-expands-open-model-families-to-power-the-next-wave-of-agentic-physical-and-healthcare-ai) | Announcement includes GR00T N1.7 and Cosmos 3; GR00T N2 was previewed | Model and simulation infrastructure are expanding; a preview is not proof of deployable production capability |
| [Gemini Robotics 2, July 30, 2026](https://deepmind.google/blog/gemini-robotics-2-brings-whole-body-intelligence-to-robots/) | Whole-body control, dexterity and multi-robot collaboration are vendor-reported capabilities | General intelligence and coordination are a weak differentiation strategy for this repo |
| [Gemini Robotics 2 model page, checked September 11, 2026](https://deepmind.google/models/gemini-robotics/vla/) | The VLA model is listed as private preview | Do not assume all announced robotics models are generally available or interchangeable APIs |
| [Intrinsic Flowstate, checked September 11, 2026](https://www.intrinsic.ai/flowstate) | Platform covers workcell design, reusable skills, behavior trees, pose estimation, simulation and transfer to hardware | A small project should not promise a competing full industrial automation stack |

Demand for industrial robotics remains substantial: the [IFR's September 25, 2025 report](https://ifr.org/ifr-press-releases/global-robot-demand-in-factories-doubles-over-10-years) reports 542,000 installations in **2024** and 4.664 million robots operating globally. These are historical industrial-robot figures, not 2026 sales, an AI-software market size, or proof that buyers want RAGA. No revenue/TAM estimate or customer validation is established here.

## Assessment: retain the problem, narrow the proposed product

**Inference:** operator fault diagnosis remains a plausible problem, but “multi-agent Physical AI over MCP” is insufficient differentiation. RAGA currently has neither the models/data of a foundation-model effort nor the hardware integration and operational tooling of an industrial platform. Its simulated random status cannot demonstrate diagnostic quality.

The more defensible hypothesis is an **evidence-grounded operator diagnostic assistant** for one fault family: combine timestamped telemetry, a reference state and approved maintenance information; explain what supports a diagnosis, what is missing and when to abstain. Keep deterministic detection and equipment safety controls separate from language-model suggestions. Preserve human responsibility through an actual review workflow, not a sentence in a prompt.

Potential value would come from representative fault data, reproducible evaluation, useful integration with existing maintenance workflows and a trustworthy decision record. None exists yet. MCP can provide a model-facing adapter; it is not the real-time robot-control loop. A2A should follow a demonstrated deployment/ownership need. Fine-tuning and Kubernetes are premature before data and operator benefit are established.

## Recommended next experiment

Spend two weeks on one labeled replay/simulation dataset, a deterministic baseline and an evidence report. Compare rules-only versus optional LLM-assisted diagnosis using identical evidence and blinded scoring. Track false alarms, harmful recommendations, abstention, latency, cost and operator decision quality. Speak with 3–5 maintenance/integration practitioners about an actual recurring fault and the information they need.

Continue only with a repeated workflow problem and a measurable benefit beyond rules. Stop or reframe if data access is infeasible, the assistant adds explanation without improving decisions, or the benefit requires autonomous calibration claims that cannot be validated. RAGA remains useful as a learning/evaluation scaffold even if that commercial hypothesis fails. See the [roadmap](capability_evolution.md) for implementation gates.
