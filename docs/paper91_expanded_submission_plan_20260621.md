# Paper 91 Expanded Submission Plan

Date frozen: 2026-06-21

Paper: `91_micro_slip_precontact_prediction`

Target: ICLR-main readiness audit, not cosmetic expansion.

Terminal policy: report `STRONG_REVISE` only if the frozen gates clear after the experiment is run. Otherwise report `KILL_ARCHIVE` honestly.

## Objective

Rebuild Paper 91 into a 25+ page submission-style artifact that tests whether precontact micro-slip prediction is a real mechanism for safer and more successful grasp control, rather than a thresholding artifact that over-triggers.

The v5 method under test is `calibrated_precontact_microslip_v5`: a calibrated, lead-time-aware precontact risk model that combines visual gap cues, approach geometry, precontact shear proxy, friction prior, compliance estimate, sensor-noise calibration, and latency-aware intervention cost.

## Frozen Main Experiment

CPU-only and RAM-light execution:

- Seeds: 10.
- Tasks: 6.
- Splits: 8.
- Methods: 14 total, including oracle.
- Episodes per task/split/method/seed: 32.
- Main rollout rows: 215,040.
- Dataset-summary rows: 15,360.

Tasks:

- `smooth_low_friction_pick`
- `textured_fragile_pick`
- `curved_surface_pinch`
- `compliant_object_lift`
- `thin_edge_pinch`
- `wet_surface_transfer`

Splits:

- `nominal_precontact`
- `low_friction_shift`
- `compliance_shift`
- `sensor_noise_shift`
- `latency_shift`
- `texture_alias_shift`
- `low_signal_high_risk_shift`
- `combined_hard_shift`

Methods:

- `vision_gap_threshold`
- `normal_force_threshold`
- `force_derivative_detector`
- `friction_cone_margin`
- `tactile_temporal_filter`
- `optical_tactile_classifier`
- `ensemble_uncertainty_guard`
- `conformal_precontact_risk`
- `particle_friction_belief`
- `mpc_grip_stabilizer`
- `recovery_aware_grasp_mpc`
- `precontact_microslip_v4`
- `calibrated_precontact_microslip_v5`
- `oracle_precontact_risk`

## Metrics

Prediction metrics:

- Average precision.
- AUROC.
- Expected calibration error.
- Early recall.
- False-alarm rate.
- Lead-time margin.

Closed-loop control metrics:

- Grasp success.
- Gross slip.
- Object damage.
- Intervention cost.
- Control chatter.
- Recovery success.
- Robust utility.

## Frozen Gates

The paper is not submission-ready unless all of these clear:

- Main prediction gate: v5 must beat the strongest non-oracle baseline on hard-aggregate AP, with positive paired lower95.
- Control gate: v5 must beat the strongest non-oracle baseline on hard-aggregate grasp success, with positive paired lower95.
- Safety gate: v5 must not be worse than the safest non-oracle baseline on gross slip plus damage.
- Calibration gate: v5 must beat the strongest non-oracle calibrated baseline on ECE or fixed-risk coverage.
- Burden gate: v5 must not buy success through excessive intervention cost or control chatter.
- Mechanism gate: no removed-component ablation may beat the full v5 method on robust utility.
- Stress gate: v5 must not be dominated at maximum combined stress.
- Fixed-risk gate: v5 must retain nonzero accepted coverage at budget 0.05 on `low_signal_high_risk_shift` and `combined_hard_shift`.
- Scope gate: no ICLR-main claim without real robot, accepted high-fidelity tactile simulation, or external tactile benchmark validation.

## Additional Experiments

Ablations:

- `full_precontact_microslip_v5`
- `minus_precontact_shear`
- `minus_friction_prior`
- `minus_compliance_model`
- `minus_latency_margin`
- `minus_calibration_layer`
- `minus_visual_gap`
- `minus_recovery_model`
- `vision_only_precontact`
- `force_only_precontact`

Stress sweep:

- Six stress levels across friction drop, compliance, occlusion, tactile noise, latency, and texture aliasing.
- Report prediction, control, safety, cost, and utility curves.

Fixed-risk deployment:

- Budgets: 0.00, 0.05, 0.10, 0.15.
- Hard splits: `low_signal_high_risk_shift`, `combined_hard_shift`.
- Report accepted coverage, accepted success, accepted gross slip, accepted damage, and regret.

Negative cases:

- At least 24 generated failure cases across tasks and hard splits.
- Include cases where v5 succeeds, cases where strong baselines succeed and v5 fails, and cases where all non-oracle methods fail.

## Theory To Add

- A lead-time decomposition separating early detection, actionable intervention window, and false-positive burden.
- A calibration lemma connecting fixed-risk thresholds to deployment coverage under bounded ECE.
- A mechanism-identifiability warning: precontact cues can be predictive without proving micro-slip causality.
- A negative theorem: if visual gap, friction prior, and compliance are aliased under shift, no thresholded precontact score can identify slip risk without additional sensing.

## Manuscript Requirements

- Minimum 25 pages, but no filler.
- Bright boxed clickable citations using `hyperref` citation borders.
- Full generated tables for main metrics, hard aggregate, paired tests, ablations, stress, fixed-risk, and negative cases.
- Generated figures for prediction/control tradeoff, false-alarm burden, ablation utility, stress curves, fixed-risk coverage, and Pareto front.
- Explicit terminal decision in abstract, introduction, results, and final audit.
- Canonical PDF must be `C:/Users/wangz/Downloads/91.pdf`.
- Do not copy PDFs to the visible Desktop.

## Verification

Before commit/push:

- `python -m py_compile src\run_experiment.py`
- `python src\run_experiment.py`
- `python scripts\generate_manuscript.py`
- LaTeX/BibTeX compile to `paper/main.pdf`
- Copy final numbered PDF to Downloads only.
- `python scripts\validate_submission_artifacts.py`
- Render PDF pages and visually inspect representative pages.
- Verify no `C:/Users/wangz/Desktop/91.pdf`.
- Commit and push to public GitHub.
- Update `GLOBAL_POOL_STATUS.md`, `BATCH_STATUS.md`, `SUBMISSION_STATUS.md`, `MASTER_REPORT.md`, `MASTER_SUBMISSION_REPORT.md`, and `SUBMISSION_AUDIT_MATRIX.csv`.
