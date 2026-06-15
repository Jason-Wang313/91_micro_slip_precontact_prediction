# Child Status 91

Current stage: ICLR main v4 evidence audit terminal
Last update: 2026-06-15 11:35:10 +01:00
PDF: C:/Users/wangz/Downloads/91.pdf
GitHub: https://github.com/Jason-Wang313/91_micro_slip_precontact_prediction
Submission-hardening version: v4
Terminal decision: KILL_ARCHIVE
ICLR main ready: no

Latest rerun: `python -m py_compile src\run_experiment.py` and full `python src\run_experiment.py` completed on 2026-06-15 with output redirected to `logs/91_micro_slip_precontact_prediction_continuation_rerun_20260615.log`.

Evidence inventory: 120,960 main rollouts, 18,816 ablation rollouts, 56,448 stress rollouts, seven seeds, four tasks, five precontact shifts, nine predictors/controllers, seven ablations, six stress levels, and three negative cases.

Reason: deterministic tactile/precontact benchmark added and rerun. The proposed method improves early warning and control over weak visual thresholding, but loses the average-precision gate to a vision threshold (`0.75146` vs `0.76754`; paired AP difference `-0.01608 +/- 0.01821`), has high false alarms/control cost, and is contradicted by vision-only and minus-friction ablations. No robot hardware or accepted high-fidelity tactile simulator validation is available.
