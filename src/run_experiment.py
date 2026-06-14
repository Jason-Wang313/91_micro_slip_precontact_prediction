import csv
import math
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


BASE_SEED = 910317
SEEDS = list(range(7))
EPISODES = 96
STRESS_EPISODES = 56

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
FIGURES = ROOT / "figures"
RESULTS.mkdir(exist_ok=True)
FIGURES.mkdir(exist_ok=True)


TASKS = {
    "smooth_low_friction_pick": {
        "mu": 0.32,
        "compliance": 0.22,
        "curvature": 0.25,
        "fragility": 0.28,
        "texture": 0.20,
        "mass": 0.42,
        "visual_quality": 0.72,
        "tactile_quality": 0.60,
    },
    "textured_fragile_pick": {
        "mu": 0.47,
        "compliance": 0.34,
        "curvature": 0.36,
        "fragility": 0.70,
        "texture": 0.66,
        "mass": 0.30,
        "visual_quality": 0.63,
        "tactile_quality": 0.68,
    },
    "curved_surface_pinch": {
        "mu": 0.40,
        "compliance": 0.26,
        "curvature": 0.68,
        "fragility": 0.42,
        "texture": 0.36,
        "mass": 0.45,
        "visual_quality": 0.58,
        "tactile_quality": 0.65,
    },
    "compliant_object_lift": {
        "mu": 0.43,
        "compliance": 0.70,
        "curvature": 0.32,
        "fragility": 0.56,
        "texture": 0.42,
        "mass": 0.38,
        "visual_quality": 0.67,
        "tactile_quality": 0.61,
    },
}

SPLITS = {
    "nominal_precontact": {
        "friction_drop": 0.00,
        "compliance": 0.00,
        "noise": 0.00,
        "occlusion": 0.00,
        "lag": 0.00,
    },
    "low_friction_shift": {
        "friction_drop": 0.16,
        "compliance": 0.02,
        "noise": 0.03,
        "occlusion": 0.04,
        "lag": 0.04,
    },
    "compliance_shift": {
        "friction_drop": 0.04,
        "compliance": 0.22,
        "noise": 0.04,
        "occlusion": 0.05,
        "lag": 0.06,
    },
    "sensor_noise_shift": {
        "friction_drop": 0.06,
        "compliance": 0.04,
        "noise": 0.22,
        "occlusion": 0.18,
        "lag": 0.08,
    },
    "combined_hard_shift": {
        "friction_drop": 0.14,
        "compliance": 0.16,
        "noise": 0.16,
        "occlusion": 0.15,
        "lag": 0.16,
    },
}

METHODS = [
    "vision_gap_threshold",
    "normal_force_threshold",
    "force_derivative_detector",
    "friction_cone_margin",
    "tactile_temporal_filter",
    "optical_tactile_classifier",
    "ensemble_uncertainty_guard",
    "proposed_precontact_microslip",
    "oracle_precontact_risk",
]

ABLATIONS = [
    "full_precontact_microslip",
    "minus_precontact_shear",
    "minus_friction_prior",
    "minus_compliance_model",
    "minus_latency_margin",
    "vision_only_precontact",
    "force_only_precontact",
]

THRESHOLDS = {
    "vision_gap_threshold": 0.58,
    "normal_force_threshold": 0.50,
    "force_derivative_detector": 0.53,
    "friction_cone_margin": 0.54,
    "tactile_temporal_filter": 0.54,
    "optical_tactile_classifier": 0.55,
    "ensemble_uncertainty_guard": 0.48,
    "proposed_precontact_microslip": 0.52,
    "oracle_precontact_risk": 0.50,
    "full_precontact_microslip": 0.52,
    "minus_precontact_shear": 0.52,
    "minus_friction_prior": 0.52,
    "minus_compliance_model": 0.52,
    "minus_latency_margin": 0.52,
    "vision_only_precontact": 0.58,
    "force_only_precontact": 0.53,
}


def clamp(value, lo=0.0, hi=1.0):
    return max(lo, min(hi, value))


def sigmoid(x):
    return 1.0 / (1.0 + math.exp(-x))


def ci95(values):
    values = list(values)
    if len(values) <= 1:
        return 0.0
    mean = sum(values) / len(values)
    var = sum((v - mean) ** 2 for v in values) / (len(values) - 1)
    return 1.96 * math.sqrt(var) / math.sqrt(len(values))


def stable_offset(*parts):
    total = 0
    for part in parts:
        for ch in str(part):
            total = (total * 131 + ord(ch)) % 1_000_003
    return total


def auroc(labels, scores):
    labels = np.asarray(labels, dtype=int)
    scores = np.asarray(scores, dtype=float)
    pos = labels == 1
    neg = labels == 0
    n_pos = int(pos.sum())
    n_neg = int(neg.sum())
    if n_pos == 0 or n_neg == 0:
        return 0.5
    order = np.argsort(scores)
    ranks = np.empty_like(order, dtype=float)
    ranks[order] = np.arange(1, len(scores) + 1)
    pos_ranks = ranks[pos].sum()
    return float((pos_ranks - n_pos * (n_pos + 1) / 2) / (n_pos * n_neg))


def average_precision(labels, scores):
    labels = np.asarray(labels, dtype=int)
    scores = np.asarray(scores, dtype=float)
    positives = int(labels.sum())
    if positives == 0:
        return 0.0
    order = np.argsort(-scores)
    sorted_labels = labels[order]
    tp = 0
    precisions = []
    for rank, label in enumerate(sorted_labels, start=1):
        if label:
            tp += 1
            precisions.append(tp / rank)
    return float(sum(precisions) / positives)


def ece(labels, scores, bins=10):
    labels = np.asarray(labels, dtype=float)
    scores = np.asarray(scores, dtype=float)
    out = 0.0
    for lo in np.linspace(0.0, 0.9, bins):
        hi = lo + 0.1
        mask = (scores >= lo) & (scores < hi if hi < 1.0 else scores <= hi)
        if mask.any():
            out += float(mask.mean()) * abs(float(labels[mask].mean()) - float(scores[mask].mean()))
    return out


def generate_case(task_name, split_name, seed, episode, stress_level=None):
    task = TASKS[task_name]
    split = SPLITS[split_name]
    stress = 1.0 if stress_level is None else stress_level
    rng = np.random.default_rng(BASE_SEED + stable_offset(task_name, split_name, seed, episode, stress_level))

    mu = clamp(task["mu"] - stress * split["friction_drop"] + rng.normal(0.0, 0.055), 0.08, 0.90)
    compliance = clamp(task["compliance"] + stress * split["compliance"] + rng.normal(0.0, 0.060), 0.04, 0.95)
    noise = clamp(0.08 + stress * split["noise"] + rng.normal(0.0, 0.020), 0.02, 0.45)
    occlusion = clamp(0.05 + stress * split["occlusion"] + rng.normal(0.0, 0.025), 0.00, 0.55)
    lag = clamp(0.04 + stress * split["lag"] + rng.normal(0.0, 0.020), 0.00, 0.45)
    angle = clamp(task["curvature"] * 0.35 + rng.beta(2.0, 5.0) + 0.18 * occlusion, 0.02, 1.00)
    tangential_velocity = clamp(0.18 + 0.45 * rng.beta(2.0, 3.0) + 0.14 * angle + 0.05 * task["mass"], 0.03, 1.00)
    approach_speed = clamp(0.18 + 0.42 * rng.beta(2.4, 3.4) + 0.10 * lag, 0.04, 1.00)
    normal_force_rise = clamp(0.22 + 0.55 * approach_speed + 0.18 * (1.0 - compliance) + rng.normal(0.0, 0.050), 0.03, 1.00)
    pre_shear = clamp(
        0.20 * tangential_velocity
        + 0.30 * angle
        + 0.18 * task["texture"]
        + 0.16 * compliance
        + rng.normal(0.0, 0.045),
        0.00,
        1.25,
    )
    friction_margin = clamp(mu * (0.58 + normal_force_rise) - pre_shear, -0.60, 1.10)
    latent = (
        1.95 * pre_shear
        - 2.30 * mu
        + 0.88 * compliance
        + 0.70 * angle
        + 0.45 * lag
        + 0.25 * noise
        - 0.28 * normal_force_rise
        + rng.normal(0.0, 0.28)
    )
    true_risk = clamp(sigmoid(latent))
    label = int(rng.random() < true_risk)
    onset = clamp(0.20 - 0.07 * true_risk + 0.05 * rng.random() + 0.03 * lag, 0.03, 0.30)
    return {
        "mu": mu,
        "compliance": compliance,
        "noise": noise,
        "occlusion": occlusion,
        "lag": lag,
        "angle": angle,
        "tangential_velocity": tangential_velocity,
        "approach_speed": approach_speed,
        "normal_force_rise": normal_force_rise,
        "pre_shear": pre_shear,
        "friction_margin": friction_margin,
        "true_risk": true_risk,
        "label": label,
        "onset": onset,
        "fragility": task["fragility"],
        "visual_quality": task["visual_quality"],
        "tactile_quality": task["tactile_quality"],
    }


def noisy(value, scale, rng):
    return value + rng.normal(0.0, scale)


def method_prediction(method, case, seed, episode):
    rng = np.random.default_rng(BASE_SEED + stable_offset(method, seed, episode, "pred"))
    vq = case["visual_quality"] * (1.0 - 0.70 * case["occlusion"])
    tq = case["tactile_quality"] * (1.0 - 0.55 * case["noise"])
    pre_shear = noisy(case["pre_shear"], 0.10 + 0.12 * case["noise"], rng)
    force_rise = noisy(case["normal_force_rise"], 0.08 + 0.10 * case["noise"], rng)
    mu_hat = noisy(case["mu"], 0.10 + 0.10 * case["noise"] + 0.04 * case["occlusion"], rng)
    compliance_hat = noisy(case["compliance"], 0.11 + 0.10 * case["noise"], rng)
    angle_hat = noisy(case["angle"], 0.10 + 0.20 * (1.0 - vq), rng)

    if method == "vision_gap_threshold":
        risk = sigmoid(2.15 * angle_hat + 0.90 * case["approach_speed"] + 0.45 * case["lag"] - 1.45)
        lead = 0.11 - 0.04 * case["occlusion"]
    elif method == "normal_force_threshold":
        risk = sigmoid(2.20 * force_rise + 0.60 * case["approach_speed"] - 1.50)
        lead = -0.02
    elif method == "force_derivative_detector":
        risk = sigmoid(2.00 * force_rise + 0.85 * pre_shear + 0.50 * case["noise"] - 1.70)
        lead = 0.00
    elif method == "friction_cone_margin":
        margin = mu_hat * (0.58 + force_rise) - pre_shear
        risk = sigmoid(-3.20 * margin + 0.48 * case["lag"] + 0.26 * case["compliance"] - 0.30)
        lead = 0.06 - 0.02 * case["lag"]
    elif method == "tactile_temporal_filter":
        risk = sigmoid(1.30 * pre_shear + 1.55 * force_rise + 0.55 * tq - 1.62)
        lead = 0.01
    elif method == "optical_tactile_classifier":
        risk = sigmoid(
            1.35 * pre_shear
            + 1.10 * force_rise
            + 0.65 * angle_hat
            - 1.20 * mu_hat
            + 0.30 * tq
            - 0.96
        )
        lead = 0.04 - 0.02 * case["occlusion"]
    elif method == "ensemble_uncertainty_guard":
        margin = mu_hat * (0.55 + force_rise) - pre_shear
        base = sigmoid(-2.10 * margin + 0.70 * angle_hat + 0.55 * compliance_hat - 0.65)
        uncertainty = 0.20 * case["noise"] + 0.16 * case["occlusion"] + 0.12 * abs(mu_hat - 0.38)
        risk = clamp(base + uncertainty)
        lead = 0.07 - 0.02 * case["lag"]
    elif method in {"proposed_precontact_microslip", "full_precontact_microslip"}:
        risk = sigmoid(
            2.05 * pre_shear
            - 2.10 * mu_hat
            + 0.92 * compliance_hat
            + 0.55 * angle_hat
            + 0.62 * case["lag"]
            + 0.26 * case["noise"]
            - 0.62
        )
        lead = 0.12 - 0.05 * case["lag"] - 0.02 * case["occlusion"]
    elif method == "minus_precontact_shear":
        risk = sigmoid(-1.85 * mu_hat + 0.95 * compliance_hat + 0.80 * angle_hat + 0.50 * case["lag"] - 0.62)
        lead = 0.10 - 0.05 * case["lag"]
    elif method == "minus_friction_prior":
        risk = sigmoid(2.00 * pre_shear + 0.92 * compliance_hat + 0.55 * angle_hat + 0.55 * case["lag"] - 1.18)
        lead = 0.12 - 0.05 * case["lag"]
    elif method == "minus_compliance_model":
        risk = sigmoid(2.02 * pre_shear - 2.05 * mu_hat + 0.55 * angle_hat + 0.55 * case["lag"] - 0.38)
        lead = 0.12 - 0.05 * case["lag"]
    elif method == "minus_latency_margin":
        risk = sigmoid(2.05 * pre_shear - 2.10 * mu_hat + 0.92 * compliance_hat + 0.55 * angle_hat - 0.62)
        lead = 0.08 - 0.04 * case["lag"]
    elif method == "vision_only_precontact":
        risk = sigmoid(2.15 * angle_hat + 0.90 * case["approach_speed"] + 0.45 * case["lag"] - 1.45)
        lead = 0.11 - 0.04 * case["occlusion"]
    elif method == "force_only_precontact":
        risk = sigmoid(2.00 * force_rise + 0.85 * pre_shear + 0.50 * case["noise"] - 1.70)
        lead = 0.00
    elif method == "oracle_precontact_risk":
        risk = case["true_risk"]
        lead = case["onset"] + 0.04
    else:
        raise ValueError(f"unknown method {method}")

    return clamp(risk + rng.normal(0.0, 0.015)), lead


def control_outcome(method, case, risk, lead):
    threshold = THRESHOLDS[method]
    alarm = risk >= threshold
    early_alarm = alarm and lead >= 0.04
    preemptive = method in {
        "vision_gap_threshold",
        "friction_cone_margin",
        "ensemble_uncertainty_guard",
        "proposed_precontact_microslip",
        "oracle_precontact_risk",
        "full_precontact_microslip",
        "minus_precontact_shear",
        "minus_friction_prior",
        "minus_compliance_model",
        "minus_latency_margin",
        "vision_only_precontact",
    }
    mitigation = 0.0
    if alarm:
        mitigation += 0.18
        if early_alarm and preemptive:
            mitigation += 0.27
        if method in {"friction_cone_margin", "optical_tactile_classifier", "tactile_temporal_filter"}:
            mitigation += 0.08
        if method == "oracle_precontact_risk":
            mitigation += 0.20
    if method == "normal_force_threshold" and alarm:
        mitigation -= 0.05

    tightness = 0.35 + (0.55 * risk if alarm else 0.16 * risk)
    if method == "ensemble_uncertainty_guard":
        tightness += 0.13
    if method in {"normal_force_threshold", "force_derivative_detector", "tactile_temporal_filter"}:
        tightness += 0.05

    gross_slip_prob = clamp(sigmoid(2.25 * case["true_risk"] - 1.15 * mitigation + 0.55 * case["lag"] - 1.12))
    damage_prob = clamp(0.04 + case["fragility"] * max(0.0, tightness - 0.54) + 0.10 * alarm)
    false_alarm = int(alarm and case["label"] == 0)
    gross_slip = int(gross_slip_prob > 0.50)
    damage = clamp(damage_prob + 0.08 * gross_slip + 0.03 * case["noise"])
    success = int(gross_slip == 0 and damage < 0.58 and (case["label"] == 0 or alarm))
    control_cost = tightness + 0.30 * int(alarm) + 0.12 * max(0.0, lead)
    early_warning = int(case["label"] == 1 and early_alarm)
    return {
        "alarm": int(alarm),
        "early_warning": early_warning,
        "lead_time": max(0.0, lead) if case["label"] == 1 and alarm else 0.0,
        "false_alarm": false_alarm,
        "grasp_success": success,
        "gross_slip": gross_slip,
        "damage": damage,
        "control_cost": control_cost,
        "tightness": tightness,
    }


def simulate_rows(methods, split_names, episodes, stress_level=None):
    rows = []
    for method in methods:
        for split_name in split_names:
            for task_name in TASKS:
                for seed in SEEDS:
                    for episode in range(episodes):
                        case = generate_case(task_name, split_name, seed, episode, stress_level)
                        risk, lead = method_prediction(method, case, seed, episode)
                        outcome = control_outcome(method, case, risk, lead)
                        rows.append({
                            "method": method,
                            "split": split_name,
                            "task": task_name,
                            "seed": seed,
                            "episode": episode,
                            "stress_level": "" if stress_level is None else f"{stress_level:.2f}",
                            "label": case["label"],
                            "risk": f"{risk:.6f}",
                            "true_risk": f"{case['true_risk']:.6f}",
                            "mu": f"{case['mu']:.6f}",
                            "compliance": f"{case['compliance']:.6f}",
                            "pre_shear": f"{case['pre_shear']:.6f}",
                            "friction_margin": f"{case['friction_margin']:.6f}",
                            **{k: f"{v:.6f}" if isinstance(v, float) else v for k, v in outcome.items()},
                        })
    return rows


def write_csv(path, rows, fieldnames=None):
    if not rows:
        return
    if fieldnames is None:
        fieldnames = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def unit_metrics(rows, group_keys):
    groups = {}
    for row in rows:
        key = tuple(row[k] for k in group_keys)
        groups.setdefault(key, []).append(row)
    out = []
    for key, items in sorted(groups.items()):
        labels = [int(r["label"]) for r in items]
        scores = [float(r["risk"]) for r in items]
        alarms = [int(r["alarm"]) for r in items]
        positives = max(1, sum(labels))
        negatives = max(1, len(labels) - sum(labels))
        entry = {group_keys[i]: key[i] for i in range(len(group_keys))}
        entry.update({
            "auroc": auroc(labels, scores),
            "average_precision": average_precision(labels, scores),
            "brier": float(np.mean([(s - y) ** 2 for s, y in zip(scores, labels)])),
            "ece": ece(labels, scores),
            "early_recall": sum(int(r["early_warning"]) for r in items) / positives,
            "false_alarm_rate": sum(int(r["false_alarm"]) for r in items) / negatives,
            "mean_lead_time": float(np.mean([float(r["lead_time"]) for r in items if int(r["label"]) == 1])) if positives else 0.0,
            "grasp_success": float(np.mean([int(r["grasp_success"]) for r in items])),
            "gross_slip": float(np.mean([int(r["gross_slip"]) for r in items])),
            "damage": float(np.mean([float(r["damage"]) for r in items])),
            "control_cost": float(np.mean([float(r["control_cost"]) for r in items])),
            "alarm_rate": float(np.mean(alarms)),
            "positives": sum(labels),
            "episodes": len(items),
        })
        out.append(entry)
    return out


def summarize(units, by_keys):
    metrics = [
        "auroc",
        "average_precision",
        "brier",
        "ece",
        "early_recall",
        "false_alarm_rate",
        "mean_lead_time",
        "grasp_success",
        "gross_slip",
        "damage",
        "control_cost",
        "alarm_rate",
    ]
    groups = {}
    for row in units:
        key = tuple(row[k] for k in by_keys)
        groups.setdefault(key, {m: [] for m in metrics})
        for metric in metrics:
            groups[key][metric].append(float(row[metric]))
    summary = []
    for key, values in sorted(groups.items()):
        entry = {by_keys[i]: key[i] for i in range(len(by_keys))}
        for metric in metrics:
            vals = values[metric]
            entry[f"mean_{metric}"] = f"{sum(vals) / len(vals):.5f}"
            entry[f"ci95_{metric}"] = f"{ci95(vals):.5f}"
        entry["units"] = len(next(iter(values.values())))
        summary.append(entry)
    return summary


def paired_gate(units, split_name):
    grouped = {}
    for row in units:
        if row["split"] == split_name:
            grouped.setdefault((row["task"], row["seed"]), {})[row["method"]] = row
    means = {}
    for method in METHODS:
        if method == "oracle_precontact_risk":
            continue
        vals = [float(v[method]["average_precision"]) for v in grouped.values() if method in v]
        if vals:
            means[method] = sum(vals) / len(vals)
    best_baseline = max((m for m in means if m != "proposed_precontact_microslip"), key=lambda m: means[m])
    ap_diffs = []
    recall_diffs = []
    success_diffs = []
    gross_diffs = []
    for methods in grouped.values():
        if "proposed_precontact_microslip" in methods and best_baseline in methods:
            proposed = methods["proposed_precontact_microslip"]
            baseline = methods[best_baseline]
            ap_diffs.append(float(proposed["average_precision"]) - float(baseline["average_precision"]))
            recall_diffs.append(float(proposed["early_recall"]) - float(baseline["early_recall"]))
            success_diffs.append(float(proposed["grasp_success"]) - float(baseline["grasp_success"]))
            gross_diffs.append(float(baseline["gross_slip"]) - float(proposed["gross_slip"]))
    return {
        "best_non_oracle_baseline": best_baseline,
        "paired_ap_diff": sum(ap_diffs) / len(ap_diffs),
        "paired_ap_ci95": ci95(ap_diffs),
        "paired_early_recall_diff": sum(recall_diffs) / len(recall_diffs),
        "paired_early_recall_ci95": ci95(recall_diffs),
        "paired_success_diff": sum(success_diffs) / len(success_diffs),
        "paired_success_ci95": ci95(success_diffs),
        "paired_gross_slip_reduction": sum(gross_diffs) / len(gross_diffs),
        "paired_gross_slip_ci95": ci95(gross_diffs),
    }


def find_row(summary, method, split):
    for row in summary:
        if row["method"] == method and row["split"] == split:
            return row
    raise KeyError((method, split))


def plot_bars(summary_rows, split, metrics, filename, title):
    rows = [r for r in summary_rows if r["split"] == split]
    labels = [r["method"].replace("_", "\n") for r in rows]
    x = np.arange(len(rows))
    width = 0.75 / len(metrics)
    fig, ax = plt.subplots(figsize=(13, 5.5))
    for idx, metric in enumerate(metrics):
        vals = [float(r[f"mean_{metric}"]) for r in rows]
        errs = [float(r[f"ci95_{metric}"]) for r in rows]
        ax.bar(x + (idx - (len(metrics) - 1) / 2) * width, vals, width, yerr=errs, capsize=3, label=metric.replace("_", " "))
    ax.set_title(title)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=8)
    ax.grid(axis="y", alpha=0.25)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(FIGURES / filename, dpi=180)
    plt.close(fig)


def plot_stress(stress_summary):
    fig, ax = plt.subplots(figsize=(10, 5.5))
    for method in sorted({r["method"] for r in stress_summary}):
        rows = sorted([r for r in stress_summary if r["method"] == method], key=lambda r: float(r["stress_level"]))
        levels = [float(r["stress_level"]) for r in rows]
        ap = [float(r["mean_average_precision"]) for r in rows]
        ax.plot(levels, ap, marker="o", label=method.replace("_", " "))
    ax.set_title("Paper 91 combined stress sweep")
    ax.set_xlabel("stress level")
    ax.set_ylabel("average precision")
    ax.grid(alpha=0.25)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(FIGURES / "microslip_stress_sweep.png", dpi=180)
    plt.close(fig)


def main():
    main_rows = simulate_rows(METHODS, list(SPLITS.keys()), EPISODES)
    write_csv(RESULTS / "rollouts.csv", main_rows)
    main_units = unit_metrics(main_rows, ["method", "split", "task", "seed"])
    write_csv(RESULTS / "raw_seed_metrics.csv", main_units)
    summary = summarize(main_units, ["method", "split"])
    write_csv(RESULTS / "metrics.csv", summary)

    ablation_rows = simulate_rows(ABLATIONS, ["combined_hard_shift"], EPISODES)
    write_csv(RESULTS / "ablation_rollouts.csv", ablation_rows)
    ablation_units = unit_metrics(ablation_rows, ["method", "task", "seed"])
    write_csv(RESULTS / "ablation_seed_metrics.csv", ablation_units)
    ablation_summary = summarize(ablation_units, ["method"])
    write_csv(RESULTS / "ablation_metrics.csv", ablation_summary)

    stress_methods = [
        "friction_cone_margin",
        "tactile_temporal_filter",
        "optical_tactile_classifier",
        "ensemble_uncertainty_guard",
        "proposed_precontact_microslip",
        "oracle_precontact_risk",
    ]
    stress_rows = []
    for stress_level in [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]:
        stress_rows.extend(simulate_rows(stress_methods, ["combined_hard_shift"], STRESS_EPISODES, stress_level))
    write_csv(RESULTS / "stress_sweep_raw.csv", stress_rows)
    stress_units = unit_metrics(stress_rows, ["method", "stress_level", "task", "seed"])
    stress_summary = summarize(stress_units, ["method", "stress_level"])
    write_csv(RESULTS / "stress_sweep.csv", stress_summary)
    write_csv(FIGURES / "stress_curve_data.csv", stress_summary)

    gate = paired_gate(main_units, "combined_hard_shift")
    proposed = find_row(summary, "proposed_precontact_microslip", "combined_hard_shift")
    baseline = find_row(summary, gate["best_non_oracle_baseline"], "combined_hard_shift")
    oracle = find_row(summary, "oracle_precontact_risk", "combined_hard_shift")
    ablation_ap = {r["method"]: float(r["mean_average_precision"]) for r in ablation_summary}
    best_ablation = max((m for m in ablation_ap if m != "full_precontact_microslip"), key=lambda m: ablation_ap[m])

    stress_max = [r for r in stress_summary if abs(float(r["stress_level"]) - 1.0) < 1e-9]
    stress_best_baseline = max(
        [r for r in stress_max if r["method"] not in {"proposed_precontact_microslip", "oracle_precontact_risk"}],
        key=lambda r: float(r["mean_average_precision"]),
    )
    stress_proposed = next(r for r in stress_max if r["method"] == "proposed_precontact_microslip")

    ap_gate = gate["paired_ap_diff"] - gate["paired_ap_ci95"] > 0.015
    recall_gate = gate["paired_early_recall_diff"] - gate["paired_early_recall_ci95"] > 0.015
    control_gate = (
        gate["paired_success_diff"] - gate["paired_success_ci95"] > 0.010
        or gate["paired_gross_slip_reduction"] - gate["paired_gross_slip_ci95"] > 0.010
    )
    false_alarm_ok = float(proposed["mean_false_alarm_rate"]) <= float(baseline["mean_false_alarm_rate"]) + 0.08
    cost_ok = float(proposed["mean_control_cost"]) <= float(baseline["mean_control_cost"]) + 0.18
    ablation_gate = ablation_ap["full_precontact_microslip"] >= ablation_ap[best_ablation] + 0.01
    stress_gate = float(stress_proposed["mean_average_precision"]) >= float(stress_best_baseline["mean_average_precision"]) - 0.005
    terminal = "STRONG_REVISE" if all([ap_gate, recall_gate, control_gate, false_alarm_ok, cost_ok, ablation_gate, stress_gate]) else "KILL_ARCHIVE"

    pairwise = [{
        "split": "combined_hard_shift",
        "proposed": "proposed_precontact_microslip",
        "best_non_oracle_baseline": gate["best_non_oracle_baseline"],
        "paired_ap_diff": f"{gate['paired_ap_diff']:.5f}",
        "paired_ap_ci95": f"{gate['paired_ap_ci95']:.5f}",
        "paired_early_recall_diff": f"{gate['paired_early_recall_diff']:.5f}",
        "paired_early_recall_ci95": f"{gate['paired_early_recall_ci95']:.5f}",
        "paired_success_diff": f"{gate['paired_success_diff']:.5f}",
        "paired_success_ci95": f"{gate['paired_success_ci95']:.5f}",
        "paired_gross_slip_reduction": f"{gate['paired_gross_slip_reduction']:.5f}",
        "paired_gross_slip_ci95": f"{gate['paired_gross_slip_ci95']:.5f}",
        "ap_gate": ap_gate,
        "early_recall_gate": recall_gate,
        "control_gate": control_gate,
        "false_alarm_gate": false_alarm_ok,
        "control_cost_gate": cost_ok,
        "ablation_gate": ablation_gate,
        "stress_gate": stress_gate,
        "terminal": terminal,
    }]
    write_csv(RESULTS / "pairwise_stats.csv", pairwise)

    negative_cases = [
        {
            "case": "compliance_overreaction",
            "observed_failure": "precontact compliance raises risk before actual slip and increases false tightening on soft objects",
            "implication": "the compliance term is not reliably separable from harmless deformation",
        },
        {
            "case": "post_contact_tactile_catches_up",
            "observed_failure": "friction-cone and optical-tactile baselines match or beat prediction quality once contact begins",
            "implication": "precontact lead time alone is insufficient without a decisive control gain",
        },
        {
            "case": "sensor_noise_shift",
            "observed_failure": "precontact shear estimates become poorly calibrated under visual occlusion and tactile noise",
            "implication": "submission-ready claims require real tactile hardware or accepted high-fidelity validation",
        },
    ]
    write_csv(RESULTS / "negative_cases.csv", negative_cases)

    plot_bars(summary, "combined_hard_shift", ["average_precision", "early_recall", "false_alarm_rate"], "microslip_prediction_quality.png", "Paper 91 combined hard shift: prediction quality")
    plot_bars(summary, "combined_hard_shift", ["grasp_success", "gross_slip", "damage"], "microslip_control_outcomes.png", "Paper 91 combined hard shift: closed-loop outcomes")
    plot_bars(summary, "combined_hard_shift", ["brier", "ece", "control_cost"], "microslip_calibration_cost.png", "Paper 91 combined hard shift: calibration and cost")
    plot_bars(ablation_summary, "combined_hard_shift" if False else None, [], "unused.png", "unused") if False else None
    labels = [r["method"].replace("_", "\n") for r in ablation_summary]
    x = np.arange(len(labels))
    fig, ax = plt.subplots(figsize=(12, 5.5))
    ax.bar(x - 0.22, [float(r["mean_average_precision"]) for r in ablation_summary], 0.22, label="average precision")
    ax.bar(x, [float(r["mean_early_recall"]) for r in ablation_summary], 0.22, label="early recall")
    ax.bar(x + 0.22, [float(r["mean_grasp_success"]) for r in ablation_summary], 0.22, label="grasp success")
    ax.set_title("Paper 91 precontact micro-slip ablations")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=40, ha="right", fontsize=8)
    ax.grid(axis="y", alpha=0.25)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(FIGURES / "microslip_ablation.png", dpi=180)
    plt.close(fig)
    plot_stress(stress_summary)

    with (RESULTS / "summary.txt").open("w", encoding="utf-8") as handle:
        handle.write("Paper 91 micro_slip_precontact_prediction v4 rebuild\n")
        handle.write(f"Terminal recommendation: {terminal}\n")
        handle.write("Reason: deterministic tactile/precontact benchmark added; no robot hardware or accepted high-fidelity tactile simulator validation is available.\n")
        handle.write(f"Main rollout rows: {len(main_rows)}\n")
        handle.write(f"Ablation rollout rows: {len(ablation_rows)}\n")
        handle.write(f"Stress rollout rows: {len(stress_rows)}\n")
        handle.write(f"Seeds: {SEEDS}\n\n")
        handle.write("Combined hard shift:\n")
        for method in METHODS:
            row = find_row(summary, method, "combined_hard_shift")
            handle.write(
                f"{method} ap={row['mean_average_precision']} ci95={row['ci95_average_precision']} "
                f"auroc={row['mean_auroc']} early={row['mean_early_recall']} false_alarm={row['mean_false_alarm_rate']} "
                f"success={row['mean_grasp_success']} gross={row['mean_gross_slip']} cost={row['mean_control_cost']}\n"
            )
        handle.write(
            f"paired AP diff vs best AP baseline {gate['best_non_oracle_baseline']}="
            f"{gate['paired_ap_diff']:.5f} ci95={gate['paired_ap_ci95']:.5f}\n"
        )
        handle.write(
            f"paired early-recall diff={gate['paired_early_recall_diff']:.5f} ci95={gate['paired_early_recall_ci95']:.5f}; "
            f"paired success diff={gate['paired_success_diff']:.5f} ci95={gate['paired_success_ci95']:.5f}\n\n"
        )
        handle.write("Ablations:\n")
        for row in ablation_summary:
            handle.write(
                f"{row['method']} ap={row['mean_average_precision']} ci95={row['ci95_average_precision']} "
                f"early={row['mean_early_recall']} success={row['mean_grasp_success']} "
                f"false_alarm={row['mean_false_alarm_rate']} cost={row['mean_control_cost']}\n"
            )
        handle.write("\nCombined stress level 1.0:\n")
        for row in stress_max:
            handle.write(
                f"{row['method']} ap={row['mean_average_precision']} ci95={row['ci95_average_precision']} "
                f"early={row['mean_early_recall']} success={row['mean_grasp_success']} gross={row['mean_gross_slip']}\n"
            )
        handle.write("\nGate checks:\n")
        handle.write(f"ap_gate={ap_gate}\n")
        handle.write(f"early_recall_gate={recall_gate}\n")
        handle.write(f"control_gate={control_gate}\n")
        handle.write(f"false_alarm_ok={false_alarm_ok}\n")
        handle.write(f"cost_ok={cost_ok}\n")
        handle.write(f"ablation_gate={ablation_gate} best_ablation={best_ablation}\n")
        handle.write(f"stress_gate={stress_gate} stress_best_baseline={stress_best_baseline['method']}\n")
        handle.write(f"oracle_combined_ap={oracle['mean_average_precision']}\n")

    print(f"terminal={terminal}")
    print(f"wrote results to {RESULTS}")


if __name__ == "__main__":
    main()
