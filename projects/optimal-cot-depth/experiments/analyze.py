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

def estimate_eta(
    curve: list[tuple[int, float, int]],
    cot_complexity: int,
) -> float | None:
    """Estimate per-step error rate eta from the decay region.

    Uses points where depth > cot_complexity to fit (1-eta)^k.
    Returns eta or None if insufficient data.
    """
    # Filter to decay region: depth >= cot_complexity and accuracy > 0
    decay_points = [
        (depth, acc) for depth, acc, _ in curve
        if depth >= cot_complexity and acc > 0
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

    print("=" * 70)
    print("ACCURACY vs DEPTH CURVES")
    print("=" * 70)

    eta_estimates: dict[str, list[float]] = defaultdict(list)
    dstar_comparisons: list[dict] = []

    for (task, diff, model), curve in sorted(curves.items()):
        c_n = cot_complexities.get((task, diff), 0)
        empirical_dstar = find_empirical_dstar(curve)
        eta = estimate_eta(curve, c_n)

        if eta is not None:
            eta_estimates[model].append(eta)
            predicted_dstar = min(c_n, int(1 / eta)) if eta > 0 else c_n
        else:
            predicted_dstar = c_n

        dstar_comparisons.append({
            "task": task,
            "difficulty": diff,
            "model": model,
            "c_n": c_n,
            "empirical_dstar": empirical_dstar,
            "predicted_dstar": predicted_dstar,
            "eta": eta,
        })

        print(f"\n{task} diff={diff} model={model} | c(n)={c_n}")
        for depth, acc, n in curve:
            bar = "█" * int(acc * 40)
            marker = " ← d*" if depth == empirical_dstar else ""
            print(f"  k={depth:3d}: {acc:5.1%} ({n:3d}) {bar}{marker}")
        if eta is not None:
            print(f"  η̂ = {eta:.3f} → ceiling ≈ {int(1/eta)}")
            print(f"  Predicted d* = min({c_n}, {int(1/eta)}) = {predicted_dstar}")
            print(f"  Empirical d* = {empirical_dstar}")

    # Per-model eta summary
    print("\n" + "=" * 70)
    print("PER-MODEL η ESTIMATES")
    print("=" * 70)
    for model, etas in sorted(eta_estimates.items()):
        if etas:
            mean_eta = sum(etas) / len(etas)
            print(f"  {model}: η̂ = {mean_eta:.4f} (ceiling ≈ {int(1/mean_eta)}, "
                  f"from {len(etas)} curves)")

    # d* comparison summary
    print("\n" + "=" * 70)
    print("d* COMPARISON: EMPIRICAL vs PREDICTED")
    print("=" * 70)
    print(f"  {'Task':<15} {'Diff':>4} {'Model':<10} {'c(n)':>5} "
          f"{'d*(emp)':>8} {'d*(pred)':>8} {'Match':>6}")
    for comp in dstar_comparisons:
        match = abs(comp["empirical_dstar"] - comp["predicted_dstar"]) <= 2
        print(f"  {comp['task']:<15} {comp['difficulty']:>4} {comp['model']:<10} "
              f"{comp['c_n']:>5} {comp['empirical_dstar']:>8} "
              f"{comp['predicted_dstar']:>8} {'✓' if match else '✗':>6}")


def main():
    parser = argparse.ArgumentParser(description="Analyze CoT depth experiment results.")
    parser.add_argument("results_dir", type=Path, nargs="?",
                        default=Path(__file__).parent / "results")
    args = parser.parse_args()
    run_analysis(args.results_dir)


if __name__ == "__main__":
    main()
