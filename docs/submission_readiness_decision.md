# Submission Readiness Decision

Decision: KILL_ARCHIVE

ICLR main-conference readiness: NO.

Paper 91 was rebuilt as a v4 deterministic tactile/precontact mechanics evidence audit. The evidence is not enough for an ICLR main submission.

Reasons:

- The proposed model improves early warning, but its combined-hard-shift AP is 0.751 versus 0.768 for the strongest non-oracle AP baseline.
- The paired AP difference is -0.016 +/- 0.018.
- The proposed method has high false-alarm rate (0.817) and high control cost (0.929).
- Ablations contradict the mechanism: vision-only and minus-friction variants beat full precontact on AP.
- Maximum-stress AP reverses in favor of optical-tactile.
- No real robot hardware, accepted high-fidelity tactile simulator, or external tactile dataset validation is available.

Honest terminal action: archive/kill for ICLR main. Do not submit this paper to ICLR main in the current form.

Revival condition: a real tactile dataset or high-fidelity tactile simulator plus a calibrated precontact mechanism that beats friction-cone, optical-tactile, and uncertainty baselines without excessive false alarms.
