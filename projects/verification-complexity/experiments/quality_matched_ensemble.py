#!/usr/bin/env python3
"""
Quality-Matched Between-Model Ensemble Analysis

Compares within-model self-consistency (from Day 1 SC data) against
between-model majority vote using quality-matched models from the
reasoning-gaps evaluation.

Key question: Does between-model ensemble outperform within-model SC
when models are quality-matched (similar base accuracy)?
"""

import json
import os
import glob
import random
import math
import numpy as np
from collections import defaultdict
from itertools import combinations

random.seed(42)
np.random.seed(42)

# Paths
RG_RESULTS = "/Users/oddurs/Code/deepwork/projects/reasoning-gaps/benchmarks/results"
SC_RESULTS = "/Users/oddurs/Code/deepwork/projects/verification-complexity/experiments/results"

TASKS = ["B4", "B6", "B7"]
HAIKU_MODEL = "claude-haiku-4-5-20251001"

# =============================================================================
# 1. Load between-model data from reasoning-gaps
# =============================================================================

def load_between_model_data():
    """Load all short_cot results for B4, B6, B7 from reasoning-gaps."""
    data = {}  # {task: {model_key: {instance_id: correct}}}

    for task in TASKS:
        data[task] = {}
        pattern = os.path.join(RG_RESULTS, f"*_{task}_short_cot.json")
        files = glob.glob(pattern)

        for fpath in files:
            fname = os.path.basename(fpath)
            # Parse model key from filename: provider_model_task_condition.json
            # Handle nested model names like openrouter_meta-llama_llama-3.1-8b-instruct
            parts = fname.replace("_short_cot.json", "").split(f"_{task}")
            model_key = parts[0]

            with open(fpath) as f:
                content = json.load(f)

            results = content.get("results", [])
            instance_data = {}
            for r in results:
                instance_data[r["instance_id"]] = r["correct"]

            accuracy = sum(instance_data.values()) / len(instance_data) if instance_data else 0
            data[task][model_key] = {
                "instances": instance_data,
                "accuracy": accuracy,
                "n_instances": len(instance_data)
            }

    return data


# =============================================================================
# 2. Load within-model SC data
# =============================================================================

def load_within_model_sc():
    """Load N=33 SC data for Haiku on B4, B6, B7."""
    sc_data = {}

    for task in TASKS:
        fpath = os.path.join(SC_RESULTS, f"sc_haiku_{task}_short_cot_n33.jsonl")
        if not os.path.exists(fpath):
            print(f"  WARNING: {fpath} not found")
            continue

        instances = []
        with open(fpath) as f:
            for line in f:
                instances.append(json.loads(line))

        sc_data[task] = instances

    return sc_data


def within_model_majority_vote(instances, n):
    """Compute majority vote accuracy using first n samples per instance."""
    correct = 0
    total = 0
    for inst in instances:
        flags = inst["correct_flags"][:n]
        vote = sum(flags) > n / 2
        if vote:
            correct += 1
        total += 1
    return correct / total if total > 0 else 0


# =============================================================================
# 3. Quality-matched between-model ensemble
# =============================================================================

def quality_matched_ensemble(between_data, haiku_acc, task, margin=0.10):
    """
    Find models within margin of Haiku's accuracy and compute
    between-model majority vote at various N values.
    """
    models_in_range = []

    print(f"\n  === {task} (Haiku acc = {haiku_acc:.3f}, margin = +/-{margin:.0%}) ===")
    print(f"  Quality band: [{haiku_acc - margin:.3f}, {haiku_acc + margin:.3f}]")

    for model_key, mdata in between_data[task].items():
        acc = mdata["accuracy"]
        in_range = abs(acc - haiku_acc) <= margin
        marker = " <-- MATCHED" if in_range else ""
        print(f"    {model_key}: acc={acc:.3f} (n={mdata['n_instances']}){marker}")
        if in_range:
            models_in_range.append(model_key)

    print(f"  Matched models: {len(models_in_range)}")

    if len(models_in_range) < 3:
        print(f"  WARNING: Only {len(models_in_range)} matched models, need >= 3")
        return None

    # Find common instances across ALL matched models
    common_instances = None
    for mk in models_in_range:
        inst_ids = set(between_data[task][mk]["instances"].keys())
        if common_instances is None:
            common_instances = inst_ids
        else:
            common_instances = common_instances & inst_ids

    common_instances = sorted(common_instances)
    print(f"  Common instances across matched models: {len(common_instances)}")

    # Build instance x model correctness matrix
    model_list = models_in_range
    n_models = len(model_list)
    n_instances = len(common_instances)

    matrix = np.zeros((n_instances, n_models), dtype=bool)
    for j, mk in enumerate(model_list):
        for i, iid in enumerate(common_instances):
            matrix[i, j] = between_data[task][mk]["instances"][iid]

    # Compute between-model majority vote at various N values
    results = {}
    for n in [3, 5, 9]:
        if n > n_models:
            print(f"  N={n}: skipped (only {n_models} models)")
            continue

        # Sample subsets of N models and compute majority vote
        n_subsets = min(200, int(math.factorial(n_models) /
                                  (math.factorial(n) * math.factorial(n_models - n)))
                        ) if n_models >= n else 0

        all_combos = list(combinations(range(n_models), n))
        if len(all_combos) > 200:
            sampled_combos = random.sample(all_combos, 200)
        else:
            sampled_combos = all_combos

        subset_accs = []
        for combo in sampled_combos:
            sub_matrix = matrix[:, combo]
            votes = sub_matrix.sum(axis=1) > n / 2
            acc = votes.mean()
            subset_accs.append(acc)

        mean_acc = np.mean(subset_accs)
        std_acc = np.std(subset_accs)

        results[n] = {
            "mean_acc": float(mean_acc),
            "std_acc": float(std_acc),
            "n_subsets": len(sampled_combos),
            "n_models_available": n_models,
            "n_instances": n_instances
        }
        print(f"  N={n}: between-model acc = {mean_acc:.3f} +/- {std_acc:.3f} "
              f"({len(sampled_combos)} subsets of {n_models} models, {n_instances} instances)")

    return {
        "matched_models": models_in_range,
        "n_matched": len(models_in_range),
        "n_common_instances": len(common_instances),
        "results_by_n": results,
        "model_accuracies": {mk: between_data[task][mk]["accuracy"] for mk in models_in_range}
    }


# =============================================================================
# 4. Compute within-model SC on common instances
# =============================================================================

def within_model_on_common(sc_data, common_instance_ids, task, ns=[3, 5, 9]):
    """Compute within-model SC accuracy on the same instances used for between-model."""
    instances = sc_data[task]

    # Map instance IDs
    sc_by_id = {inst["instance_id"]: inst for inst in instances}

    results = {}
    for n in ns:
        correct = 0
        total = 0
        for iid in common_instance_ids:
            if iid in sc_by_id:
                flags = sc_by_id[iid]["correct_flags"][:n]
                vote = sum(flags) > n / 2
                if vote:
                    correct += 1
                total += 1

        acc = correct / total if total > 0 else 0
        results[n] = {"accuracy": float(acc), "n_instances": total}

    return results


# =============================================================================
# 5. Compute between-model correlation on quality-matched models
# =============================================================================

def compute_between_model_rho(between_data, matched_models, task, common_instances):
    """Compute pairwise error correlation among quality-matched models."""
    model_list = matched_models
    n_models = len(model_list)
    n_instances = len(common_instances)

    # Build error matrix (1 = error, 0 = correct)
    error_matrix = np.zeros((n_instances, n_models))
    for j, mk in enumerate(model_list):
        for i, iid in enumerate(common_instances):
            error_matrix[i, j] = 0 if between_data[task][mk]["instances"][iid] else 1

    # Compute pairwise correlations
    correlations = []
    for j1 in range(n_models):
        for j2 in range(j1 + 1, n_models):
            e1 = error_matrix[:, j1]
            e2 = error_matrix[:, j2]
            # Pearson correlation of error indicators
            if np.std(e1) > 0 and np.std(e2) > 0:
                rho = np.corrcoef(e1, e2)[0, 1]
                correlations.append(rho)

    mean_rho = np.mean(correlations) if correlations else float('nan')
    return float(mean_rho), [float(c) for c in correlations]


# =============================================================================
# Main
# =============================================================================

def main():
    print("=" * 70)
    print("QUALITY-MATCHED BETWEEN-MODEL ENSEMBLE ANALYSIS")
    print("=" * 70)

    # Load data
    print("\n1. Loading between-model data from reasoning-gaps...")
    between_data = load_between_model_data()
    for task in TASKS:
        print(f"  {task}: {len(between_data[task])} models loaded")

    print("\n2. Loading within-model SC data...")
    sc_data = load_within_model_sc()
    for task in TASKS:
        if task in sc_data:
            print(f"  {task}: {len(sc_data[task])} instances")

    # Haiku's base accuracy (from SC data, N=1)
    haiku_base_acc = {}
    for task in TASKS:
        instances = sc_data[task]
        acc = sum(1 for inst in instances if inst["correct_flags"][0]) / len(instances)
        haiku_base_acc[task] = acc
        print(f"  Haiku {task} base acc (SC N=1): {acc:.3f}")

    # Quality-matched ensemble analysis
    print("\n3. Quality-matched between-model ensemble analysis...")
    ensemble_results = {}

    for task in TASKS:
        result = quality_matched_ensemble(
            between_data,
            haiku_base_acc[task],
            task,
            margin=0.10
        )
        ensemble_results[task] = result

    # If any task has too few models, try wider margin
    for task in TASKS:
        if ensemble_results[task] is None or ensemble_results[task]["n_matched"] < 3:
            print(f"\n  Retrying {task} with margin=0.15...")
            result = quality_matched_ensemble(
                between_data,
                haiku_base_acc[task],
                task,
                margin=0.15
            )
            ensemble_results[task] = result

    # Compute within-model SC on matching instances for fair comparison
    print("\n4. Within-model SC on common instances (fair comparison)...")
    within_results = {}

    for task in TASKS:
        if ensemble_results[task] is None:
            print(f"  {task}: skipped (no between-model data)")
            continue

        # Get the common instance IDs from the between-model analysis
        matched_models = ensemble_results[task]["matched_models"]
        common_ids = set()
        for mk in matched_models:
            ids = set(between_data[task][mk]["instances"].keys())
            if not common_ids:
                common_ids = ids
            else:
                common_ids = common_ids & ids
        common_ids = sorted(common_ids)

        # Also intersect with SC data instance IDs
        sc_ids = {inst["instance_id"] for inst in sc_data[task]}
        common_ids = sorted(set(common_ids) & sc_ids)

        print(f"  {task}: {len(common_ids)} common instances (SC ∩ between-model)")

        within = within_model_on_common(sc_data, common_ids, task)
        within_results[task] = within

        for n in [3, 5, 9]:
            if n in within:
                print(f"    Within SC N={n}: {within[n]['accuracy']:.3f}")

    # Compute between-model rho for quality-matched models
    print("\n5. Between-model error correlation (quality-matched)...")
    rho_results = {}
    for task in TASKS:
        if ensemble_results[task] is None:
            continue
        matched = ensemble_results[task]["matched_models"]
        common_ids = set()
        for mk in matched:
            ids = set(between_data[task][mk]["instances"].keys())
            if not common_ids:
                common_ids = ids
            else:
                common_ids = common_ids & ids
        common_ids = sorted(common_ids)

        mean_rho, all_rhos = compute_between_model_rho(between_data, matched, task, common_ids)
        rho_results[task] = {"mean_rho": mean_rho, "n_pairs": len(all_rhos)}
        print(f"  {task}: mean between-model rho = {mean_rho:.3f} ({len(all_rhos)} pairs)")

    # Summary comparison table
    print("\n" + "=" * 70)
    print("SUMMARY: Within-Model SC vs Quality-Matched Between-Model Ensemble")
    print("=" * 70)

    summary = {}

    for task in TASKS:
        if ensemble_results[task] is None:
            continue

        print(f"\n--- {task} ---")
        print(f"  Haiku base acc: {haiku_base_acc[task]:.3f}")
        print(f"  Quality-matched models: {ensemble_results[task]['n_matched']}")

        if task in rho_results:
            print(f"  Between-model rho (quality-matched): {rho_results[task]['mean_rho']:.3f}")

        task_summary = {"base_acc": haiku_base_acc[task]}

        for n in [3, 5, 9]:
            within_acc = within_results.get(task, {}).get(n, {}).get("accuracy", None)
            between_acc = ensemble_results[task]["results_by_n"].get(n, {}).get("mean_acc", None)
            between_std = ensemble_results[task]["results_by_n"].get(n, {}).get("std_acc", None)

            if within_acc is not None and between_acc is not None:
                delta = between_acc - within_acc
                print(f"  N={n}: within={within_acc:.3f}, between={between_acc:.3f} "
                      f"(+/- {between_std:.3f}), delta={delta:+.3f} "
                      f"({'BETWEEN wins' if delta > 0 else 'WITHIN wins'})")

                task_summary[f"n{n}"] = {
                    "within": float(within_acc),
                    "between_mean": float(between_acc),
                    "between_std": float(between_std),
                    "delta": float(delta)
                }

        summary[task] = task_summary

    # Test the key hypotheses
    print("\n" + "=" * 70)
    print("HYPOTHESIS TESTS")
    print("=" * 70)

    # H1: Between-model beats within-model on B7 (stochastic, low rho)
    b7_n9 = summary.get("B7", {}).get("n9", {})
    if b7_n9:
        print(f"\nH1: Between-model beats within-model on B7 at N=9")
        print(f"    delta = {b7_n9.get('delta', 0):+.3f}")
        print(f"    Result: {'CONFIRMED' if b7_n9.get('delta', 0) > 0 else 'NOT CONFIRMED'}")

    # H2: Gap smaller or reversed on B6 (shared, high rho)
    b6_n9 = summary.get("B6", {}).get("n9", {})
    b7_n9_delta = b7_n9.get("delta", 0) if b7_n9 else 0
    b6_n9_delta = b6_n9.get("delta", 0) if b6_n9 else 0
    if b6_n9 and b7_n9:
        print(f"\nH2: Between-model gap on B6 <= gap on B7")
        print(f"    B6 delta = {b6_n9_delta:+.3f}, B7 delta = {b7_n9_delta:+.3f}")
        print(f"    Result: {'CONFIRMED' if b6_n9_delta <= b7_n9_delta else 'NOT CONFIRMED'}")

    # Save full results
    output = {
        "summary": summary,
        "ensemble_results": {},
        "within_results": {},
        "rho_results": rho_results,
        "haiku_base_acc": haiku_base_acc
    }

    for task in TASKS:
        if ensemble_results[task]:
            output["ensemble_results"][task] = {
                "matched_models": ensemble_results[task]["matched_models"],
                "n_matched": ensemble_results[task]["n_matched"],
                "model_accuracies": ensemble_results[task]["model_accuracies"],
                "results_by_n": ensemble_results[task]["results_by_n"]
            }
        if task in within_results:
            output["within_results"][task] = within_results[task]

    outpath = os.path.join(SC_RESULTS, "analysis", "quality_matched_ensemble.json")
    os.makedirs(os.path.dirname(outpath), exist_ok=True)
    with open(outpath, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved to {outpath}")


if __name__ == "__main__":
    main()
