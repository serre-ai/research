#!/usr/bin/env python3
"""Generate synthetic data and test analysis pipeline.

Creates fake evaluation results that match the expected format
and tests that the analysis pipeline runs without errors.
"""

import json
import numpy as np
from pathlib import Path
import shutil

# Configuration
N_INSTANCES_PER_CONFIG = 20  # Small number for testing
OUTPUT_DIR = Path("test_data")
RESULTS_DIR = OUTPUT_DIR / "raw"
PROCESSED_DIR = OUTPUT_DIR / "processed"
FIGURES_DIR = OUTPUT_DIR / "figures"

# Tasks and their gap types
TASKS = {
    "B1": {"gap_type": "Type 1: Sensitivity", "difficulties": [10, 20, 40, 80]},
    "B2": {"gap_type": "Type 2: Depth-bounded", "difficulties": [2, 3, 4, 5]},
    "B3": {"gap_type": "Type 3: Serial", "difficulties": [5, 10, 15, 20]},
    "B4": {"gap_type": "Type 3: Serial", "difficulties": [10, 20, 30, 40]},
    "B5": {"gap_type": "Type 2: Depth-bounded", "difficulties": [3, 5, 7, 9]},
    "B6": {"gap_type": "Type 5: Algorithmic", "difficulties": [10, 20, 30, 40]},
    "B7": {"gap_type": "Type 6: Intractability", "difficulties": [10, 20, 30]},
    "B8": {"gap_type": "Type 4: Counterfactual", "difficulties": [5, 10, 15, 20]},
    "B9": {"gap_type": "Type 4: Counterfactual", "difficulties": [1, 2, 3, 4]},
}

MODELS = [
    {"name": "claude-haiku-3.5", "family": "Claude", "size": "small", "base_acc": 0.7},
    {"name": "claude-sonnet-3.5", "family": "Claude", "size": "medium", "base_acc": 0.8},
    {"name": "gpt-4o-mini", "family": "GPT", "size": "small", "base_acc": 0.65},
    {"name": "gpt-4o", "family": "GPT", "size": "medium", "base_acc": 0.85},
    {"name": "llama-3.1-8b", "family": "Llama", "size": "small", "base_acc": 0.6},
    {"name": "llama-3.1-70b", "family": "Llama", "size": "medium", "base_acc": 0.75},
]

CONDITIONS = ["direct", "short_cot", "tool"]


def generate_accuracy(model, task, difficulty, condition, gap_type):
    """Generate synthetic accuracy based on model, task, difficulty, and condition.

    Implements expected patterns:
    - Accuracy decreases with difficulty
    - CoT helps more for Types 2-3
    - Tools help for Type 5, not Type 6
    - Larger models perform better
    """
    base_acc = model["base_acc"]

    # Difficulty penalty (normalized)
    max_difficulty = max(TASKS[task]["difficulties"])
    difficulty_factor = 1 - (difficulty / max_difficulty) * 0.5  # Max 50% penalty

    # Start with base accuracy adjusted for difficulty
    acc = base_acc * difficulty_factor

    # Gap-specific adjustments
    if "Type 1" in gap_type:
        # Sensitivity: hard for all, CoT helps little
        acc *= 0.7
        if condition == "short_cot":
            acc += 0.05
    elif "Type 2" in gap_type:
        # Depth-bounded: CoT helps significantly
        if condition == "short_cot":
            acc += 0.15
    elif "Type 3" in gap_type:
        # Serial: CoT helps significantly
        if condition == "short_cot":
            acc += 0.20
    elif "Type 4" in gap_type:
        # Counterfactual: moderate CoT help
        if condition == "short_cot":
            acc += 0.10
    elif "Type 5" in gap_type:
        # Algorithmic: tools help a lot
        if condition == "short_cot":
            acc += 0.10
        elif condition == "tool":
            acc += 0.30
    elif "Type 6" in gap_type:
        # Intractability: nothing helps much
        if condition == "short_cot":
            acc += 0.02
        elif condition == "tool":
            acc += 0.03

    # Add noise
    acc += np.random.normal(0, 0.05)

    # Clip to [0, 1]
    return np.clip(acc, 0, 1)


def generate_synthetic_data():
    """Generate synthetic evaluation results."""
    print("Generating synthetic data...")

    # Clean up existing test data
    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    total_results = 0

    for task_id, task_info in TASKS.items():
        for model in MODELS:
            for condition in CONDITIONS:
                # Skip tool condition for non-tool tasks
                if condition == "tool" and task_id not in ["B5", "B6", "B7"]:
                    continue

                results = []

                for difficulty in task_info["difficulties"]:
                    for inst_idx in range(N_INSTANCES_PER_CONFIG):
                        # Generate accuracy
                        acc = generate_accuracy(
                            model, task_id, difficulty, condition, task_info["gap_type"]
                        )

                        # Determine if correct (bernoulli trial)
                        correct = np.random.random() < acc

                        result = {
                            "instance_id": f"{task_id.lower()}_d{difficulty}_inst{inst_idx:03d}",
                            "task": task_id,
                            "difficulty": difficulty,
                            "condition": condition,
                            "model": model["name"],
                            "prompt_sent": f"Solve this {task_id} problem...",
                            "model_response": "...",
                            "extracted_answer": "1" if correct else "0",
                            "ground_truth": "1",
                            "correct": correct,
                            "latency_ms": np.random.uniform(500, 2000),
                            "tokens_used": {
                                "input": np.random.randint(50, 200),
                                "output": np.random.randint(20, 150)
                            },
                            "metadata": {}
                        }

                        results.append(result)

                # Save results for this (task, model, condition)
                output_file = RESULTS_DIR / f"{task_id.lower()}_{model['name']}_{condition}.json"
                with open(output_file, "w") as f:
                    json.dump(results, f, indent=2)

                total_results += len(results)

    print(f"Generated {total_results} synthetic evaluation results")
    print(f"Saved to: {RESULTS_DIR}")
    return total_results


def test_analysis_pipeline():
    """Test the analysis pipeline on synthetic data."""
    print("\n" + "="*70)
    print("Testing Analysis Pipeline")
    print("="*70)

    try:
        from analysis.primary import run_all_primary_analyses

        print("\nRunning primary analyses...")
        PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

        results = run_all_primary_analyses(RESULTS_DIR, PROCESSED_DIR)

        print("\n✓ Primary analyses completed successfully")

        # Check outputs
        expected_files = [
            "all_primary_analyses.json",
            "analysis_1_gap_validation.json",
            "analysis_2_cot_effectiveness.json",
            "analysis_3_budget_sufficiency.json",
            "analysis_4_scale_dependence.json",
            "analysis_5_tool_augmentation.json",
            "analysis_6_faithfulness.json",
        ]

        missing = []
        for fname in expected_files:
            if not (PROCESSED_DIR / fname).exists():
                missing.append(fname)

        if missing:
            print(f"\n✗ Warning: Missing output files: {missing}")
        else:
            print(f"\n✓ All expected output files created")

        return True

    except Exception as e:
        print(f"\n✗ Error during analysis: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_visualization_pipeline():
    """Test the visualization pipeline on synthetic data."""
    print("\n" + "="*70)
    print("Testing Visualization Pipeline")
    print("="*70)

    try:
        from visualizations.figures import generate_all_figures

        print("\nGenerating figures...")
        FIGURES_DIR.mkdir(parents=True, exist_ok=True)

        generate_all_figures(RESULTS_DIR, FIGURES_DIR)

        print("\n✓ Figure generation completed successfully")

        # Check outputs
        expected_figures = [
            "figure_1_degradation.pdf",
            "figure_1_degradation.png",
            "figure_2_cot_lift.pdf",
            "figure_2_cot_lift.png",
            "figure_3_scale.pdf",
            "figure_3_scale.png",
            "figure_4_tools.pdf",
            "figure_4_tools.png",
        ]

        missing = []
        for fname in expected_figures:
            if not (FIGURES_DIR / fname).exists():
                missing.append(fname)

        if missing:
            print(f"\n✗ Warning: Missing figure files: {missing}")
        else:
            print(f"\n✓ All expected figures created")

        return True

    except Exception as e:
        print(f"\n✗ Error during visualization: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("="*70)
    print("ReasonGap Analysis Pipeline Test")
    print("="*70)

    # Generate synthetic data
    n_results = generate_synthetic_data()

    # Test analysis pipeline
    analysis_ok = test_analysis_pipeline()

    # Test visualization pipeline
    viz_ok = test_visualization_pipeline()

    # Summary
    print("\n" + "="*70)
    print("Test Summary")
    print("="*70)
    print(f"Synthetic data generation: ✓ ({n_results} results)")
    print(f"Analysis pipeline: {'✓' if analysis_ok else '✗'}")
    print(f"Visualization pipeline: {'✓' if viz_ok else '✗'}")

    if analysis_ok and viz_ok:
        print("\n✓ All tests passed!")
        print(f"\nTest outputs saved to: {OUTPUT_DIR}")
        print("You can inspect the generated files to verify correctness.")
        return 0
    else:
        print("\n✗ Some tests failed. See errors above.")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
