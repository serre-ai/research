#!/usr/bin/env python3
"""Analyze cross-model verification results for verification-complexity paper.

Implements all pre-registered analyses from spec.yaml:

Primary:
  1. Verification accuracy by VC class (one-way ANOVA + pairwise Bonferroni)
  2. Cross-model consistency within VC class (ICC)
  3. Two-way ANOVA (generator x VC class interaction)
  3a. Generator x VC interaction ANOVA with partial eta-squared effect sizes

Theorem 2c:
  4. Between-model error agreement per task (Cochran's Q)
  4a. Consolidated Theorem 2c: agreement + phi + non-monotonicity + ranking
  5. Phi coefficients for pairwise error correlation

Secondary:
  6. Difficulty scaling (linear regression)
  7. Error type analysis for B7 (3-SAT)
  8. Latency by VC class (Kruskal-Wallis)

Generates 3 publication-ready figures + LaTeX output (stats.tex, table2.tex).

Usage:
    python analyze_verification_results.py --results results/verify_*.jsonl
    python analyze_verification_results.py --results results/verify_*.jsonl --no-figures
    python analyze_verification_results.py --results results/verify_*.jsonl --output-dir results/analysis
"""

from __future__ import annotations

import argparse
import json
import sys
import warnings
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from scipy import stats as sp_stats
from scipy.stats import bootstrap

# ---------------------------------------------------------------------------
# pub_style import (lives in reasoning-gaps/benchmarks/analysis/)
# ---------------------------------------------------------------------------

_THIS_DIR = Path(__file__).resolve().parent
_PUB_STYLE_PATH = (
    _THIS_DIR.parents[1] / "reasoning-gaps" / "benchmarks" / "analysis" / "pub_style.py"
)

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.ticker as mticker
    import seaborn as sns

    # Load pub_style.py directly via importlib to avoid polluting sys.path
    # (the reasoning-gaps analysis dir has a statistics.py that shadows stdlib)
    import importlib.util
    _spec = importlib.util.spec_from_file_location("pub_style", _PUB_STYLE_PATH)
    pub_style = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(pub_style)
    _HAS_PLOTTING = True
except (ImportError, FileNotFoundError, AttributeError):
    _HAS_PLOTTING = False

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

TASKS = ["B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8", "B9"]

VC_CLASS = {
    "B1": "P", "B2": "P", "B3": "P",
    "B4": "P", "B5": "P", "B6": "P",
    "B7": "P/coNP",
    "B8": "Arch", "B9": "Arch",
}

# Known between-model error correlation from reasoning-gaps evaluation.
# All 9 values are computed in error_correlation_results.json (12 models, 500
# instances each, short_cot condition).  The paper text only discusses B2, B3,
# B6, B7 explicitly, but the remaining values are equally legitimate.
KNOWN_RHO = {
    "B1": 0.22, "B2": 0.22, "B3": 0.31,
    "B4": 0.22, "B5": 0.11, "B6": 0.42,
    "B7": 0.06,
    "B8": 0.15, "B9": 0.07,
}

# VC class palette (colorblind-safe)
VC_CLASS_COLORS = {
    "P":      "#0072B2",  # blue
    "P/coNP": "#D55E00",  # vermillion
    "Arch":   "#CC79A7",  # purple
}

VC_CLASS_ORDER = ["P", "P/coNP", "Arch"]


# =====================================================================
# Data loading
# =====================================================================

def load_verification_results(result_files: list[Path]) -> pd.DataFrame:
    """Load all verification results into a DataFrame."""
    records = []
    for f in result_files:
        if not f.exists():
            print(f"Warning: {f} not found, skipping", file=sys.stderr)
            continue

        with open(f) as fh:
            for line_num, line in enumerate(fh, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    record = json.loads(line)
                    records.append(record)
                except json.JSONDecodeError as e:
                    print(f"Warning: corrupt line {line_num} in {f}: {e}", file=sys.stderr)

    if not records:
        raise ValueError("No valid records found in result files")

    df = pd.DataFrame(records)

    # Ensure required columns exist
    required = [
        "task", "vc_class", "verification_accurate", "generator_model",
        "verifier_model", "difficulty", "generator_correct", "verifier_judgment",
    ]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    # Normalize task names: strip file suffixes if present (e.g. "B7_3sat" -> "B7")
    if df["task"].str.contains("_").any():
        df["task_short"] = df["task"].str.extract(r"(B\d+)", expand=False)
    else:
        df["task_short"] = df["task"]

    # Ensure vc_class is set
    if df["vc_class"].isna().any():
        df["vc_class"] = df["task_short"].map(VC_CLASS)

    # Ensure instance_id exists (needed for agreement analyses)
    if "instance_id" not in df.columns:
        df["instance_id"] = (
            df["task"].astype(str) + "_d" + df["difficulty"].astype(str)
            + "_" + df.index.astype(str)
        )

    return df


# =====================================================================
# Bootstrap helper
# =====================================================================

def bootstrap_ci(
    data: np.ndarray,
    confidence: float = 0.95,
    n_bootstrap: int = 1000,
) -> tuple[float, float, float]:
    """Compute mean and bootstrap confidence interval."""
    if len(data) == 0:
        return np.nan, np.nan, np.nan
    mean = float(np.mean(data))
    if len(data) < 2:
        return mean, mean, mean

    rng = np.random.default_rng(42)
    res = bootstrap(
        (data,), np.mean,
        confidence_level=confidence,
        n_resamples=n_bootstrap,
        random_state=rng,
    )
    return mean, float(res.confidence_interval.low), float(res.confidence_interval.high)


# =====================================================================
# Analysis 1: Verification accuracy by VC class
# =====================================================================

def analyze_accuracy_by_vc_class(df: pd.DataFrame) -> dict[str, Any]:
    """Primary Analysis 1: One-way ANOVA + Bonferroni pairwise comparisons."""
    results: dict[str, Any] = {}

    # --- Per-task accuracy ---
    accuracy_by_task: dict[str, dict] = {}
    for task in TASKS:
        task_df = df[df["task_short"] == task]
        if task_df.empty:
            continue
        acc_array = task_df["verification_accurate"].values.astype(float)
        mean, ci_low, ci_high = bootstrap_ci(acc_array)
        accuracy_by_task[task] = {
            "mean": mean, "ci_low": ci_low, "ci_high": ci_high,
            "n": len(acc_array), "vc_class": VC_CLASS.get(task, "?"),
        }
    results["accuracy_by_task"] = accuracy_by_task

    # --- Per-VC-class accuracy ---
    grouped = df.groupby("vc_class")["verification_accurate"].apply(
        lambda x: x.values.astype(float)
    )
    accuracy_by_class: dict[str, dict] = {}
    for vc_class in VC_CLASS_ORDER:
        if vc_class not in grouped.index:
            continue
        arr = grouped[vc_class]
        mean, ci_low, ci_high = bootstrap_ci(arr)
        accuracy_by_class[vc_class] = {
            "mean": mean, "ci_low": ci_low, "ci_high": ci_high, "n": len(arr),
        }
    results["accuracy_by_class"] = accuracy_by_class

    # --- One-way ANOVA ---
    groups = [grouped[vc] for vc in VC_CLASS_ORDER if vc in grouped.index]
    if len(groups) >= 2:
        f_stat, p_value = sp_stats.f_oneway(*groups)
        # Eta-squared effect size
        grand_mean = np.concatenate(groups).mean()
        ss_between = sum(len(g) * (g.mean() - grand_mean) ** 2 for g in groups)
        ss_total = sum(np.sum((g - grand_mean) ** 2) for g in groups)
        eta_sq = ss_between / ss_total if ss_total > 0 else 0.0
        results["anova"] = {
            "f_statistic": float(f_stat),
            "p_value": float(p_value),
            "eta_squared": float(eta_sq),
            "significant": p_value < 0.05,
        }

    # --- Pairwise comparisons (Bonferroni) ---
    vc_list = [vc for vc in VC_CLASS_ORDER if vc in grouped.index]
    n_comparisons = len(vc_list) * (len(vc_list) - 1) // 2
    bonferroni_alpha = 0.05 / n_comparisons if n_comparisons > 0 else 0.05

    pairwise = []
    for i, vc1 in enumerate(vc_list):
        for vc2 in vc_list[i + 1:]:
            g1, g2 = grouped[vc1], grouped[vc2]
            t_stat, p_val = sp_stats.ttest_ind(g1, g2, equal_var=False)
            # Cohen's d
            pooled_std = np.sqrt(
                (np.std(g1, ddof=1) ** 2 + np.std(g2, ddof=1) ** 2) / 2
            )
            cohens_d = float(
                (np.mean(g1) - np.mean(g2)) / pooled_std if pooled_std > 0 else 0
            )
            pairwise.append({
                "pair": f"{vc1} vs {vc2}",
                "t_statistic": float(t_stat),
                "p_value": float(p_val),
                "significant_bonferroni": p_val < bonferroni_alpha,
                "cohens_d": cohens_d,
            })
    results["pairwise_comparisons"] = pairwise
    results["bonferroni_alpha"] = bonferroni_alpha

    return results


# =====================================================================
# Analysis 2: Cross-model consistency (ICC)
# =====================================================================

def analyze_cross_model_consistency(df: pd.DataFrame) -> dict[str, Any]:
    """Primary Analysis 2: ICC within each VC class across model pairs."""
    results: dict[str, Any] = {}
    icc_by_class: dict[str, dict] = {}

    for vc_class in VC_CLASS_ORDER:
        group_df = df[df["vc_class"] == vc_class].copy()
        if group_df.empty:
            continue

        group_df["model_pair"] = (
            group_df["generator_model"] + " -> " + group_df["verifier_model"]
        )

        pivot = group_df.pivot_table(
            index="instance_id",
            columns="model_pair",
            values="verification_accurate",
            aggfunc="first",
        )

        # Need at least 2 instances and 2 raters
        pivot = pivot.dropna()
        n, k = pivot.shape
        if n < 2 or k < 2:
            icc_by_class[vc_class] = {
                "icc": np.nan, "n_instances": n, "n_pairs": k,
            }
            continue

        # ICC(2,1) — two-way random effects, single measurement
        vals = pivot.values.astype(float)
        grand_mean = vals.mean()
        row_means = vals.mean(axis=1)
        col_means = vals.mean(axis=0)

        ss_rows = k * np.sum((row_means - grand_mean) ** 2)
        ss_cols = n * np.sum((col_means - grand_mean) ** 2)
        ss_total = np.sum((vals - grand_mean) ** 2)
        ss_error = ss_total - ss_rows - ss_cols

        ms_rows = ss_rows / (n - 1) if n > 1 else 0
        ms_error = ss_error / ((n - 1) * (k - 1)) if ((n - 1) * (k - 1)) > 0 else 0
        ms_cols = ss_cols / (k - 1) if k > 1 else 0

        denom = ms_rows + (k - 1) * ms_error + (k / n) * (ms_cols - ms_error)
        icc = float((ms_rows - ms_error) / denom) if denom > 0 else 0.0

        icc_by_class[vc_class] = {
            "icc": icc,
            "n_instances": n,
            "n_pairs": k,
        }

    results["icc_by_class"] = icc_by_class
    return results


# =====================================================================
# Analysis 3a: Two-way ANOVA with effect sizes (generator x VC class)
# =====================================================================

def generator_vc_interaction_anova(df: pd.DataFrame) -> dict[str, Any]:
    """Two-way ANOVA testing whether verification accuracy depends on
    (a) generator model, (b) VC class, and (c) their interaction.

    The interaction term tests whether verification accuracy is independent
    of which generator produced the output — the key prediction from Theorem 1
    that verification complexity is an architectural property, not a
    model-specific one.

    Returns F-statistics, p-values, and partial eta-squared effect sizes
    for each factor.

    Tries statsmodels for a proper Type II ANOVA. Falls back to manual
    computation (sequential SS) if statsmodels is unavailable.
    """
    results: dict[str, Any] = {}

    # Cell means for interpretability
    cell_means = df.groupby(["generator_model", "vc_class"])[
        "verification_accurate"
    ].mean().unstack(fill_value=np.nan)
    results["cell_means"] = cell_means.to_dict()

    try:
        import statsmodels.api as sm
        from statsmodels.formula.api import ols

        df_anova = df[["verification_accurate", "generator_model", "vc_class"]].copy()
        df_anova["verification_accurate"] = df_anova["verification_accurate"].astype(float)
        df_anova["gen"] = df_anova["generator_model"].astype(str)
        df_anova["vc"] = df_anova["vc_class"].astype(str)

        model = ols("verification_accurate ~ C(gen) * C(vc)", data=df_anova).fit()
        anova_table = sm.stats.anova_lm(model, typ=2)

        results["method"] = "statsmodels_type2"

        # Extract SS_residual for partial eta-squared computation
        ss_residual = float(anova_table.loc["Residual", "sum_sq"])

        results["factors"] = {}
        for idx in anova_table.index:
            row = anova_table.loc[idx]
            ss = float(row.get("sum_sq", 0))
            f_val = float(row.get("F", 0)) if not np.isnan(row.get("F", np.nan)) else None
            p_val = float(row.get("PR(>F)", 1)) if not np.isnan(row.get("PR(>F)", np.nan)) else None

            # Partial eta-squared: SS_effect / (SS_effect + SS_residual)
            if idx != "Residual" and (ss + ss_residual) > 0:
                partial_eta_sq = ss / (ss + ss_residual)
            else:
                partial_eta_sq = None

            results["factors"][str(idx)] = {
                "sum_sq": ss,
                "df": float(row.get("df", 0)),
                "F": f_val,
                "p_value": p_val,
                "partial_eta_sq": float(partial_eta_sq) if partial_eta_sq is not None else None,
            }

        # Extract interaction significance
        interaction_key = [k for k in results["factors"] if ":" in k]
        if interaction_key:
            inter = results["factors"][interaction_key[0]]
            results["interaction_significant"] = (
                inter["p_value"] is not None and inter["p_value"] < 0.05
            )
            results["interaction_p"] = inter["p_value"]
            results["interaction_F"] = inter["F"]
            results["interaction_partial_eta_sq"] = inter["partial_eta_sq"]
        else:
            results["interaction_significant"] = None

    except ImportError:
        # Manual two-way ANOVA (sequential Type I sums of squares)
        results["method"] = "manual_type1"

        y_all = df["verification_accurate"].values.astype(float)
        grand_mean = y_all.mean()
        N = len(y_all)
        ss_total = np.sum((y_all - grand_mean) ** 2)

        # Factor A: generator_model
        gen_groups = df.groupby("generator_model")["verification_accurate"]
        ss_gen = sum(
            len(g) * (g.mean() - grand_mean) ** 2
            for _, g in gen_groups
        )
        df_gen = gen_groups.ngroups - 1

        # Factor B: vc_class
        vc_groups = df.groupby("vc_class")["verification_accurate"]
        ss_vc = sum(
            len(g) * (g.mean() - grand_mean) ** 2
            for _, g in vc_groups
        )
        df_vc = vc_groups.ngroups - 1

        # Interaction: compute cell-level SS
        cell_groups = df.groupby(["generator_model", "vc_class"])["verification_accurate"]
        ss_cells = sum(
            len(g) * (g.mean() - grand_mean) ** 2
            for _, g in cell_groups
        )
        ss_interaction = ss_cells - ss_gen - ss_vc
        if ss_interaction < 0:
            warnings.warn(
                "Negative interaction SS in manual two-way ANOVA "
                f"(ss_interaction={ss_interaction:.4f}); clamping to 0. "
                "Interaction term is unreliable for this unbalanced design."
            )
            ss_interaction = 0.0
        df_interaction = df_gen * df_vc

        ss_error = ss_total - ss_cells
        df_error = N - cell_groups.ngroups

        # Mean squares
        ms_gen = ss_gen / df_gen if df_gen > 0 else 0
        ms_vc = ss_vc / df_vc if df_vc > 0 else 0
        ms_interaction = ss_interaction / df_interaction if df_interaction > 0 else 0
        ms_error = ss_error / df_error if df_error > 0 else 0

        # F-statistics
        f_gen = ms_gen / ms_error if ms_error > 0 else np.nan
        f_vc = ms_vc / ms_error if ms_error > 0 else np.nan
        f_interaction = ms_interaction / ms_error if ms_error > 0 else np.nan

        # p-values (survival function for better numerical precision)
        p_gen = float(sp_stats.f.sf(f_gen, df_gen, df_error)) if not np.isnan(f_gen) else np.nan
        p_vc = float(sp_stats.f.sf(f_vc, df_vc, df_error)) if not np.isnan(f_vc) else np.nan
        p_interaction = float(sp_stats.f.sf(f_interaction, df_interaction, df_error)) if not np.isnan(f_interaction) else np.nan

        # Partial eta-squared: SS_effect / (SS_effect + SS_error)
        eta_gen = float(ss_gen / (ss_gen + ss_error)) if (ss_gen + ss_error) > 0 else None
        eta_vc = float(ss_vc / (ss_vc + ss_error)) if (ss_vc + ss_error) > 0 else None
        eta_interaction = float(ss_interaction / (ss_interaction + ss_error)) if (ss_interaction + ss_error) > 0 else None

        results["factors"] = {
            "C(gen)": {
                "sum_sq": float(ss_gen), "df": float(df_gen),
                "F": float(f_gen), "p_value": p_gen,
                "partial_eta_sq": eta_gen,
            },
            "C(vc)": {
                "sum_sq": float(ss_vc), "df": float(df_vc),
                "F": float(f_vc), "p_value": p_vc,
                "partial_eta_sq": eta_vc,
            },
            "C(gen):C(vc)": {
                "sum_sq": float(ss_interaction), "df": float(df_interaction),
                "F": float(f_interaction), "p_value": p_interaction,
                "partial_eta_sq": eta_interaction,
            },
            "Residual": {
                "sum_sq": float(ss_error), "df": float(df_error),
                "F": None, "p_value": None, "partial_eta_sq": None,
            },
        }
        results["interaction_significant"] = p_interaction < 0.05 if not np.isnan(p_interaction) else None
        results["interaction_p"] = float(p_interaction) if not np.isnan(p_interaction) else None
        results["interaction_F"] = float(f_interaction) if not np.isnan(f_interaction) else None
        results["interaction_partial_eta_sq"] = eta_interaction

    return results


# =====================================================================
# Analysis 3 (legacy wrapper): Two-way ANOVA (generator x VC class)
# =====================================================================

def analyze_two_way_anova(df: pd.DataFrame) -> dict[str, Any]:
    """Primary Analysis 3: generator x VC class interaction.

    Legacy wrapper around generator_vc_interaction_anova(). Converts the
    new ``factors`` dict back to the ``anova_table`` dict expected by
    print_summary() and write_latex_stats().
    """
    raw = generator_vc_interaction_anova(df)

    # Build backward-compatible anova_table from factors
    results: dict[str, Any] = {
        "cell_means": raw.get("cell_means", {}),
        "method": raw.get("method", "unknown"),
        "interaction_significant": raw.get("interaction_significant"),
        "interaction_p": raw.get("interaction_p"),
    }

    anova_table: dict[str, dict] = {}
    for factor_name, factor_data in raw.get("factors", {}).items():
        anova_table[factor_name] = {
            "sum_sq": factor_data.get("sum_sq", 0),
            "df": factor_data.get("df", 0),
            "F": factor_data.get("F"),
            "PR(>F)": factor_data.get("p_value"),
        }
    results["anova_table"] = anova_table

    return results


# =====================================================================
# Analysis 4: Between-model error agreement (Cochran's Q)
# =====================================================================

def cochrans_q(binary_matrix: np.ndarray) -> tuple[float, float, int]:
    """Cochran's Q test for k related dichotomous samples.

    Args:
        binary_matrix: (n_subjects, k_raters) binary matrix (1=success, 0=failure).

    Returns:
        (Q_statistic, p_value, df)

    Implementation follows Cochran (1950). No statsmodels dependency.
    """
    n, k = binary_matrix.shape
    if k < 2 or n < 1:
        return np.nan, np.nan, 0

    # Row totals (T_i) and column totals (C_j)
    T = binary_matrix.sum(axis=1)  # shape (n,)
    C = binary_matrix.sum(axis=0)  # shape (k,)

    T_sum = T.sum()
    T_sq_sum = (T ** 2).sum()
    C_sq_sum = (C ** 2).sum()

    numerator = (k - 1) * (k * C_sq_sum - T_sum ** 2)
    denominator = k * T_sum - T_sq_sum

    if denominator == 0:
        return 0.0, 1.0, k - 1

    Q = float(numerator / denominator)
    df = k - 1
    p_value = float(1 - sp_stats.chi2.cdf(Q, df))

    return Q, p_value, df


def analyze_between_model_agreement(
    df: pd.DataFrame,
    consolidated: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Legacy wrapper: delegates to between_model_error_agreement() and
    converts the result to the old schema expected by print_summary() and
    write_latex_stats().

    Args:
        df: Full verification DataFrame.
        consolidated: Output of between_model_error_agreement(). If provided,
            avoids recomputation.
    """
    if consolidated is None:
        consolidated = between_model_error_agreement(df)

    # Convert per_task -> agreement_by_task (old schema)
    agreement_by_task: dict[str, dict] = {}
    for task, d in consolidated.get("per_task", {}).items():
        agreement_by_task[task] = {
            "agreement_rate": d.get("agreement_rate", np.nan),
            "n_instances": d.get("n_instances", 0),
            "n_raters": d.get("n_raters", 0),
            "cochrans_q": d.get("cochrans_q", np.nan),
            "cochrans_p": d.get("cochrans_p", np.nan),
            "cochrans_df": d.get("cochrans_df", 0),
            "known_rho": d.get("known_rho", np.nan),
            "vc_class": d.get("vc_class", "?"),
        }

    results: dict[str, Any] = {"agreement_by_task": agreement_by_task}

    # Map non_monotonicity -> non_monotonicity_test (old key)
    nm = consolidated.get("non_monotonicity")
    if nm:
        results["non_monotonicity_test"] = {
            "B6_agreement": nm["B6_agreement"],
            "B7_agreement": nm["B7_agreement"],
            "B6_gt_B7": nm["B6_gt_B7"],
            "prediction": "B6 > B7 (shared bottleneck > stochastic)",
        }

    return results


# =====================================================================
# Analysis 5: Phi coefficients for pairwise error correlation
# =====================================================================

def phi_coefficient(x: np.ndarray, y: np.ndarray) -> float:
    """Compute phi coefficient between two binary vectors.

    Phi = (n11*n00 - n10*n01) / sqrt((n1.)(n0.)(n.1)(n.0))

    No sklearn/statsmodels dependency.
    """
    x = x.astype(float)
    y = y.astype(float)
    n = len(x)
    if n == 0:
        return np.nan

    n11 = np.sum(x * y)
    n00 = np.sum((1 - x) * (1 - y))
    n10 = np.sum(x * (1 - y))
    n01 = np.sum((1 - x) * y)

    # Marginals
    n1_dot = n11 + n10
    n0_dot = n01 + n00
    n_dot1 = n11 + n01
    n_dot0 = n10 + n00

    denom = np.sqrt(n1_dot * n0_dot * n_dot1 * n_dot0)
    if denom == 0:
        return 0.0

    return float((n11 * n00 - n10 * n01) / denom)


def analyze_phi_coefficients(df: pd.DataFrame) -> dict[str, Any]:
    """Theorem 2c Analysis 2: Pairwise phi coefficients between verifier error patterns.

    For each task, computes pairwise phi between each pair of (generator, verifier)
    model pairs on their error patterns. The mean phi per task should correlate
    with the known between-model rho from reasoning-gaps.
    """
    results: dict[str, Any] = {}
    phi_by_task: dict[str, dict] = {}

    for task in TASKS:
        task_df = df[df["task_short"] == task].copy()
        if task_df.empty:
            continue

        task_df["rater"] = (
            task_df["generator_model"] + " -> " + task_df["verifier_model"]
        )

        pivot = task_df.pivot_table(
            index="instance_id",
            columns="rater",
            values="verification_accurate",
            aggfunc="first",
        )
        pivot = pivot.dropna()

        n_instances, n_raters = pivot.shape
        if n_instances < 2 or n_raters < 2:
            phi_by_task[task] = {
                "mean_phi": np.nan,
                "n_pairs": 0,
                "n_instances": n_instances,
            }
            continue

        # Compute ERROR patterns (1 = error, 0 = correct)
        error_matrix = 1 - pivot.values.astype(float)
        rater_names = list(pivot.columns)

        phis = []
        pair_details = []
        for i in range(n_raters):
            for j in range(i + 1, n_raters):
                phi = phi_coefficient(error_matrix[:, i], error_matrix[:, j])
                phis.append(phi)
                pair_details.append({
                    "rater_1": rater_names[i],
                    "rater_2": rater_names[j],
                    "phi": phi,
                })

        mean_phi = float(np.mean(phis)) if phis else np.nan

        phi_by_task[task] = {
            "mean_phi": mean_phi,
            "median_phi": float(np.median(phis)) if phis else np.nan,
            "std_phi": float(np.std(phis)) if phis else np.nan,
            "n_pairs": len(phis),
            "n_instances": n_instances,
            "known_rho": KNOWN_RHO.get(task, np.nan),
            "vc_class": VC_CLASS.get(task, "?"),
            "pair_details": pair_details,
        }

    results["phi_by_task"] = phi_by_task

    # Correlation between mean phi and known rho
    tasks_with_both = [
        t for t in TASKS
        if t in phi_by_task
        and not np.isnan(phi_by_task[t].get("mean_phi", np.nan))
        and t in KNOWN_RHO
    ]
    if len(tasks_with_both) >= 3:
        phi_vals = [phi_by_task[t]["mean_phi"] for t in tasks_with_both]
        rho_vals = [KNOWN_RHO[t] for t in tasks_with_both]
        r, p = sp_stats.pearsonr(phi_vals, rho_vals)
        r_s, p_s = sp_stats.spearmanr(phi_vals, rho_vals)
        results["phi_rho_correlation"] = {
            "pearson_r": float(r),
            "pearson_p": float(p),
            "spearman_r": float(r_s),
            "spearman_p": float(p_s),
            "n_tasks": len(tasks_with_both),
            "tasks": tasks_with_both,
        }

    return results


# =====================================================================
# Consolidated Theorem 2c: between-model error agreement analysis
# =====================================================================

def between_model_error_agreement(df: pd.DataFrame) -> dict[str, Any]:
    """Consolidated Theorem 2c analysis: between-model error agreement.

    For each task:
      1. Computes the fraction of instances where all verifiers agree
         (all correct or all incorrect).
      2. Computes pairwise phi coefficients between verifier error patterns.
      3. Compares agreement rates across tasks, with special attention to
         B6 vs B7 for non-monotonicity (Remark 1).
      4. Uses Cochran's Q test for significance of verifier heterogeneity.

    Tests Theorem 2c: error correlation tracks bottleneck type (shared vs
    stochastic), not VC class. B6 (P-class, shared bottleneck, rho=0.42)
    should show higher between-model agreement than B7 (coNP, stochastic,
    rho=0.06).

    Returns a dict with per-task agreement, phi coefficients, non-monotonicity
    test, and cross-task comparison.
    """
    results: dict[str, Any] = {}
    per_task: dict[str, dict] = {}

    for task in TASKS:
        task_df = df[df["task_short"] == task].copy()
        if task_df.empty:
            continue

        # Build rater identity from generator-verifier pair
        task_df["rater"] = (
            task_df["generator_model"] + " -> " + task_df["verifier_model"]
        )

        pivot = task_df.pivot_table(
            index="instance_id",
            columns="rater",
            values="verification_accurate",
            aggfunc="first",
        )
        pivot = pivot.dropna()

        n_instances, n_raters = pivot.shape
        if n_instances < 2 or n_raters < 2:
            per_task[task] = {
                "agreement_rate": np.nan,
                "mean_phi": np.nan,
                "n_instances": n_instances,
                "n_raters": n_raters,
                "cochrans_q": np.nan,
                "cochrans_p": np.nan,
                "vc_class": VC_CLASS.get(task, "?"),
                "known_rho": KNOWN_RHO.get(task, np.nan),
                "pairwise_phis": [],
            }
            continue

        binary = pivot.values.astype(float)

        # --- Agreement rate: fraction where ALL raters agree ---
        row_sums = binary.sum(axis=1)
        all_agree = ((row_sums == 0) | (row_sums == n_raters)).sum()
        agreement_rate = float(all_agree / n_instances)

        # --- Cochran's Q for verifier heterogeneity ---
        Q, p_val, q_df = cochrans_q(binary)

        # --- Pairwise phi coefficients on ERROR patterns ---
        error_matrix = 1 - binary
        rater_names = list(pivot.columns)
        pairwise_phis = []
        for i in range(n_raters):
            for j in range(i + 1, n_raters):
                phi = phi_coefficient(error_matrix[:, i], error_matrix[:, j])
                pairwise_phis.append({
                    "rater_1": rater_names[i],
                    "rater_2": rater_names[j],
                    "phi": phi,
                })

        phi_values = [p["phi"] for p in pairwise_phis]
        mean_phi = float(np.mean(phi_values)) if phi_values else np.nan

        per_task[task] = {
            "agreement_rate": agreement_rate,
            "mean_phi": mean_phi,
            "median_phi": float(np.median(phi_values)) if phi_values else np.nan,
            "std_phi": float(np.std(phi_values)) if phi_values else np.nan,
            "n_phi_pairs": len(phi_values),
            "n_instances": n_instances,
            "n_raters": n_raters,
            "cochrans_q": float(Q),
            "cochrans_p": float(p_val),
            "cochrans_df": q_df,
            "vc_class": VC_CLASS.get(task, "?"),
            "known_rho": KNOWN_RHO.get(task, np.nan),
            "pairwise_phis": pairwise_phis,
        }

    results["per_task"] = per_task

    # --- Non-monotonicity test: B6 vs B7 ---
    b6 = per_task.get("B6", {})
    b7 = per_task.get("B7", {})
    b6_ar = b6.get("agreement_rate")
    b7_ar = b7.get("agreement_rate")
    if (b6_ar is not None and not np.isnan(b6_ar)
            and b7_ar is not None and not np.isnan(b7_ar)):
        results["non_monotonicity"] = {
            "B6_agreement": b6_ar,
            "B7_agreement": b7_ar,
            "B6_gt_B7": b6_ar > b7_ar,
            "B6_mean_phi": b6.get("mean_phi", np.nan),
            "B7_mean_phi": b7.get("mean_phi", np.nan),
            "prediction": (
                "B6 (P-class, shared bottleneck, rho=0.42) > "
                "B7 (coNP, stochastic, rho=0.06)"
            ),
        }

    # --- Cross-task agreement ranking ---
    ranked = sorted(
        [(t, d["agreement_rate"]) for t, d in per_task.items()
         if not np.isnan(d.get("agreement_rate", np.nan))],
        key=lambda x: x[1],
        reverse=True,
    )
    results["agreement_ranking"] = [
        {"task": t, "agreement_rate": ar, "vc_class": VC_CLASS.get(t, "?")}
        for t, ar in ranked
    ]

    # --- Correlation between agreement/phi and known rho ---
    tasks_with_rho = [
        t for t in TASKS
        if t in per_task
        and not np.isnan(per_task[t].get("agreement_rate", np.nan))
        and t in KNOWN_RHO
    ]
    if len(tasks_with_rho) >= 3:
        agree_vals = [per_task[t]["agreement_rate"] for t in tasks_with_rho]
        phi_vals = [per_task[t]["mean_phi"] for t in tasks_with_rho]
        rho_vals = [KNOWN_RHO[t] for t in tasks_with_rho]

        r_agree, p_agree = sp_stats.spearmanr(agree_vals, rho_vals)
        r_phi, p_phi = sp_stats.spearmanr(phi_vals, rho_vals)
        results["agreement_rho_correlation"] = {
            "spearman_r": float(r_agree),
            "spearman_p": float(p_agree),
            "n_tasks": len(tasks_with_rho),
        }
        results["phi_rho_correlation"] = {
            "spearman_r": float(r_phi),
            "spearman_p": float(p_phi),
            "n_tasks": len(tasks_with_rho),
        }

    return results


# =====================================================================
# Analysis 6: Difficulty scaling
# =====================================================================

def analyze_difficulty_scaling(df: pd.DataFrame) -> dict[str, Any]:
    """Secondary: linear regression accuracy ~ difficulty, overall and by VC class."""
    results: dict[str, Any] = {}

    grouped = df.groupby(["task_short", "difficulty", "vc_class"]).agg(
        accuracy=("verification_accurate", "mean"),
        n=("verification_accurate", "count"),
    ).reset_index()

    if len(grouped) < 2:
        return {"error": "Insufficient data for regression"}

    X = grouped["difficulty"].values.astype(float)
    y = grouped["accuracy"].values.astype(float)

    slope, intercept, r_value, p_value, std_err = sp_stats.linregress(X, y)
    results["overall"] = {
        "slope": float(slope),
        "intercept": float(intercept),
        "r_squared": float(r_value ** 2),
        "p_value": float(p_value),
        "significant": p_value < 0.05,
    }

    by_vc_class: dict[str, dict] = {}
    for vc_class, vc_df in grouped.groupby("vc_class"):
        X_vc = vc_df["difficulty"].values.astype(float)
        y_vc = vc_df["accuracy"].values.astype(float)
        if len(X_vc) < 2:
            continue
        s, i, r, p, se = sp_stats.linregress(X_vc, y_vc)
        by_vc_class[vc_class] = {
            "slope": float(s), "intercept": float(i),
            "r_squared": float(r ** 2), "p_value": float(p),
        }
    results["by_vc_class"] = by_vc_class

    return results


# =====================================================================
# Analysis 7: Error type analysis for B7
# =====================================================================

def analyze_error_types_b7(df: pd.DataFrame) -> dict[str, Any]:
    """Secondary: B7 (3-SAT) error type breakdown (FP vs FN)."""
    b7_df = df[df["task_short"] == "B7"]
    if len(b7_df) == 0:
        return {"error": "No B7 results found"}

    total = len(b7_df)
    errors = b7_df[~b7_df["verification_accurate"].astype(bool)]

    error_counts: dict[str, int] = defaultdict(int)
    for _, row in errors.iterrows():
        gen_correct = row["generator_correct"]
        ver_judgment = row["verifier_judgment"]

        if gen_correct and ver_judgment == "Incorrect":
            error_counts["False Negative"] += 1  # rejected correct answer
        elif not gen_correct and ver_judgment == "Correct":
            error_counts["False Positive"] += 1  # confirmed incorrect answer
        else:
            error_counts["Extraction Failure"] += 1

    accuracy = float((total - len(errors)) / total) if total > 0 else 0.0

    # Break down by generator correctness
    gen_correct_df = b7_df[b7_df["generator_correct"].astype(bool)]
    gen_incorrect_df = b7_df[~b7_df["generator_correct"].astype(bool)]

    results = {
        "total_instances": total,
        "total_errors": len(errors),
        "accuracy": accuracy,
        "error_counts": dict(error_counts),
        "gen_correct_instances": len(gen_correct_df),
        "gen_correct_verified": int(
            gen_correct_df["verification_accurate"].astype(bool).sum()
        ) if len(gen_correct_df) > 0 else 0,
        "gen_incorrect_instances": len(gen_incorrect_df),
        "gen_incorrect_detected": int(
            gen_incorrect_df["verification_accurate"].astype(bool).sum()
        ) if len(gen_incorrect_df) > 0 else 0,
    }

    return results


# =====================================================================
# Analysis 8: Latency by VC class
# =====================================================================

def analyze_latency_by_vc_class(df: pd.DataFrame) -> dict[str, Any]:
    """Secondary: Kruskal-Wallis test on latency across VC classes."""
    if "latency_ms" not in df.columns:
        return {"error": "No latency data available"}

    # Drop rows with missing or zero latency
    latency_df = df[df["latency_ms"].notna() & (df["latency_ms"] > 0)]
    if latency_df.empty:
        return {"error": "No valid latency data"}

    grouped = latency_df.groupby("vc_class")["latency_ms"].apply(
        lambda x: x.values
    )

    latency_by_class: dict[str, dict] = {}
    for vc_class in VC_CLASS_ORDER:
        if vc_class not in grouped.index:
            continue
        arr = grouped[vc_class]
        latency_by_class[vc_class] = {
            "median_ms": float(np.median(arr)),
            "q25_ms": float(np.percentile(arr, 25)),
            "q75_ms": float(np.percentile(arr, 75)),
            "mean_ms": float(np.mean(arr)),
            "n": len(arr),
        }

    groups = [grouped[vc] for vc in VC_CLASS_ORDER if vc in grouped.index]
    result: dict[str, Any] = {"latency_by_class": latency_by_class}

    if len(groups) >= 2:
        h_stat, p_value = sp_stats.kruskal(*groups)
        result["kruskal_wallis"] = {
            "h_statistic": float(h_stat),
            "p_value": float(p_value),
            "significant": p_value < 0.05,
        }

    return result


# =====================================================================
# Analysis 9: Gap-collapse (B7 generation vs verification accuracy)
# =====================================================================

# B7 generation accuracy from reasoning-gaps stats.tex
# (12 models, 500 instances, averaged across models)
_B7_GEN_ACC_DIRECT = 0.510
_B7_GEN_ACC_SHORT_COT = 0.514


def analyze_gap_collapse(df: pd.DataFrame) -> dict[str, Any]:
    """Test whether the generation-verification gap collapses for B7 (3-SAT).

    Compares B7 generation accuracy (from reasoning-gaps) against B7
    verification accuracy (from this experiment's data) using a two-proportion
    z-test.  The gap is considered "collapsed" when (a) the absolute difference
    is less than 10 percentage points AND (b) the z-test is not significant
    at alpha = 0.05.

    Returns dict with generation/verification accuracy, z-test results, and
    a boolean ``collapsed`` flag.
    """
    results: dict[str, Any] = {
        "b7_gen_acc_direct": _B7_GEN_ACC_DIRECT,
        "b7_gen_acc_short_cot": _B7_GEN_ACC_SHORT_COT,
    }

    b7_df = df[df["task_short"] == "B7"]
    if b7_df.empty:
        results["error"] = "No B7 verification data"
        return results

    n_ver = len(b7_df)
    ver_acc = float(b7_df["verification_accurate"].astype(float).mean())
    results["b7_ver_acc"] = ver_acc
    results["b7_ver_n"] = n_ver

    # Compare against both generation conditions
    for label, gen_acc in [("direct", _B7_GEN_ACC_DIRECT),
                           ("short_cot", _B7_GEN_ACC_SHORT_COT)]:
        diff = ver_acc - gen_acc

        # Two-proportion z-test
        # H0: p_ver = p_gen  (no gap)
        # Use the generation sample size from reasoning-gaps: 12 models x 500
        # instances, but individual-instance accuracy is the mean, so we
        # approximate n_gen as the total number of (model, instance) evaluations
        # for B7 in reasoning-gaps: 12 * 500 = 6000.
        n_gen = 6000
        p_pooled = (ver_acc * n_ver + gen_acc * n_gen) / (n_ver + n_gen)
        se = np.sqrt(p_pooled * (1 - p_pooled) * (1 / n_ver + 1 / n_gen))
        if se > 0:
            z = diff / se
            p_value = float(2 * sp_stats.norm.sf(abs(z)))  # two-tailed
        else:
            z = 0.0
            p_value = 1.0

        collapsed = abs(diff) < 0.10 and p_value > 0.05

        results[f"vs_{label}"] = {
            "gen_acc": gen_acc,
            "ver_acc": ver_acc,
            "diff": float(diff),
            "diff_pp": float(diff * 100),
            "z": float(z),
            "p_value": p_value,
            "significant": p_value < 0.05,
            "collapsed": collapsed,
        }

    # Overall verdict: collapsed if both conditions show collapse
    results["collapsed"] = (
        results.get("vs_direct", {}).get("collapsed", False)
        and results.get("vs_short_cot", {}).get("collapsed", False)
    )

    return results


# =====================================================================
# Figure 1: Bar chart — verification accuracy by task, colored by VC class
# =====================================================================

def plot_accuracy_by_task(
    df: pd.DataFrame,
    accuracy_results: dict[str, Any],
    output_dir: Path,
) -> None:
    """Figure 1: Verification accuracy by task, colored by VC class."""
    # NOTE: targeting ICLR 2027, but pub_style has no iclr2027 config yet;
    # neurips2026 sizing is similar enough for now.
    pub_style.setup(usetex=False, conference="neurips2026")

    fig, ax = pub_style.figure(width="full", height=3.0)

    tasks_present = [t for t in TASKS if t in accuracy_results.get("accuracy_by_task", {})]
    if not tasks_present:
        plt.close(fig)
        return

    means = [accuracy_results["accuracy_by_task"][t]["mean"] for t in tasks_present]
    ci_lows = [accuracy_results["accuracy_by_task"][t]["ci_low"] for t in tasks_present]
    ci_highs = [accuracy_results["accuracy_by_task"][t]["ci_high"] for t in tasks_present]
    colors = [VC_CLASS_COLORS.get(VC_CLASS.get(t, "P"), "#999999") for t in tasks_present]

    yerr_low = [m - lo for m, lo in zip(means, ci_lows)]
    yerr_high = [hi - m for m, hi in zip(means, ci_highs)]

    x = np.arange(len(tasks_present))
    bars = ax.bar(
        x, means,
        yerr=[yerr_low, yerr_high],
        color=colors,
        edgecolor="white",
        linewidth=0.5,
        capsize=3,
        alpha=0.85,
        width=0.7,
    )

    # Reference lines for predictions
    ax.axhline(y=0.85, color="#0072B2", linestyle="--", linewidth=0.5, alpha=0.5)
    ax.axhline(y=0.75, color="#D55E00", linestyle="--", linewidth=0.5, alpha=0.5)

    ax.set_xticks(x)
    ax.set_xticklabels(tasks_present)
    ax.set_xlabel("Task")
    ax.set_ylabel("Verification Accuracy")
    ax.set_ylim(0, 1.05)
    ax.set_title("Verification Accuracy by Task and VC Class")

    # Legend for VC classes
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor=VC_CLASS_COLORS[vc], label=vc, alpha=0.85)
        for vc in VC_CLASS_ORDER
        if any(VC_CLASS.get(t) == vc for t in tasks_present)
    ]
    ax.legend(handles=legend_elements, loc="lower left", title="VC Class")

    pub_style.savefig(fig, output_dir / "fig1_accuracy_by_task")


# =====================================================================
# Figure 2: Heatmap — generator x verifier rows, task columns
# =====================================================================

def plot_verification_heatmap(df: pd.DataFrame, output_dir: Path) -> None:
    """Figure 2: Verification accuracy heatmap (model pair x task)."""
    # NOTE: targeting ICLR 2027, but pub_style has no iclr2027 config yet;
    # neurips2026 sizing is similar enough for now.
    pub_style.setup(usetex=False, conference="neurips2026")

    df_copy = df.copy()
    # Build short display names for generators and verifiers
    df_copy["gen_short"] = df_copy["generator_model"].map(
        lambda m: pub_style.get_model_display(m) if _HAS_PLOTTING else m.split("/")[-1]
    )
    df_copy["ver_short"] = df_copy["verifier_model"].map(
        lambda m: pub_style.get_model_display(m) if _HAS_PLOTTING else m.split("/")[-1]
    )
    df_copy["model_pair"] = df_copy["gen_short"] + " | " + df_copy["ver_short"]

    # Pivot: rows = model_pair, columns = task
    tasks_present = [t for t in TASKS if t in df_copy["task_short"].unique()]
    pivot = df_copy.pivot_table(
        index="model_pair",
        columns="task_short",
        values="verification_accurate",
        aggfunc="mean",
    )
    # Reorder columns
    pivot = pivot[[t for t in tasks_present if t in pivot.columns]]

    if pivot.empty:
        return

    n_rows = len(pivot)
    fig_height = max(2.5, 0.45 * n_rows + 0.8)
    fig, ax = pub_style.figure(width="full", height=fig_height)

    sns.heatmap(
        pivot,
        annot=True,
        fmt=".2f",
        cmap="YlOrRd",
        vmin=0.0,
        vmax=1.0,
        linewidths=0.5,
        linecolor="white",
        cbar_kws={"label": "Accuracy", "shrink": 0.8},
        ax=ax,
        annot_kws={"fontsize": 7},
    )

    ax.set_title("Verification accuracy: generator | verifier, by task")
    ax.set_xlabel("Task (P-class: B1-B6, P/coNP: B7, Architectural: B8-B9)")
    ax.set_ylabel("")
    ax.set_yticklabels(ax.get_yticklabels(), rotation=0)

    pub_style.savefig(fig, output_dir / "fig2_verification_heatmap")


# =====================================================================
# Figure 3: Scatter — verifier agreement vs known rho ("money figure")
# =====================================================================

# Use the canonical KNOWN_RHO for plotting — all 9 values are computed from
# error_correlation_results.json and are legitimate.  The earlier version had
# None for B1, B4, B5, B8, B9 because the paper text only discussed four
# tasks, but the underlying data covers all nine.
_KNOWN_RHO_FOR_PLOT: dict[str, float | None] = dict(KNOWN_RHO)


def plot_agreement_vs_rho(
    df: pd.DataFrame,
    output_dir: Path,
    agreement_results: dict[str, Any] | None = None,
) -> None:
    """Figure 3: Agreement vs known rho scatter plot.

    Creates a scatter plot testing non-monotonicity (Remark 1):
      X-axis: known between-model rho from reasoning-gaps
      Y-axis: verifier agreement rate from this experiment
      Point labels: task names (B1-B9)
      Colored by VC class

    Tests the prediction that B6 (P-class, rho=0.42) shows higher
    agreement than B7 (coNP, rho=0.06).

    Args:
        df: Full verification DataFrame.
        output_dir: Where to save figure.
        agreement_results: Output of between_model_error_agreement(). If
            provided, agreement rates are read from ``per_task`` instead of
            being recomputed from *df*.
    """
    # NOTE: targeting ICLR 2027, but pub_style has no iclr2027 config yet;
    # neurips2026 sizing is similar enough for now.
    pub_style.setup(usetex=False, conference="neurips2026")

    fig, ax = pub_style.figure(width="col", height=3.0)

    # --- Obtain per-task agreement rate ---
    agreement_by_task: dict[str, float] = {}
    if agreement_results and agreement_results.get("per_task"):
        # Use pre-computed results
        for task, d in agreement_results["per_task"].items():
            ar = d.get("agreement_rate", np.nan)
            if not np.isnan(ar):
                agreement_by_task[task] = ar
    else:
        # Fallback: compute from df directly
        for task in TASKS:
            task_df = df[df["task_short"] == task].copy()
            if task_df.empty:
                continue

            task_df["rater"] = (
                task_df["generator_model"] + " -> " + task_df["verifier_model"]
            )

            pivot = task_df.pivot_table(
                index="instance_id",
                columns="rater",
                values="verification_accurate",
                aggfunc="first",
            )
            pivot = pivot.dropna()
            n_instances, n_raters = pivot.shape
            if n_instances < 2 or n_raters < 2:
                continue

            binary = pivot.values.astype(float)
            row_sums = binary.sum(axis=1)
            all_agree = ((row_sums == 0) | (row_sums == n_raters)).sum()
            agreement_by_task[task] = float(all_agree / n_instances)

    # --- Filter to tasks with known rho ---
    tasks_with_data = [
        t for t in TASKS
        if t in agreement_by_task
        and _KNOWN_RHO_FOR_PLOT.get(t) is not None
    ]

    if len(tasks_with_data) < 2:
        plt.close(fig)
        return

    x_rho = [_KNOWN_RHO_FOR_PLOT[t] for t in tasks_with_data]
    y_agree = [agreement_by_task[t] for t in tasks_with_data]
    colors = [VC_CLASS_COLORS.get(VC_CLASS.get(t, "P"), "#999999") for t in tasks_with_data]

    ax.scatter(x_rho, y_agree, c=colors, s=60, zorder=5,
               edgecolors="white", linewidths=0.5)

    # Annotate each point with task label
    for t, xr, ya in zip(tasks_with_data, x_rho, y_agree):
        offset_x = 0.01
        offset_y = 0.01
        # Adjust specific labels to reduce overlap
        if t == "B6":
            offset_y = -0.03
        elif t == "B7":
            offset_x = 0.015

        ax.annotate(
            t, (xr, ya),
            textcoords="offset points",
            xytext=(offset_x * 400, offset_y * 400),
            fontsize=7,
            fontweight="bold",
        )

    # Fit trend line if enough points
    if len(tasks_with_data) >= 3:
        slope, intercept, r_val, p_val, _ = sp_stats.linregress(x_rho, y_agree)
        x_line = np.linspace(min(x_rho) - 0.02, max(x_rho) + 0.02, 100)
        y_line = slope * x_line + intercept
        ax.plot(x_line, y_line, "--", color="0.5", linewidth=0.8, zorder=1)

        # Spearman correlation annotation
        if len(tasks_with_data) >= 3:
            r_s, p_s = sp_stats.spearmanr(x_rho, y_agree)
        else:
            r_s, p_s = r_val, p_val
        ax.text(
            0.05, 0.95,
            f"$r_s = {r_s:.2f}$, $p = {p_s:.3f}$",
            transform=ax.transAxes,
            fontsize=7,
            va="top",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="white",
                      edgecolor="0.8", alpha=0.85),
        )

    # Highlight the B6 vs B7 prediction
    b6_data = ("B6" in tasks_with_data, agreement_by_task.get("B6"))
    b7_data = ("B7" in tasks_with_data, agreement_by_task.get("B7"))
    if b6_data[0] and b7_data[0]:
        prediction_met = b6_data[1] > b7_data[1]
        verdict = "confirmed" if prediction_met else "not confirmed"
        ax.text(
            0.05, 0.85,
            f"B6 > B7: {verdict}",
            transform=ax.transAxes,
            fontsize=6,
            va="top",
            color="#0072B2" if prediction_met else "#D55E00",
            fontstyle="italic",
        )

    ax.set_xlabel(r"Known between-model $\rho$ (reasoning-gaps)")
    ax.set_ylabel("Verifier agreement rate (this experiment)")
    ax.set_title("Verifier Agreement vs Known Error Correlation")

    # Legend for VC classes
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor=VC_CLASS_COLORS[vc], label=vc, alpha=0.85)
        for vc in VC_CLASS_ORDER
        if any(VC_CLASS.get(t) == vc for t in tasks_with_data)
    ]
    ax.legend(handles=legend_elements, loc="lower right", title="VC Class", fontsize=6)

    pub_style.savefig(fig, output_dir / "fig3_agreement_vs_rho")


# =====================================================================
# LaTeX output: stats.tex and table2.tex
# =====================================================================

def write_latex_stats(analyses: dict[str, Any], output_dir: Path) -> None:
    """Write stats.tex with \\newcommand definitions for inline use in paper."""
    lines = [
        "% Auto-generated by analyze_verification_results.py",
        "% Do not edit manually.",
        "",
    ]

    def cmd(name: str, value: str) -> str:
        # Use \def to silently overwrite if the command already exists
        # (safe for auto-generated stats files that may be \input'd multiple times)
        return f"\\def\\{name}{{{value}}}"

    # --- Overall ---
    acc_by_class = analyses.get("accuracy_by_vc_class", {}).get("accuracy_by_class", {})
    for vc in VC_CLASS_ORDER:
        if vc not in acc_by_class:
            continue
        safe_vc = vc.replace("/", "").replace(" ", "")
        d = acc_by_class[vc]
        lines.append(cmd(f"vcAcc{safe_vc}", f"{d['mean']*100:.1f}\\%"))
        lines.append(cmd(f"vcAccN{safe_vc}", f"{d['n']}"))
        lines.append(cmd(f"vcAccCI{safe_vc}",
                         f"[{d['ci_low']*100:.1f}\\%, {d['ci_high']*100:.1f}\\%]"))

    # --- Per-task accuracy ---
    acc_by_task = analyses.get("accuracy_by_vc_class", {}).get("accuracy_by_task", {})
    for task, d in acc_by_task.items():
        lines.append(cmd(f"taskAcc{task}", f"{d['mean']*100:.1f}\\%"))

    # --- ANOVA ---
    anova = analyses.get("accuracy_by_vc_class", {}).get("anova", {})
    if anova:
        lines.append(cmd("anovaF", f"{anova['f_statistic']:.2f}"))
        p = anova["p_value"]
        if p < 0.001:
            lines.append(cmd("anovaP", "< 0.001"))
        else:
            lines.append(cmd("anovaP", f"= {p:.3f}"))
        lines.append(cmd("anovaEta", f"{anova['eta_squared']:.3f}"))

    # --- Pairwise ---
    for pair in analyses.get("accuracy_by_vc_class", {}).get("pairwise_comparisons", []):
        safe_name = pair["pair"].replace(" vs ", "Vs").replace("/", "").replace(" ", "")
        lines.append(cmd(f"pairD{safe_name}", f"{pair['cohens_d']:.2f}"))

    # --- ICC ---
    icc_data = analyses.get("cross_model_consistency", {}).get("icc_by_class", {})
    for vc, d in icc_data.items():
        safe_vc = vc.replace("/", "").replace(" ", "")
        icc_val = d["icc"]
        lines.append(cmd(f"icc{safe_vc}",
                         f"{icc_val:.2f}" if not np.isnan(icc_val) else "N/A"))

    # --- Two-way ANOVA ---
    tw = analyses.get("two_way_anova", {})
    if tw.get("interaction_p") is not None:
        p_int = tw["interaction_p"]
        if p_int < 0.001:
            lines.append(cmd("twowayInterP", "< 0.001"))
        else:
            lines.append(cmd("twowayInterP", f"= {p_int:.3f}"))
        lines.append(cmd("twowayInterSig",
                         "significant" if tw.get("interaction_significant") else "not significant"))

    # --- Generator x VC interaction ANOVA (with effect sizes) ---
    gva = analyses.get("generator_vc_interaction_anova", {})
    if gva.get("factors"):
        for factor_name, fd in gva["factors"].items():
            safe_name = factor_name.replace("(", "").replace(")", "").replace(":", "X").replace(" ", "")
            f_val = fd.get("F")
            p_val = fd.get("p_value")
            eta = fd.get("partial_eta_sq")
            if f_val is not None:
                lines.append(cmd(f"gva{safe_name}F", f"{f_val:.2f}"))
            if p_val is not None:
                if p_val < 0.001:
                    lines.append(cmd(f"gva{safe_name}P", "< 0.001"))
                else:
                    lines.append(cmd(f"gva{safe_name}P", f"= {p_val:.3f}"))
            if eta is not None:
                lines.append(cmd(f"gva{safe_name}Eta", f"{eta:.4f}"))
        if gva.get("interaction_partial_eta_sq") is not None:
            lines.append(cmd("gvaInterEta", f"{gva['interaction_partial_eta_sq']:.4f}"))

    # --- Agreement ---
    agreement = analyses.get("between_model_agreement", {}).get("agreement_by_task", {})
    for task, d in agreement.items():
        ar = d.get("agreement_rate", np.nan)
        lines.append(cmd(f"agree{task}",
                         f"{ar*100:.1f}\\%" if not np.isnan(ar) else "N/A"))

    # --- Non-monotonicity ---
    nm = analyses.get("between_model_agreement", {}).get("non_monotonicity_test", {})
    if nm:
        lines.append(cmd("nonMonBsixAgree", f"{nm['B6_agreement']*100:.1f}\\%"))
        lines.append(cmd("nonMonBsevenAgree", f"{nm['B7_agreement']*100:.1f}\\%"))
        lines.append(cmd("nonMonResult",
                         "confirmed" if nm.get("B6_gt_B7") else "not confirmed"))

    # --- Theorem 2c consolidated ---
    t2c = analyses.get("theorem_2c_agreement", {})
    if t2c.get("per_task"):
        for task, d in t2c["per_task"].items():
            mp = d.get("mean_phi", np.nan)
            lines.append(cmd(f"t2cPhi{task}",
                             f"{mp:.3f}" if not np.isnan(mp) else "N/A"))
    t2c_nm = t2c.get("non_monotonicity", {})
    if t2c_nm:
        lines.append(cmd("t2cBsixPhi", f"{t2c_nm['B6_mean_phi']:.3f}"))
        lines.append(cmd("t2cBsevenPhi", f"{t2c_nm['B7_mean_phi']:.3f}"))
    t2c_ar_corr = t2c.get("agreement_rho_correlation", {})
    if t2c_ar_corr:
        lines.append(cmd("t2cAgreeRhoR", f"{t2c_ar_corr['spearman_r']:.2f}"))
        p_ar = t2c_ar_corr["spearman_p"]
        if p_ar < 0.001:
            lines.append(cmd("t2cAgreeRhoP", "< 0.001"))
        else:
            lines.append(cmd("t2cAgreeRhoP", f"= {p_ar:.3f}"))

    # --- Phi-rho correlation ---
    pr = analyses.get("phi_coefficients", {}).get("phi_rho_correlation", {})
    if pr:
        lines.append(cmd("phiRhoR", f"{pr['spearman_r']:.2f}"))
        p_pr = pr["spearman_p"]
        if p_pr < 0.001:
            lines.append(cmd("phiRhoP", "< 0.001"))
        else:
            lines.append(cmd("phiRhoP", f"= {p_pr:.3f}"))

    # --- Difficulty ---
    diff = analyses.get("difficulty_scaling", {}).get("overall", {})
    if diff:
        lines.append(cmd("diffSlope", f"{diff['slope']:.4f}"))
        lines.append(cmd("diffRsq", f"{diff['r_squared']:.3f}"))

    # --- B7 errors ---
    b7 = analyses.get("error_types_b7", {})
    if b7 and "accuracy" in b7:
        lines.append(cmd("bsevenAcc", f"{b7['accuracy']*100:.1f}\\%"))
        for etype, count in b7.get("error_counts", {}).items():
            safe = etype.replace(" ", "")
            lines.append(cmd(f"bseven{safe}", str(count)))

    # --- Latency ---
    lat = analyses.get("latency_by_vc_class", {}).get("latency_by_class", {})
    for vc, d in lat.items():
        safe_vc = vc.replace("/", "").replace(" ", "")
        lines.append(cmd(f"latMedian{safe_vc}", f"{d['median_ms']:.0f}"))

    # --- Gap collapse ---
    gc = analyses.get("gap_collapse", {})
    if gc and "b7_ver_acc" in gc:
        lines.append(cmd("gapCollapseVerAcc", f"{gc['b7_ver_acc']*100:.1f}\\%"))
        for label in ("direct", "short_cot"):
            cond = gc.get(f"vs_{label}", {})
            if cond:
                safe = label.replace("_", "")
                lines.append(cmd(f"gapCollapseDiff{safe.capitalize()}",
                                 f"{cond['diff_pp']:+.1f}"))
                p = cond["p_value"]
                if p < 0.001:
                    lines.append(cmd(f"gapCollapseP{safe.capitalize()}", "< 0.001"))
                else:
                    lines.append(cmd(f"gapCollapseP{safe.capitalize()}", f"= {p:.3f}"))
        lines.append(cmd("gapCollapseResult",
                         "collapsed" if gc.get("collapsed") else "persists"))

    lines.append("")
    (output_dir / "stats.tex").write_text("\n".join(lines))
    print(f"  -> {output_dir / 'stats.tex'}")


def write_latex_table2(analyses: dict[str, Any], output_dir: Path) -> None:
    """Write table2.tex: per-task verification results summary.

    Columns: Task | VC Class | Accuracy | 95% CI | Agreement | Phi | Known rho
    """
    acc_data = analyses.get("accuracy_by_vc_class", {}).get("accuracy_by_task", {})
    agree_data = analyses.get("between_model_agreement", {}).get("agreement_by_task", {})
    phi_data = analyses.get("phi_coefficients", {}).get("phi_by_task", {})

    lines = [
        "% Auto-generated by analyze_verification_results.py",
        "% Table 2: Cross-model verification results by task",
        "\\begin{tabular}{lcccccc}",
        "\\toprule",
        "Task & VC Class & Accuracy & 95\\% CI & Agreement & $\\bar{\\phi}$ & Known $\\rho$ \\\\",
        "\\midrule",
    ]

    prev_vc = None
    for task in TASKS:
        vc = VC_CLASS.get(task, "?")

        # Add midrule between VC class groups
        if prev_vc is not None and vc != prev_vc:
            lines.append("\\midrule")
        prev_vc = vc

        acc = acc_data.get(task, {})
        agr = agree_data.get(task, {})
        phi = phi_data.get(task, {})

        acc_str = f"{acc['mean']:.2f}" if acc.get("mean") is not None else "--"
        ci_str = (
            f"[{acc['ci_low']:.2f}, {acc['ci_high']:.2f}]"
            if acc.get("ci_low") is not None
            else "--"
        )
        agree_str = (
            f"{agr['agreement_rate']:.2f}"
            if agr.get("agreement_rate") is not None and not np.isnan(agr.get("agreement_rate", np.nan))
            else "--"
        )
        phi_str = (
            f"{phi['mean_phi']:.2f}"
            if phi.get("mean_phi") is not None and not np.isnan(phi.get("mean_phi", np.nan))
            else "--"
        )
        rho_str = f"{KNOWN_RHO.get(task, np.nan):.2f}" if task in KNOWN_RHO else "--"

        lines.append(f"{task} & {vc} & {acc_str} & {ci_str} & {agree_str} & {phi_str} & {rho_str} \\\\")

    lines.extend([
        "\\bottomrule",
        "\\end{tabular}",
    ])

    (output_dir / "table2.tex").write_text("\n".join(lines))
    print(f"  -> {output_dir / 'table2.tex'}")


# =====================================================================
# Console summary
# =====================================================================

def print_summary(analyses: dict[str, Any]) -> None:
    """Print a human-readable summary to stdout."""
    sep = "=" * 65
    print(f"\n{sep}")
    print("ANALYSIS SUMMARY")
    print(sep)

    # 1. Accuracy by VC class
    acc_class = analyses.get("accuracy_by_vc_class", {})
    if acc_class.get("accuracy_by_class"):
        print("\n1. VERIFICATION ACCURACY BY VC CLASS")
        for vc, d in acc_class["accuracy_by_class"].items():
            print(f"   {vc:8s}: {d['mean']:.3f} (95% CI: [{d['ci_low']:.3f}, {d['ci_high']:.3f}]), n={d['n']}")
        if acc_class.get("anova"):
            a = acc_class["anova"]
            p_str = "<0.001" if a['p_value'] < 0.001 else f"{a['p_value']:.4f}"
            print(f"   ANOVA: F={a['f_statistic']:.2f}, p={p_str}, eta^2={a['eta_squared']:.3f}")
        for pair in acc_class.get("pairwise_comparisons", []):
            sig = "***" if pair["significant_bonferroni"] else "n.s."
            print(f"   {pair['pair']:20s}: d={pair['cohens_d']:.2f}, p={pair['p_value']:.4f} {sig}")

    # 2. ICC
    icc_data = analyses.get("cross_model_consistency", {}).get("icc_by_class", {})
    if icc_data:
        print("\n2. CROSS-MODEL CONSISTENCY (ICC)")
        for vc, d in icc_data.items():
            icc_val = d["icc"]
            print(f"   {vc:8s}: ICC={icc_val:.3f}" if not np.isnan(icc_val) else f"   {vc:8s}: ICC=N/A")

    # 3. Two-way ANOVA
    tw = analyses.get("two_way_anova", {})
    if tw:
        print(f"\n3. TWO-WAY ANOVA (generator x VC class) [{tw.get('method', '?')}]")
        for factor, d in tw.get("anova_table", {}).items():
            f_val = d.get("F")
            p_val = d.get("PR(>F)")
            f_str = f"F={f_val:.2f}" if f_val is not None else ""
            p_str = f"p={p_val:.4f}" if p_val is not None else ""
            print(f"   {factor:25s}: {f_str:12s} {p_str}")
        print(f"   Interaction: {'SIGNIFICANT' if tw.get('interaction_significant') else 'not significant'}")

    # 3a. Generator x VC interaction ANOVA (with effect sizes)
    gva = analyses.get("generator_vc_interaction_anova", {})
    if gva.get("factors"):
        print(f"\n3a. GENERATOR x VC INTERACTION ANOVA (with effect sizes) [{gva.get('method', '?')}]")
        for factor, d in gva["factors"].items():
            f_val = d.get("F")
            p_val = d.get("p_value")
            eta = d.get("partial_eta_sq")
            f_str = f"F={f_val:.2f}" if f_val is not None else ""
            p_str = f"p={p_val:.4f}" if p_val is not None else ""
            eta_str = f"eta_p^2={eta:.4f}" if eta is not None else ""
            print(f"   {factor:25s}: {f_str:12s} {p_str:12s} {eta_str}")
        inter_sig = gva.get("interaction_significant")
        inter_p = gva.get("interaction_p")
        inter_eta = gva.get("interaction_partial_eta_sq")
        sig_str = "SIGNIFICANT" if inter_sig else "not significant"
        p_suffix = f" (p={inter_p:.4f})" if inter_p is not None else ""
        print(f"   Interaction: {sig_str}{p_suffix}")
        if inter_eta is not None:
            print(f"   Interaction effect size: partial eta^2 = {inter_eta:.4f}")

    # 4. Between-model agreement
    agree = analyses.get("between_model_agreement", {})
    if agree.get("agreement_by_task"):
        print("\n4. BETWEEN-MODEL ERROR AGREEMENT (Cochran's Q)")
        for task in TASKS:
            d = agree["agreement_by_task"].get(task)
            if d is None:
                continue
            ar = d["agreement_rate"]
            q = d.get("cochrans_q", np.nan)
            p = d.get("cochrans_p", np.nan)
            ar_str = f"{ar:.3f}" if not np.isnan(ar) else "N/A"
            q_str = f"Q={q:.2f}" if not np.isnan(q) else "Q=N/A"
            p_str = f"p={p:.4f}" if not np.isnan(p) else ""
            print(f"   {task} ({VC_CLASS.get(task,'?'):6s}): agree={ar_str}, {q_str} {p_str}")
        nm = agree.get("non_monotonicity_test", {})
        if nm:
            print(f"   Non-monotonicity: B6={nm['B6_agreement']:.3f} vs B7={nm['B7_agreement']:.3f} -> {'CONFIRMED' if nm['B6_gt_B7'] else 'NOT confirmed'}")

    # 4a. Consolidated Theorem 2c analysis
    t2c = analyses.get("theorem_2c_agreement", {})
    if t2c.get("per_task"):
        print("\n4a. THEOREM 2c: CONSOLIDATED ERROR AGREEMENT ANALYSIS")
        for task in TASKS:
            d = t2c["per_task"].get(task)
            if d is None:
                continue
            ar = d.get("agreement_rate", np.nan)
            mp = d.get("mean_phi", np.nan)
            q = d.get("cochrans_q", np.nan)
            rho = d.get("known_rho", np.nan)
            ar_str = f"agree={ar:.3f}" if not np.isnan(ar) else "agree=N/A"
            mp_str = f"phi={mp:.3f}" if not np.isnan(mp) else "phi=N/A"
            q_str = f"Q={q:.2f}" if not np.isnan(q) else "Q=N/A"
            rho_str = f"rho={rho:.2f}" if not np.isnan(rho) else "rho=?"
            print(f"   {task} ({d.get('vc_class','?'):6s}): {ar_str}, {mp_str}, {q_str}, {rho_str}")
        nm = t2c.get("non_monotonicity", {})
        if nm:
            print(f"   Non-monotonicity (B6 vs B7):")
            print(f"     B6 agreement={nm['B6_agreement']:.3f}, phi={nm['B6_mean_phi']:.3f}")
            print(f"     B7 agreement={nm['B7_agreement']:.3f}, phi={nm['B7_mean_phi']:.3f}")
            print(f"     B6 > B7: {'CONFIRMED' if nm['B6_gt_B7'] else 'NOT confirmed'}")
        ar_corr = t2c.get("agreement_rho_correlation", {})
        if ar_corr:
            print(f"   Agreement-Rho correlation: r_s={ar_corr['spearman_r']:.3f}, p={ar_corr['spearman_p']:.4f}")
        pr_corr = t2c.get("phi_rho_correlation", {})
        if pr_corr:
            print(f"   Phi-Rho correlation: r_s={pr_corr['spearman_r']:.3f}, p={pr_corr['spearman_p']:.4f}")
        ranking = t2c.get("agreement_ranking", [])
        if ranking:
            parts = [f"{r['task']}({r['agreement_rate']:.2f})" for r in ranking]
            print(f"   Agreement ranking: {', '.join(parts)}")

    # 5. Phi coefficients
    phi = analyses.get("phi_coefficients", {})
    if phi.get("phi_by_task"):
        print("\n5. PAIRWISE ERROR CORRELATION (phi)")
        for task in TASKS:
            d = phi["phi_by_task"].get(task)
            if d is None:
                continue
            mp = d["mean_phi"]
            rho = d.get("known_rho", np.nan)
            mp_str = f"{mp:.3f}" if not np.isnan(mp) else "N/A"
            print(f"   {task} ({VC_CLASS.get(task,'?'):6s}): mean_phi={mp_str}, known_rho={rho:.2f}")
        corr = phi.get("phi_rho_correlation", {})
        if corr:
            print(f"   Phi-Rho correlation: r_s={corr['spearman_r']:.3f}, p={corr['spearman_p']:.4f}")

    # 6. Difficulty scaling
    diff = analyses.get("difficulty_scaling", {}).get("overall", {})
    if diff:
        print(f"\n6. DIFFICULTY SCALING")
        print(f"   slope={diff['slope']:.4f}, R^2={diff['r_squared']:.3f}, p={diff['p_value']:.4f}")

    # 7. B7 errors
    b7 = analyses.get("error_types_b7", {})
    if b7 and "accuracy" in b7:
        print(f"\n7. B7 ERROR ANALYSIS")
        print(f"   Accuracy: {b7['accuracy']:.3f} ({b7['total_errors']} errors / {b7['total_instances']} total)")
        for etype, count in b7.get("error_counts", {}).items():
            print(f"   {etype}: {count}")

    # 8. Latency
    lat = analyses.get("latency_by_vc_class", {}).get("latency_by_class", {})
    if lat:
        print(f"\n8. LATENCY BY VC CLASS")
        for vc, d in lat.items():
            print(f"   {vc:8s}: median={d['median_ms']:.0f}ms, IQR=[{d['q25_ms']:.0f}, {d['q75_ms']:.0f}]")
        kw = analyses.get("latency_by_vc_class", {}).get("kruskal_wallis", {})
        if kw:
            print(f"   Kruskal-Wallis: H={kw['h_statistic']:.2f}, p={kw['p_value']:.4f}")

    # 9. Gap collapse
    gc = analyses.get("gap_collapse", {})
    if gc and "b7_ver_acc" in gc:
        print(f"\n9. GAP-COLLAPSE ANALYSIS (B7)")
        print(f"   B7 verification accuracy: {gc['b7_ver_acc']:.3f} (n={gc['b7_ver_n']})")
        for label in ("direct", "short_cot"):
            cond = gc.get(f"vs_{label}", {})
            if cond:
                p_str = f"p={cond['p_value']:.4f}" if cond['p_value'] >= 0.001 else "p<0.001"
                sig = "SIG" if cond["significant"] else "n.s."
                coll = "COLLAPSED" if cond["collapsed"] else "NOT collapsed"
                print(f"   vs {label}: gen={cond['gen_acc']:.3f}, diff={cond['diff_pp']:+.1f}pp, "
                      f"z={cond['z']:.2f}, {p_str} {sig} -> {coll}")
        print(f"   Overall: {'GAP COLLAPSED' if gc.get('collapsed') else 'GAP PERSISTS'}")

    print()


# =====================================================================
# Main
# =====================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Analyze cross-model verification results",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--results", nargs="+", type=Path,
        help="Verification result files (JSONL). Default: results/verify_*.jsonl",
    )
    parser.add_argument(
        "--output-dir", type=Path,
        default=Path(__file__).resolve().parent / "results" / "analysis",
        help="Output directory for figures, tables, and JSON report",
    )
    parser.add_argument(
        "--no-figures", action="store_true",
        help="Skip figure generation (useful on headless servers)",
    )
    parser.add_argument(
        "--no-latex", action="store_true",
        help="Skip LaTeX output (stats.tex, table2.tex)",
    )

    args = parser.parse_args()

    # Resolve result files
    if args.results:
        result_files = args.results
    else:
        results_dir = Path(__file__).resolve().parent / "results"
        result_files = sorted(results_dir.glob("verify_*.jsonl"))

    if not result_files:
        print("Error: No result files found. Use --results to specify.", file=sys.stderr)
        sys.exit(1)

    args.output_dir.mkdir(parents=True, exist_ok=True)

    # --- Load ---
    print(f"Loading results from {len(result_files)} file(s)...")
    df = load_verification_results(result_files)
    print(f"Loaded {len(df)} verification records")
    print(f"  Tasks: {sorted(df['task_short'].unique())}")
    print(f"  VC classes: {sorted(df['vc_class'].unique())}")
    print(f"  Generators: {sorted(df['generator_model'].unique())}")
    print(f"  Verifiers: {sorted(df['verifier_model'].unique())}")
    print()

    # --- Run all analyses ---
    analyses: dict[str, Any] = {}

    print(" 1/12  Verification accuracy by VC class (ANOVA)...")
    analyses["accuracy_by_vc_class"] = analyze_accuracy_by_vc_class(df)

    print(" 2/12  Cross-model consistency (ICC)...")
    analyses["cross_model_consistency"] = analyze_cross_model_consistency(df)

    print(" 3/12  Two-way ANOVA (generator x VC class) [legacy]...")
    analyses["two_way_anova"] = analyze_two_way_anova(df)

    print(" 4/12  Generator x VC interaction ANOVA (with effect sizes)...")
    analyses["generator_vc_interaction_anova"] = generator_vc_interaction_anova(df)

    print(" 5/12  Consolidated Theorem 2c: error agreement analysis...")
    analyses["theorem_2c_agreement"] = between_model_error_agreement(df)

    print(" 6/12  Between-model error agreement (legacy wrapper)...")
    analyses["between_model_agreement"] = analyze_between_model_agreement(
        df, consolidated=analyses["theorem_2c_agreement"],
    )

    print(" 7/12  Phi coefficients for error correlation...")
    analyses["phi_coefficients"] = analyze_phi_coefficients(df)

    print(" 8/12  Difficulty scaling...")
    analyses["difficulty_scaling"] = analyze_difficulty_scaling(df)

    print(" 9/12  B7 error type analysis...")
    analyses["error_types_b7"] = analyze_error_types_b7(df)

    print("10/12  Latency by VC class...")
    analyses["latency_by_vc_class"] = analyze_latency_by_vc_class(df)

    print("11/12  Gap-collapse analysis (B7 generation vs verification)...")
    analyses["gap_collapse"] = analyze_gap_collapse(df)

    print("12/12  Done.")

    # --- Save JSON report ---
    report_path = args.output_dir / "analysis_report.json"

    def _json_default(obj):
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, (np.bool_,)):
            return bool(obj)
        return str(obj)

    with open(report_path, "w") as f:
        json.dump(analyses, f, indent=2, default=_json_default)
    print(f"\nJSON report: {report_path}")

    # --- Figures ---
    if not args.no_figures:
        if _HAS_PLOTTING:
            print("\nGenerating figures...")
            print("  Figure 1: Accuracy by task...")
            plot_accuracy_by_task(df, analyses["accuracy_by_vc_class"], args.output_dir)
            print("  Figure 2: Verification heatmap...")
            plot_verification_heatmap(df, args.output_dir)
            print("  Figure 3: Agreement vs rho (money figure)...")
            plot_agreement_vs_rho(df, args.output_dir, analyses.get("theorem_2c_agreement"))
        else:
            print("\nWarning: matplotlib/seaborn not available, skipping figures", file=sys.stderr)

    # --- LaTeX ---
    if not args.no_latex:
        print("\nGenerating LaTeX output...")
        write_latex_stats(analyses, args.output_dir)
        write_latex_table2(analyses, args.output_dir)

    # --- Console summary ---
    print_summary(analyses)


if __name__ == "__main__":
    main()
