#!/usr/bin/env python3
"""Analysis pipeline for CoT depth experiments.

Reads JSONL results and produces:
1. Accuracy vs. depth curves per (task, difficulty, model)
2. Empirical d* (peak location) vs. predicted min(c(n), 1/eta)
3. Per-model eta estimation from noise ceiling decay
4. Capability ceiling validation

Usage:
    python3 experiments/analyze.py results/
    python3 experiments/analyze.py results/ --plot
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from collections import defaultdict
from pathlib import Path


def load_results(results_dir: Path) -> list[dict]:
    """Load all JSONL result files from a directory."""
    results = []
    for path in sorted(results_dir.glob("*.jsonl")):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line:
                    results.append(json.loads(line))
    return results


def group_results(
    results: list[dict],
) -> dict[tuple[str, int, int, str], list[dict]]:
    """Group results by (task, difficulty, depth, model)."""
    groups: dict[tuple, list[dict]] = defaultdict(list)
    for r in results:
        key = (r["task"], r["difficulty"], r["depth_requested"], r["model"])
        groups[key].append(r)
    return groups


def compute_accuracy(results: list[dict]) -> float:
    """Compute accuracy from a list of result dicts."""
    if not results:
        return 0.0
    correct = sum(1 for r in results if r.get("correct", False))
    return correct / len(results)


# ---------------------------------------------------------------------------
# Analysis 1: Accuracy vs. depth curves
# ---------------------------------------------------------------------------

def accuracy_curves(results: list[dict]) -> dict:
    """Compute accuracy vs. depth for each (task, difficulty, model).

    Returns dict mapping (task, difficulty, model) -> list of (depth, accuracy, n).
    """
    groups = group_results(results)

    # Regroup by (task, difficulty, model)
    curves: dict[tuple[str, int, str], list[tuple[int, float, int]]] = defaultdict(list)
    for (task, diff, depth, model), group in sorted(groups.items()):
        acc = compute_accuracy(group)
        curves[(task, diff, model)].append((depth, acc, len(group)))

    return dict(curves)


# ---------------------------------------------------------------------------
# Analysis 2: Estimate eta from noise ceiling
# ---------------------------------------------------------------------------

def estimate_eta_from_curve(
    curve: list[tuple[int, float, int]],
    cot_complexity: int,
) -> float | None:
    """Estimate per-step error rate eta from the decay region of ONE curve.

    Uses ONLY points where depth >= cot_complexity (sufficiency saturated,
    pure exponential decay). Returns eta or None if insufficient data.
    """
    # Filter to pure decay region: depth >= c(n) and accuracy > 0
    decay_points = [
        (depth, acc) for depth, acc, _ in curve
        if depth >= cot_complexity and acc > 0 and cot_complexity > 0
    ]

    if len(decay_points) < 2:
        return None

    # Log-linear fit: log(acc(k)) = log(S_max) + k * log(1-eta)
    # Slope = log(1-eta), so eta = 1 - exp(slope)
    n = len(decay_points)
    sum_k = sum(k for k, _ in decay_points)
    sum_log_a = sum(math.log(a) for _, a in decay_points)
    sum_k2 = sum(k * k for k, _ in decay_points)
    sum_k_log_a = sum(k * math.log(a) for k, a in decay_points)

    denom = n * sum_k2 - sum_k * sum_k
    if abs(denom) < 1e-10:
        return None

    slope = (n * sum_k_log_a - sum_k * sum_log_a) / denom

    if slope >= 0:
        return None  # No decay — can't estimate eta

    eta = 1 - math.exp(slope)
    return max(0.001, min(eta, 0.5))  # Clamp to reasonable range


def estimate_model_eta(
    curves: dict[tuple[str, int, str], list[tuple[int, float, int]]],
    cot_complexities: dict[tuple[str, int], int],
    model: str,
) -> float | None:
    """Estimate eta for a model using ALL curves where decay data exists.

    Strategy: estimate eta from low-complexity tasks (where we have
    post-saturation data), then apply as a model-level parameter.
    """
    etas: list[float] = []
    for (task, diff, m), curve in curves.items():
        if m != model:
            continue
        c_n = cot_complexities.get((task, diff), 0)
        eta = estimate_eta_from_curve(curve, c_n)
        if eta is not None:
            etas.append(eta)

    if not etas:
        return None

    # Median is more robust than mean for small samples
    etas.sort()
    mid = len(etas) // 2
    return etas[mid] if len(etas) % 2 else (etas[mid - 1] + etas[mid]) / 2


# ---------------------------------------------------------------------------
# Analysis 3: Find empirical d*
# ---------------------------------------------------------------------------

def find_empirical_dstar(curve: list[tuple[int, float, int]]) -> int:
    """Find the depth with maximum accuracy."""
    if not curve:
        return 0
    best_depth, best_acc = 0, 0.0
    for depth, acc, _ in curve:
        if acc > best_acc:
            best_acc = acc
            best_depth = depth
    return best_depth


# ---------------------------------------------------------------------------
# Analysis 4: Bootstrap confidence intervals
# ---------------------------------------------------------------------------

def _bootstrap_accuracy(
    results: list[dict], n_bootstrap: int = 1000, seed: int = 99
) -> tuple[float, float, float]:
    """Bootstrap 95% CI for accuracy.

    Returns (accuracy, ci_low, ci_high).
    """
    import random
    rng = random.Random(seed)

    n = len(results)
    if n == 0:
        return 0.0, 0.0, 0.0

    point = compute_accuracy(results)
    if n < 5:
        return point, 0.0, 1.0  # Too few for meaningful CI

    boot_accs = []
    for _ in range(n_bootstrap):
        sample = [rng.choice(results) for _ in range(n)]
        boot_accs.append(compute_accuracy(sample))

    boot_accs.sort()
    lo = boot_accs[int(0.025 * n_bootstrap)]
    hi = boot_accs[int(0.975 * n_bootstrap)]
    return point, lo, hi


def bootstrap_dstar(
    grouped_results: dict[int, list[dict]],
    n_bootstrap: int = 1000,
    seed: int = 99,
) -> tuple[int, int, int]:
    """Bootstrap 95% CI for the empirical d*.

    Args:
        grouped_results: dict mapping depth -> list of result dicts

    Returns (dstar, ci_low, ci_high).
    """
    import random
    rng = random.Random(seed)

    depths = sorted(grouped_results.keys())
    if not depths:
        return 0, 0, 0

    # Point estimate
    accs = {d: compute_accuracy(grouped_results[d]) for d in depths}
    dstar = max(accs, key=accs.get)  # type: ignore

    # Bootstrap: resample within each depth, find peak
    boot_dstars = []
    for _ in range(n_bootstrap):
        boot_accs = {}
        for d in depths:
            rs = grouped_results[d]
            sample = [rng.choice(rs) for _ in range(len(rs))]
            boot_accs[d] = compute_accuracy(sample)
        boot_dstars.append(max(boot_accs, key=boot_accs.get))  # type: ignore

    boot_dstars.sort()
    lo = boot_dstars[int(0.025 * n_bootstrap)]
    hi = boot_dstars[int(0.975 * n_bootstrap)]
    return dstar, lo, hi


# ---------------------------------------------------------------------------
# Main analysis
# ---------------------------------------------------------------------------

def run_analysis(results_dir: Path):
    """Run the full analysis pipeline."""
    results = load_results(results_dir)
    if not results:
        print(f"No results found in {results_dir}")
        return

    print(f"Loaded {len(results)} results\n")

    curves = accuracy_curves(results)

    # Get cot_complexity from results
    cot_complexities: dict[tuple[str, int], int] = {}
    for r in results:
        key = (r["task"], r["difficulty"])
        cot_complexities[key] = r.get("cot_complexity", 0)

    # Step 1: Estimate per-model eta from low-complexity tasks
    print("=" * 70)
    print("PER-MODEL η ESTIMATES (from low-complexity decay regions)")
    print("=" * 70)

    models_found = sorted(set(m for _, _, m in curves.keys()))
    model_etas: dict[str, float] = {}
    for model in models_found:
        eta = estimate_model_eta(curves, cot_complexities, model)
        if eta is not None:
            model_etas[model] = eta
            print(f"  {model}: η̂ = {eta:.4f} → ceiling ≈ {int(1/eta)} steps")
        else:
            print(f"  {model}: insufficient decay data")

    # Step 2: Accuracy vs depth curves with bootstrap CIs
    print("\n" + "=" * 70)
    print("ACCURACY vs DEPTH CURVES")
    print("=" * 70)

    groups = group_results(results)
    dstar_comparisons: list[dict] = []

    for (task, diff, model), curve in sorted(curves.items()):
        c_n = cot_complexities.get((task, diff), 0)
        eta = model_etas.get(model)

        # Bootstrap d* with CI
        depth_groups: dict[int, list[dict]] = defaultdict(list)
        for r in results:
            if r["task"] == task and r["difficulty"] == diff and r.get("model") == model:
                depth_groups[r["depth_requested"]].append(r)

        if depth_groups:
            dstar, dstar_lo, dstar_hi = bootstrap_dstar(depth_groups)
        else:
            dstar = find_empirical_dstar(curve)
            dstar_lo = dstar_hi = dstar

        if eta is not None and eta > 0:
            predicted_dstar = min(c_n, int(1 / eta))
        else:
            predicted_dstar = c_n

        dstar_comparisons.append({
            "task": task,
            "difficulty": diff,
            "model": model,
            "c_n": c_n,
            "empirical_dstar": dstar,
            "dstar_ci": (dstar_lo, dstar_hi),
            "predicted_dstar": predicted_dstar,
            "eta": eta,
        })

        print(f"\n{task} diff={diff} model={model} | c(n)={c_n}")
        for depth, acc, n in curve:
            _, ci_lo, ci_hi = _bootstrap_accuracy(
                [r for r in results
                 if r["task"] == task and r["difficulty"] == diff
                 and r.get("model") == model and r["depth_requested"] == depth]
            )
            bar = "█" * int(acc * 40)
            marker = " ← d*" if depth == dstar else ""
            print(f"  k={depth:3d}: {acc:5.1%} [{ci_lo:.0%}-{ci_hi:.0%}] ({n:3d}) {bar}{marker}")
        print(f"  d* = {dstar} (95% CI: [{dstar_lo}, {dstar_hi}])")
        if eta is not None:
            print(f"  Predicted d* = min({c_n}, {int(1/eta)}) = {predicted_dstar}")

    # Step 3: d* comparison summary
    print("\n" + "=" * 70)
    print("d* COMPARISON: EMPIRICAL vs PREDICTED")
    print("=" * 70)
    print(f"  {'Task':<15} {'Diff':>4} {'Model':<10} {'c(n)':>5} "
          f"{'d*(emp)':>8} {'95%CI':>12} {'d*(pred)':>8} {'Match':>6}")
    for comp in dstar_comparisons:
        lo, hi = comp["dstar_ci"]
        pred = comp["predicted_dstar"]
        # Match if predicted falls within bootstrap CI
        match = lo <= pred <= hi
        print(f"  {comp['task']:<15} {comp['difficulty']:>4} {comp['model']:<10} "
              f"{comp['c_n']:>5} {comp['empirical_dstar']:>8} "
              f"[{lo:>4},{hi:>4}] "
              f"{pred:>8} {'✓' if match else '✗':>6}")


def main():
    parser = argparse.ArgumentParser(description="Analyze CoT depth experiment results.")
    parser.add_argument("results_dir", type=Path, nargs="?",
                        default=Path(__file__).parent / "results")
    args = parser.parse_args()
    run_analysis(args.results_dir)


if __name__ == "__main__":
    main()
