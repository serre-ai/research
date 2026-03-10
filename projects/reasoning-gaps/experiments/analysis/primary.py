"""Primary analyses for ReasonGap benchmark evaluation.

Implements the 6 primary analyses specified in empirical analysis plan:
1. Gap Type Validation
2. CoT Effectiveness by Gap Type
3. CoT Budget Sufficiency
4. Scale Dependence
5. Tool Augmentation
6. Faithfulness Correlation
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Any
from pathlib import Path
import json

from .stats_utils import (
    spearman_correlation,
    one_way_anova,
    tukey_hsd_posthoc,
    friedman_test,
    jonckheere_terpstra_test,
    paired_t_test,
    cohens_d,
    mixed_effects_model,
    chi_square_test,
    bonferroni_correction,
    bootstrap_ci,
    TestResult
)


# Task to gap type mapping (from formal framework)
TASK_GAP_TYPES = {
    "B1": "Type 1: Sensitivity",
    "B2": "Type 2: Depth-bounded",
    "B3": "Type 3: Serial",
    "B4": "Type 3: Serial",
    "B5": "Type 2: Depth-bounded",
    "B6": "Type 5: Algorithmic",
    "B7": "Type 6: Intractability",
    "B8": "Type 4: Counterfactual",
    "B9": "Type 4: Counterfactual"
}

# Model size categories
MODEL_SIZES = {
    "claude-haiku-3.5": "small",
    "claude-sonnet-3.5": "medium",
    "claude-opus-3": "large",
    "gpt-4o-mini": "small",
    "gpt-4o": "medium",
    "o3": "large",
    "llama-3.1-8b": "small",
    "llama-3.1-70b": "medium",
    "mistral-7b": "small",
    "mistral-large": "medium",
    "qwen-2.5-7b": "small",
    "qwen-2.5-72b": "medium"
}

# Model families
MODEL_FAMILIES = {
    "claude-haiku-3.5": "Claude",
    "claude-sonnet-3.5": "Claude",
    "claude-opus-3": "Claude",
    "gpt-4o-mini": "GPT",
    "gpt-4o": "GPT",
    "o3": "GPT",
    "llama-3.1-8b": "Llama",
    "llama-3.1-70b": "Llama",
    "mistral-7b": "Mistral",
    "mistral-large": "Mistral",
    "qwen-2.5-7b": "Qwen",
    "qwen-2.5-72b": "Qwen"
}


def load_results(results_dir: Path) -> pd.DataFrame:
    """Load all evaluation results into a DataFrame.

    Args:
        results_dir: Directory containing result JSON files

    Returns:
        DataFrame with all evaluation results
    """
    results = []

    for result_file in results_dir.glob("*.json"):
        with open(result_file) as f:
            data = json.load(f)

        # Handle both single result and batch results
        if isinstance(data, list):
            results.extend(data)
        else:
            results.append(data)

    df = pd.DataFrame(results)

    # Add derived columns
    df["gap_type"] = df["task"].map(TASK_GAP_TYPES)
    df["model_size"] = df["model"].map(MODEL_SIZES)
    df["model_family"] = df["model"].map(MODEL_FAMILIES)

    return df


def analysis_1_gap_type_validation(
    df: pd.DataFrame,
    output_dir: Path
) -> Dict[str, Any]:
    """Analysis 1: Gap Type Validation.

    Hypothesis: Each task exhibits systematic performance degradation with difficulty.
    Statistical test: Spearman correlation (negative) between difficulty and accuracy.
    Success criterion: Significant negative correlation for all 9 tasks.

    Args:
        df: Results DataFrame
        output_dir: Directory to save detailed results

    Returns:
        Dictionary with test results
    """
    results = {
        "analysis_name": "Gap Type Validation",
        "hypothesis": "Each task shows systematic accuracy degradation with difficulty",
        "test": "Spearman correlation",
        "per_task": {},
        "summary": {}
    }

    # Test each task separately (direct condition only for base validation)
    direct_df = df[df["condition"] == "direct"]

    task_results = []
    significant_count = 0

    for task in sorted(df["task"].unique()):
        task_df = direct_df[direct_df["task"] == task]

        if len(task_df) == 0:
            continue

        # Aggregate by difficulty level
        difficulty_groups = task_df.groupby("difficulty")["correct"].mean()

        if len(difficulty_groups) < 3:
            continue

        difficulties = difficulty_groups.index.values
        accuracies = difficulty_groups.values

        # Spearman correlation
        test_result = spearman_correlation(difficulties, accuracies)

        # Check if negative and significant
        is_negative = test_result.statistic < 0
        is_significant = test_result.is_significant()

        if is_negative and is_significant:
            significant_count += 1

        task_results.append({
            "task": task,
            "gap_type": TASK_GAP_TYPES[task],
            "rho": test_result.statistic,
            "p_value": test_result.p_value,
            "is_negative": is_negative,
            "is_significant": is_significant,
            "n_levels": len(difficulties),
            "interpretation": test_result.interpretation
        })

        results["per_task"][task] = test_result.to_dict()

    # Summary
    results["summary"] = {
        "total_tasks": len(task_results),
        "significant_negative": significant_count,
        "proportion": significant_count / len(task_results) if task_results else 0,
        "success": significant_count == len(task_results)
    }

    results["task_details"] = task_results

    # Save detailed results
    output_dir.mkdir(parents=True, exist_ok=True)
    with open(output_dir / "analysis_1_gap_validation.json", "w") as f:
        json.dump(results, f, indent=2)

    return results


def analysis_2_cot_effectiveness(
    df: pd.DataFrame,
    output_dir: Path
) -> Dict[str, Any]:
    """Analysis 2: CoT Effectiveness by Gap Type.

    Hypothesis: CoT lift varies systematically by gap type.
    Predicted order: Lift(Type 2,3) > Lift(Type 1,4) > Lift(Type 5,6)
    Statistical test: One-way ANOVA + Tukey HSD post-hoc.

    Args:
        df: Results DataFrame
        output_dir: Directory to save detailed results

    Returns:
        Dictionary with test results
    """
    results = {
        "analysis_name": "CoT Effectiveness by Gap Type",
        "hypothesis": "CoT lift varies by gap type: Types 2,3 > Types 1,4 > Types 5,6",
        "test": "One-way ANOVA with Tukey HSD",
        "per_gap_type": {},
        "anova": {},
        "posthoc": {},
        "summary": {}
    }

    # Calculate CoT lift for each (model, task, difficulty)
    direct_df = df[df["condition"] == "direct"]
    cot_df = df[df["condition"] == "short_cot"]

    # Merge to compute lift
    merged = pd.merge(
        direct_df,
        cot_df,
        on=["model", "task", "difficulty", "instance_id"],
        suffixes=("_direct", "_cot")
    )

    # CoT lift = accuracy_cot - accuracy_direct
    merged["cot_lift"] = merged["correct_cot"].astype(float) - merged["correct_direct"].astype(float)

    # Aggregate by (model, task)
    lift_by_model_task = merged.groupby(["model", "task", "gap_type_cot"])["cot_lift"].mean().reset_index()
    lift_by_model_task.rename(columns={"gap_type_cot": "gap_type"}, inplace=True)

    # Group by gap type
    gap_types = lift_by_model_task["gap_type"].unique()
    gap_type_groups = [
        lift_by_model_task[lift_by_model_task["gap_type"] == gt]["cot_lift"].values
        for gt in gap_types
    ]

    # ANOVA
    anova_result = one_way_anova(gap_type_groups, list(gap_types))
    results["anova"] = anova_result.to_dict()

    # Post-hoc Tukey HSD
    if anova_result.is_significant():
        tukey_results = tukey_hsd_posthoc(
            lift_by_model_task,
            value_col="cot_lift",
            group_col="gap_type"
        )
        results["posthoc"]["significant_pairs"] = tukey_results[
            tukey_results["reject"] == True
        ].to_dict(orient="records")
        results["posthoc"]["all_pairs"] = tukey_results.to_dict(orient="records")
    else:
        results["posthoc"]["note"] = "ANOVA not significant, post-hoc not performed"

    # Per gap type summary
    for gap_type in gap_types:
        gap_lifts = lift_by_model_task[lift_by_model_task["gap_type"] == gap_type]["cot_lift"]

        mean_lift = gap_lifts.mean()
        _, ci_low, ci_high = bootstrap_ci(gap_lifts.values, n_bootstrap=1000, random_seed=42)

        results["per_gap_type"][gap_type] = {
            "mean_lift": float(mean_lift),
            "std": float(gap_lifts.std()),
            "n": int(len(gap_lifts)),
            "ci_95": [float(ci_low), float(ci_high)]
        }

    # Check if predicted order holds
    type_means = {gt: results["per_gap_type"][gt]["mean_lift"] for gt in gap_types}

    # Extract types (assuming format "Type N: Description")
    type_nums = {gt: int(gt.split()[1].rstrip(':')) for gt in gap_types}

    # Check if Type 2,3 > Type 1,4 > Type 5,6
    types_2_3 = [gt for gt, num in type_nums.items() if num in [2, 3]]
    types_1_4 = [gt for gt, num in type_nums.items() if num in [1, 4]]
    types_5_6 = [gt for gt, num in type_nums.items() if num in [5, 6]]

    mean_2_3 = np.mean([type_means[t] for t in types_2_3]) if types_2_3 else 0
    mean_1_4 = np.mean([type_means[t] for t in types_1_4]) if types_1_4 else 0
    mean_5_6 = np.mean([type_means[t] for t in types_5_6]) if types_5_6 else 0

    predicted_order_holds = (mean_2_3 > mean_1_4) and (mean_1_4 > mean_5_6)

    results["summary"] = {
        "anova_significant": anova_result.is_significant(),
        "effect_size": anova_result.effect_size,
        "predicted_order": "Types 2,3 > Types 1,4 > Types 5,6",
        "observed_means": {
            "Types 2,3": float(mean_2_3),
            "Types 1,4": float(mean_1_4),
            "Types 5,6": float(mean_5_6)
        },
        "predicted_order_holds": predicted_order_holds
    }

    # Save
    output_dir.mkdir(parents=True, exist_ok=True)
    with open(output_dir / "analysis_2_cot_effectiveness.json", "w") as f:
        json.dump(results, f, indent=2)

    return results


def analysis_3_cot_budget_sufficiency(
    df: pd.DataFrame,
    output_dir: Path
) -> Dict[str, Any]:
    """Analysis 3: CoT Budget Sufficiency.

    Hypothesis: Accuracy plateaus at theoretically predicted budget.
    Statistical test: Friedman test + Jonckheere-Terpstra trend test.
    Tests Proposition 4 (monotonicity).

    Args:
        df: Results DataFrame
        output_dir: Directory to save detailed results

    Returns:
        Dictionary with test results
    """
    results = {
        "analysis_name": "CoT Budget Sufficiency",
        "hypothesis": "Accuracy increases monotonically with budget up to optimal",
        "test": "Friedman test + Jonckheere-Terpstra",
        "per_task": {},
        "summary": {}
    }

    # Budget conditions: direct, log, linear, quadratic
    budget_order = ["direct", "budget_cot_log", "budget_cot_linear", "short_cot"]

    task_results = []

    for task in sorted(df["task"].unique()):
        task_df = df[df["task"] == task]

        # Get accuracy for each budget level (averaged across difficulty and models)
        budget_accuracies = {}

        for condition in budget_order:
            cond_df = task_df[task_df["condition"] == condition]
            if len(cond_df) > 0:
                budget_accuracies[condition] = cond_df["correct"].mean()

        if len(budget_accuracies) < 3:
            continue

        # Prepare data for Friedman test (need repeated measures)
        # Group by (model, difficulty) and get accuracy for each budget
        grouped = task_df.groupby(["model", "difficulty", "condition"])["correct"].mean().unstack(fill_value=0)

        # Filter to budget conditions that exist
        available_budgets = [b for b in budget_order if b in grouped.columns]

        if len(available_budgets) < 3:
            continue

        # Friedman test
        budget_arrays = [grouped[b].values for b in available_budgets]
        friedman_result = friedman_test(*budget_arrays)

        # Jonckheere-Terpstra (test for monotonic trend)
        jt_result = jonckheere_terpstra_test(budget_arrays, alternative="increasing")

        task_results.append({
            "task": task,
            "gap_type": TASK_GAP_TYPES[task],
            "friedman_p": friedman_result.p_value,
            "friedman_significant": friedman_result.is_significant(),
            "jt_p": jt_result.p_value,
            "jt_significant": jt_result.is_significant(),
            "monotonic_trend": jt_result.is_significant(),
            "budgets_tested": available_budgets,
            "mean_accuracies": {b: float(budget_accuracies.get(b, 0)) for b in available_budgets}
        })

        results["per_task"][task] = {
            "friedman": friedman_result.to_dict(),
            "jonckheere_terpstra": jt_result.to_dict(),
            "budget_accuracies": {b: float(budget_accuracies.get(b, 0)) for b in available_budgets}
        }

    # Summary
    monotonic_count = sum(1 for t in task_results if t["monotonic_trend"])

    results["summary"] = {
        "total_tasks": len(task_results),
        "monotonic_trend_confirmed": monotonic_count,
        "proportion": monotonic_count / len(task_results) if task_results else 0,
        "success": monotonic_count >= len(task_results) * 0.8  # 80% threshold
    }

    results["task_details"] = task_results

    # Save
    output_dir.mkdir(parents=True, exist_ok=True)
    with open(output_dir / "analysis_3_budget_sufficiency.json", "w") as f:
        json.dump(results, f, indent=2)

    return results


def analysis_4_scale_dependence(
    df: pd.DataFrame,
    output_dir: Path
) -> Dict[str, Any]:
    """Analysis 4: Scale Dependence.

    Hypothesis: Architectural gaps (Types 5,6) are scale-invariant;
                other gaps improve moderately with scale.
    Statistical test: Mixed-effects model with size × gap_type interaction.

    Args:
        df: Results DataFrame
        output_dir: Directory to save detailed results

    Returns:
        Dictionary with test results
    """
    results = {
        "analysis_name": "Scale Dependence",
        "hypothesis": "Architectural gaps (5,6) scale-invariant; others improve with scale",
        "test": "Mixed-effects model",
        "model": {},
        "per_gap_type": {},
        "summary": {}
    }

    # Use direct condition only
    direct_df = df[df["condition"] == "direct"]

    # Aggregate by (model, task, model_size)
    agg_df = direct_df.groupby(["model", "task", "model_size", "gap_type", "model_family"])["correct"].mean().reset_index()
    agg_df.rename(columns={"correct": "accuracy"}, inplace=True)

    # Convert size to numeric
    size_map = {"small": 1, "medium": 2, "large": 3}
    agg_df["size_numeric"] = agg_df["model_size"].map(size_map)

    # Fit mixed-effects model: accuracy ~ size * gap_type + (1 | model_family)
    try:
        model_result = mixed_effects_model(
            agg_df,
            formula="accuracy ~ size_numeric * gap_type",
            groups="model_family"
        )

        results["model"] = model_result

        # Check for significant size × gap_type interaction
        interaction_terms = [k for k in model_result["pvalues"].keys() if "size_numeric:gap_type" in k]
        significant_interactions = [
            term for term in interaction_terms
            if model_result["pvalues"][term] < 0.05
        ]

        results["summary"]["significant_interactions"] = significant_interactions
        results["summary"]["interaction_detected"] = len(significant_interactions) > 0

    except Exception as e:
        results["model"]["error"] = str(e)
        results["summary"]["note"] = "Mixed-effects model failed to fit"

    # Per gap type: correlation between size and accuracy
    for gap_type in agg_df["gap_type"].unique():
        gap_df = agg_df[agg_df["gap_type"] == gap_type]

        corr_result = spearman_correlation(
            gap_df["size_numeric"].values,
            gap_df["accuracy"].values
        )

        # Bootstrap CI for mean accuracy at each size
        size_means = {}
        for size in ["small", "medium", "large"]:
            size_acc = gap_df[gap_df["model_size"] == size]["accuracy"]
            if len(size_acc) > 0:
                mean_acc, ci_low, ci_high = bootstrap_ci(
                    size_acc.values,
                    n_bootstrap=1000,
                    random_seed=42
                )
                size_means[size] = {
                    "mean": float(mean_acc),
                    "ci_95": [float(ci_low), float(ci_high)]
                }

        results["per_gap_type"][gap_type] = {
            "correlation": corr_result.to_dict(),
            "size_means": size_means,
            "scale_dependent": corr_result.is_significant() and corr_result.statistic > 0
        }

    # Check hypothesis: Types 5,6 should have low/non-significant correlation
    types_5_6 = [gt for gt in results["per_gap_type"].keys() if any(f"Type {i}" in gt for i in [5, 6])]
    types_others = [gt for gt in results["per_gap_type"].keys() if gt not in types_5_6]

    scale_inv_5_6 = [
        not results["per_gap_type"][gt]["scale_dependent"]
        for gt in types_5_6
    ]
    scale_dep_others = [
        results["per_gap_type"][gt]["scale_dependent"]
        for gt in types_others
    ]

    results["summary"]["hypothesis_check"] = {
        "types_5_6_scale_invariant": all(scale_inv_5_6) if scale_inv_5_6 else None,
        "other_types_scale_dependent": any(scale_dep_others) if scale_dep_others else None,
        "success": all(scale_inv_5_6) if scale_inv_5_6 else False
    }

    # Save
    output_dir.mkdir(parents=True, exist_ok=True)
    with open(output_dir / "analysis_4_scale_dependence.json", "w") as f:
        json.dump(results, f, indent=2)

    return results


def analysis_5_tool_augmentation(
    df: pd.DataFrame,
    output_dir: Path
) -> Dict[str, Any]:
    """Analysis 5: Tool Augmentation.

    Hypothesis: Tool use provides large lift for algorithmic tasks (B6),
                minimal lift for intractable tasks (B7).
    Statistical test: Paired t-test with Cohen's d.

    Args:
        df: Results DataFrame
        output_dir: Directory to save detailed results

    Returns:
        Dictionary with test results
    """
    results = {
        "analysis_name": "Tool Augmentation",
        "hypothesis": "Tools help algorithmic (B6) but not intractable (B7) tasks",
        "test": "Paired t-test",
        "per_task": {},
        "summary": {}
    }

    # Tool condition only available for B5, B6, B7
    tool_tasks = ["B5", "B6", "B7"]

    for task in tool_tasks:
        task_df = df[df["task"] == task]

        # Compare short_cot vs tool
        cot_df = task_df[task_df["condition"] == "short_cot"]
        tool_df = task_df[task_df["condition"] == "tool"]

        if len(cot_df) == 0 or len(tool_df) == 0:
            continue

        # Merge on (model, difficulty, instance_id)
        merged = pd.merge(
            cot_df,
            tool_df,
            on=["model", "difficulty", "instance_id"],
            suffixes=("_cot", "_tool")
        )

        # Aggregate by model
        model_agg = merged.groupby("model").agg({
            "correct_cot": "mean",
            "correct_tool": "mean"
        }).reset_index()

        cot_acc = model_agg["correct_cot"].values
        tool_acc = model_agg["correct_tool"].values

        # Paired t-test
        ttest_result = paired_t_test(cot_acc, tool_acc, alternative="less")

        # Tool lift
        mean_lift = (tool_acc - cot_acc).mean()

        results["per_task"][task] = {
            "gap_type": TASK_GAP_TYPES[task],
            "mean_cot_accuracy": float(cot_acc.mean()),
            "mean_tool_accuracy": float(tool_acc.mean()),
            "mean_lift": float(mean_lift),
            "ttest": ttest_result.to_dict(),
            "significant_improvement": ttest_result.is_significant() and ttest_result.statistic < 0
        }

    # Summary: Check if B6 shows large lift and B7 shows minimal lift
    b6_lift = results["per_task"].get("B6", {}).get("mean_lift", 0)
    b7_lift = results["per_task"].get("B7", {}).get("mean_lift", 0)

    b6_significant = results["per_task"].get("B6", {}).get("significant_improvement", False)
    b7_not_significant = not results["per_task"].get("B7", {}).get("significant_improvement", True)

    results["summary"] = {
        "b6_algorithmic_lift": float(b6_lift),
        "b7_intractable_lift": float(b7_lift),
        "b6_significant": b6_significant,
        "b7_not_significant": b7_not_significant,
        "hypothesis_confirmed": b6_significant and b7_not_significant and (b6_lift > b7_lift)
    }

    # Save
    output_dir.mkdir(parents=True, exist_ok=True)
    with open(output_dir / "analysis_5_tool_augmentation.json", "w") as f:
        json.dump(results, f, indent=2)

    return results


def analysis_6_faithfulness_correlation(
    df: pd.DataFrame,
    output_dir: Path
) -> Dict[str, Any]:
    """Analysis 6: Faithfulness Correlation.

    Hypothesis: CoT reasoning is more faithful when computationally necessary (Types 2,3).
    Statistical test: Chi-square test for association between gap type and faithfulness.

    Note: Requires faithfulness annotation in data (manual or automated).

    Args:
        df: Results DataFrame
        output_dir: Directory to save detailed results

    Returns:
        Dictionary with test results
    """
    results = {
        "analysis_name": "Faithfulness Correlation",
        "hypothesis": "CoT more faithful for Types 2,3 (computationally necessary)",
        "test": "Chi-square test",
        "contingency_table": {},
        "chi_square": {},
        "summary": {}
    }

    # Check if faithfulness data available
    if "faithful" not in df.columns:
        results["summary"]["note"] = "Faithfulness annotation not available in data"
        results["summary"]["status"] = "skipped"

        # Save
        output_dir.mkdir(parents=True, exist_ok=True)
        with open(output_dir / "analysis_6_faithfulness.json", "w") as f:
            json.dump(results, f, indent=2)

        return results

    # Use short_cot condition only
    cot_df = df[df["condition"] == "short_cot"]

    # Create contingency table: gap type × faithful
    # Group types: 2-3 (computationally necessary) vs others
    cot_df["gap_group"] = cot_df["gap_type"].apply(
        lambda x: "Types 2-3" if any(f"Type {i}" in x for i in [2, 3]) else "Other Types"
    )

    contingency = pd.crosstab(cot_df["gap_group"], cot_df["faithful"])
    results["contingency_table"] = contingency.to_dict()

    # Chi-square test
    chi2_result = chi_square_test(contingency.values)
    results["chi_square"] = chi2_result.to_dict()

    # Per gap type faithfulness rate
    per_type = cot_df.groupby("gap_type")["faithful"].mean().to_dict()
    results["per_gap_type"] = {k: float(v) for k, v in per_type.items()}

    # Check hypothesis: Types 2-3 should have higher faithfulness rate
    types_2_3_faithful = cot_df[cot_df["gap_group"] == "Types 2-3"]["faithful"].mean()
    others_faithful = cot_df[cot_df["gap_group"] == "Other Types"]["faithful"].mean()

    results["summary"] = {
        "association_significant": chi2_result.is_significant(),
        "effect_size": chi2_result.effect_size,
        "types_2_3_faithfulness_rate": float(types_2_3_faithful),
        "other_types_faithfulness_rate": float(others_faithful),
        "hypothesis_confirmed": chi2_result.is_significant() and (types_2_3_faithful > others_faithful)
    }

    # Save
    output_dir.mkdir(parents=True, exist_ok=True)
    with open(output_dir / "analysis_6_faithfulness.json", "w") as f:
        json.dump(results, f, indent=2)

    return results


def run_all_primary_analyses(
    results_dir: Path,
    output_dir: Path
) -> Dict[str, Any]:
    """Run all 6 primary analyses.

    Args:
        results_dir: Directory with evaluation results
        output_dir: Directory to save analysis outputs

    Returns:
        Dictionary with all analysis results
    """
    print("Loading results...")
    df = load_results(results_dir)

    print(f"Loaded {len(df)} evaluation results")
    print(f"Tasks: {sorted(df['task'].unique())}")
    print(f"Models: {sorted(df['model'].unique())}")
    print(f"Conditions: {sorted(df['condition'].unique())}")

    all_results = {}

    print("\n" + "="*60)
    print("Running Analysis 1: Gap Type Validation")
    print("="*60)
    all_results["analysis_1"] = analysis_1_gap_type_validation(df, output_dir)

    print("\n" + "="*60)
    print("Running Analysis 2: CoT Effectiveness by Gap Type")
    print("="*60)
    all_results["analysis_2"] = analysis_2_cot_effectiveness(df, output_dir)

    print("\n" + "="*60)
    print("Running Analysis 3: CoT Budget Sufficiency")
    print("="*60)
    all_results["analysis_3"] = analysis_3_cot_budget_sufficiency(df, output_dir)

    print("\n" + "="*60)
    print("Running Analysis 4: Scale Dependence")
    print("="*60)
    all_results["analysis_4"] = analysis_4_scale_dependence(df, output_dir)

    print("\n" + "="*60)
    print("Running Analysis 5: Tool Augmentation")
    print("="*60)
    all_results["analysis_5"] = analysis_5_tool_augmentation(df, output_dir)

    print("\n" + "="*60)
    print("Running Analysis 6: Faithfulness Correlation")
    print("="*60)
    all_results["analysis_6"] = analysis_6_faithfulness_correlation(df, output_dir)

    # Save combined results
    with open(output_dir / "all_primary_analyses.json", "w") as f:
        json.dump(all_results, f, indent=2)

    print("\n" + "="*60)
    print("All primary analyses complete!")
    print("="*60)

    return all_results
