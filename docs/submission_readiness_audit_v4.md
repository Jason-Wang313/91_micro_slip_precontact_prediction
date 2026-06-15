# Submission Readiness Audit v4

Date: 2026-06-15

Paper: 91 Micro-Slip Precontact Prediction

Terminal decision: KILL_ARCHIVE

## Commands Run

```powershell
python -m py_compile src\run_experiment.py
python src\run_experiment.py
```

Both commands completed. The full experiment output was redirected to `logs/91_micro_slip_precontact_prediction_continuation_rerun_20260615.log`.

## Evidence Coverage

- Main rollouts: 120,960 rows.
- Main seed metrics: 1,260 rows.
- Main aggregate metrics: 45 rows.
- Pairwise gate rows: 1 row.
- Ablation rollouts: 18,816 rows.
- Ablation seed metrics: 196 rows.
- Ablation aggregate metrics: 7 rows.
- Stress rollouts: 56,448 rows.
- Stress aggregates: 36 rows.
- Negative cases: 3 rows.
- Seeds: 0, 1, 2, 3, 4, 5, 6.
- Tasks: `smooth_low_friction_pick`, `textured_fragile_pick`, `curved_surface_pinch`, `compliant_object_lift`.
- Splits: `nominal_precontact`, `low_friction_shift`, `compliance_shift`, `sensor_noise_shift`, `combined_hard_shift`.
- Methods: `vision_gap_threshold`, `normal_force_threshold`, `force_derivative_detector`, `friction_cone_margin`, `tactile_temporal_filter`, `optical_tactile_classifier`, `ensemble_uncertainty_guard`, `proposed_precontact_microslip`, `oracle_precontact_risk`.

## Main Gate

On combined hard shift, `proposed_precontact_microslip` reaches AP `0.75146 +/- 0.02453`. The strongest non-oracle AP baseline, `vision_gap_threshold`, reaches AP `0.76754 +/- 0.02514`. The paired AP difference is `-0.01608 +/- 0.01821`, which directly fails the primary gate.

## Contradictory Evidence

- False-alarm rate is `0.81723` for the proposed method.
- Control cost is `0.92853` for the proposed method.
- `vision_only_precontact` reaches AP `0.76620`, above the full method's ablation AP `0.74431`.
- `minus_friction_prior` reaches AP `0.76400`, also above the full method.
- At maximum combined stress, `optical_tactile_classifier` reaches AP `0.76949`, while the proposed method reaches `0.76101`.

## Readiness Judgment

The paper is reproducible as a local negative evidence audit, but not submission-ready for ICLR main. It lacks robot hardware, accepted high-fidelity tactile simulation, external tactile dataset validation, and decisive evidence over strong tactile/physics/uncertainty baselines.

## Terminal Action

Keep `KILL_ARCHIVE`. Do not submit this paper to ICLR main in the current form.
