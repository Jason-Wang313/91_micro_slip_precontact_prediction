# 91 Micro-Slip Precontact Prediction

Submission-hardening version: v5 expanded

Terminal decision: KILL_ARCHIVE for ICLR main conference.

This repository contains a deterministic CPU-only, RAM-light hostile-review audit for the claim that precontact micro-slip prediction can improve robotic grasp control before stable contact is visually apparent. The v5 rebuild expands the old short artifact into a 27-page ICLR-style negative archive manuscript with bright boxed clickable citations, generated tables, full CSV evidence, validation scripts, and a Downloads-only canonical PDF.

## Key Result

The proposed `calibrated_precontact_microslip_v5` improves over `precontact_microslip_v4`, but it is still not submission-ready:

- Hard-aggregate AP: `calibrated_precontact_microslip_v5` 0.80088 versus `particle_friction_belief` 0.80598.
- Hard-aggregate task success: `calibrated_precontact_microslip_v5` 0.32799 versus `recovery_aware_grasp_mpc` 0.40325.
- Gross slip: `calibrated_precontact_microslip_v5` 0.42383 versus `recovery_aware_grasp_mpc` 0.39844.
- Robust utility: `calibrated_precontact_microslip_v5` -0.02258 versus `recovery_aware_grasp_mpc` 0.06676.
- False-alarm rate: `calibrated_precontact_microslip_v5` 0.91561 versus `normal_force_threshold` 0.16578.
- Fixed-risk budget 0.05 coverage: zero on both hard fixed-risk splits.
- Frozen gates: `main_gate=False`, `control_gate=False`, `safety_gate=False`, `calibration_gate=False`, `burden_gate=False`, `stress_gate=False`, `fixed_risk_gate=False`, `scope_gate=False`.

The terminal decision stays `KILL_ARCHIVE`: v5 is stronger and more honest than v4, but the method fails strong-baseline, safety, calibration, burden, stress, fixed-risk, and external-validation gates.

## Evidence Coverage

- Main rollout rows: 215,040.
- Dataset summary rows: 15,360.
- Main seed-metric rows: 1,120.
- Main aggregate metric rows: 1,456.
- Main paired rows: 1,248.
- Hard-aggregate seed rows: 140.
- Hard-aggregate metric rows: 182.
- Hard-aggregate paired rows: 156.
- Ablation rollout rows: 76,800.
- Stress raw rows: 302,400.
- Fixed-risk raw rows: 69,120.
- Negative cases: 24.
- Splits: eight precontact and deployment-stress splits, including `low_signal_high_risk_shift` and `combined_hard_shift`.
- Methods: fourteen predictors/controllers, including optical-tactile, conformal, particle-friction, MPC, recovery-aware MPC, v4, v5, and oracle references.

## Reproduce Evidence

```powershell
python -m py_compile src\run_experiment.py
python src\run_experiment.py
python scripts\generate_manuscript.py
python scripts\validate_submission_artifacts.py
```

## Rebuild PDF

```powershell
cd paper
pdflatex -interaction=nonstopmode -halt-on-error main.tex
bibtex main
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
Copy-Item -LiteralPath main.pdf -Destination C:\Users\wangz\Downloads\91.pdf -Force
```

Canonical local PDF: `C:/Users/wangz/Downloads/91.pdf`

Validated PDF: 27 pages, SHA256 `8BDFFBECC6B674EC45B269F80A8426D2A6EE1DC0ECA4E469D6FCF8B4F4ECDF6C`.

No PDF should be copied to the visible Desktop.
