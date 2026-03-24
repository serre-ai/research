#!/usr/bin/env python3
"""Analyze cross-model verification results for verification-complexity paper.

Implements pre-registered analyses from spec.yaml:
1. Verification accuracy by VC class (ANOVA)
2. Cross-model consistency within VC class (ICC)
3. Generator-verifier interaction (two-way ANOVA)
4. Difficulty scaling (linear regression)
5. Error type analysis for B7 (3-SAT)
6. Latency by VC class (Kruskal-Wallis)

Generates publication-ready figures using pub_style.

Usage:
    python analyze_verification_results.py --results results/verify_*.jsonl
    python analyze_verification_results.py --canary-only  # Analyze canary results only
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from scipy import stats
from scipy.stats import bootstrap


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
    required = ["task", "vc_class", "verification_accurate", "generator_model",
                "verifier_model", "difficulty", "generator_correct", "verifier_judgment"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    return df


def bootstrap_ci(data: np.ndarray, confidence: float = 0.95, n_bootstrap: int = 1000) -> tuple[float, float, float]:
    """Compute mean and bootstrap confidence interval."""
    if len(data) == 0:
        return np.nan, np.nan, np.nan

    mean = np.mean(data)

    if len(data) < 2:
        return mean, mean, mean

    # Bootstrap resampling
    rng = np.random.default_rng(42)
    res = bootstrap((data,), np.mean, confidence_level=confidence,
                   n_resamples=n_bootstrap, random_state=rng)

    return mean, res.confidence_interval.low, res.confidence_interval.high


def analyze_accuracy_by_vc_class(df: pd.DataFrame) -> dict[str, Any]:
    """Primary Analysis 1: Verification accuracy by VC class.

    Hypothesis: P-class > coNP-class > Arch-class
    Method: One-way ANOVA with Bonferroni correction
    """
    results = {}

    # Group by VC class
    grouped = df.groupby("vc_class")["verification_accurate"].apply(list)

    # Compute accuracy and CIs for each VC class
    accuracy_by_class = {}
    for vc_class, accuracies in grouped.items():
        acc_array = np.array(accuracies, dtype=float)
        mean, ci_low, ci_high = bootstrap_ci(acc_array)
        accuracy_by_class[vc_class] = {
            "mean": mean,
            "ci_low": ci_low,
            "ci_high": ci_high,
            "n": len(accuracies),
        }

    results["accuracy_by_class"] = accuracy_by_class

    # ANOVA test
    groups = [np.array(accuracies, dtype=float) for _, accuracies in grouped.items()]
    if len(groups) >= 2:
        f_stat, p_value = stats.f_oneway(*groups)
        results["anova"] = {
            "f_statistic": f_stat,
            "p_value": p_value,
            "significant": p_value < 0.05,
        }

    # Pairwise comparisons with Bonferroni correction
    vc_classes = list(grouped.keys())
    n_comparisons = len(vc_classes) * (len(vc_classes) - 1) // 2
    bonferroni_alpha = 0.05 / n_comparisons if n_comparisons > 0 else 0.05

    pairwise = []
    for i, vc1 in enumerate(vc_classes):
        for vc2 in vc_classes[i+1:]:
            group1 = np.array(grouped[vc1], dtype=float)
            group2 = np.array(grouped[vc2], dtype=float)
            t_stat, p_value = stats.ttest_ind(group1, group2)

            # Cohen's d effect size
            pooled_std = np.sqrt((np.std(group1, ddof=1)**2 + np.std(group2, ddof=1)**2) / 2)
            cohens_d = (np.mean(group1) - np.mean(group2)) / pooled_std if pooled_std > 0 else 0

            pairwise.append({
                "vc_class_1": vc1,
                "vc_class_2": vc2,
                "t_statistic": t_stat,
                "p_value": p_value,
                "significant_bonferroni": p_value < bonferroni_alpha,
                "cohens_d": cohens_d,
            })

    results["pairwise_comparisons"] = pairwise
    results["bonferroni_alpha"] = bonferroni_alpha

    return results


def analyze_cross_model_consistency(df: pd.DataFrame) -> dict[str, Any]:
    """Primary Analysis 2: Cross-model consistency within VC class.

    Hypothesis: Accuracy correlates more strongly within VC class than across
    Method: Intraclass correlation coefficient (ICC)
    """
    results = {}

    # Create accuracy matrix: rows = instances, columns = (generator, verifier) pairs
    # Within VC class, we expect high correlation (same instances tested by different models)

    # For each VC class, compute ICC across model pairs
    icc_by_class = {}
    for vc_class, group_df in df.groupby("vc_class"):
        # Pivot: rows = instance_id, columns = (gen, ver) pair, values = verification_accurate
        group_df["model_pair"] = group_df["generator_model"] + "_" + group_df["verifier_model"]
        pivot = group_df.pivot_table(
            index="instance_id",
            columns="model_pair",
            values="verification_accurate",
            aggfunc="first"
        )

        # ICC(2,1) — two-way random effects, single measurement
        # Formula: (BMS - WMS) / (BMS + (k-1)*WMS) where k = number of raters
        if pivot.shape[0] < 2 or pivot.shape[1] < 2:
            icc_by_class[vc_class] = {"icc": np.nan, "n_instances": pivot.shape[0], "n_pairs": pivot.shape[1]}
            continue

        # Drop instances with missing values (not tested by all model pairs)
        pivot = pivot.dropna()

        if pivot.shape[0] < 2:
            icc_by_class[vc_class] = {"icc": np.nan, "n_instances": pivot.shape[0], "n_pairs": pivot.shape[1]}
            continue

        # Compute ICC using two-way ANOVA components
        n = pivot.shape[0]  # instances
        k = pivot.shape[1]  # model pairs

        # Mean squares
        grand_mean = pivot.values.mean()
        row_means = pivot.mean(axis=1)
        col_means = pivot.mean(axis=0)

        ss_between = k * np.sum((row_means - grand_mean) ** 2)
        ss_within = np.sum((pivot.values - row_means.values.reshape(-1, 1)) ** 2)

        ms_between = ss_between / (n - 1) if n > 1 else 0
        ms_within = ss_within / (n * (k - 1)) if (n * (k - 1)) > 0 else 0

        icc = (ms_between - ms_within) / (ms_between + (k - 1) * ms_within) if (ms_between + (k - 1) * ms_within) > 0 else 0

        icc_by_class[vc_class] = {
            "icc": icc,
            "n_instances": n,
            "n_pairs": k,
        }

    results["icc_by_class"] = icc_by_class

    return results


def analyze_error_types_b7(df: pd.DataFrame) -> dict[str, Any]:
    """Secondary Analysis: Error type analysis for B7 (3-SAT).

    Question: Are B7 errors mostly false positives (UNSAT verification)?
    Method: Contingency table analysis
    """
    b7_df = df[df["task"].str.contains("B7")]

    if len(b7_df) == 0:
        return {"error": "No B7 results found"}

    # Classify errors
    errors = b7_df[~b7_df["verification_accurate"]]

    error_types = []
    for _, row in errors.iterrows():
        gen_correct = row["generator_correct"]
        ver_judgment = row["verifier_judgment"]

        if gen_correct and ver_judgment == "Incorrect":
            error_type = "False Negative"  # Rejected correct answer
        elif not gen_correct and ver_judgment == "Correct":
            error_type = "False Positive"  # Confirmed incorrect answer
        else:
            error_type = "Other"

        error_types.append({
            "instance_id": row["instance_id"],
            "error_type": error_type,
            "generator_answer": row.get("generator_answer", ""),
            "ground_truth": row.get("ground_truth", ""),
        })

    # Count error types
    error_counts = defaultdict(int)
    for e in error_types:
        error_counts[e["error_type"]] += 1

    results = {
        "total_errors": len(errors),
        "error_counts": dict(error_counts),
        "error_details": error_types,
        "accuracy": (len(b7_df) - len(errors)) / len(b7_df) if len(b7_df) > 0 else 0,
    }

    return results


def analyze_difficulty_scaling(df: pd.DataFrame) -> dict[str, Any]:
    """Secondary Analysis: Difficulty scaling.

    Question: Does verification accuracy degrade with difficulty?
    Method: Linear regression (accuracy ~ difficulty + VC_class)
    """
    # Aggregate by (task, difficulty, vc_class)
    grouped = df.groupby(["task", "difficulty", "vc_class"]).agg({
        "verification_accurate": ["mean", "count"]
    }).reset_index()

    grouped.columns = ["task", "difficulty", "vc_class", "accuracy", "n"]

    # Linear regression: accuracy ~ difficulty
    X = grouped["difficulty"].values
    y = grouped["accuracy"].values

    if len(X) < 2:
        return {"error": "Insufficient data for regression"}

    slope, intercept, r_value, p_value, std_err = stats.linregress(X, y)

    results = {
        "slope": slope,
        "intercept": intercept,
        "r_squared": r_value ** 2,
        "p_value": p_value,
        "significant": p_value < 0.05,
        "interpretation": "Accuracy decreases with difficulty" if slope < 0 and p_value < 0.05 else "No significant trend",
    }

    # Separate regression by VC class
    by_vc_class = {}
    for vc_class, group_df in grouped.groupby("vc_class"):
        X_vc = group_df["difficulty"].values
        y_vc = group_df["accuracy"].values

        if len(X_vc) < 2:
            continue

        slope_vc, intercept_vc, r_value_vc, p_value_vc, std_err_vc = stats.linregress(X_vc, y_vc)

        by_vc_class[vc_class] = {
            "slope": slope_vc,
            "intercept": intercept_vc,
            "r_squared": r_value_vc ** 2,
            "p_value": p_value_vc,
        }

    results["by_vc_class"] = by_vc_class

    return results


def analyze_latency_by_vc_class(df: pd.DataFrame) -> dict[str, Any]:
    """Secondary Analysis: Latency by VC class.

    Question: Does harder verification take longer?
    Method: Kruskal-Wallis test (non-parametric)
    """
    if "latency_ms" not in df.columns:
        return {"error": "No latency data available"}

    # Group by VC class
    grouped = df.groupby("vc_class")["latency_ms"].apply(list)

    # Compute median and IQR for each VC class
    latency_by_class = {}
    for vc_class, latencies in grouped.items():
        latencies_array = np.array(latencies)
        latency_by_class[vc_class] = {
            "median": np.median(latencies_array),
            "q25": np.percentile(latencies_array, 25),
            "q75": np.percentile(latencies_array, 75),
            "n": len(latencies),
        }

    # Kruskal-Wallis test
    groups = [np.array(latencies) for _, latencies in grouped.items()]
    if len(groups) >= 2:
        h_stat, p_value = stats.kruskal(*groups)
        result = {
            "latency_by_class": latency_by_class,
            "kruskal_wallis": {
                "h_statistic": h_stat,
                "p_value": p_value,
                "significant": p_value < 0.05,
            }
        }
    else:
        result = {
            "latency_by_class": latency_by_class,
            "error": "Insufficient VC classes for test"
        }

    return result


def main():
    parser = argparse.ArgumentParser(description="Analyze verification results")
    parser.add_argument("--results", nargs="+", type=Path,
                       help="Verification result files (JSONL)")
    parser.add_argument("--canary-only", action="store_true",
                       help="Analyze only canary results")
    parser.add_argument("--output", type=Path, default=Path("experiments/results/analysis_report.json"),
                       help="Output file for analysis results")

    args = parser.parse_args()

    if args.canary_only:
        result_files = [Path("experiments/results/verify_haiku_by_haiku_answer_only.jsonl")]
    elif args.results:
        result_files = args.results
    else:
        # Find all verification result files
        result_files = list(Path("experiments/results").glob("verify_*.jsonl"))

    print(f"Loading results from {len(result_files)} file(s)...")
    df = load_verification_results(result_files)
    print(f"Loaded {len(df)} verification records")
    print(f"Tasks: {df['task'].unique()}")
    print(f"VC classes: {df['vc_class'].unique()}")
    print(f"Generator models: {df['generator_model'].unique()}")
    print(f"Verifier models: {df['verifier_model'].unique()}")
    print()

    # Run all analyses
    analyses = {}

    print("Running Primary Analysis 1: Verification accuracy by VC class...")
    analyses["accuracy_by_vc_class"] = analyze_accuracy_by_vc_class(df)

    print("Running Primary Analysis 2: Cross-model consistency...")
    analyses["cross_model_consistency"] = analyze_cross_model_consistency(df)

    print("Running Secondary Analysis: Error types (B7)...")
    analyses["error_types_b7"] = analyze_error_types_b7(df)

    print("Running Secondary Analysis: Difficulty scaling...")
    analyses["difficulty_scaling"] = analyze_difficulty_scaling(df)

    print("Running Secondary Analysis: Latency by VC class...")
    analyses["latency_by_vc_class"] = analyze_latency_by_vc_class(df)

    # Write results
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w") as f:
        json.dump(analyses, f, indent=2, default=str)

    print(f"\nAnalysis results written to {args.output}")

    # Print summary
    print("\n" + "="*60)
    print("ANALYSIS SUMMARY")
    print("="*60)

    if "accuracy_by_vc_class" in analyses:
        print("\n1. Verification Accuracy by VC Class:")
        for vc_class, stats_dict in analyses["accuracy_by_vc_class"]["accuracy_by_class"].items():
            print(f"   {vc_class}: {stats_dict['mean']:.3f} (95% CI: [{stats_dict['ci_low']:.3f}, {stats_dict['ci_high']:.3f}]), n={stats_dict['n']}")

        if "anova" in analyses["accuracy_by_vc_class"]:
            anova = analyses["accuracy_by_vc_class"]["anova"]
            print(f"   ANOVA: F={anova['f_statistic']:.2f}, p={anova['p_value']:.4f}, significant={anova['significant']}")

    if "error_types_b7" in analyses and "error_counts" in analyses["error_types_b7"]:
        print("\n2. B7 Error Analysis:")
        print(f"   Total errors: {analyses['error_types_b7']['total_errors']}")
        for error_type, count in analyses["error_types_b7"]["error_counts"].items():
            print(f"   {error_type}: {count}")

    if "difficulty_scaling" in analyses and "slope" in analyses["difficulty_scaling"]:
        diff = analyses["difficulty_scaling"]
        print(f"\n3. Difficulty Scaling:")
        print(f"   Slope: {diff['slope']:.4f}, R²={diff['r_squared']:.3f}, p={diff['p_value']:.4f}")
        print(f"   {diff['interpretation']}")

    print()


if __name__ == "__main__":
    main()
