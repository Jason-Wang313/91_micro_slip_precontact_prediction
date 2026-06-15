# Paper 91 Terminal Audit

Date: 2026-06-15

Paper: `91_micro_slip_precontact_prediction`

Decision: `KILL_ARCHIVE`

## Reproduction

- `python -m py_compile src\run_experiment.py`: passed.
- `python src\run_experiment.py`: passed; log at `logs/91_micro_slip_precontact_prediction_continuation_rerun_20260615.log`.
- PDF target: `C:/Users/wangz/Downloads/91.pdf`.
- Visible Desktop copy: not allowed.

## Evidence Files

- `results/rollouts.csv`: 120,960 rows.
- `results/raw_seed_metrics.csv`: 1,260 rows.
- `results/metrics.csv`: 45 rows.
- `results/pairwise_stats.csv`: 1 row.
- `results/ablation_rollouts.csv`: 18,816 rows.
- `results/ablation_seed_metrics.csv`: 196 rows.
- `results/ablation_metrics.csv`: 7 rows.
- `results/stress_sweep_raw.csv`: 56,448 rows.
- `results/stress_sweep.csv`: 36 rows.
- `results/negative_cases.csv`: 3 rows.

## Key Results

Combined hard shift:

- `proposed_precontact_microslip`: AP `0.75146 +/- 0.02453`, early recall `0.83276`, false-alarm rate `0.81723`, grasp success `0.22619`, gross slip `0.77344`, control cost `0.92853`.
- `vision_gap_threshold`: AP `0.76754 +/- 0.02514`, early recall `0.26130`, false-alarm rate `0.18968`, grasp success `0.04241`.
- `ensemble_uncertainty_guard`: AP `0.74598`, early recall `0.87167`, grasp success `0.24591`.
- Paired AP difference versus `vision_gap_threshold`: `-0.01608 +/- 0.01821`.

Ablation:

- Full method AP: `0.74431`.
- `vision_only_precontact` AP: `0.76620`.
- `minus_friction_prior` AP: `0.76400`.

Maximum combined stress:

- `proposed_precontact_microslip` AP: `0.76101`.
- `optical_tactile_classifier` AP: `0.76949`.
- `ensemble_uncertainty_guard` success: `0.23533`, above the proposed method's `0.20727`.

## Terminal Reason

The local benchmark is useful and reproducible, and precontact warning helps early recall. However, the method fails the AP gate, has excessive false alarms/control cost, is contradicted by ablations, loses a maximum-stress AP comparison, and has no robot hardware or accepted high-fidelity benchmark evidence. The only honest ICLR-main decision is `KILL_ARCHIVE`.

## PDF Verification

- Build command: two-pass `pdflatex -interaction=nonstopmode -halt-on-error main.tex`.
- Canonical PDF: `C:/Users/wangz/Downloads/91.pdf`.
- PDF SHA256: `8B3C2FA0BE5ED710952A0301E095A1ECDB207B829DF57D34D64796F2D3843F54`.
- PDF size: 486,597 bytes.
- LaTeX log scan: no document warnings/errors requiring action after the second pass.
- Desktop copy: absent.
