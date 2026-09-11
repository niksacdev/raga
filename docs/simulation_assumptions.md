# Simulation assumptions and limits

Status: 2026-09-11. These distributions describe the code, not measured robot behavior or vendor specifications.

| Field | Implemented distribution |
| --- | --- |
| Six joint angles | Independent uniform samples from −180 to 180 degrees |
| Position X / Y / Z | Uniform 400–600 / −100–100 / 800–1200 mm |
| Roll / pitch / yaw | Uniform −180–180 / −90–90 / −180–180 degrees |
| Gripper | Random open/closed; independent force from 0–100 N |
| Forces fx, fy, fz | Independent Gaussian samples, mean 0, standard deviation 2 N |
| Torques tx, ty, tz | Independent Gaussian samples, mean 0, standard deviation 0.5 Nm |
| Status | Random `ok` / `misaligned` / `error` with probabilities 0.90 / 0.08 / 0.02 |

A first read creates a snapshot. Later reads return the same values and measurement timestamp until an explicit state update. There is no periodic telemetry emission, 2–5-second scheduler, stream, cumulative drift, dropout or abrupt-fault simulation. Pose is uniformly sampled, not Gaussian jitter around a reference. Force/torque standard deviations are absolute values, not percentages.

Joint angles, pose, grip force and status are independent. The simulator has no forward kinematics, coordinate frame, reference pose, collision geometry, payload model or physical sensor. A random status label cannot train or validate a deviation detector. Schema validation does not enforce physical feasibility.

The earlier robot-make tolerance examples were unsourced and have been removed. Repeatability, absolute accuracy and application-specific allowable error are different quantities. The proposed 2 mm / 2° threshold is an experiment parameter only.

Before testing detection, implement seeded scenarios with explicit reference frames, timestamps and independently assigned fault labels; separate normal noise, drift, sudden displacement and stale data. Define how angular wraparound and missing readings are handled. Report dataset composition and false positives as well as recall. Real telemetry sampling rates and tolerances must come from the selected equipment and use case.
