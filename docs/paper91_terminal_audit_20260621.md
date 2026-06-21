# Paper 91 Terminal Audit 2026-06-21

Terminal action: KILL_ARCHIVE

The v5 expanded-standard run completed the requested plan-first hostile-review protocol for Paper 91. It produced a 27-page manuscript, generated tables and figures, seed-level paired tests, ablations, stress sweeps, fixed-risk checks, negative cases, bright boxed clickable citations, and a validated Downloads-only PDF.

## Validation

- `python -m py_compile src\run_experiment.py`: pass.
- `python src\run_experiment.py`: pass.
- `python scripts\generate_manuscript.py`: pass.
- LaTeX/BibTeX compile: pass.
- `python scripts\validate_submission_artifacts.py`: pass.
- PDF pages: 27.
- PDF SHA256: `8BDFFBECC6B674EC45B269F80A8426D2A6EE1DC0ECA4E469D6FCF8B4F4ECDF6C`.
- Desktop PDF leak: none.

## Decision Rationale

The expanded experiment improves the local evidence base but does not rescue the submission. `calibrated_precontact_microslip_v5` reaches 0.80088 hard-aggregate AP, behind `particle_friction_belief` at 0.80598. Its hard-aggregate task success is 0.32799, behind `recovery_aware_grasp_mpc` at 0.40325. Its robust utility is -0.02258, behind recovery-aware MPC at 0.06676. Its false-alarm rate remains 0.91561, and fixed-risk budget 0.05 coverage is zero on both hard deployment splits.

The result is a useful negative audit: v5 is clearer and stronger than v4, but the evidence still says archive rather than submit.
