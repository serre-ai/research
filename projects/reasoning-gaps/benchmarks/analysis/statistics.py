"""Statistical testing and confidence intervals for ReasonGap analysis."""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats


def bootstrap_ci(
    accuracies: np.ndarray,
    n_bootstrap: int = 10_000,
    ci: float = 0.95,
    seed: int | None = None,
) -> tuple[float, float]:
    """Compute bootstrap confidence interval for accuracy (proportion).

    Args:
        accuracies: Boolean array (1 = correct, 0 = incorrect).
        n_bootstrap: Number of bootstrap resamples.
        ci: Confidence level (default 0.95 for 95% CI).
        seed: Random seed for reproducibility.

    Returns:
        (lower_bound, upper_bound) of the confidence interval.
    """
    accuracies = np.asarray(accuracies, dtype=float)
    n = len(accuracies)

    if n == 0:
        return (0.0, 0.0)
    if n == 1:
        val = float(accuracies[0])
        return (val, val)

    rng = np.random.default_rng(seed)
    boot_means = np.empty(n_bootstrap)

    for i in range(n_bootstrap):
        sample = rng.choice(accuracies, size=n, replace=True)
        boot_means[i] = sample.mean()

    alpha = 1 - ci
    lower = float(np.percentile(boot_means, 100 * alpha / 2))
    upper = float(np.percentile(boot_means, 100 * (1 - alpha / 2)))

    return (lower, upper)


def mcnemar_test(
    correct_a: np.ndarray,
    correct_b: np.ndarray,
) -> tuple[float, float]:
    """McNemar's test for paired comparison of two models.

    Tests whether two models have the same error rate on paired instances.

    Args:
        correct_a: Boolean array of correctness for model A.
        correct_b: Boolean array of correctness for model B.

    Returns:
        (statistic, p_value). Uses continuity correction.
    """
    correct_a = np.asarray(correct_a, dtype=bool)
    correct_b = np.asarray(correct_b, dtype=bool)

    if len(correct_a) != len(correct_b):
        raise ValueError(
            f"Arrays must have same length: {len(correct_a)} vs {len(correct_b)}"
        )

    # Contingency counts
    # b = model A correct, model B wrong
    # c = model A wrong, model B correct
    b = int(np.sum(correct_a & ~correct_b))
    c = int(np.sum(~correct_a & correct_b))

    # McNemar's test with continuity correction
    if b + c == 0:
        return (0.0, 1.0)

    statistic = (abs(b - c) - 1) ** 2 / (b + c)
    p_value = float(1 - stats.chi2.cdf(statistic, df=1))

    return (float(statistic), p_value)


def compute_all_cis(
    df: pd.DataFrame,
    n_bootstrap: int = 10_000,
    ci: float = 0.95,
    seed: int = 42,
) -> pd.DataFrame:
    """Compute 95% CI on accuracy for each (task, model, condition) group.

    Args:
        df: DataFrame with columns: task, model, condition, correct.
        n_bootstrap: Number of bootstrap resamples per group.
        ci: Confidence level.
        seed: Random seed.

    Returns:
        DataFrame with columns: task, model, condition, accuracy,
        ci_lower, ci_upper, n_instances.
    """
    rows = []
    groups = df.groupby(["task", "model", "condition"], sort=False)

    for (task, model, condition), group in groups:
        correct_arr = group["correct"].values.astype(float)
        accuracy = correct_arr.mean()
        lower, upper = bootstrap_ci(correct_arr, n_bootstrap=n_bootstrap, ci=ci, seed=seed)

        rows.append({
            "task": task,
            "model": model,
            "condition": condition,
            "accuracy": accuracy,
            "ci_lower": lower,
            "ci_upper": upper,
            "n_instances": len(correct_arr),
        })

    return pd.DataFrame(rows)


def pairwise_model_comparison(
    df: pd.DataFrame,
    model_a: str,
    model_b: str,
) -> pd.DataFrame:
    """Run McNemar's test comparing two models on each task.

    Pairs instances by instance_id within each (task, condition) group.

    Args:
        df: DataFrame with columns: task, model, condition, instance_id, correct.
        model_a: Name of the first model.
        model_b: Name of the second model.

    Returns:
        DataFrame with columns: task, condition, accuracy_a, accuracy_b,
        mcnemar_stat, p_value, significant (at alpha=0.05).
    """
    df_a = df[df["model"] == model_a].set_index(["task", "condition", "instance_id"])
    df_b = df[df["model"] == model_b].set_index(["task", "condition", "instance_id"])

    # Find shared instances
    shared_idx = df_a.index.intersection(df_b.index)

    if shared_idx.empty:
        return pd.DataFrame(columns=[
            "task", "condition", "accuracy_a", "accuracy_b",
            "mcnemar_stat", "p_value", "significant",
        ])

    df_a_shared = df_a.loc[shared_idx]
    df_b_shared = df_b.loc[shared_idx]

    rows = []
    for (task, condition), group_idx in shared_idx.to_frame(index=False).groupby(
        ["task", "condition"]
    ).groups.items():
        ids = shared_idx[group_idx]
        correct_a = df_a_shared.loc[ids, "correct"].values.astype(bool)
        correct_b = df_b_shared.loc[ids, "correct"].values.astype(bool)

        stat, p_val = mcnemar_test(correct_a, correct_b)

        rows.append({
            "task": task,
            "condition": condition,
            "accuracy_a": correct_a.mean(),
            "accuracy_b": correct_b.mean(),
            "mcnemar_stat": stat,
            "p_value": p_val,
            "significant": p_val < 0.05,
        })

    result = pd.DataFrame(rows)
    return result.sort_values(["task", "condition"]).reset_index(drop=True)
