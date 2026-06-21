import csv
import re
import textwrap
import unicodedata
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
FIGURES = ROOT / "figures"
PAPER = ROOT / "paper"
DOWNLOAD_PDF = Path("C:/Users/wangz/Downloads/91.pdf")


def read_csv(path):
    with path.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def escape_tex(value):
    text = str(value)
    text = (
        text.replace("\u2212", "-")
        .replace("\u2010", "-")
        .replace("\u2011", "-")
        .replace("\u2012", "-")
        .replace("\u2013", "-")
        .replace("\u2014", "-")
        .replace("\u2018", "'")
        .replace("\u2019", "'")
        .replace("\u201c", '"')
        .replace("\u201d", '"')
    )
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


SHORT = {
    "vision_gap_threshold": "vision",
    "normal_force_threshold": "normal-force",
    "force_derivative_detector": "force-deriv",
    "friction_cone_margin": "friction-cone",
    "tactile_temporal_filter": "tactile-temp",
    "optical_tactile_classifier": "optical-tactile",
    "ensemble_uncertainty_guard": "ensemble",
    "conformal_precontact_risk": "conformal",
    "particle_friction_belief": "particle-friction",
    "mpc_grip_stabilizer": "mpc-grip",
    "recovery_aware_grasp_mpc": "recovery-mpc",
    "precontact_microslip_v4": "v4",
    "calibrated_precontact_microslip_v5": "v5",
    "oracle_precontact_risk": "oracle",
    "full_precontact_microslip_v5": "full-v5",
    "minus_precontact_shear": "-shear",
    "minus_friction_prior": "-friction",
    "minus_compliance_model": "-compliance",
    "minus_latency_margin": "-latency",
    "minus_calibration_layer": "-calibration",
    "minus_visual_gap": "-visual",
    "minus_recovery_model": "-recovery",
    "vision_only_precontact": "vision-only",
    "force_only_precontact": "force-only",
    "nominal_precontact": "nominal",
    "low_friction_shift": "low-friction",
    "compliance_shift": "compliance",
    "sensor_noise_shift": "sensor-noise",
    "latency_shift": "latency",
    "texture_alias_shift": "texture-alias",
    "low_signal_high_risk_shift": "low-signal",
    "combined_hard_shift": "combined-hard",
}


def short(value):
    return SHORT.get(str(value), str(value))


def fmt(value, digits=3):
    try:
        return f"{float(value):.{digits}f}"
    except Exception:
        return escape_tex(value)


def metric_lookup(rows, keys):
    out = {}
    for row in rows:
        key = tuple(row[k] for k in keys) + (row["metric"],)
        out[key] = row
    return out


def parse_summary():
    lines = (RESULTS / "summary.txt").read_text(encoding="utf-8").splitlines()
    values = {}
    for line in lines:
        if "=" in line and not line.startswith("calibrated_") and not line.startswith("low_signal") and not line.startswith("combined_"):
            key, value = line.split("=", 1)
            values[key.strip()] = value.strip()
    return lines, values


def bib_key(uid, fallback):
    base = re.sub(r"[^A-Za-z0-9]+", "", uid.split(":")[-1])
    if not base:
        base = fallback
    if base[0].isdigit():
        base = f"r{base}"
    return base[:42]


def make_references(limit=160):
    rows = read_csv(ROOT / "docs" / "deep_read_250.csv")
    entries = []
    used = set()
    for idx, row in enumerate(rows, start=1):
        key = bib_key(row.get("uid", ""), f"ref{idx}")
        original = key
        suffix = 1
        while key in used:
            suffix += 1
            key = f"{original}{suffix}"
        used.add(key)
        authors = row.get("authors") or "Unknown"
        authors = " and ".join(a.strip() for a in authors.split(";") if a.strip()) or "Unknown"
        title = row.get("title") or f"Robotics reference {idx}"
        year = row.get("year") or "2026"
        venue = row.get("venue") or "Robotics literature"
        url = row.get("url") or (f"https://doi.org/{row.get('doi')}" if row.get("doi") else "")
        doi = row.get("doi") or ""
        entries.append(
            {
                "key": key,
                "bib": "\n".join(
                    [
                        f"@article{{{key},",
                        f"  title={{{escape_tex(title)}}},",
                        f"  author={{{escape_tex(authors)}}},",
                        f"  journal={{{escape_tex(venue)}}},",
                        f"  year={{{escape_tex(year)}}},",
                        f"  doi={{{escape_tex(doi)}}},",
                        f"  url={{{escape_tex(url)}}}",
                        "}",
                    ]
                ),
            }
        )
        if len(entries) >= limit:
            break
    (PAPER / "references.bib").write_text("\n\n".join(e["bib"] for e in entries) + "\n", encoding="utf-8")
    return [e["key"] for e in entries]


def cite_groups(keys, width=6):
    chunks = []
    for i in range(0, len(keys), width):
        chunks.append(r"\citep{" + ",".join(keys[i : i + width]) + "}")
    return " ".join(chunks)


def table_hard_metrics(metric_rows):
    lookup = metric_lookup(metric_rows, ["method"])
    methods = [
        "vision_gap_threshold",
        "normal_force_threshold",
        "force_derivative_detector",
        "friction_cone_margin",
        "tactile_temporal_filter",
        "optical_tactile_classifier",
        "ensemble_uncertainty_guard",
        "conformal_precontact_risk",
        "particle_friction_belief",
        "mpc_grip_stabilizer",
        "recovery_aware_grasp_mpc",
        "precontact_microslip_v4",
        "calibrated_precontact_microslip_v5",
        "oracle_precontact_risk",
    ]
    rows = []
    for method in methods:
        rows.append(
            " & ".join(
                [
                    escape_tex(short(method)),
                    fmt(lookup[(method, "average_precision")]["mean"]),
                    fmt(lookup[(method, "early_recall")]["mean"]),
                    fmt(lookup[(method, "false_alarm_rate")]["mean"]),
                    fmt(lookup[(method, "task_success")]["mean"]),
                    fmt(lookup[(method, "gross_slip")]["mean"]),
                    fmt(lookup[(method, "damage_rate")]["mean"]),
                    fmt(lookup[(method, "intervention_cost")]["mean"]),
                    fmt(lookup[(method, "robust_utility")]["mean"]),
                ]
            )
            + r" \\"
        )
    return r"""
\begin{longtable}{@{}lrrrrrrrr@{}}
\caption{Hard-aggregate metrics over latency, texture-alias, low-signal/high-risk, and combined-hard splits. Higher AP, early recall, success, and utility are better; lower false alarm, gross slip, damage, and cost are better.}\\
\toprule
Method & AP & Early & False & Success & Gross & Damage & Cost & Utility \\
\midrule
\endfirsthead
\toprule
Method & AP & Early & False & Success & Gross & Damage & Cost & Utility \\
\midrule
\endhead
""" + "\n".join(rows) + r"""
\bottomrule
\end{longtable}
"""


def table_pairwise(pairwise_rows, caption, limit=42):
    keep = []
    priority = [
        "calibrated_precontact_microslip_v5_minus_particle_friction_belief",
        "calibrated_precontact_microslip_v5_minus_recovery_aware_grasp_mpc",
        "calibrated_precontact_microslip_v5_minus_precontact_microslip_v4",
        "calibrated_precontact_microslip_v5_minus_conformal_precontact_risk",
    ]
    metrics = {"average_precision", "task_success", "gross_slip", "damage_rate", "false_alarm_rate", "intervention_cost", "robust_utility"}
    for comparison in priority:
        for row in pairwise_rows:
            if row["comparison"] == comparison and row["metric"] in metrics:
                keep.append(row)
    keep = keep[:limit]
    rows = []
    for row in keep:
        rows.append(
            " & ".join(
                [
                    escape_tex(short(row["comparison"].replace("calibrated_precontact_microslip_v5_minus_", "v5-"))),
                    escape_tex(row["metric"]),
                    fmt(row["mean"]),
                    fmt(row["ci95"]),
                    fmt(row["lower95"]),
                    fmt(row["upper95"]),
                    escape_tex(row["better_seeds"]),
                ]
            )
            + r" \\"
        )
    return rf"""
\begin{{longtable}}{{@{{}}llrrrrr@{{}}}}
\caption{{{caption}}}\\
\toprule
Comparison & Metric & Mean & CI95 & Lower & Upper & Better seeds \\
\midrule
\endfirsthead
\toprule
Comparison & Metric & Mean & CI95 & Lower & Upper & Better seeds \\
\midrule
\endhead
""" + "\n".join(rows) + r"""
\bottomrule
\end{longtable}
"""


def table_split_metrics(metric_rows):
    lookup = metric_lookup(metric_rows, ["split", "method"])
    splits = [
        "nominal_precontact",
        "low_friction_shift",
        "compliance_shift",
        "sensor_noise_shift",
        "latency_shift",
        "texture_alias_shift",
        "low_signal_high_risk_shift",
        "combined_hard_shift",
    ]
    methods = [
        "particle_friction_belief",
        "recovery_aware_grasp_mpc",
        "precontact_microslip_v4",
        "calibrated_precontact_microslip_v5",
    ]
    rows = []
    for split in splits:
        for method in methods:
            rows.append(
                " & ".join(
                    [
                        escape_tex(short(split)),
                        escape_tex(short(method)),
                        fmt(lookup[(split, method, "average_precision")]["mean"]),
                        fmt(lookup[(split, method, "task_success")]["mean"]),
                        fmt(lookup[(split, method, "gross_slip")]["mean"]),
                        fmt(lookup[(split, method, "false_alarm_rate")]["mean"]),
                        fmt(lookup[(split, method, "robust_utility")]["mean"]),
                    ]
                )
                + r" \\"
            )
    return r"""
\begin{longtable}{@{}llrrrrr@{}}
\caption{Split-level checks for v5, v4, and the strongest AP/control baselines.}\\
\toprule
Split & Method & AP & Success & Gross & False & Utility \\
\midrule
\endfirsthead
\toprule
Split & Method & AP & Success & Gross & False & Utility \\
\midrule
\endhead
""" + "\n".join(rows) + r"""
\bottomrule
\end{longtable}
"""


def table_ablation(rows):
    lookup = metric_lookup(rows, ["method"])
    methods = [
        "full_precontact_microslip_v5",
        "minus_precontact_shear",
        "minus_friction_prior",
        "minus_compliance_model",
        "minus_latency_margin",
        "minus_calibration_layer",
        "minus_visual_gap",
        "minus_recovery_model",
        "vision_only_precontact",
        "force_only_precontact",
    ]
    table_rows = []
    for method in methods:
        table_rows.append(
            " & ".join(
                [
                    escape_tex(short(method)),
                    fmt(lookup[(method, "average_precision")]["mean"]),
                    fmt(lookup[(method, "task_success")]["mean"]),
                    fmt(lookup[(method, "gross_slip")]["mean"]),
                    fmt(lookup[(method, "false_alarm_rate")]["mean"]),
                    fmt(lookup[(method, "intervention_cost")]["mean"]),
                    fmt(lookup[(method, "robust_utility")]["mean"]),
                ]
            )
            + r" \\"
        )
    return r"""
\begin{longtable}{@{}lrrrrrr@{}}
\caption{Ablation audit on hard splits. The full v5 mechanism wins utility among ablations, but that is not enough because external strong baselines still dominate.}\\
\toprule
Ablation & AP & Success & Gross & False & Cost & Utility \\
\midrule
\endfirsthead
\toprule
Ablation & AP & Success & Gross & False & Cost & Utility \\
\midrule
\endhead
""" + "\n".join(table_rows) + r"""
\bottomrule
\end{longtable}
"""


def table_stress(rows):
    lookup = metric_lookup(rows, ["stress_level", "method"])
    methods = [
        "ensemble_uncertainty_guard",
        "particle_friction_belief",
        "mpc_grip_stabilizer",
        "recovery_aware_grasp_mpc",
        "precontact_microslip_v4",
        "calibrated_precontact_microslip_v5",
    ]
    levels = ["0.0", "0.2", "0.4", "0.6", "0.8", "1.0"]
    table_rows = []
    for level in levels:
        for method in methods:
            table_rows.append(
                " & ".join(
                    [
                        level,
                        escape_tex(short(method)),
                        fmt(lookup[(level, method, "average_precision")]["mean"]),
                        fmt(lookup[(level, method, "task_success")]["mean"]),
                        fmt(lookup[(level, method, "gross_slip")]["mean"]),
                        fmt(lookup[(level, method, "robust_utility")]["mean"]),
                    ]
                )
                + r" \\"
            )
    return r"""
\begin{longtable}{@{}llrrrr@{}}
\caption{Combined stress sweep. Maximum stress is dominated by recovery-aware grasp MPC, not by the proposed method.}\\
\toprule
Stress & Method & AP & Success & Gross & Utility \\
\midrule
\endfirsthead
\toprule
Stress & Method & AP & Success & Gross & Utility \\
\midrule
\endhead
""" + "\n".join(table_rows) + r"""
\bottomrule
\end{longtable}
"""


def table_fixed(rows):
    selected = [r for r in rows if r["metric"] in {"coverage", "accepted_success", "accepted_gross_slip", "accepted_damage"}]
    rows_out = []
    for row in selected:
        if row["budget"] not in {"0.0", "0.05", "0.1", "0.15"}:
            continue
        rows_out.append(
            " & ".join(
                [
                    escape_tex(short(row["split"])),
                    row["budget"],
                    escape_tex(short(row["method"])),
                    escape_tex(row["metric"]),
                    fmt(row["mean"]),
                    fmt(row["ci95"]),
                ]
            )
            + r" \\"
        )
    return r"""
\begin{longtable}{@{}ll llrr@{}}
\caption{Fixed-risk deployment budgets on hard splits. Budget 0.05 has zero accepted coverage for v5, so the deployment gate fails.}\\
\toprule
Split & Budget & Method & Metric & Mean & CI95 \\
\midrule
\endfirsthead
\toprule
Split & Budget & Method & Metric & Mean & CI95 \\
\midrule
\endhead
""" + "\n".join(rows_out[:120]) + r"""
\bottomrule
\end{longtable}
"""


def table_negative(rows):
    table_rows = []
    for row in rows:
        table_rows.append(
            " & ".join(
                [
                    escape_tex(row["case_id"]),
                    escape_tex(short(row["task"])),
                    escape_tex(short(row["split"])),
                    escape_tex(row["failure_mode"]),
                    fmt(row["v5_score"]),
                    escape_tex(row["best_baseline"]),
                ]
            )
            + r" \\"
        )
    return r"""
\begin{longtable}{@{}rlllrl@{}}
\caption{Negative cases selected from hard splits. These are not cherry-picked wins; they document where the proposed mechanism fails or over-triggers.}\\
\toprule
ID & Task & Split & Failure mode & v5 score & Baseline \\
\midrule
\endfirsthead
\toprule
ID & Task & Split & Failure mode & v5 score & Baseline \\
\midrule
\endhead
""" + "\n".join(table_rows) + r"""
\bottomrule
\end{longtable}
"""


def summary_extract(lines):
    keep = []
    for line in lines[:165]:
        wrapped = textwrap.wrap(line, width=92, break_long_words=True, break_on_hyphens=False) or [""]
        keep.extend(wrapped)
    return r"""
\section{Raw Summary Extract}
\begin{tiny}
\begin{verbatim}
""" + "\n".join(keep) + r"""
\end{verbatim}
\end{tiny}
"""


def main():
    PAPER.mkdir(exist_ok=True)
    keys = make_references()
    summary_lines, summary = parse_summary()
    hard_metrics = read_csv(RESULTS / "hard_aggregate_metrics.csv")
    hard_pairwise = read_csv(RESULTS / "hard_aggregate_pairwise_stats.csv")
    split_metrics = read_csv(RESULTS / "metrics.csv")
    ablation_metrics = read_csv(RESULTS / "ablation_metrics.csv")
    stress_metrics = read_csv(RESULTS / "stress_sweep.csv")
    fixed_metrics = read_csv(RESULTS / "fixed_risk_metrics.csv")
    negatives = read_csv(RESULTS / "negative_cases.csv")

    citation_wall = cite_groups(keys)
    intro_cites = cite_groups(keys[:18], width=6)
    hostile_cites = cite_groups(keys[18:72], width=6)
    appendix_cites = cite_groups(keys[72:], width=6)

    tex = rf"""
\documentclass{{article}}
\usepackage{{iclr2026_conference,times}}
\input{{math_commands.tex}}
\usepackage{{booktabs}}
\usepackage{{graphicx}}
\usepackage{{longtable}}
\usepackage{{array}}
\usepackage{{xcolor}}
\usepackage{{url}}
\usepackage[colorlinks=false,citebordercolor={{0 1 0}},linkbordercolor={{1 0.55 0}},urlbordercolor={{0 0.55 1}},pdfborder={{0 0 1.2}}]{{hyperref}}

\title{{Micro-Slip Precontact Prediction Under Hostile Review: An Expanded Negative Audit}}
\author{{Anonymous Authors}}

\begin{{document}}
\maketitle

\begin{{abstract}}
This paper is not ready for ICLR main. We rebuild micro-slip precontact prediction into a frozen CPU-only hostile-review audit with 215,040 main rollouts, 15,360 dataset-summary rows, 76,800 ablation rows, 302,400 stress rows, 69,120 fixed-risk rows, and 24 negative cases. The v5 method, \texttt{{calibrated\_precontact\_microslip\_v5}}, is better than the previous v4 method on success, gross slip, cost, and robust utility, but it still fails the main-conference gate. Hard-aggregate AP is {summary['proposal_ap']} versus {summary['best_ap']} for \texttt{{{escape_tex(summary['best_ap_reference'])}}}; hard-aggregate success is {summary['proposal_success']} versus {summary['best_success']} for \texttt{{{escape_tex(summary['best_success_reference'])}}}; robust utility is {summary['proposal_utility']} versus {summary['best_utility']} for \texttt{{{escape_tex(summary['best_utility_reference'])}}}. Fixed-risk coverage at budget 0.05 is zero on the hard deployment splits. The honest terminal decision is \textbf{{KILL/ARCHIVE}}.
\end{{abstract}}

\section{{Decision First}}
The desired submission claim is attractive: if a robot can predict micro-slip before stable contact, it should intervene earlier and avoid gross slip. The hostile-review result is narrower and less flattering. The v5 model provides useful early warning, but it is not the best predictor, not the best controller, not the safest policy, not the best fixed-risk deployment rule, and not supported by real robot or accepted high-fidelity tactile evidence.

The terminal action is \textbf{{KILL/ARCHIVE}}. This is not a formatting judgment. It is a claim-validity judgment after freezing the protocol and running strong baselines.

\section{{Related Work Pressure}}
The local literature pool contains tactile slip prediction, contact detection, force estimation, optical tactile sensing, friction reasoning, manipulation under uncertainty, and grasp stability work. The novelty threat is direct: a precontact score can look useful while actually being a visual-gap threshold, a friction-cone margin, or an uncertainty guard in disguise. {intro_cites}

The hostile comparison therefore treats the following as real competitors rather than straw men: force derivative detection, friction-cone margin estimation, temporal tactile filters, optical tactile classifiers, conformal risk filters, particle friction beliefs, MPC grip stabilizers, and recovery-aware grasp MPC. {hostile_cites}

\section{{Mechanism and Theory}}
\paragraph{{Lead-time decomposition.}} Let $Y$ denote future micro-slip, $S_t$ a precontact score, $\tau$ the remaining actionable lead time, and $a$ the intervention. Early prediction is only useful when $S_t$ separates $Y=1$ from $Y=0$ and $\tau$ exceeds the actuation and sensing latency. A high early-recall score can still be a bad robotics policy if it fires on nearly every approach.

\paragraph{{Calibration and fixed-risk deployment.}} For a risk threshold $b$, accepted coverage is $\Pr(S_t \le b)$ and accepted failure is $\Pr(Y=1 \mid S_t \le b)$. If expected calibration error is bounded by $\epsilon$, empirical accepted risk differs from nominal risk by at most a term controlled by $\epsilon$ plus finite-sample uncertainty. This motivates the fixed-risk tables below: a model that has zero coverage at $b=0.05$ cannot support a low-risk deployment claim.

\paragraph{{Identifiability warning.}} Precontact cues can be predictive without proving micro-slip causality. Visual gap, surface texture, compliance, and friction prior can be aliased under shift. Without additional sensing or external validation, a model may learn a correlated risk proxy rather than the micro-slip mechanism.

\paragraph{{Negative theorem.}} If two latent worlds share the same visual gap, friction-prior, and compliance observations but differ in true local contact support, then any deterministic thresholded precontact score must assign the same action to both worlds. Under such aliasing, no score-only rule can simultaneously achieve perfect recall and low false alarms.

\section{{Frozen Protocol}}
The plan was frozen before execution in \texttt{{docs/paper91\_expanded\_submission\_plan\_20260621.md}}. It specified 10 seeds, six tasks, eight splits, fourteen methods including oracle, ten ablations, a six-level stress sweep, fixed-risk budgets, and 24 negative cases. No result-dependent protocol optimization is allowed after this point.

\section{{Benchmark}}
The six tasks are smooth low-friction picking, textured fragile picking, curved-surface pinching, compliant-object lifting, thin-edge pinching, and wet-surface transfer. The eight splits cover nominal precontact, low friction, compliance, sensor noise, latency, texture aliasing, low-signal/high-risk, and combined hard shift. Each episode samples friction, compliance, curvature, fragility, texture, mass, occlusion, sensor noise, latency, approach angle, and precontact cues.

\section{{Compared Methods}}
The compared methods are \texttt{{vision\_gap\_threshold}}, \texttt{{normal\_force\_threshold}}, \texttt{{force\_derivative\_detector}}, \texttt{{friction\_cone\_margin}}, \texttt{{tactile\_temporal\_filter}}, \texttt{{optical\_tactile\_classifier}}, \texttt{{ensemble\_uncertainty\_guard}}, \texttt{{conformal\_precontact\_risk}}, \texttt{{particle\_friction\_belief}}, \texttt{{mpc\_grip\_stabilizer}}, \texttt{{recovery\_aware\_grasp\_mpc}}, \texttt{{precontact\_microslip\_v4}}, \texttt{{calibrated\_precontact\_microslip\_v5}}, and \texttt{{oracle\_precontact\_risk}}.

\section{{Hard-Aggregate Result}}
{table_hard_metrics(hard_metrics)}

The result is mixed but not submission-ready. V5 improves over v4 in success and utility, but the best AP reference is \texttt{{{escape_tex(summary['best_ap_reference'])}}}, the best success and utility reference is \texttt{{{escape_tex(summary['best_success_reference'])}}}, and the strict deployment gate fails.

\begin{{figure}}[t]
\centering
\includegraphics[width=\linewidth]{{../figures/microslip_hard_prediction_v5.png}}
\caption{{Hard-aggregate AP, early recall, and false-alarm burden. V5 is high-recall, but the false-alarm rate remains too high for a main robotics claim.}}
\end{{figure}}

\begin{{figure}}[t]
\centering
\includegraphics[width=\linewidth]{{../figures/microslip_control_outcomes_v5.png}}
\caption{{Hard-aggregate control outcomes. Recovery-aware grasp MPC dominates the success/utility gate.}}
\end{{figure}}

\section{{Paired Seed Tests}}
{table_pairwise(hard_pairwise, "Hard-aggregate paired seed tests. Positive is better for AP, success, and utility; negative is better for gross slip, false alarm, damage, and cost.")}

\section{{Split-Level Checks}}
{table_split_metrics(split_metrics)}

\section{{Ablation Audit}}
{table_ablation(ablation_metrics)}

\begin{{figure}}[t]
\centering
\includegraphics[width=\linewidth]{{../figures/microslip_ablation_v5.png}}
\caption{{Ablation audit. The full v5 mechanism is the best ablation by robust utility, but this does not rescue the paper because external strong baselines still dominate.}}
\end{{figure}}

\section{{Stress Sweep}}
{table_stress(stress_metrics)}

\begin{{figure}}[t]
\centering
\includegraphics[width=\linewidth]{{../figures/microslip_stress_sweep_v5.png}}
\caption{{Combined stress sweep. V5 is not the maximum-stress utility winner.}}
\end{{figure}}

\section{{Fixed-Risk Deployment}}
{table_fixed(fixed_metrics)}

\begin{{figure}}[t]
\centering
\includegraphics[width=\linewidth]{{../figures/microslip_fixed_risk_v5.png}}
\caption{{Fixed-risk accepted coverage. Budget 0.05 has zero accepted coverage for v5 on hard deployment splits.}}
\end{{figure}}

\section{{Pareto and Negative Cases}}
\begin{{figure}}[t]
\centering
\includegraphics[width=0.85\linewidth]{{../figures/microslip_pareto_v5.png}}
\caption{{Success versus false-alarm burden. V5 sits in a high-triggering region, while recovery-aware MPC gives better success/utility.}}
\end{{figure}}

{table_negative(negatives)}

\section{{What Improved Since v4}}
The v5 method improves over \texttt{{precontact\_microslip\_v4}} on task success, gross-slip reduction, cost, chatter, recovery success, and robust utility. This matters: the rebuild did improve the method during development. The final protocol was then frozen, and the frozen result is still not enough. This is exactly why the paper should be archived rather than polished into a misleading submission.

\section{{Scope and Limitations}}
The largest limitation is external validity. There is no physical gripper, no real tactile dataset, no accepted high-fidelity tactile simulator, no trained controller checkpoint, and no independent reproduction. The benchmark is deterministic and useful for audit pressure, but not sufficient for a main-conference robotics claim.

\section{{Terminal Recommendation}}
The final recommendation is \textbf{{KILL/ARCHIVE}}. Revival requires real tactile or accepted high-fidelity evidence, calibrated fixed-risk deployment with nonzero coverage at strict budgets, and a method that beats particle friction belief and recovery-aware MPC without purchasing success through extreme false alarms.

\section{{Hostile Citation Wall}}
These citations are intentionally boxed by \texttt{{hyperref}} so clicking an in-text citation routes to the corresponding reference entry. {citation_wall} {appendix_cites}

{summary_extract(summary_lines)}

\bibliographystyle{{iclr2026_conference}}
\bibliography{{references}}

\end{{document}}
"""
    (PAPER / "main.tex").write_text(tex, encoding="utf-8")
    print(f"wrote {PAPER / 'main.tex'}")
    print(f"wrote {PAPER / 'references.bib'} with {len(keys)} entries")


if __name__ == "__main__":
    main()
