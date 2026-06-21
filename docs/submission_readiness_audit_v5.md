# Paper 91 Submission Readiness Audit v5

Date: 2026-06-22

Decision: KILL_ARCHIVE

ICLR main ready: no

## Artifact

- Canonical PDF: `C:/Users/wangz/Downloads/91.pdf`
- Pages: 27
- SHA256: `8BDFFBECC6B674EC45B269F80A8426D2A6EE1DC0ECA4E469D6FCF8B4F4ECDF6C`
- Citation UX: bright boxed clickable internal citation links.
- Desktop policy: no visible Desktop PDF copy.

## Evidence Inventory

- Main rollout rows: 215,040.
- Dataset summary rows: 15,360.
- Main seed-metric rows: 1,120.
- Main metric rows: 1,456.
- Main pairwise rows: 1,248.
- Hard aggregate seed rows: 140.
- Hard aggregate metric rows: 182.
- Hard aggregate pairwise rows: 156.
- Ablation rollout rows: 76,800.
- Ablation seed rows: 100.
- Ablation metric rows: 130.
- Stress raw rows: 302,400.
- Stress seed rows: 840.
- Stress metric rows: 1,092.
- Fixed-risk raw rows: 69,120.
- Fixed-risk seed rows: 480.
- Fixed-risk metric rows: 288.
- Fixed-risk pairwise rows: 240.
- Negative cases: 24.

## Frozen Gate Result

- Best AP reference: `particle_friction_belief`.
- Best success reference: `recovery_aware_grasp_mpc`.
- Safest reference: `recovery_aware_grasp_mpc`.
- Best utility reference: `recovery_aware_grasp_mpc`.
- Proposed AP: 0.80088 versus best AP 0.80598.
- Proposed success: 0.32799 versus best success 0.40325.
- Proposed gross slip: 0.42383 versus safest gross slip 0.39844.
- Proposed false alarm: 0.91561 versus lowest false alarm 0.16578.
- Proposed cost: 0.33957 versus lowest cost 0.07896.
- Proposed utility: -0.02258 versus best utility 0.06676.
- Paired AP lower95: -0.01806.
- Paired success lower95: -0.08393.
- Paired gross-slip upper95: 0.04221.
- Main gate: false.
- Control gate: false.
- Safety gate: false.
- Calibration gate: false.
- Burden gate: false.
- Stress gate: false.
- Fixed-risk gate: false.
- Scope gate: false.

## Why The Paper Is Not Submission Ready

`calibrated_precontact_microslip_v5` is scientifically more defensible than v4, but it does not survive hostile review. Particle-friction belief wins AP, recovery-aware grasp MPC wins success, safety, and robust utility, and v5 still relies on a very high false-alarm rate. Fixed-risk coverage at budget 0.05 is zero on both hard deployment splits.

The missing external evidence is decisive. Without real tactile hardware, accepted high-fidelity tactile simulation, trained deployed controller artifacts, or independent external baselines, this remains an archive-quality negative result.
