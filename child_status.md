# Child Status 91

Current stage: expanded-standard v5 terminal audit
Last update: 2026-06-22 03:56:49 +08:00
PDF: C:/Users/wangz/Downloads/91.pdf
PDF SHA256: 8BDFFBECC6B674EC45B269F80A8426D2A6EE1DC0ECA4E469D6FCF8B4F4ECDF6C
PDF pages: 27
GitHub: https://github.com/Jason-Wang313/91_micro_slip_precontact_prediction
Submission-hardening version: v5 expanded
Terminal decision: KILL_ARCHIVE
ICLR main ready: no

Latest rerun: `python -m py_compile src\run_experiment.py`, full `python src\run_experiment.py`, `python scripts\generate_manuscript.py`, LaTeX/BibTeX compilation, and `python scripts\validate_submission_artifacts.py` completed on 2026-06-22.

Evidence inventory: 215,040 main rollouts, 15,360 dataset-summary rows, 1,120 seed-metric rows, 1,456 aggregate metric rows, 1,248 paired rows, 140 hard-aggregate seed rows, 182 hard-aggregate metric rows, 156 hard-aggregate paired rows, 76,800 ablation rows, 302,400 stress rows, 69,120 fixed-risk rows, and 24 negative cases.

Reason: `calibrated_precontact_microslip_v5` improves over v4 but remains dominated under the frozen hostile-review gates. It reaches 0.80088 hard-aggregate AP versus 0.80598 for `particle_friction_belief`, 0.32799 hard-aggregate success versus 0.40325 for `recovery_aware_grasp_mpc`, worse gross slip than recovery-aware MPC (0.42383 versus 0.39844), worse robust utility (-0.02258 versus 0.06676), a very high false-alarm rate (0.91561), and zero fixed-risk coverage at budget 0.05 on both hard fixed-risk splits. No robot hardware or accepted high-fidelity tactile simulator validation is available.
