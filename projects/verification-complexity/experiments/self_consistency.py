#!/usr/bin/env python3
"""Self-consistency (majority voting) evaluator for verification-complexity paper.

Tests whether majority voting over N samples improves accuracy, and whether
the improvement correlates with verification complexity class as predicted
by Theorems 1-2.

Wraps the reasoning-gaps evaluation infrastructure — reuses model clients,
answer extraction, and benchmark data.

Usage:
    # Dry run (estimate cost)
    python self_consistency.py --dry-run

    # Validation run (4 tasks, Haiku, short_cot, N=9)
    python self_consistency.py --tasks B2,B4,B7,B9 --models haiku --num-samples 9 \\
        --difficulties 2,3,4 --instances-per-difficulty 20

    # Full run (all tasks, N=17, short_cot)
    python self_consistency.py --models haiku --num-samples 17 --instances-per-difficulty 30

    # Direct condition comparison
    python self_consistency.py --condition direct --num-samples 5
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import random
import sys
import time
from collections import Counter
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any

# Add reasoning-gaps benchmarks to path
BENCHMARKS_DIR = Path(__file__).resolve().parents[2] / "reasoning-gaps" / "benchmarks"
sys.path.insert(0, str(BENCHMARKS_DIR))
sys.path.insert(0, str(BENCHMARKS_DIR / "clients"))

from evaluate import evaluate_instance, EvalResult  # noqa: E402
from answer_extraction import extract_answer  # noqa: E402
from io_utils import atomic_jsonl_append  # noqa: E402

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("vc.self_consistency")


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

DATA_DIR = BENCHMARKS_DIR / "data"
OUTPUT_DIR = Path(__file__).resolve().parent / "results"

TASK_FILES = {
    "B1": "b1_B1_masked_majority.json",
    "B2": "b2_B2_nested_boolean.json",
    "B3": "b3_B3_permutation_composition.json",
    "B4": "b4_B4_state_machine.json",
    "B5": "b5_B5_graph_reachability.json",
    "B6": "b6_B6_longest_increasing_subsequence.json",
    "B7": "b7_B7_3sat.json",
    "B8": "b8_B8_reversal_inference.json",
    "B9": "b9_B9_negation_sensitivity.json",
}

# Verification complexity classification
VC_CLASS = {
    "B1": "P",       # Type 1: Sensitivity — rho=0.22
    "B2": "P",       # Type 2: Depth — rho=0.22
    "B3": "P",       # Type 3: Serial — rho=0.31
    "B4": "P",       # Type 3: Serial — rho=0.22
    "B5": "P",       # Type 2/4: Depth/Algo — rho=0.11
    "B6": "P",       # Type 4: Algorithmic — rho=0.42 (highest, shared bottleneck)
    "B7": "P/coNP",  # Type 5: Intractability — rho=0.06 (lowest, stochastic)
    "B8": "Arch",    # Type 6: Architectural — rho=0.15 (ceiling effect)
    "B9": "Arch",    # Type 6: Architectural — rho=0.07
}

MODEL_CONFIGS = {
    "haiku": ("anthropic", "claude-haiku-4-5-20251001"),
    "gpt4o-mini": ("openai", "gpt-4o-mini"),
    "llama-8b": ("openrouter", "meta-llama/llama-3.1-8b-instruct"),
}


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class EnsembleResult:
    """Result of majority voting over N samples for one instance."""
    instance_id: str
    task: str
    difficulty: int
    model: str
    num_samples: int
    temperature: float
    condition: str
    # Individual sample results
    answers: list[str]
    correct_flags: list[bool]
    latencies_ms: list[float]
    # Majority vote (computed from valid extractions only)
    majority_answer: str
    majority_correct: bool
    agreement: float  # fraction of valid samples matching majority
    # Ground truth
    ground_truth: str
    # Metadata
    vc_class: str
    single_correct: bool  # was the first sample correct? (N=1 baseline)
    extraction_failures: int  # number of samples where extraction returned ""


# ---------------------------------------------------------------------------
# Client factory
# ---------------------------------------------------------------------------

def create_client(provider: str, model_name: str, temperature: float = 0.7):
    """Create a model client with the specified temperature.

    Uses the native client temperature parameter, preserving retry logic,
    rate limiting, and cost tracking from the base client classes.
    """
    if provider == "anthropic":
        from anthropic_client import AnthropicClient
        client = AnthropicClient(model_name)
    elif provider == "openai":
        from openai_client import OpenAIClient
        client = OpenAIClient(model_name)
    elif provider == "openrouter":
        from openrouter_client import OpenRouterClient
        client = OpenRouterClient(model_name)
    else:
        raise ValueError(f"Unknown provider: {provider}")

    # Wrap query to inject temperature — keeps retry, rate limiting, cost tracking
    _original_query = client.query

    def query_with_temp(prompt, system_prompt="", max_tokens=512, **kwargs):
        return _original_query(prompt, system_prompt, max_tokens, temperature=temperature, **kwargs)

    client.query = query_with_temp
    return client


# ---------------------------------------------------------------------------
# Core evaluation
# ---------------------------------------------------------------------------

def evaluate_ensemble(
    instance: dict,
    client,
    num_samples: int,
    temperature: float,
    condition: str = "short_cot",
) -> EnsembleResult:
    """Evaluate one instance with N independent samples and majority vote."""
    answers = []
    correct_flags = []
    latencies = []
    ground_truth = str(instance["answer"])

    for i in range(num_samples):
        result = evaluate_instance(instance, client, condition=condition)
        answers.append(result.extracted_answer)
        correct_flags.append(result.correct)
        latencies.append(result.latency_ms)

    # Filter out extraction failures before majority vote
    valid_answers = [a for a in answers if a != ""]
    extraction_failures = len(answers) - len(valid_answers)

    if valid_answers:
        vote_counts = Counter(valid_answers)
        majority_answer = vote_counts.most_common(1)[0][0]
        majority_correct = majority_answer.strip().lower() == ground_truth.strip().lower()
        agreement = vote_counts[majority_answer] / len(valid_answers)
    else:
        majority_answer = ""
        majority_correct = False
        agreement = 0.0

    task_key = instance["task"].split("_")[0].upper()

    return EnsembleResult(
        instance_id=instance["id"],
        task=instance["task"],
        difficulty=instance["difficulty"],
        model=client.model_name,
        num_samples=num_samples,
        temperature=temperature,
        condition=condition,
        answers=answers,
        correct_flags=correct_flags,
        latencies_ms=latencies,
        majority_answer=majority_answer,
        majority_correct=majority_correct,
        agreement=agreement,
        ground_truth=ground_truth,
        vc_class=VC_CLASS.get(task_key, "?"),
        single_correct=correct_flags[0],
        extraction_failures=extraction_failures,
    )


def load_instances(task_key: str, difficulties: list[int], per_difficulty: int) -> list[dict]:
    """Load benchmark instances for a task, sampling per difficulty level."""
    filename = TASK_FILES.get(task_key)
    if not filename:
        raise ValueError(f"Unknown task: {task_key}")

    data = json.loads((DATA_DIR / filename).read_text())
    instances = data["instances"]

    selected = []
    for d in difficulties:
        d_instances = [i for i in instances if i["difficulty"] == d]
        selected.extend(d_instances[:per_difficulty])

    return selected


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Self-consistency evaluation")
    parser.add_argument("--tasks", default="B1,B2,B3,B4,B5,B6,B7,B8,B9",
                        help="Comma-separated task keys")
    parser.add_argument("--models", default="haiku,gpt4o-mini,llama-8b",
                        help="Comma-separated model keys")
    parser.add_argument("--num-samples", type=int, default=5,
                        help="Number of samples per instance for majority voting")
    parser.add_argument("--temperature", type=float, default=1.0,
                        help="Sampling temperature (1.0 recommended for diversity; 0.7 showed 96-99%% agreement)")
    parser.add_argument("--difficulties", default="1,2,3,4,5",
                        help="Comma-separated difficulty levels")
    parser.add_argument("--instances-per-difficulty", type=int, default=50,
                        help="Max instances per difficulty level per task")
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    parser.add_argument("--dry-run", action="store_true",
                        help="Estimate cost without running")
    parser.add_argument("--condition", default="short_cot",
                        choices=["direct", "short_cot", "budget_cot"],
                        help="Evaluation condition (default: short_cot for self-consistency)")
    parser.add_argument("--resume", action="store_true",
                        help="Skip instances already in output file")
    parser.add_argument("--seed", type=int, default=42,
                        help="Random seed for reproducibility (default: 42)")

    args = parser.parse_args()

    # Set random seed for reproducibility
    random.seed(args.seed)

    tasks = args.tasks.split(",")
    models = args.models.split(",")
    difficulties = [int(d) for d in args.difficulties.split(",")]
    args.output_dir.mkdir(parents=True, exist_ok=True)

    # Cost estimation
    total_instances = 0
    for task in tasks:
        instances = load_instances(task, difficulties, args.instances_per_difficulty)
        total_instances += len(instances)

    total_api_calls = total_instances * len(models) * args.num_samples

    # Cost estimate per API call (short_cot: ~500 input + ~200 output tokens)
    cost_per_call = {
        "haiku": 0.002,
        "gpt4o-mini": 0.002,
        "llama-8b": 0.0005,
    }
    if args.condition == "direct":
        # Direct condition uses ~10 output tokens
        cost_per_call = {"haiku": 0.0003, "gpt4o-mini": 0.0004, "llama-8b": 0.0001}
    estimated_cost = sum(
        total_instances * args.num_samples * cost_per_call.get(m, 0.0003)
        for m in models
    )

    logger.info(f"Tasks: {tasks}")
    logger.info(f"Models: {models}")
    logger.info(f"Condition: {args.condition}")
    logger.info(f"Samples per instance: {args.num_samples}")
    logger.info(f"Temperature: {args.temperature}")
    logger.info(f"Instances per task: {total_instances // len(tasks)}")
    logger.info(f"Total instances: {total_instances}")
    logger.info(f"Total API calls: {total_api_calls:,}")
    logger.info(f"Estimated cost: ${estimated_cost:.2f}")

    if args.dry_run:
        logger.info("DRY RUN — exiting without running experiments")
        return

    # Run experiments
    for model_key in models:
        provider, model_name = MODEL_CONFIGS[model_key]
        logger.info(f"\n{'='*60}")
        logger.info(f"Model: {model_name}")
        logger.info(f"{'='*60}")

        client = create_client(provider, model_name, args.temperature)

        for task in tasks:
            instances = load_instances(task, difficulties, args.instances_per_difficulty)
            output_file = args.output_dir / f"sc_{model_key}_{task}_{args.condition}_n{args.num_samples}.jsonl"

            # Resume support
            completed_ids = set()
            if args.resume and output_file.exists():
                with open(output_file) as f:
                    for line_num, line in enumerate(f, 1):
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            r = json.loads(line)
                            completed_ids.add(r["instance_id"])
                        except json.JSONDecodeError:
                            logger.warning(f"  Corrupt line {line_num} in {output_file}, skipping")
                logger.info(f"  Resuming: {len(completed_ids)} already done")

            remaining = [i for i in instances if i["id"] not in completed_ids]
            if not remaining:
                logger.info(f"  {task}: all done, skipping")
                continue

            logger.info(f"  {task}: {len(remaining)} instances × {args.num_samples} samples")

            for idx, instance in enumerate(remaining):
                try:
                    result = evaluate_ensemble(
                        instance, client, args.num_samples, args.temperature,
                        condition=args.condition,
                    )
                    atomic_jsonl_append(output_file, asdict(result))

                    status = "✓" if result.majority_correct else "✗"
                    if (idx + 1) % 10 == 0 or idx == 0:
                        ext_warn = f" ext_fail={result.extraction_failures}" if result.extraction_failures else ""
                        logger.info(
                            f"    [{idx+1}/{len(remaining)}] {status} "
                            f"agree={result.agreement:.0%} "
                            f"single={'✓' if result.single_correct else '✗'}"
                            f"{ext_warn}"
                        )
                except Exception as e:
                    logger.error(f"    [{idx+1}] {instance['id']}: {e}")
                    continue

            logger.info(f"  {task}: done → {output_file}")

    logger.info("\nAll experiments complete.")


if __name__ == "__main__":
    main()
