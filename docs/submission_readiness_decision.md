# Submission Readiness Decision

Decision: KILL_ARCHIVE

ICLR main-conference readiness: NO.

Paper 91 was rebuilt as a v5 expanded-standard deterministic tactile/precontact audit. The artifact is much stronger than the old draft and meets the requested 25+ page manuscript bar, but the evidence still does not justify an ICLR main submission.

Latest rerun: 2026-06-22 from `src/run_experiment.py`, followed by generated manuscript rebuild and `scripts/validate_submission_artifacts.py`.

Evidence coverage: 215,040 main rollouts, 15,360 dataset-summary rows, 1,120 seed-metric rows, 1,456 aggregate metric rows, 1,248 paired rows, 140 hard-aggregate seed rows, 182 hard-aggregate metric rows, 156 hard-aggregate paired rows, 76,800 ablation rows, 302,400 stress rows, 69,120 fixed-risk rows, and 24 negative cases.

Reasons:

- Hard-aggregate AP is 0.80088 for `calibrated_precontact_microslip_v5` versus 0.80598 for `particle_friction_belief`.
- Hard-aggregate task success is 0.32799 for v5 versus 0.40325 for `recovery_aware_grasp_mpc`.
- Gross slip is worse than the safest reference (0.42383 versus 0.39844).
- Robust utility is worse than `recovery_aware_grasp_mpc` (-0.02258 versus 0.06676).
- False-alarm rate remains extremely high at 0.91561.
- Paired AP lower95 is -0.01806; paired success lower95 is -0.08393.
- Maximum combined stress is dominated by `recovery_aware_grasp_mpc`.
- Fixed-risk budget 0.05 coverage is zero on both hard fixed-risk splits.
- No robot hardware, accepted high-fidelity tactile simulator, trained deployed controller, or external tactile benchmark validation is available.

Honest terminal action: archive/kill for ICLR main. Do not submit this paper to ICLR main in the current form.

Revival condition: real tactile or accepted high-fidelity evidence, calibrated fixed-risk deployment with nonzero strict-budget coverage, and a mechanism that beats particle-friction and recovery-aware MPC baselines without purchasing success through extreme false alarms.
