# Paper 91 Rebuild Plan: Micro-Slip Precontact Prediction

Timestamp: 2026-06-14 14:47:00 +01:00

## Starting Point

Paper 91 is a v3 archive. The original bet is:

> Predict micro-slip risk before stable contact is visually apparent.

The hostile prior-work pressure is strong: tactile-driven grasp stability, slip prediction, sensor-less contact/force estimation, barometric and capacitive tactile sensors, distributed contact-force slip detection, friction estimation before gross slip, GelSight/GelSlim tactile sensing, and adaptive grasp-force control already cover much of the obvious space. A rebuild cannot claim novelty by saying "predict slip" or "use uncertainty." It must show that precontact risk changes closed-loop grasp outcomes before conventional contact/tactile detectors can react.

## Rebuilt Claim Under Test

The strongest defensible claim is:

> A precontact micro-slip model can use visual/tactile-proxy approach dynamics, incipient shear, friction priors, and compliance estimates to warn before stable contact, allowing a controller to adjust approach/grip earlier than contact-threshold or post-contact tactile slip detectors.

This is a local evidence audit, not hardware validation.

## Benchmark Design

I will replace the template success-rate generator with a deterministic tactile/contact mechanics benchmark. Each episode simulates a gripper approaching and grasping an object under hidden friction, compliance, surface texture, approach angle, actuator noise, and sensor noise. The simulator will produce time-indexed precontact signals, future micro-slip labels, risk predictions, and closed-loop control outcomes.

Tasks:

1. `smooth_low_friction_pick`
2. `textured_fragile_pick`
3. `curved_surface_pinch`
4. `compliant_object_lift`

Splits:

1. `nominal_precontact`
2. `low_friction_shift`
3. `compliance_shift`
4. `sensor_noise_shift`
5. `combined_hard_shift`

## Methods To Compare

Strong non-oracle baselines:

1. `vision_gap_threshold`: reacts from visual distance/angle only.
2. `normal_force_threshold`: waits for normal-force rise.
3. `force_derivative_detector`: uses post-contact force derivative.
4. `friction_cone_margin`: physics-style slip-margin estimator.
5. `tactile_temporal_filter`: temporal tactile slip detector.
6. `optical_tactile_classifier`: learned optical-tactile proxy after contact onset.
7. `ensemble_uncertainty_guard`: ensemble risk guard with abstention.
8. `proposed_precontact_microslip`: precontact risk from shear, friction prior, compliance, and latency margin.
9. `oracle_precontact_risk`: upper bound with hidden friction/compliance access.

## Metrics

Prediction metrics:

1. AUROC.
2. Average precision.
3. Early-warning recall at a fixed false-alarm budget.
4. Mean lead time before micro-slip onset.
5. Brier score and calibration error.

Closed-loop metrics:

1. Grasp success.
2. Gross-slip rate.
3. Object damage.
4. Unnecessary grip-tightening false alarms.
5. Control cost.

Statistics:

1. Seven deterministic seeds.
2. Per-task and per-split means with 95 percent confidence intervals.
3. Paired seed/task difference against the strongest non-oracle baseline.
4. Explicit terminal decision in `results/summary.txt`.

## Ablations

The full method must beat its stripped versions:

1. `full_precontact_microslip`
2. `minus_precontact_shear`
3. `minus_friction_prior`
4. `minus_compliance_model`
5. `minus_latency_margin`
6. `vision_only_precontact`
7. `force_only_precontact`

If a stripped method matches or beats full on closed-loop success or average precision without a clear tradeoff, the mechanism is not submission-ready.

## Stress Tests

Stress axes:

1. Friction drop.
2. Compliance variation.
3. Sensor noise.
4. Visual occlusion / poor approach-angle estimate.
5. Actuator lag.
6. Combined maximum stress.

The stress sweep must show whether the proposed method survives where post-contact tactile and friction-margin baselines usually degrade.

## Paper Rewrite Requirements

After experiments:

1. Rewrite `paper/main.tex` as either a strong-revise evidence report or a negative evidence audit.
2. Replace template claims with measured claims only.
3. Include tables for combined hard shift, ablations, and failure cases.
4. Include figures for prediction quality, closed-loop control, calibration/burden, ablations, and stress curves.
5. Update README, child status, and submission-readiness docs.
6. Build only `C:/Users/wangz/Downloads/91.pdf`; do not copy anything to Desktop.
7. Commit and push to `https://github.com/Jason-Wang313/91_micro_slip_precontact_prediction`.

## Terminal Gate

Mark `STRONG_REVISE` only if all of the following are true:

1. `proposed_precontact_microslip` beats the strongest non-oracle baseline on combined-hard-shift average precision and early-warning recall.
2. It also improves closed-loop grasp success or gross-slip rate without excessive false alarms or grip force.
3. Core ablations degrade in the expected directions.
4. The maximum-stress sweep does not reverse in favor of friction-cone, optical-tactile, temporal tactile, or ensemble uncertainty baselines.
5. The paper honestly states the evidence is local/simulated and not real robot validation.

Otherwise mark `KILL_ARCHIVE`. A local predictor that is merely plausible or matched by existing tactile/physics baselines is not ICLR-main ready.
