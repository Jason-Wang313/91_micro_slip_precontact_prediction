# 91 Micro-Slip Precontact Prediction

Submission-hardening version: v4

Terminal decision: KILL_ARCHIVE for ICLR main conference.

This repository now contains a deterministic tactile/precontact mechanics evidence audit for the claim that micro-slip can be predicted before stable contact and used to improve grasp control. The rebuilt benchmark includes four tasks, five shifts, seven seeds, nine predictors/controllers, seven ablations, and a stress sweep.

Latest audited rerun: 2026-06-15. The source experiment compiled and regenerated the CSVs, figures, gate checks, and summary from `src/run_experiment.py`; the successful full rerun output is logged at `logs/91_micro_slip_precontact_prediction_continuation_rerun_20260615.log`.

## Key Result

On combined hard shift:

- Proposed precontact model: AP 0.751, early recall 0.833, false-alarm rate 0.817, grasp success 0.226.
- Vision threshold baseline: AP 0.768, early recall 0.261, false-alarm rate 0.190, grasp success 0.042.
- Ensemble uncertainty guard: AP 0.746, early recall 0.872, false-alarm rate 0.850, grasp success 0.246.
- Paired AP difference vs strongest non-oracle AP baseline: -0.016 +/- 0.018.

The proposed method improves early warning and closed-loop success over weak visual thresholding, but it fails the ICLR-main gate because it does not win average precision, has high false alarms/control cost, and is contradicted by ablations. Vision-only and minus-friction ablations beat the full method on AP.

## Evidence Coverage

- Main rollouts: 120,960 rows.
- Ablation rollouts: 18,816 rows.
- Stress rollouts: 56,448 rows.
- Seeds: 0 through 6.
- Splits: `nominal_precontact`, `low_friction_shift`, `compliance_shift`, `sensor_noise_shift`, `combined_hard_shift`.
- Tasks: `smooth_low_friction_pick`, `textured_fragile_pick`, `curved_surface_pinch`, `compliant_object_lift`.
- Terminal gate: `KILL_ARCHIVE`, because the evidence supports a reproducible negative audit, not an ICLR-main submission.

## Reproduce Evidence

```powershell
python src\run_experiment.py
```

## Rebuild PDF

```powershell
cd paper
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
```

Canonical local PDF: `C:/Users/wangz/Downloads/91.pdf`

No PDF should be copied to the visible Desktop.
