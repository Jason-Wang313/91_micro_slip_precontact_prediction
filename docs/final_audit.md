# Final Audit

1. Chosen thesis: Micro-Slip Precontact Prediction explores `Predict micro-slip risk before stable contact is visually apparent.` for tactile and force prediction.
2. Rebuild version: v5 expanded-standard deterministic tactile/precontact evidence audit.
3. ICLR-main decision: KILL_ARCHIVE.
4. Reason: `calibrated_precontact_microslip_v5` improves over v4 but fails frozen hostile-review gates against particle-friction, recovery-aware MPC, low-burden thresholding, stress, fixed-risk, and external-validation requirements.
5. Closest hostile prior work: see `docs/hostile_prior_work.md`, `docs/hostile_prior_work_100_cards.csv`, `docs/hostile_reviewer_response.md`, and the generated 160-reference bibliography in `paper/references.bib`.
6. Reproducibility: `python -m py_compile src\run_experiment.py`, `python src\run_experiment.py`, `python scripts\generate_manuscript.py`, LaTeX/BibTeX compilation, and `python scripts\validate_submission_artifacts.py` completed on 2026-06-22.
7. Claim-validity status: precontact warning is diagnostically useful, but the paper is not a submission-ready robotics contribution.
8. Evidence coverage: 215,040 main rollouts, 15,360 dataset-summary rows, 1,120 seed-metric rows, 1,456 aggregate metric rows, 1,248 paired rows, 140 hard-aggregate seed rows, 182 hard-aggregate metric rows, 156 hard-aggregate paired rows, 76,800 ablation rows, 302,400 stress rows, 69,120 fixed-risk rows, and 24 negative cases.
9. Prediction result: hard-aggregate `calibrated_precontact_microslip_v5` AP `0.80088` versus `0.80598` for `particle_friction_belief`; paired AP lower95 `-0.01806`.
10. Control result: hard-aggregate success `0.32799` versus `0.40325` for `recovery_aware_grasp_mpc`; paired success lower95 `-0.08393`.
11. Safety result: gross slip `0.42383` versus `0.39844` for `recovery_aware_grasp_mpc`; paired gross-slip upper95 `0.04221`.
12. Burden result: false-alarm rate `0.91561` versus `0.16578` for `normal_force_threshold`; intervention cost `0.33957` versus `0.07896`.
13. Mechanism result: full v5 is the best ablation by robust utility, but this does not rescue the paper because external strong baselines dominate.
14. Stress result: maximum combined stress is dominated by `recovery_aware_grasp_mpc`; `stress_gate=False`.
15. Fixed-risk result: budget 0.05 coverage is zero on both hard fixed-risk splits; `fixed_risk_gate=False`.
16. Exact Downloads PDF path: `C:/Users/wangz/Downloads/91.pdf`
17. PDF validation: 27 pages, SHA256 `8BDFFBECC6B674EC45B269F80A8426D2A6EE1DC0ECA4E469D6FCF8B4F4ECDF6C`, bright boxed internal citation links validated.
18. GitHub URL: https://github.com/Jason-Wang313/91_micro_slip_precontact_prediction
19. Confirmation: no visible Desktop copy was requested or made.
