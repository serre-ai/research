#!/usr/bin/env python3
"""CoT depth evaluation — measure accuracy as a function of reasoning depth.

Runs tasks at varying CoT depths using structured step prompting.
Results stored as JSONL for analysis.

Usage:
    python3 experiments/evaluate.py --task parity --difficulty 3 --depth 8 --model haiku --n 30
    python3 experiments/evaluate.py --task all --depth all --model all --dry-run
    python3 experiments/evaluate.py --sweep              # full experiment sweep
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path

# Task modules
from tasks import majority, parity, composition, arithmetic

TASKS = {
    "majority": majority,
    "parity": parity,
    "composition": composition,
    "arithmetic": arithmetic,
}

DEPTH_LEVELS = [0, 1, 2, 4, 6, 8, 12, 16, 20, 25, 30]

MODELS = {
    "haiku": "claude-3-5-haiku-20241022",
    "gpt4omini": "gpt-4o-mini",
    "sonnet": "claude-sonnet-4-20250514",
}

RESULTS_DIR = Path(__file__).parent / "results"


# ---------------------------------------------------------------------------
# Prompt construction
# ---------------------------------------------------------------------------

def build_prompt(task_text: str, depth: int) -> str:
    """Build a prompt with the specified CoT depth constraint.

    depth=0: Direct answer, no reasoning.
    depth>0: Structured step prompting with exactly `depth` steps.
    """
    if depth == 0:
        return (
            f"{task_text}\n\n"
            "Answer immediately with no explanation.\n"
            "ANSWER: "
        )

    return (
        f"{task_text}\n\n"
        f"Solve this in exactly {depth} numbered steps. "
        f"Show your work as Step 1, Step 2, etc. "
        f"After Step {depth}, give your final answer on a new line.\n"
        "ANSWER: <your answer>\n\n"
        "Step 1:"
    )


# ---------------------------------------------------------------------------
# Response parsing
# ---------------------------------------------------------------------------

def extract_answer(response: str) -> str | None:
    """Extract the answer from a model response."""
    # Look for ANSWER: pattern
    match = re.search(r"ANSWER:\s*(.+?)(?:\n|$)", response, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    # Fallback: last line
    lines = response.strip().split("\n")
    if lines:
        return lines[-1].strip()
    return None


def count_steps(response: str) -> int:
    """Count the number of 'Step N:' markers in the response."""
    return len(re.findall(r"Step\s+\d+\s*:", response, re.IGNORECASE))


# ---------------------------------------------------------------------------
# Model client (stub — to be replaced with real API calls)
# ---------------------------------------------------------------------------

def call_model(model_id: str, prompt: str) -> dict:
    """Call a model API and return the response.

    Returns dict with: response_text, latency_ms, input_tokens, output_tokens.

    TODO: Implement real API calls via anthropic/openai SDKs.
    """
    raise NotImplementedError(
        f"Model client not yet implemented for {model_id}. "
        "Use --dry-run to preview prompts."
    )


# ---------------------------------------------------------------------------
# Evaluation loop
# ---------------------------------------------------------------------------

def evaluate_single(
    task_name: str,
    difficulty: int,
    depth: int,
    model_key: str,
    n_instances: int = 30,
    seed: int = 42,
    dry_run: bool = False,
) -> list[dict]:
    """Evaluate a single (task, difficulty, depth, model) combination.

    Returns list of result dicts.
    """
    task_module = TASKS[task_name]
    instances = task_module.generate(n_instances, difficulty, seed)

    results = []
    for inst in instances:
        prompt = build_prompt(inst["prompt_text"], depth)

        if dry_run:
            print(f"\n{'='*60}")
            print(f"Task: {task_name} | Difficulty: {difficulty} | Depth: {depth}")
            print(f"Instance: {inst['instance_id']}")
            print(f"c(n) = {inst['cot_complexity']}")
            print(f"Ground truth: {inst['ground_truth']}")
            print(f"\nPROMPT:\n{prompt}")
            results.append({
                "instance_id": inst["instance_id"],
                "task": task_name,
                "difficulty": difficulty,
                "depth_requested": depth,
                "cot_complexity": inst["cot_complexity"],
                "ground_truth": inst["ground_truth"],
                "prompt": prompt,
                "dry_run": True,
            })
            continue

        model_id = MODELS[model_key]
        t0 = time.time()
        resp = call_model(model_id, prompt)
        latency = (time.time() - t0) * 1000

        response_text = resp["response_text"]
        extracted = extract_answer(response_text)
        actual_steps = count_steps(response_text)
        correct = (extracted == inst["ground_truth"]) if extracted else False
        compliant = abs(actual_steps - depth) <= 1 if depth > 0 else True

        results.append({
            "instance_id": inst["instance_id"],
            "task": task_name,
            "difficulty": difficulty,
            "depth_requested": depth,
            "depth_actual": actual_steps,
            "depth_compliant": compliant,
            "cot_complexity": inst["cot_complexity"],
            "model": model_key,
            "ground_truth": inst["ground_truth"],
            "extracted_answer": extracted,
            "correct": correct,
            "latency_ms": round(latency, 1),
            "input_tokens": resp.get("input_tokens", 0),
            "output_tokens": resp.get("output_tokens", 0),
        })

    return results


def save_results(results: list[dict], tag: str) -> Path:
    """Save results to a JSONL file."""
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    path = RESULTS_DIR / f"{tag}.jsonl"
    with open(path, "a") as f:
        for r in results:
            f.write(json.dumps(r) + "\n")
    return path


# ---------------------------------------------------------------------------
# Sweep configuration
# ---------------------------------------------------------------------------

SWEEP_CONFIG = {
    "majority": {
        "difficulties": [1, 2, 3],
        "depths": [0, 1, 2, 4, 8, 16],
    },
    "composition": {
        "difficulties": [1, 2, 3, 4, 5, 6, 7, 8],
        "depths": [0, 1, 2, 4, 6, 8, 12, 16, 20, 25, 30],
    },
    "parity": {
        "difficulties": [1, 2, 3, 4, 5, 6, 7],
        "depths": [0, 1, 2, 4, 6, 8, 12, 16, 20, 25, 30],
    },
    "arithmetic": {
        "difficulties": [1, 2, 3, 4, 5, 6, 7],
        "depths": [0, 1, 2, 4, 6, 8, 12, 16, 20, 25, 30],
    },
}


def run_sweep(model_key: str, n_instances: int = 30, dry_run: bool = False):
    """Run the full experiment sweep for one model."""
    total_calls = 0
    for task_name, config in SWEEP_CONFIG.items():
        for diff in config["difficulties"]:
            for depth in config["depths"]:
                total_calls += n_instances

    print(f"Sweep: {total_calls} API calls for model={model_key}")
    if dry_run:
        print("(dry run — showing first instance of each combination)\n")

    for task_name, config in SWEEP_CONFIG.items():
        for diff in config["difficulties"]:
            for depth in config["depths"]:
                n = 1 if dry_run else n_instances
                results = evaluate_single(
                    task_name, diff, depth, model_key, n, dry_run=dry_run
                )
                if not dry_run:
                    tag = f"{model_key}_{task_name}_d{diff}_k{depth}"
                    save_results(results, tag)
                    acc = sum(r["correct"] for r in results) / len(results)
                    comp = sum(r.get("depth_compliant", True) for r in results) / len(results)
                    print(
                        f"  {task_name} diff={diff} depth={depth}: "
                        f"acc={acc:.1%} compliance={comp:.1%}"
                    )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="CoT depth evaluation for optimal-cot-depth project."
    )
    parser.add_argument("--task", type=str, default="parity",
                        choices=list(TASKS) + ["all"])
    parser.add_argument("--difficulty", type=int, default=3)
    parser.add_argument("--depth", type=int, default=8)
    parser.add_argument("--model", type=str, default="haiku",
                        choices=list(MODELS) + ["all"])
    parser.add_argument("--n", type=int, default=30,
                        help="Instances per combination")
    parser.add_argument("--sweep", action="store_true",
                        help="Run full experiment sweep")
    parser.add_argument("--dry-run", action="store_true",
                        help="Preview prompts without calling APIs")

    args = parser.parse_args()

    if args.sweep:
        models = list(MODELS) if args.model == "all" else [args.model]
        for m in models:
            run_sweep(m, args.n, args.dry_run)
        return

    # Single evaluation
    results = evaluate_single(
        args.task, args.difficulty, args.depth, args.model,
        args.n, dry_run=args.dry_run,
    )
    if args.dry_run:
        # Only show first instance in dry run
        return

    tag = f"{args.model}_{args.task}_d{args.difficulty}_k{args.depth}"
    path = save_results(results, tag)
    acc = sum(r["correct"] for r in results) / len(results)
    print(f"Results: {path} ({len(results)} instances, accuracy={acc:.1%})")


if __name__ == "__main__":
    main()
