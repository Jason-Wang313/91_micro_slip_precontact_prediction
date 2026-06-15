# Paper 91 ICLR-Main Submission-Readiness Execution Plan

Date: 2026-06-15

Paper: `91_micro_slip_precontact_prediction`

Target venue standard: ICLR main conference, evidence-first. The paper can advance only if precontact micro-slip prediction beats strong vision, force-threshold, friction-cone, tactile-temporal, optical-tactile, ensemble-uncertainty, and oracle baselines on both prediction quality and closed-loop grasp control. Early-warning recall alone is not enough if average precision, false alarms, or control cost fail.

## Current State

The repository currently reports a v4 terminal decision of `KILL_ARCHIVE`. The prior v4 evidence found a real early-warning and grasp-success improvement over weak visual thresholding, but the proposed method loses the average-precision gate to `vision_gap_threshold`, has high false alarms and control cost, is contradicted by vision-only and minus-friction ablations, and loses maximum-stress AP to an optical-tactile baseline.

## Execution Order

1. Verify repository hygiene before touching evidence.
   - Confirm worktree status.
   - Record current commit and remote.
   - Confirm the existing Downloads PDF and Desktop exclusion state.

2. Re-run the evidence generator from source.
   - Compile-check `src/run_experiment.py`.
   - Run `python src/run_experiment.py`.
   - Preserve generated CSVs, figures, summary, and terminal gate checks.

3. Audit evidence completeness.
   - Confirm seven seeds.
   - Confirm all tasks, shifts, predictors/controllers, ablations, stress levels, pairwise stats, and negative cases.
   - Confirm row counts and schemas for rollout, seed-level, aggregate, pairwise, ablation, stress, and negative-case outputs.

4. Apply the ICLR-main decision gate.
   - Require the proposed method to beat the strongest non-oracle baseline on combined-hard-shift average precision with paired uncertainty.
   - Require early-warning recall and closed-loop grasp success/gross-slip improvement without excessive false alarms or control cost.
   - Require ablations to degrade when precontact shear, friction prior, compliance model, and latency margin are removed.
   - Require stress tests to avoid reversal against friction-cone, optical-tactile, tactile-temporal, or ensemble uncertainty baselines.

5. Decide honestly.
   - If all local gates pass but evidence remains local synthetic only, mark at most `STRONG_REVISE`.
   - If average precision, false-alarm, cost, ablation, or stress gates fail, preserve `KILL_ARCHIVE`.
   - Do not claim ICLR-main readiness without robot hardware, accepted high-fidelity tactile simulation, or external tactile dataset validation.

6. Update child documentation and paper.
   - Align `README.md`, `child_status.md`, `plan.md`, readiness decision, final audit, hostile reviewer response, attack log, version log, and checklists with the rerun.
   - Add terminal audit docs with exact row counts, seed coverage, metric conclusions, PDF hash, and artifact-location checks.

7. Build and verify the PDF.
   - Build `paper/main.pdf` twice with LaTeX.
   - Copy only to `C:/Users/wangz/Downloads/91.pdf`.
   - Do not copy any PDF to the visible Desktop.
   - Scan the LaTeX log for warnings or errors that affect quality.

8. Update root ledgers.
   - Update `GLOBAL_POOL_STATUS.md`, `BATCH_STATUS.md`, `SUBMISSION_STATUS.md`, `MASTER_REPORT.md`, and `MASTER_SUBMISSION_REPORT.md`.

9. Commit, push, and verify.
   - Commit only Paper 91 child-repo files inside its repo.
   - Push `main` to the public GitHub repo.
   - Verify local `HEAD` equals `origin/main`.
   - Verify `C:/Users/wangz/Downloads/91.pdf` exists and `C:/Users/wangz/Desktop/91.pdf` does not.

## Expected Outcome Risk

The likely terminal decision is `KILL_ARCHIVE`. The previous v4 evidence reports AP loss versus `vision_gap_threshold`, excessive false alarms/control cost, ablation contradiction, and maximum-stress reversal. The rerun will still be performed end-to-end, and the final decision will be evidence-bound.
