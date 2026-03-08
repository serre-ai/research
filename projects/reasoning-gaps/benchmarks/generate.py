#!/usr/bin/env python3
"""ReasonGap Benchmark Suite -- Task Generator.

Generates benchmark instances for the ReasonGap diagnostic suite.

Usage:
    python generate.py --task B1 --n-instances 100 --difficulty 5
    python generate.py --all --n-instances 100
    python generate.py --all --n-instances 100 --difficulty 3

Outputs JSON files to benchmarks/data/.
"""

import argparse
import json
import os
import sys
from pathlib import Path

# Add parent directory to path so we can import tasks
sys.path.insert(0, str(Path(__file__).resolve().parent))

from tasks import TASK_REGISTRY


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate ReasonGap benchmark instances.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Available tasks:\n"
            "  B1  Masked Majority (Sensitivity Gap)\n"
            "  B2  Nested Boolean Evaluation (Depth Gap)\n"
            "  B3  Iterated Permutation Composition (Serial Gap)\n"
            "  B4  State Tracking Machine (Serial Gap variant)\n"
            "  B5  Graph Reachability (Depth/Algorithmic Gap)\n"
            "  B6  Longest Increasing Subsequence (Algorithmic Gap)\n"
            "  B7  3-SAT at Phase Transition (Intractability Gap)\n"
            "  B8  String Reversal Inference (Architectural Gap)\n"
            "  B9  Negation Sensitivity (Architectural Gap variant)\n"
        ),
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--task",
        type=str,
        choices=list(TASK_REGISTRY.keys()),
        help="Generate a specific task (e.g., B1, B2, ...).",
    )
    group.add_argument(
        "--all",
        action="store_true",
        help="Generate all benchmark tasks.",
    )

    parser.add_argument(
        "--n-instances",
        type=int,
        default=100,
        help="Number of instances per difficulty level (default: 100).",
    )
    parser.add_argument(
        "--difficulty",
        type=int,
        choices=[1, 2, 3, 4, 5],
        default=None,
        help="Specific difficulty level (default: generate all 1-5).",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducibility (default: 42).",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=None,
        help="Output directory (default: benchmarks/data/).",
    )

    args = parser.parse_args()

    # Determine output directory
    if args.output_dir:
        output_dir = Path(args.output_dir)
    else:
        output_dir = Path(__file__).resolve().parent / "data"

    output_dir.mkdir(parents=True, exist_ok=True)

    # Determine which tasks to generate
    if args.all:
        task_keys = list(TASK_REGISTRY.keys())
    else:
        task_keys = [args.task]

    # Determine difficulty levels
    if args.difficulty is not None:
        difficulties = [args.difficulty]
    else:
        difficulties = [1, 2, 3, 4, 5]

    total_instances = 0

    for task_key in task_keys:
        module = TASK_REGISTRY[task_key]
        task_name = module.TASK_NAME
        print(f"\n{'='*60}")
        print(f"Generating {task_key}: {task_name}")
        print(f"{'='*60}")

        all_instances: list[dict] = []

        for diff in difficulties:
            # Use a different seed per difficulty to get distinct instances
            diff_seed = args.seed + diff * 1000
            print(f"  Difficulty {diff} (seed={diff_seed})...", end=" ", flush=True)

            instances = module.generate(
                n_instances=args.n_instances,
                difficulty=diff,
                seed=diff_seed,
            )

            all_instances.extend(instances)
            print(f"{len(instances)} instances generated.")

            # Print one example
            if instances:
                ex = instances[0]
                print(f"    Example: answer={ex['answer']}")
                # Truncate prompt for display
                prompt_preview = ex["prompt"][:120].replace("\n", " ")
                print(f"    Prompt: {prompt_preview}...")

        # Write to file
        output_file = output_dir / f"{task_key.lower()}_{task_name}.json"
        with open(output_file, "w") as f:
            json.dump(
                {
                    "task": task_key,
                    "task_name": task_name,
                    "n_instances_per_difficulty": args.n_instances,
                    "difficulties": difficulties,
                    "seed": args.seed,
                    "total_instances": len(all_instances),
                    "instances": all_instances,
                },
                f,
                indent=2,
            )

        total_instances += len(all_instances)
        print(f"  -> Saved {len(all_instances)} instances to {output_file}")

    print(f"\n{'='*60}")
    print(f"Generation complete. Total: {total_instances} instances.")
    print(f"Output directory: {output_dir}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
