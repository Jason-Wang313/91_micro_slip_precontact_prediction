# Hostile Reviewer Response

Paper: 91 Micro-Slip Precontact Prediction

## Strongest Technical Threats
- Tactile sensor-less fingertip contact detection and force estimation for stable grasping with an under-actuated hand (2024)
- Tactile-Driven Grasp Stability and Slip Prediction (2019)
- A Soft Barometric Tactile Sensor to Simultaneously Localize Contact and Estimate Normal Force With Validation to Detect Slip in a Robotic Gripper (2022)
- Leveraging distributed contact force measurements for slip detection: a physics-based approach enabled by a data-driven tactile sensor (2022)
- Physical model of electrical contact friction for wear failure analysis and prediction of aerospace slip rings (2026)
- Friction coefficient estimation before gross slip for slippage prediction during prosthetic hand grasping (2024)
- A Nonarray Soft Capacitive Tactile Sensor With Simultaneous Contact Force and Location Measurement for Intelligent Robotic Grippers (2023)
- A Novel Incipient Slip Degree Evaluation Method and its Application in Adaptive Control of Grasping Force (n.d.)

## ICLR Main Response
A hostile ICLR reviewer would be correct to reject this as a main-conference submission. The v4 paper has a deterministic tactile/precontact benchmark, seven seeds, strong vision/force/friction/tactile/uncertainty baselines, ablations, stress sweeps, and negative cases. Even so, the proposed method loses average precision to `vision_gap_threshold`, carries high false-alarm/control cost, is contradicted by vision-only and minus-friction ablations, and loses maximum-stress AP to `optical_tactile_classifier`. The paper also lacks robot hardware, accepted high-fidelity tactile simulation, or external tactile dataset validation.

## Honest Action
The paper is marked `KILL_ARCHIVE`. This avoids converting a useful negative audit into an overstated main-conference claim.

## What Would Be Needed To Revive
- Real robot or accepted high-fidelity tactile benchmark experiments.
- External tactile dataset validation.
- Stronger calibration with lower false-alarm/control cost.
- Manual full-paper related-work audit.
- Evidence that precontact micro-slip prediction beats friction-cone, optical-tactile, temporal tactile, and uncertainty baselines without simply over-triggering.
