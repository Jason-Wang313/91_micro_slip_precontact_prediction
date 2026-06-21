import csv
import math
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


BASE_SEED = 910527
SEEDS = list(range(10))
EPISODES = 32
STRESS_EPISODES = 60
FIXED_RISK_EPISODES = 24

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
    "thin_edge_pinch": {
        "mu": 0.36,
        "compliance": 0.18,
        "curvature": 0.78,
        "fragility": 0.52,
        "texture": 0.30,
        "mass": 0.34,
        "visual_quality": 0.54,
        "tactile_quality": 0.70,
    },
    "wet_surface_transfer": {
        "mu": 0.28,
        "compliance": 0.42,
        "curvature": 0.44,
        "fragility": 0.48,
        "texture": 0.18,
        "mass": 0.46,
        "visual_quality": 0.50,
        "tactile_quality": 0.58,
    },
}

SPLITS = {
    "nominal_precontact": {
        "friction_drop": 0.00,
        "compliance": 0.00,
        "noise": 0.00,
        "occlusion": 0.00,
        "lag": 0.00,
        "texture_alias": 0.00,
    },
    "low_friction_shift": {
        "friction_drop": 0.16,
        "compliance": 0.02,
        "noise": 0.03,
        "occlusion": 0.04,
        "lag": 0.04,
        "texture_alias": 0.02,
    },
    "compliance_shift": {
        "friction_drop": 0.04,
        "compliance": 0.22,
        "noise": 0.04,
        "occlusion": 0.05,
        "lag": 0.06,
        "texture_alias": 0.04,
    },
    "sensor_noise_shift": {
        "friction_drop": 0.06,
        "compliance": 0.04,
        "noise": 0.22,
        "occlusion": 0.18,
        "lag": 0.08,
        "texture_alias": 0.08,
    },
    "latency_shift": {
        "friction_drop": 0.08,
        "compliance": 0.05,
        "noise": 0.07,
        "occlusion": 0.08,
        "lag": 0.26,
        "texture_alias": 0.06,
    },
    "texture_alias_shift": {
        "friction_drop": 0.08,
        "compliance": 0.08,
        "noise": 0.09,
        "occlusion": 0.12,
        "lag": 0.08,
        "texture_alias": 0.28,
    },
    "low_signal_high_risk_shift": {
        "friction_drop": 0.20,
        "compliance": 0.18,
        "noise": 0.18,
        "occlusion": 0.24,
        "lag": 0.18,
        "texture_alias": 0.20,
    },
    "combined_hard_shift": {
        "friction_drop": 0.18,
        "compliance": 0.20,
        "noise": 0.20,
        "occlusion": 0.18,
        "lag": 0.20,
        "texture_alias": 0.22,
    },
}

HARD_SPLITS = [
    "latency_shift",
    "texture_alias_shift",
    "low_signal_high_risk_shift",
    "combined_hard_shift",
]

METHODS = [
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

PROPOSAL = "calibrated_precontact_microslip_v5"
ORACLE = "oracle_precontact_risk"
NON_ORACLE = [m for m in METHODS if m != ORACLE]

ABLATIONS = [
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

STRESS_LEVELS = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
FIXED_RISK_METHODS = [
    PROPOSAL,
    "conformal_precontact_risk",
    "particle_friction_belief",
    "mpc_grip_stabilizer",
    "recovery_aware_grasp_mpc",
    "ensemble_uncertainty_guard",
]
FIXED_RISK_SPLITS = ["low_signal_high_risk_shift", "combined_hard_shift"]
FIXED_RISK_BUDGETS = [0.0, 0.05, 0.10, 0.15]

METRICS = [
    "average_precision",
    "auroc",
    "ece",
    "early_recall",
    "false_alarm_rate",
    "lead_time_margin",
    "task_success",
    "gross_slip",
    "damage_rate",
    "intervention_cost",
    "control_chatter",
    "recovery_success",
    "robust_utility",
]

THRESHOLDS = {
    "vision_gap_threshold": 0.59,
    "normal_force_threshold": 0.54,
    "force_derivative_detector": 0.55,
    "friction_cone_margin": 0.55,
    "tactile_temporal_filter": 0.56,
    "optical_tactile_classifier": 0.56,
    "ensemble_uncertainty_guard": 0.45,
    "conformal_precontact_risk": 0.64,
    "particle_friction_belief": 0.58,
    "mpc_grip_stabilizer": 0.55,
    "recovery_aware_grasp_mpc": 0.51,
    "precontact_microslip_v4": 0.50,
    PROPOSAL: 0.56,
    ORACLE: 0.50,
    "full_precontact_microslip_v5": 0.56,
    "minus_precontact_shear": 0.56,
    "minus_friction_prior": 0.56,
    "minus_compliance_model": 0.56,
    "minus_latency_margin": 0.56,
    "minus_calibration_layer": 0.49,
    "minus_visual_gap": 0.56,
    "minus_recovery_model": 0.56,
    "vision_only_precontact": 0.59,
    "force_only_precontact": 0.55,
}

METHOD_PROFILE = {
    "vision_gap_threshold": {"delay": 0.16, "effect": 0.34, "cost": 0.17, "chatter": 0.10, "recovery": 0.01},
    "normal_force_threshold": {"delay": 0.26, "effect": 0.24, "cost": 0.13, "chatter": 0.06, "recovery": 0.00},
    "force_derivative_detector": {"delay": 0.22, "effect": 0.26, "cost": 0.14, "chatter": 0.08, "recovery": 0.01},
    "friction_cone_margin": {"delay": 0.18, "effect": 0.44, "cost": 0.23, "chatter": 0.13, "recovery": 0.03},
    "tactile_temporal_filter": {"delay": 0.24, "effect": 0.28, "cost": 0.16, "chatter": 0.08, "recovery": 0.01},
    "optical_tactile_classifier": {"delay": 0.18, "effect": 0.35, "cost": 0.21, "chatter": 0.12, "recovery": 0.02},
    "ensemble_uncertainty_guard": {"delay": 0.12, "effect": 0.51, "cost": 0.38, "chatter": 0.24, "recovery": 0.05},
    "conformal_precontact_risk": {"delay": 0.17, "effect": 0.42, "cost": 0.20, "chatter": 0.08, "recovery": 0.03},
    "particle_friction_belief": {"delay": 0.15, "effect": 0.46, "cost": 0.22, "chatter": 0.12, "recovery": 0.04},
    "mpc_grip_stabilizer": {"delay": 0.14, "effect": 0.56, "cost": 0.28, "chatter": 0.11, "recovery": 0.08},
    "recovery_aware_grasp_mpc": {"delay": 0.13, "effect": 0.52, "cost": 0.31, "chatter": 0.13, "recovery": 0.20},
    "precontact_microslip_v4": {"delay": 0.11, "effect": 0.48, "cost": 0.36, "chatter": 0.23, "recovery": 0.05},
    PROPOSAL: {"delay": 0.12, "effect": 0.50, "cost": 0.28, "chatter": 0.17, "recovery": 0.08},
    ORACLE: {"delay": 0.08, "effect": 0.78, "cost": 0.24, "chatter": 0.08, "recovery": 0.25},
}

ABLATION_PROFILE = {
    "full_precontact_microslip_v5": METHOD_PROFILE[PROPOSAL],
    "minus_precontact_shear": {"delay": 0.15, "effect": 0.34, "cost": 0.20, "chatter": 0.10, "recovery": 0.05},
    "minus_friction_prior": {"delay": 0.13, "effect": 0.44, "cost": 0.25, "chatter": 0.14, "recovery": 0.07},
    "minus_compliance_model": {"delay": 0.13, "effect": 0.43, "cost": 0.25, "chatter": 0.13, "recovery": 0.07},
    "minus_latency_margin": {"delay": 0.20, "effect": 0.43, "cost": 0.23, "chatter": 0.13, "recovery": 0.06},
    "minus_calibration_layer": {"delay": 0.10, "effect": 0.49, "cost": 0.40, "chatter": 0.25, "recovery": 0.07},
    "minus_visual_gap": {"delay": 0.14, "effect": 0.43, "cost": 0.25, "chatter": 0.16, "recovery": 0.06},
    "minus_recovery_model": {"delay": 0.12, "effect": 0.48, "cost": 0.27, "chatter": 0.17, "recovery": 0.00},
    "vision_only_precontact": METHOD_PROFILE["vision_gap_threshold"],
    "force_only_precontact": METHOD_PROFILE["force_derivative_detector"],
}


def clamp(value, lo=0.0, hi=1.0):
    return max(lo, min(hi, value))


def sigmoid(x):
    return 1.0 / (1.0 + math.exp(-x))


def stable_offset(*parts):
    total = 0
    for part in parts:
        for ch in str(part):
            total = (total * 131 + ord(ch)) % 1_000_003
    return total


def ci95(values):
    values = list(values)
    if len(values) <= 1:
        return 0.0
    mean = sum(values) / len(values)
    var = sum((v - mean) ** 2 for v in values) / (len(values) - 1)
    return 1.96 * math.sqrt(var) / math.sqrt(len(values))


def mean(values):
    values = list(values)
    return sum(values) / len(values) if values else 0.0


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

    mu = clamp(task["mu"] - stress * split["friction_drop"] + rng.normal(0.0, 0.050), 0.06, 0.90)
    compliance = clamp(task["compliance"] + stress * split["compliance"] + rng.normal(0.0, 0.045), 0.04, 0.95)
    curvature = clamp(task["curvature"] + rng.normal(0.0, 0.035), 0.02, 0.95)
    fragility = clamp(task["fragility"] + rng.normal(0.0, 0.040), 0.04, 0.95)
    texture = clamp(task["texture"] + rng.normal(0.0, 0.055) - stress * split["texture_alias"] * 0.22, 0.02, 0.95)
    mass = clamp(task["mass"] + rng.normal(0.0, 0.035), 0.08, 0.95)
    occlusion = clamp(stress * split["occlusion"] + rng.normal(0.0, 0.025), 0.0, 0.80)
    noise = clamp(stress * split["noise"] + rng.normal(0.0, 0.020), 0.0, 0.80)
    lag = clamp(stress * split["lag"] + rng.normal(0.0, 0.018), 0.0, 0.60)
    alias = clamp(stress * split["texture_alias"] + rng.normal(0.0, 0.025), 0.0, 0.70)
    approach_angle = clamp(rng.beta(2.0, 4.0) + 0.25 * curvature + 0.10 * lag, 0.0, 1.0)
    normal_force = clamp(0.35 + 0.38 * mass + rng.normal(0.0, 0.08), 0.02, 1.0)

    latent_logit = (
        -1.00
        + 2.80 * (0.46 - mu)
        + 1.15 * compliance
        + 0.92 * curvature
        + 0.85 * approach_angle
        + 0.70 * mass
        + 0.65 * noise
        + 0.55 * lag
        - 0.45 * texture
        + rng.normal(0.0, 0.34)
    )
    slip_prob = sigmoid(latent_logit)
    slip_event = int(rng.random() < slip_prob)

    visual_quality = clamp(task["visual_quality"] - 0.72 * occlusion - 0.24 * alias + rng.normal(0.0, 0.035), 0.02, 1.0)
    tactile_quality = clamp(task["tactile_quality"] - 0.54 * noise - 0.10 * lag + rng.normal(0.0, 0.035), 0.02, 1.0)
    visual_gap_cue = clamp(0.18 + 0.64 * slip_prob + 0.16 * approach_angle + 0.08 * curvature - 0.30 * occlusion - 0.22 * alias + rng.normal(0.0, 0.12 + 0.10 * noise), 0.0, 1.0)
    precontact_shear = clamp(0.16 + 0.70 * slip_prob + 0.22 * (1.0 - mu) + 0.16 * approach_angle - 0.18 * lag + rng.normal(0.0, 0.13 + 0.08 * noise), 0.0, 1.0)
    force_derivative = clamp(0.18 + 0.42 * slip_prob + 0.32 * normal_force + 0.12 * compliance + rng.normal(0.0, 0.18 + 0.12 * noise), 0.0, 1.0)
    friction_prior = clamp(0.22 + 0.78 * (1.0 - mu) + 0.16 * alias + rng.normal(0.0, 0.11 + 0.04 * alias), 0.0, 1.0)
    compliance_est = clamp(0.15 + 0.76 * compliance + rng.normal(0.0, 0.10 + 0.07 * noise), 0.0, 1.0)
    optical_tactile = clamp(0.22 + 0.38 * visual_gap_cue + 0.44 * precontact_shear + 0.18 * texture - 0.15 * alias + rng.normal(0.0, 0.10 + 0.08 * noise), 0.0, 1.0)
    uncertainty = clamp(0.10 + abs(visual_gap_cue - precontact_shear) + 0.44 * noise + 0.36 * occlusion + 0.24 * alias + rng.normal(0.0, 0.035), 0.0, 1.0)
    lead_time = clamp(0.54 + 0.30 * visual_quality + 0.20 * tactile_quality - 0.35 * lag - 0.18 * slip_prob + rng.normal(0.0, 0.060), 0.0, 1.0)

    return {
        "seed": seed,
        "task": task_name,
        "split": split_name,
        "episode": episode,
        "stress_level": "" if stress_level is None else stress_level,
        "mu": mu,
        "compliance": compliance,
        "curvature": curvature,
        "fragility": fragility,
        "texture": texture,
        "mass": mass,
        "occlusion": occlusion,
        "noise": noise,
        "lag": lag,
        "texture_alias": alias,
        "approach_angle": approach_angle,
        "normal_force": normal_force,
        "slip_probability": slip_prob,
        "slip_event": slip_event,
        "visual_quality": visual_quality,
        "tactile_quality": tactile_quality,
        "visual_gap_cue": visual_gap_cue,
        "precontact_shear": precontact_shear,
        "force_derivative": force_derivative,
        "friction_prior": friction_prior,
        "compliance_est": compliance_est,
        "optical_tactile": optical_tactile,
        "uncertainty": uncertainty,
        "lead_time": lead_time,
    }


def method_score(case, method):
    rng = np.random.default_rng(
        BASE_SEED + stable_offset("method", method, case["task"], case["split"], case["seed"], case["episode"], case["stress_level"])
    )
    v = case["visual_gap_cue"]
    s = case["precontact_shear"]
    f = case["force_derivative"]
    fp = case["friction_prior"]
    c = case["compliance_est"]
    o = case["optical_tactile"]
    u = case["uncertainty"]
    angle = case["approach_angle"]
    lag = case["lag"]
    noise = case["noise"]

    if method == "vision_gap_threshold":
        raw = 0.72 * v + 0.12 * angle + 0.08 * case["curvature"] - 0.08 * case["texture_alias"]
        sigma = 0.120 + 0.08 * case["occlusion"]
    elif method == "normal_force_threshold":
        raw = 0.40 * case["normal_force"] + 0.20 * c + 0.12 * case["mass"]
        sigma = 0.190 + 0.10 * noise
    elif method == "force_derivative_detector":
        raw = 0.64 * f + 0.12 * case["normal_force"] - 0.05 * lag
        sigma = 0.180 + 0.10 * noise
    elif method == "friction_cone_margin":
        raw = 0.48 * fp + 0.30 * s + 0.14 * angle + 0.08 * c
        sigma = 0.135 + 0.06 * noise
    elif method == "tactile_temporal_filter":
        raw = 0.42 * s + 0.36 * f + 0.10 * c - 0.18 * lag
        sigma = 0.170 + 0.10 * noise
    elif method == "optical_tactile_classifier":
        raw = 0.42 * o + 0.28 * v + 0.22 * s + 0.07 * fp - 0.06 * case["texture_alias"]
        sigma = 0.105 + 0.08 * noise
    elif method == "ensemble_uncertainty_guard":
        raw = 0.30 * v + 0.24 * s + 0.18 * fp + 0.14 * o + 0.28 * u
        sigma = 0.120 + 0.06 * noise
    elif method == "conformal_precontact_risk":
        raw = 0.34 * o + 0.22 * fp + 0.20 * s + 0.16 * c + 0.08 * v - 0.10 * u
        sigma = 0.095 + 0.05 * noise
    elif method == "particle_friction_belief":
        raw = 0.46 * fp + 0.23 * s + 0.15 * o + 0.12 * c + 0.05 * angle
        sigma = 0.085 + 0.05 * noise
    elif method == "mpc_grip_stabilizer":
        raw = 0.28 * fp + 0.25 * s + 0.18 * o + 0.16 * c + 0.10 * u
        sigma = 0.120 + 0.05 * noise
    elif method == "recovery_aware_grasp_mpc":
        raw = 0.26 * fp + 0.24 * s + 0.18 * o + 0.16 * c + 0.12 * u + 0.05 * case["mass"]
        sigma = 0.130 + 0.05 * noise
    elif method == "precontact_microslip_v4":
        raw = 0.35 * s + 0.24 * fp + 0.18 * c + 0.16 * v + 0.15 * u - 0.04 * lag
        sigma = 0.145 + 0.07 * noise
    elif method == PROPOSAL:
        raw = 0.28 * s + 0.24 * fp + 0.18 * o + 0.16 * c + 0.11 * v + 0.05 * u - 0.08 * lag
        sigma = 0.105 + 0.06 * noise
    elif method == ORACLE:
        raw = 0.92 * case["slip_probability"] + 0.04 * s + 0.04 * fp
        sigma = 0.035
    elif method == "full_precontact_microslip_v5":
        raw = 0.28 * s + 0.24 * fp + 0.18 * o + 0.16 * c + 0.11 * v + 0.05 * u - 0.08 * lag
        sigma = 0.105 + 0.06 * noise
    elif method == "minus_precontact_shear":
        raw = 0.31 * fp + 0.25 * o + 0.22 * c + 0.15 * v - 0.05 * lag
        sigma = 0.135 + 0.07 * noise
    elif method == "minus_friction_prior":
        raw = 0.35 * s + 0.24 * o + 0.18 * c + 0.14 * v + 0.05 * u - 0.06 * lag
        sigma = 0.125 + 0.07 * noise
    elif method == "minus_compliance_model":
        raw = 0.34 * s + 0.27 * fp + 0.20 * o + 0.12 * v + 0.05 * u - 0.07 * lag
        sigma = 0.120 + 0.07 * noise
    elif method == "minus_latency_margin":
        raw = 0.31 * s + 0.26 * fp + 0.20 * o + 0.15 * c + 0.10 * v + 0.07 * u
        sigma = 0.118 + 0.07 * noise
    elif method == "minus_calibration_layer":
        raw = 0.34 * s + 0.28 * fp + 0.20 * o + 0.18 * c + 0.16 * u
        sigma = 0.145 + 0.09 * noise
    elif method == "minus_visual_gap":
        raw = 0.34 * s + 0.28 * fp + 0.20 * o + 0.17 * c + 0.04 * u - 0.08 * lag
        sigma = 0.115 + 0.07 * noise
    elif method == "minus_recovery_model":
        raw = 0.30 * s + 0.25 * fp + 0.18 * o + 0.16 * c + 0.11 * v - 0.08 * lag
        sigma = 0.110 + 0.06 * noise
    elif method == "vision_only_precontact":
        raw = 0.74 * v + 0.12 * angle + 0.07 * case["curvature"] - 0.08 * case["texture_alias"]
        sigma = 0.120 + 0.08 * case["occlusion"]
    elif method == "force_only_precontact":
        raw = 0.62 * f + 0.16 * case["normal_force"] - 0.04 * lag
        sigma = 0.180 + 0.10 * noise
    else:
        raise KeyError(method)

    return clamp(raw + rng.normal(0.0, sigma))


def evaluate_method(case, method, fixed_risk_budget=None):
    score = method_score(case, method)
    threshold = THRESHOLDS[method]
    if fixed_risk_budget is None:
        trigger = int(score >= threshold)
        accepted = 1
    else:
        # Fixed-risk deployment accepts only low predicted-risk episodes. Hard splits
        # intentionally expose the low-coverage failure mode at strict budgets.
        accept_threshold = fixed_risk_budget + {
            "conformal_precontact_risk": 0.02,
            "particle_friction_belief": 0.01,
            "mpc_grip_stabilizer": 0.015,
            "recovery_aware_grasp_mpc": 0.015,
            "ensemble_uncertainty_guard": -0.015,
            PROPOSAL: 0.00,
        }.get(method, 0.0)
        accepted = int(score <= accept_threshold)
        trigger = int(score >= threshold and accepted)

    profile = ABLATION_PROFILE.get(method, METHOD_PROFILE.get(method))
    if profile is None:
        raise KeyError(method)

    rng = np.random.default_rng(
        BASE_SEED + stable_offset("outcome", method, fixed_risk_budget, case["task"], case["split"], case["seed"], case["episode"], case["stress_level"])
    )
    needed_lead = profile["delay"] + 0.50 * case["lag"] + 0.08 * case["noise"]
    early_warning = int(trigger and case["slip_event"] and case["lead_time"] > needed_lead)
    false_alarm = int(trigger and not case["slip_event"])
    late_alarm = int(trigger and case["slip_event"] and not early_warning)

    raw_protection = early_warning * profile["effect"] + late_alarm * profile["effect"] * 0.30
    recovery_bonus = profile["recovery"] * (0.4 + 0.6 * trigger)
    false_alarm_penalty = false_alarm * (0.055 + 0.075 * profile["cost"])
    base_difficulty = (
        0.16
        + 0.50 * case["slip_event"]
        + 0.18 * case["fragility"]
        + 0.13 * case["curvature"]
        + 0.10 * case["compliance"]
        + 0.08 * case["mass"]
        + 0.10 * case["noise"]
        + 0.08 * case["lag"]
    )
    success_prob = clamp(0.82 - base_difficulty + 0.76 * raw_protection + 0.60 * recovery_bonus - false_alarm_penalty)
    task_success = int(rng.random() < success_prob and accepted)

    gross_slip_prob = clamp(
        0.05
        + 0.70 * case["slip_event"]
        + 0.12 * case["lag"]
        + 0.10 * case["compliance"]
        - 0.62 * raw_protection
        - 0.22 * recovery_bonus
        + 0.03 * false_alarm
    )
    gross_slip = int(rng.random() < gross_slip_prob and accepted)
    damage_prob = clamp(
        0.03
        + 0.23 * case["fragility"] * case["slip_event"]
        + 0.09 * case["fragility"] * gross_slip
        + 0.08 * false_alarm * profile["cost"]
        - 0.12 * raw_protection
        - 0.06 * recovery_bonus
    )
    damage = int(rng.random() < damage_prob and accepted)

    intervention_cost = 0.04 + trigger * profile["cost"] + false_alarm * (0.10 + 0.08 * profile["cost"]) + 0.06 * case["lag"]
    control_chatter = trigger * profile["chatter"] * (0.45 + 0.55 * case["uncertainty"]) + false_alarm * 0.08
    recovery_success = int(case["slip_event"] and task_success and (early_warning or recovery_bonus > 0.07))
    lead_margin = max(0.0, case["lead_time"] - needed_lead) if trigger else 0.0
    robust_utility = (
        task_success
        - 0.48 * gross_slip
        - 0.42 * damage
        - 0.18 * intervention_cost
        - 0.16 * false_alarm
        - 0.10 * control_chatter
    )

    return {
        "seed": case["seed"],
        "task": case["task"],
        "split": case["split"],
        "episode": case["episode"],
        "stress_level": case["stress_level"],
        "method": method,
        "threshold": threshold,
        "score": score,
        "slip_event": case["slip_event"],
        "slip_probability": case["slip_probability"],
        "accepted": accepted,
        "triggered": trigger,
        "early_warning": early_warning,
        "false_alarm": false_alarm,
        "lead_time_margin": lead_margin,
        "task_success": task_success,
        "gross_slip": gross_slip,
        "damage": damage,
        "intervention_cost": intervention_cost,
        "control_chatter": control_chatter,
        "recovery_success": recovery_success,
        "robust_utility": robust_utility,
    }


def write_csv(path, rows, fieldnames):
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def dataset_row(case):
    return {
        "seed": case["seed"],
        "task": case["task"],
        "split": case["split"],
        "episode": case["episode"],
        "mu": f"{case['mu']:.6f}",
        "compliance": f"{case['compliance']:.6f}",
        "curvature": f"{case['curvature']:.6f}",
        "fragility": f"{case['fragility']:.6f}",
        "texture": f"{case['texture']:.6f}",
        "occlusion": f"{case['occlusion']:.6f}",
        "noise": f"{case['noise']:.6f}",
        "lag": f"{case['lag']:.6f}",
        "texture_alias": f"{case['texture_alias']:.6f}",
        "slip_probability": f"{case['slip_probability']:.6f}",
        "slip_event": case["slip_event"],
        "lead_time": f"{case['lead_time']:.6f}",
    }


def rollout_csv_row(row):
    out = dict(row)
    for key in [
        "threshold",
        "score",
        "slip_probability",
        "lead_time_margin",
        "intervention_cost",
        "control_chatter",
        "robust_utility",
    ]:
        out[key] = f"{float(out[key]):.6f}"
    return out


def summarize_rollouts(rows):
    labels = [int(r["slip_event"]) for r in rows]
    scores = [float(r["score"]) for r in rows]
    positives = sum(labels)
    negatives = len(labels) - positives
    true_positive = sum(int(r["early_warning"]) for r in rows)
    false_alarm_count = sum(int(r["false_alarm"]) for r in rows)
    return {
        "average_precision": average_precision(labels, scores),
        "auroc": auroc(labels, scores),
        "ece": ece(labels, scores),
        "early_recall": true_positive / positives if positives else 0.0,
        "false_alarm_rate": false_alarm_count / negatives if negatives else 0.0,
        "lead_time_margin": mean(float(r["lead_time_margin"]) for r in rows if int(r["triggered"])) if any(int(r["triggered"]) for r in rows) else 0.0,
        "task_success": mean(int(r["task_success"]) for r in rows),
        "gross_slip": mean(int(r["gross_slip"]) for r in rows),
        "damage_rate": mean(int(r["damage"]) for r in rows),
        "intervention_cost": mean(float(r["intervention_cost"]) for r in rows),
        "control_chatter": mean(float(r["control_chatter"]) for r in rows),
        "recovery_success": mean(int(r["recovery_success"]) for r in rows),
        "robust_utility": mean(float(r["robust_utility"]) for r in rows),
    }


def group_by(rows, keys):
    groups = defaultdict(list)
    for row in rows:
        groups[tuple(row[k] for k in keys)].append(row)
    return groups


def seed_metric_rows(rows, keys):
    out = []
    for key, group in sorted(group_by(rows, keys).items()):
        metrics = summarize_rollouts(group)
        row = {k: v for k, v in zip(keys, key)}
        row.update({m: f"{metrics[m]:.6f}" for m in METRICS})
        out.append(row)
    return out


def metric_long_rows(seed_rows, group_keys):
    grouped = defaultdict(list)
    for row in seed_rows:
        key = tuple(row[k] for k in group_keys)
        for metric in METRICS:
            grouped[(key, metric)].append(float(row[metric]))
    out = []
    for (key, metric), values in sorted(grouped.items()):
        row = {k: v for k, v in zip(group_keys, key)}
        row.update({"metric": metric, "mean": f"{mean(values):.6f}", "ci95": f"{ci95(values):.6f}", "n": len(values)})
        out.append(row)
    return out


def pairwise_rows(seed_rows, group_keys, baseline_methods, reference_method=PROPOSAL):
    index = {}
    for row in seed_rows:
        key = tuple(row[k] for k in group_keys) + (row["seed"], row["method"])
        index[key] = row
    out = []
    group_values = sorted(set(tuple(row[k] for k in group_keys) for row in seed_rows))
    for group_key in group_values:
        for baseline in baseline_methods:
            for metric in METRICS:
                diffs = []
                for seed in SEEDS:
                    ref = index.get(group_key + (seed, reference_method))
                    base = index.get(group_key + (seed, baseline))
                    if ref is None or base is None:
                        continue
                    diff = float(ref[metric]) - float(base[metric])
                    diffs.append(diff)
                if diffs:
                    row = {k: v for k, v in zip(group_keys, group_key)}
                    row.update(
                        {
                            "comparison": f"{reference_method}_minus_{baseline}",
                            "metric": metric,
                            "mean": f"{mean(diffs):.6f}",
                            "ci95": f"{ci95(diffs):.6f}",
                            "lower95": f"{mean(diffs) - ci95(diffs):.6f}",
                            "upper95": f"{mean(diffs) + ci95(diffs):.6f}",
                            "better_seeds": sum(1 for d in diffs if d > 0),
                            "n": len(diffs),
                        }
                    )
                    out.append(row)
    return out


def make_main_rollouts():
    dataset_rows = []
    rollout_rows = []
    for seed in SEEDS:
        for task in TASKS:
            for split in SPLITS:
                for episode in range(EPISODES):
                    case = generate_case(task, split, seed, episode)
                    dataset_rows.append(dataset_row(case))
                    for method in METHODS:
                        rollout_rows.append(evaluate_method(case, method))
    return dataset_rows, rollout_rows


def make_ablation_rollouts():
    rows = []
    for seed in SEEDS:
        for task in TASKS:
            for split in HARD_SPLITS:
                for episode in range(EPISODES):
                    case = generate_case(task, split, seed, episode)
                    for method in ABLATIONS:
                        rows.append(evaluate_method(case, method))
    return rows


def make_stress_rollouts():
    rows = []
    for seed in SEEDS:
        for task in TASKS:
            for stress_level in STRESS_LEVELS:
                for method in METHODS:
                    for episode in range(STRESS_EPISODES):
                        case = generate_case(task, "combined_hard_shift", seed, episode, stress_level=stress_level)
                        row = evaluate_method(case, method)
                        row["stress_level"] = stress_level
                        rows.append(row)
    return rows


def make_fixed_risk_rollouts():
    rows = []
    for seed in SEEDS:
        for task in TASKS:
            for split in FIXED_RISK_SPLITS:
                for budget in FIXED_RISK_BUDGETS:
                    for method in FIXED_RISK_METHODS:
                        for episode in range(FIXED_RISK_EPISODES):
                            case = generate_case(task, split, seed, episode)
                            row = evaluate_method(case, method, fixed_risk_budget=budget)
                            row["budget"] = budget
                            rows.append(row)
    return rows


def summarize_fixed_risk(rows):
    seed_out = []
    for key, group in sorted(group_by(rows, ["seed", "split", "budget", "method"]).items()):
        accepted = [r for r in group if int(r["accepted"])]
        coverage = len(accepted) / len(group) if group else 0.0
        metrics = summarize_rollouts(accepted) if accepted else {m: 0.0 for m in METRICS}
        row = {k: v for k, v in zip(["seed", "split", "budget", "method"], key)}
        row.update(
            {
                "coverage": f"{coverage:.6f}",
                "accepted_success": f"{metrics['task_success']:.6f}",
                "accepted_gross_slip": f"{metrics['gross_slip']:.6f}",
                "accepted_damage": f"{metrics['damage_rate']:.6f}",
                "accepted_utility": f"{metrics['robust_utility']:.6f}",
                "accepted_ap": f"{metrics['average_precision']:.6f}",
            }
        )
        seed_out.append(row)

    metric_out = []
    for key, group in sorted(group_by(seed_out, ["split", "budget", "method"]).items()):
        for metric in ["coverage", "accepted_success", "accepted_gross_slip", "accepted_damage", "accepted_utility", "accepted_ap"]:
            values = [float(r[metric]) for r in group]
            row = {k: v for k, v in zip(["split", "budget", "method"], key)}
            row.update({"metric": metric, "mean": f"{mean(values):.6f}", "ci95": f"{ci95(values):.6f}", "n": len(values)})
            metric_out.append(row)

    pairwise = []
    index = {}
    for row in seed_out:
        index[(row["seed"], row["split"], row["budget"], row["method"])] = row
    for split in FIXED_RISK_SPLITS:
        for budget in FIXED_RISK_BUDGETS:
            for baseline in [m for m in FIXED_RISK_METHODS if m != PROPOSAL]:
                for metric in ["coverage", "accepted_success", "accepted_gross_slip", "accepted_damage", "accepted_utility", "accepted_ap"]:
                    diffs = []
                    for seed in SEEDS:
                        ref = index[(seed, split, budget, PROPOSAL)]
                        base = index[(seed, split, budget, baseline)]
                        diffs.append(float(ref[metric]) - float(base[metric]))
                    pairwise.append(
                        {
                            "split": split,
                            "budget": budget,
                            "comparison": f"{PROPOSAL}_minus_{baseline}",
                            "metric": metric,
                            "mean": f"{mean(diffs):.6f}",
                            "ci95": f"{ci95(diffs):.6f}",
                            "lower95": f"{mean(diffs) - ci95(diffs):.6f}",
                            "upper95": f"{mean(diffs) + ci95(diffs):.6f}",
                            "better_seeds": sum(1 for d in diffs if d > 0),
                            "n": len(diffs),
                        }
                    )
    return seed_out, metric_out, pairwise


def hard_aggregate_rows(rollouts):
    hard = [r for r in rollouts if r["split"] in HARD_SPLITS]
    return seed_metric_rows(hard, ["seed", "method"])


def make_negative_cases(main_rows):
    by_case = defaultdict(dict)
    for row in main_rows:
        if row["split"] in HARD_SPLITS:
            key = (row["seed"], row["task"], row["split"], row["episode"])
            by_case[key][row["method"]] = row

    cases = []
    for key, methods in sorted(by_case.items()):
        if PROPOSAL not in methods:
            continue
        v5 = methods[PROPOSAL]
        candidates = [m for m in ["recovery_aware_grasp_mpc", "mpc_grip_stabilizer", "conformal_precontact_risk", "particle_friction_belief", "ensemble_uncertainty_guard"] if m in methods]
        best = max(candidates, key=lambda m: float(methods[m]["robust_utility"])) if candidates else ""
        best_row = methods.get(best, {})
        failure_mode = None
        if int(v5["slip_event"]) and not int(v5["task_success"]) and best and int(best_row["task_success"]):
            failure_mode = "baseline_recovers_v5_fails"
        elif int(v5["false_alarm"]) and float(v5["intervention_cost"]) > 0.35:
            failure_mode = "false_positive_burden"
        elif int(v5["slip_event"]) and not int(v5["triggered"]):
            failure_mode = "missed_precontact_slip"
        elif int(v5["slip_event"]) and all(not int(methods[m]["task_success"]) for m in candidates if m in methods):
            failure_mode = "all_non_oracle_fail"
        if failure_mode:
            seed, task, split, episode = key
            cases.append(
                {
                    "case_id": len(cases) + 1,
                    "seed": seed,
                    "task": task,
                    "split": split,
                    "episode": episode,
                    "failure_mode": failure_mode,
                    "slip_event": v5["slip_event"],
                    "v5_score": f"{float(v5['score']):.6f}",
                    "v5_success": v5["task_success"],
                    "v5_false_alarm": v5["false_alarm"],
                    "v5_cost": f"{float(v5['intervention_cost']):.6f}",
                    "best_baseline": best,
                    "best_baseline_success": best_row.get("task_success", ""),
                    "best_baseline_utility": f"{float(best_row.get('robust_utility', 0.0)):.6f}" if best_row else "",
                }
            )
        if len(cases) >= 24:
            break
    return cases


def metric_lookup(metric_rows, group_keys):
    out = {}
    for row in metric_rows:
        key = tuple(row[k] for k in group_keys) + (row["metric"],)
        out[key] = float(row["mean"])
    return out


def seed_lookup(seed_rows, key_fields):
    return {tuple(row[k] for k in key_fields): row for row in seed_rows}


def best_reference(hard_metrics, metric, lower_is_better=False, exclude_oracle=True):
    candidates = [r for r in hard_metrics if r["metric"] == metric]
    if exclude_oracle:
        candidates = [r for r in candidates if r["method"] != ORACLE]
    return min(candidates, key=lambda r: float(r["mean"])) if lower_is_better else max(candidates, key=lambda r: float(r["mean"]))


def pairwise_stat(hard_pairwise, baseline, metric):
    comp = f"{PROPOSAL}_minus_{baseline}"
    for row in hard_pairwise:
        if row["comparison"] == comp and row["metric"] == metric:
            return row
    return None


def plot_bar(path, title, labels, series):
    fig, ax = plt.subplots(figsize=(12, 5))
    x = np.arange(len(labels))
    width = 0.8 / len(series)
    for i, (name, values) in enumerate(series.items()):
        ax.bar(x + i * width - 0.4 + width / 2, values, width=width, label=name)
    ax.set_title(title)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=35, ha="right")
    ax.grid(axis="y", alpha=0.25)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)


def make_figures(hard_metric_rows, ablation_metric_rows, stress_metric_rows, fixed_metric_rows):
    hard = metric_lookup(hard_metric_rows, ["method"])
    labels = [m for m in METHODS if m != ORACLE]
    plot_bar(
        FIGURES / "microslip_hard_prediction_v5.png",
        "Hard-Aggregate Prediction and Burden",
        labels,
        {
            "AP": [hard[(m, "average_precision")] for m in labels],
            "Early recall": [hard[(m, "early_recall")] for m in labels],
            "False alarm": [hard[(m, "false_alarm_rate")] for m in labels],
        },
    )
    plot_bar(
        FIGURES / "microslip_control_outcomes_v5.png",
        "Hard-Aggregate Control Outcomes",
        labels,
        {
            "Success": [hard[(m, "task_success")] for m in labels],
            "Gross slip": [hard[(m, "gross_slip")] for m in labels],
            "Utility": [hard[(m, "robust_utility")] for m in labels],
        },
    )

    ab = metric_lookup(ablation_metric_rows, ["method"])
    plot_bar(
        FIGURES / "microslip_ablation_v5.png",
        "Ablation Utility and Prediction",
        ABLATIONS,
        {
            "AP": [ab[(m, "average_precision")] for m in ABLATIONS],
            "Utility": [ab[(m, "robust_utility")] for m in ABLATIONS],
        },
    )

    stress_lookup = metric_lookup(stress_metric_rows, ["stress_level", "method"])
    fig, ax = plt.subplots(figsize=(10, 5))
    shown = [PROPOSAL, "conformal_precontact_risk", "particle_friction_belief", "recovery_aware_grasp_mpc", "optical_tactile_classifier", "ensemble_uncertainty_guard"]
    for method in shown:
        ax.plot(STRESS_LEVELS, [stress_lookup[(level, method, "robust_utility")] for level in STRESS_LEVELS], marker="o", label=method)
    ax.set_title("Combined Stress Sweep: Robust Utility")
    ax.set_xlabel("Stress level")
    ax.set_ylabel("Robust utility")
    ax.grid(alpha=0.25)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(FIGURES / "microslip_stress_sweep_v5.png", dpi=180)
    plt.close(fig)

    fixed_lookup = metric_lookup(fixed_metric_rows, ["split", "budget", "method"])
    fig, ax = plt.subplots(figsize=(10, 5))
    for method in FIXED_RISK_METHODS:
        values = []
        for budget in FIXED_RISK_BUDGETS:
            vals = [fixed_lookup[(split, budget, method, "coverage")] for split in FIXED_RISK_SPLITS]
            values.append(mean(vals))
        ax.plot(FIXED_RISK_BUDGETS, values, marker="o", label=method)
    ax.set_title("Fixed-Risk Coverage on Hard Splits")
    ax.set_xlabel("Risk budget")
    ax.set_ylabel("Accepted coverage")
    ax.grid(alpha=0.25)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(FIGURES / "microslip_fixed_risk_v5.png", dpi=180)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 6))
    for method in labels:
        ax.scatter(hard[(method, "false_alarm_rate")], hard[(method, "task_success")], s=60)
        ax.text(hard[(method, "false_alarm_rate")] + 0.004, hard[(method, "task_success")] + 0.002, method, fontsize=7)
    ax.set_title("Success vs False-Alarm Burden")
    ax.set_xlabel("False-alarm rate")
    ax.set_ylabel("Task success")
    ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(FIGURES / "microslip_pareto_v5.png", dpi=180)
    plt.close(fig)


def write_summary(
    main_rows,
    dataset_rows,
    seed_rows_main,
    metric_rows_main,
    pairwise_main,
    hard_seed_rows,
    hard_metric_rows,
    hard_pairwise,
    ablation_rows,
    ablation_seed_rows,
    ablation_metric_rows,
    stress_rows,
    stress_seed_rows,
    stress_metric_rows,
    fixed_rows,
    fixed_seed_rows,
    fixed_metric_rows,
    fixed_pairwise,
    negative_cases,
):
    best_ap = best_reference(hard_metric_rows, "average_precision")
    best_success = best_reference(hard_metric_rows, "task_success")
    safest = best_reference(hard_metric_rows, "gross_slip", lower_is_better=True)
    lowest_damage = best_reference(hard_metric_rows, "damage_rate", lower_is_better=True)
    lowest_cost = best_reference(hard_metric_rows, "intervention_cost", lower_is_better=True)
    best_utility = best_reference(hard_metric_rows, "robust_utility")
    best_calibration = best_reference(hard_metric_rows, "ece", lower_is_better=True)
    lowest_false_alarm = best_reference(hard_metric_rows, "false_alarm_rate", lower_is_better=True)
    hard = metric_lookup(hard_metric_rows, ["method"])
    proposal = {m: hard[(PROPOSAL, m)] for m in METRICS}

    ap_pair = pairwise_stat(hard_pairwise, best_ap["method"], "average_precision")
    success_pair = pairwise_stat(hard_pairwise, best_success["method"], "task_success")
    gross_pair = pairwise_stat(hard_pairwise, safest["method"], "gross_slip")
    utility_pair = pairwise_stat(hard_pairwise, best_utility["method"], "robust_utility")

    ab = metric_lookup(ablation_metric_rows, ["method"])
    best_ablation = max(ABLATIONS, key=lambda m: ab[(m, "robust_utility")])
    mechanism_gate = best_ablation == "full_precontact_microslip_v5"

    stress = metric_lookup(stress_metric_rows, ["stress_level", "method"])
    max_level = STRESS_LEVELS[-1]
    stress_candidates = [m for m in NON_ORACLE if m != PROPOSAL]
    stress_best = max(stress_candidates, key=lambda m: stress[(max_level, m, "robust_utility")])
    stress_gate = stress[(max_level, PROPOSAL, "robust_utility")] >= stress[(max_level, stress_best, "robust_utility")]

    fixed = metric_lookup(fixed_metric_rows, ["split", "budget", "method"])
    fixed_gate = all(fixed[(split, 0.05, PROPOSAL, "coverage")] > 0.0 for split in FIXED_RISK_SPLITS)

    main_gate = float(ap_pair["lower95"]) > 0.0 if ap_pair else False
    control_gate = float(success_pair["lower95"]) > 0.0 if success_pair else False
    safety_gate = float(gross_pair["upper95"]) <= 0.0 if gross_pair else False
    utility_gate = float(utility_pair["lower95"]) > 0.0 if utility_pair else False
    calibration_gate = proposal["ece"] <= float(best_calibration["mean"])
    burden_gate = proposal["false_alarm_rate"] <= float(lowest_false_alarm["mean"]) + 0.05 and proposal["intervention_cost"] <= float(lowest_cost["mean"]) + 0.05
    scope_gate = False

    lines = [
        "Paper 91 micro_slip_precontact_prediction v5 expanded audit",
        "Terminal recommendation: KILL_ARCHIVE",
        "ICLR main ready: no",
        "Reason: expanded CPU-only micro-slip/precontact audit adds stronger optical-tactile, conformal, particle-friction, MPC, recovery-aware, ablation, stress, and fixed-risk tests, but no real robot or accepted high-fidelity tactile benchmark evidence exists.",
        f"Main rollout rows: {len(main_rows)}",
        f"Dataset summary rows: {len(dataset_rows)}",
        f"Main seed-metric rows: {len(seed_rows_main)}",
        f"Main metric rows: {len(metric_rows_main)}",
        f"Main pairwise rows: {len(pairwise_main)}",
        f"Hard aggregate seed rows: {len(hard_seed_rows)}",
        f"Hard aggregate metric rows: {len(hard_metric_rows)}",
        f"Hard aggregate pairwise rows: {len(hard_pairwise)}",
        f"Ablation rollout rows: {len(ablation_rows)}",
        f"Ablation seed rows: {len(ablation_seed_rows)}",
        f"Ablation metric rows: {len(ablation_metric_rows)}",
        f"Stress raw rows: {len(stress_rows)}",
        f"Stress seed rows: {len(stress_seed_rows)}",
        f"Stress metric rows: {len(stress_metric_rows)}",
        f"Fixed-risk raw rows: {len(fixed_rows)}",
        f"Fixed-risk seed rows: {len(fixed_seed_rows)}",
        f"Fixed-risk metric rows: {len(fixed_metric_rows)}",
        f"Fixed-risk pairwise rows: {len(fixed_pairwise)}",
        f"Negative cases: {len(negative_cases)}",
        "",
        "Frozen hard-aggregate gate:",
        f"best_ap_reference={best_ap['method']}",
        f"best_success_reference={best_success['method']}",
        f"safest_reference={safest['method']}",
        f"lowest_damage_reference={lowest_damage['method']}",
        f"lowest_cost_reference={lowest_cost['method']}",
        f"best_calibration_reference={best_calibration['method']}",
        f"lowest_false_alarm_reference={lowest_false_alarm['method']}",
        f"best_utility_reference={best_utility['method']}",
        f"proposal_ap={proposal['average_precision']:.5f}",
        f"best_ap={float(best_ap['mean']):.5f}",
        f"proposal_success={proposal['task_success']:.5f}",
        f"best_success={float(best_success['mean']):.5f}",
        f"proposal_gross_slip={proposal['gross_slip']:.5f}",
        f"safest_gross_slip={float(safest['mean']):.5f}",
        f"proposal_damage={proposal['damage_rate']:.5f}",
        f"lowest_damage={float(lowest_damage['mean']):.5f}",
        f"proposal_false_alarm={proposal['false_alarm_rate']:.5f}",
        f"lowest_false_alarm={float(lowest_false_alarm['mean']):.5f}",
        f"proposal_cost={proposal['intervention_cost']:.5f}",
        f"lowest_cost={float(lowest_cost['mean']):.5f}",
        f"proposal_ece={proposal['ece']:.5f}",
        f"best_ece={float(best_calibration['mean']):.5f}",
        f"proposal_utility={proposal['robust_utility']:.5f}",
        f"best_utility={float(best_utility['mean']):.5f}",
        f"paired_ap_lower95={float(ap_pair['lower95']) if ap_pair else 0.0:.5f}",
        f"paired_success_lower95={float(success_pair['lower95']) if success_pair else 0.0:.5f}",
        f"paired_gross_slip_upper95={float(gross_pair['upper95']) if gross_pair else 0.0:.5f}",
        f"paired_utility_lower95={float(utility_pair['lower95']) if utility_pair else 0.0:.5f}",
        f"main_gate={main_gate}",
        f"control_gate={control_gate}",
        f"safety_gate={safety_gate}",
        f"calibration_gate={calibration_gate}",
        f"burden_gate={burden_gate}",
        f"mechanism_gate={mechanism_gate}",
        f"mechanism_best_ablation={best_ablation}",
        f"stress_gate={stress_gate}",
        f"stress_dominated_by={stress_best}",
        f"fixed_risk_gate={fixed_gate}",
        f"scope_gate={scope_gate}",
    ]

    for split in FIXED_RISK_SPLITS:
        lines.append(
            f"{split}: v5_coverage={fixed[(split, 0.05, PROPOSAL, 'coverage')]:.5f}, "
            f"v5_success={fixed[(split, 0.05, PROPOSAL, 'accepted_success')]:.5f}, "
            f"v5_gross_slip={fixed[(split, 0.05, PROPOSAL, 'accepted_gross_slip')]:.5f}"
        )

    lines.extend(["", "Hard aggregate metrics:"])
    for method in METHODS:
        vals = {metric: hard[(method, metric)] for metric in METRICS}
        lines.append(
            f"{method} ap={vals['average_precision']:.5f} auroc={vals['auroc']:.5f} ece={vals['ece']:.5f} "
            f"early={vals['early_recall']:.5f} false_alarm={vals['false_alarm_rate']:.5f} "
            f"success={vals['task_success']:.5f} gross={vals['gross_slip']:.5f} damage={vals['damage_rate']:.5f} "
            f"cost={vals['intervention_cost']:.5f} utility={vals['robust_utility']:.5f}"
        )

    lines.extend(["", "Key paired hard-aggregate differences:"])
    for row in hard_pairwise:
        if row["comparison"] in {
            f"{PROPOSAL}_minus_{best_ap['method']}",
            f"{PROPOSAL}_minus_{best_success['method']}",
            f"{PROPOSAL}_minus_{safest['method']}",
            f"{PROPOSAL}_minus_{best_utility['method']}",
            f"{PROPOSAL}_minus_precontact_microslip_v4",
        }:
            lines.append(
                f"{row['comparison']} {row['metric']}: mean={row['mean']} ci95={row['ci95']} "
                f"lower95={row['lower95']} upper95={row['upper95']}"
            )

    lines.extend(["", "Ablation utility:"])
    for method in ABLATIONS:
        lines.append(
            f"{method} ap={ab[(method, 'average_precision')]:.5f} success={ab[(method, 'task_success')]:.5f} "
            f"gross={ab[(method, 'gross_slip')]:.5f} false_alarm={ab[(method, 'false_alarm_rate')]:.5f} "
            f"utility={ab[(method, 'robust_utility')]:.5f}"
        )

    lines.extend(["", "Maximum combined stress:"])
    for method in [m for m in METHODS if m != ORACLE]:
        lines.append(
            f"{method} ap={stress[(max_level, method, 'average_precision')]:.5f} "
            f"success={stress[(max_level, method, 'task_success')]:.5f} "
            f"gross={stress[(max_level, method, 'gross_slip')]:.5f} "
            f"utility={stress[(max_level, method, 'robust_utility')]:.5f}"
        )

    lines.extend(["", "Fixed-risk budget 0.05:"])
    for split in FIXED_RISK_SPLITS:
        for method in FIXED_RISK_METHODS:
            lines.append(
                f"{split} {method} coverage={fixed[(split, 0.05, method, 'coverage')]:.5f} "
                f"accepted_success={fixed[(split, 0.05, method, 'accepted_success')]:.5f} "
                f"accepted_gross_slip={fixed[(split, 0.05, method, 'accepted_gross_slip')]:.5f} "
                f"accepted_damage={fixed[(split, 0.05, method, 'accepted_damage')]:.5f}"
            )

    lines.extend(["", f"Negative cases: {len(negative_cases)}", "terminal=KILL_ARCHIVE"])
    (RESULTS / "summary.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    dataset_rows, main_rows = make_main_rollouts()
    ablation_rows = make_ablation_rollouts()
    stress_rows = make_stress_rollouts()
    fixed_rows = make_fixed_risk_rollouts()
    negative_cases = make_negative_cases(main_rows)

    write_csv(RESULTS / "dataset_summary.csv", dataset_rows, list(dataset_rows[0].keys()))
    write_csv(RESULTS / "rollouts.csv", [rollout_csv_row(r) for r in main_rows], list(rollout_csv_row(main_rows[0]).keys()))
    write_csv(RESULTS / "ablation_rollouts.csv", [rollout_csv_row(r) for r in ablation_rows], list(rollout_csv_row(ablation_rows[0]).keys()))
    write_csv(RESULTS / "stress_sweep_raw.csv", [rollout_csv_row(r) for r in stress_rows], list(rollout_csv_row(stress_rows[0]).keys()))

    fixed_fieldnames = list(rollout_csv_row(fixed_rows[0]).keys()) + ["budget"]
    write_csv(RESULTS / "fixed_risk_raw.csv", [rollout_csv_row(r) for r in fixed_rows], fixed_fieldnames)
    write_csv(RESULTS / "negative_cases.csv", negative_cases, list(negative_cases[0].keys()))

    seed_rows_main = seed_metric_rows(main_rows, ["seed", "split", "method"])
    metric_rows_main = metric_long_rows(seed_rows_main, ["split", "method"])
    pairwise_main = pairwise_rows(seed_rows_main, ["split"], [m for m in NON_ORACLE if m != PROPOSAL])

    hard_seed_rows = hard_aggregate_rows(main_rows)
    hard_metric_rows = metric_long_rows(hard_seed_rows, ["method"])
    hard_pairwise = pairwise_rows(hard_seed_rows, [], [m for m in NON_ORACLE if m != PROPOSAL])

    ablation_seed_rows = seed_metric_rows(ablation_rows, ["seed", "method"])
    ablation_metric_rows = metric_long_rows(ablation_seed_rows, ["method"])

    stress_seed_rows = seed_metric_rows(stress_rows, ["seed", "stress_level", "method"])
    stress_metric_rows = metric_long_rows(stress_seed_rows, ["stress_level", "method"])

    fixed_seed_rows, fixed_metric_rows, fixed_pairwise = summarize_fixed_risk(fixed_rows)

    write_csv(RESULTS / "raw_seed_metrics.csv", seed_rows_main, list(seed_rows_main[0].keys()))
    write_csv(RESULTS / "metrics.csv", metric_rows_main, list(metric_rows_main[0].keys()))
    write_csv(RESULTS / "pairwise_stats.csv", pairwise_main, list(pairwise_main[0].keys()))
    write_csv(RESULTS / "hard_aggregate_seed_metrics.csv", hard_seed_rows, list(hard_seed_rows[0].keys()))
    write_csv(RESULTS / "hard_aggregate_metrics.csv", hard_metric_rows, list(hard_metric_rows[0].keys()))
    write_csv(RESULTS / "hard_aggregate_pairwise_stats.csv", hard_pairwise, list(hard_pairwise[0].keys()))
    write_csv(RESULTS / "ablation_seed_metrics.csv", ablation_seed_rows, list(ablation_seed_rows[0].keys()))
    write_csv(RESULTS / "ablation_metrics.csv", ablation_metric_rows, list(ablation_metric_rows[0].keys()))
    write_csv(RESULTS / "ablation_metric_long.csv", ablation_metric_rows, list(ablation_metric_rows[0].keys()))
    write_csv(RESULTS / "stress_sweep_seed_metrics.csv", stress_seed_rows, list(stress_seed_rows[0].keys()))
    write_csv(RESULTS / "stress_sweep.csv", stress_metric_rows, list(stress_metric_rows[0].keys()))
    write_csv(RESULTS / "stress_sweep_metric_long.csv", stress_metric_rows, list(stress_metric_rows[0].keys()))
    write_csv(RESULTS / "fixed_risk_seed_metrics.csv", fixed_seed_rows, list(fixed_seed_rows[0].keys()))
    write_csv(RESULTS / "fixed_risk_metrics.csv", fixed_metric_rows, list(fixed_metric_rows[0].keys()))
    write_csv(RESULTS / "fixed_risk_pairwise.csv", fixed_pairwise, list(fixed_pairwise[0].keys()))

    make_figures(hard_metric_rows, ablation_metric_rows, stress_metric_rows, fixed_metric_rows)
    write_summary(
        main_rows,
        dataset_rows,
        seed_rows_main,
        metric_rows_main,
        pairwise_main,
        hard_seed_rows,
        hard_metric_rows,
        hard_pairwise,
        ablation_rows,
        ablation_seed_rows,
        ablation_metric_rows,
        stress_rows,
        stress_seed_rows,
        stress_metric_rows,
        fixed_rows,
        fixed_seed_rows,
        fixed_metric_rows,
        fixed_pairwise,
        negative_cases,
    )
    print("Paper 91 v5 expanded audit complete")
    print((RESULTS / "summary.txt").read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
