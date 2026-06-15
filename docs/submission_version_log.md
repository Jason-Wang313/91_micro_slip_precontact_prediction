# Submission Version Log

## v1 - Generated Draft
- Original continuation-batch generated paper and toy single-seed experiment.

## v2 - Submission Hardening
- Added hostile reviewer attack log and response docs.
- Replaced the toy experiment with seven-seed metrics, stronger baselines, ablations, stress tests, and negative cases.
- Narrowed claims to synthetic diagnostic evidence.
- Recompiled canonical PDF at `C:/Users/wangz/Downloads/91.pdf`.
- Terminal decision: WORKSHOP_ONLY.

## v3 - ICLR Main Gate Archive
- Applied the stricter ICLR-main-conference standard.
- Re-read local paper, docs, experiments, prior-work artifacts, PDF state, and repo state.
- Determined that missing real-robot/high-fidelity evidence, template-generated experiments, and unresolved novelty threats are not recoverable from local artifacts.
- Recompiled the canonical PDF with `Submission-hardening version: v3`.
- Terminal decision: KILL_ARCHIVE.

## v4 - Paper-Specific Micro-Slip Rebuild
- Replaced the generic archive framing with a deterministic tactile/precontact mechanics benchmark.
- Added four tasks, five shifts, nine predictors/controllers, seven seeds, ablations, stress sweep, negative cases, and figures.
- Reported 120,960 main rollouts, 18,816 ablation rollouts, and 56,448 stress rollouts.
- Found that precontact warning improves early recall and control over weak visual thresholding but fails AP, false-alarm, ablation, and stress gates.
- Terminal decision: KILL_ARCHIVE.

## v4.1 - 2026-06-15 Rerun Audit
- Re-ran `python -m py_compile src\run_experiment.py` and the full `python src\run_experiment.py`.
- Confirmed the paired AP difference versus `vision_gap_threshold` is `-0.01608 +/- 0.01821`.
- Confirmed high false-alarm/control cost, ablation contradiction, and maximum-stress AP reversal.
- Updated child docs and paper source to keep the v4 KILL_ARCHIVE decision evidence-bound.
