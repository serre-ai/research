#!/usr/bin/env python3
"""Cross-model verification experiment for verification-complexity paper.

Tests Theorem 1 (Verification Advantage): can a verifier model judge the
correctness of a generator model's output, and does verification accuracy
correlate with the task's verification complexity class?

The verifier sees only the problem and the generator's response — no ground
truth. It must reason about the problem to judge correctness. For P-class
verification tasks, this computation is tractable. For coNP tasks, it's not.

Uses generator outputs from the reasoning-gaps evaluation (short_cot condition).

Usage:
    # Dry run (estimate cost)
    python cross_model_verification.py --dry-run

    # Run with specific generators/verifiers
    python cross_model_verification.py --generators haiku --verifiers haiku,sonnet

    # Full run
    python cross_model_verification.py --instances-per-difficulty 10
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import re
import sys
import time
from dataclasses import dataclass, asdict
from pathlib import Path

# Add reasoning-gaps benchmarks to path for client reuse
BENCHMARKS_DIR = Path(__file__).resolve().parents[2] / "reasoning-gaps" / "benchmarks"
sys.path.insert(0, str(BENCHMARKS_DIR))
sys.path.insert(0, str(BENCHMARKS_DIR / "clients"))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("vc.verification")

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

RESULTS_DIR = BENCHMARKS_DIR / "results"
OUTPUT_DIR = Path(__file__).resolve().parent / "results"

GENERATOR_MODELS = {
    "haiku": "claude-haiku-4-5-20251001",
    "gpt4o": "gpt-4o",
    "llama70b": "meta-llama/llama-3.1-70b-instruct",
}

VERIFIER_MODELS = {
    "haiku": ("anthropic", "claude-haiku-4-5-20251001"),
    "sonnet": ("anthropic", "claude-sonnet-4-20250514"),
    "gpt4o-mini": ("openai", "gpt-4o-mini"),
}

TASKS = ["B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8", "B9"]

TASK_FILES = {
    "B1": "B1_masked_majority",
    "B2": "B2_nested_boolean",
    "B3": "B3_permutation_composition",
    "B4": "B4_state_machine",
    "B5": "B5_graph_reachability",
    "B6": "B6_longest_increasing_subsequence",
    "B7": "B7_3sat",
    "B8": "B8_reversal_inference",
    "B9": "B9_negation_sensitivity",
}

VC_CLASS = {
    "B1": "P",
    "B2": "P",
    "B3": "P",
    "B4": "P",
    "B5": "P",
    "B6": "P",
    "B7": "P/coNP",
    "B8": "Arch",
    "B9": "Arch",
}


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class VerificationResult:
    """Result of one cross-model verification judgment."""
    instance_id: str
    task: str
    difficulty: int
    generator_model: str
    generator_answer: str
    generator_correct: bool
    verifier_model: str
    verifier_response: str
    verifier_judgment: str  # "Correct" or "Incorrect" or "" (extraction failure)
    verification_accurate: bool  # did verifier's judgment match ground truth?
    ground_truth: str
    vc_class: str
    latency_ms: float


# ---------------------------------------------------------------------------
# Verification prompt
# ---------------------------------------------------------------------------

VERIFICATION_PROMPT = """You are evaluating whether a student's answer to a reasoning problem is correct.

## Problem
{prompt}

## Student's Response
{response}

Is the student's final answer correct? Think step by step about the problem, then on the last line write just "Correct" or "Incorrect"."""


def extract_verification_judgment(response: str) -> str:
    """Extract 'Correct' or 'Incorrect' from verifier's response."""
    if not response or not response.strip():
        return ""

    text = response.strip()

    # Check last line first
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    if lines:
        last = lines[-1].lower().strip(".*!,;:")
        if "incorrect" in last:
            return "Incorrect"
        if "correct" in last:
            return "Correct"

    # Search full text for last occurrence
    correct_pos = -1
    incorrect_pos = -1
    for m in re.finditer(r"\bcorrect\b", text.lower()):
        # Make sure it's not "incorrect"
        start = m.start()
        if start > 0 and text[start-2:start].lower() == "in":
            incorrect_pos = start
        else:
            correct_pos = start
    for m in re.finditer(r"\bincorrect\b", text.lower()):
        incorrect_pos = m.start()

    if incorrect_pos > correct_pos:
        return "Incorrect"
    if correct_pos > incorrect_pos and correct_pos >= 0:
        return "Correct"

    return ""


# ---------------------------------------------------------------------------
# Client factory
# ---------------------------------------------------------------------------

def create_verifier_client(provider: str, model_name: str):
    """Create a client for the verifier model."""
    if provider == "anthropic":
        from anthropic_client import AnthropicClient
        return AnthropicClient(model_name)
    elif provider == "openai":
        from openai_client import OpenAIClient
        return OpenAIClient(model_name)
    else:
        raise ValueError(f"Unknown provider: {provider}")


# ---------------------------------------------------------------------------
# Load generator results
# ---------------------------------------------------------------------------

def load_generator_results(
    generator_model: str,
    tasks: list[str],
    difficulties: list[int],
    per_difficulty: int,
    condition: str = "short_cot",
) -> dict[str, list[dict]]:
    """Load generator results from reasoning-gaps evaluation files."""
    results_by_task: dict[str, list[dict]] = {}

    for task_key in tasks:
        task_full = TASK_FILES[task_key]
        # Find the result file for this generator + task + condition
        pattern = f"*{generator_model}*{task_full}*{condition}*"
        matches = list(RESULTS_DIR.glob(pattern + ".json"))

        if not matches:
            # Try without full task name
            pattern2 = f"*{generator_model}*{task_key}*{condition}*"
            matches = list(RESULTS_DIR.glob(pattern2 + ".json"))

        if not matches:
            logger.warning(f"  No results found for {generator_model} / {task_key} / {condition}")
            continue

        data = json.loads(matches[0].read_text())
        all_results = data.get("results", data) if isinstance(data, dict) else data

        # Filter by difficulty and sample
        selected = []
        for d in difficulties:
            d_results = [r for r in all_results if r.get("difficulty") == d]
            selected.extend(d_results[:per_difficulty])

        results_by_task[task_key] = selected
        logger.info(f"  Loaded {len(selected)} instances for {task_key} ({generator_model})")

    return results_by_task


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Cross-model verification experiment")
    parser.add_argument("--generators", default="haiku,gpt4o,llama70b",
                        help="Comma-separated generator model keys")
    parser.add_argument("--verifiers", default="haiku,sonnet,gpt4o-mini",
                        help="Comma-separated verifier model keys")
    parser.add_argument("--tasks", default=",".join(TASKS),
                        help="Comma-separated task keys")
    parser.add_argument("--difficulties", default="1,2,3,4,5",
                        help="Comma-separated difficulty levels")
    parser.add_argument("--instances-per-difficulty", type=int, default=10,
                        help="Instances per difficulty level per task")
    parser.add_argument("--condition", default="short_cot",
                        help="Generator condition to use")
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--resume", action="store_true")

    args = parser.parse_args()

    generators = args.generators.split(",")
    verifiers = args.verifiers.split(",")
    tasks = args.tasks.split(",")
    difficulties = [int(d) for d in args.difficulties.split(",")]
    args.output_dir.mkdir(parents=True, exist_ok=True)

    # Count instances
    total_instances = len(tasks) * len(difficulties) * args.instances_per_difficulty
    total_calls = total_instances * len(generators) * len(verifiers)

    cost_per_call = {
        "haiku": 0.002,
        "sonnet": 0.01,
        "gpt4o-mini": 0.002,
    }
    estimated_cost = sum(
        total_instances * len(generators) * cost_per_call.get(v, 0.005)
        for v in verifiers
    )

    logger.info(f"Tasks: {tasks}")
    logger.info(f"Generators: {generators}")
    logger.info(f"Verifiers: {verifiers}")
    logger.info(f"Instances per task: {len(difficulties) * args.instances_per_difficulty}")
    logger.info(f"Total instances: {total_instances}")
    logger.info(f"Total verification calls: {total_calls:,}")
    logger.info(f"Estimated cost: ${estimated_cost:.2f}")

    if args.dry_run:
        logger.info("DRY RUN — exiting")
        return

    # Run verification for each (generator, verifier) pair
    for gen_key in generators:
        gen_model = GENERATOR_MODELS[gen_key]
        logger.info(f"\n{'='*60}")
        logger.info(f"Generator: {gen_model}")
        logger.info(f"{'='*60}")

        # Load generator results
        gen_results = load_generator_results(
            gen_model, tasks, difficulties, args.instances_per_difficulty, args.condition
        )

        for ver_key in verifiers:
            ver_provider, ver_model = VERIFIER_MODELS[ver_key]
            logger.info(f"\n  Verifier: {ver_model}")

            client = create_verifier_client(ver_provider, ver_model)

            output_file = args.output_dir / f"verify_{gen_key}_by_{ver_key}.jsonl"

            # Resume support
            completed_ids = set()
            if args.resume and output_file.exists():
                with open(output_file) as f:
                    for line in f:
                        r = json.loads(line)
                        completed_ids.add(r["instance_id"])
                logger.info(f"    Resuming: {len(completed_ids)} already done")

            with open(output_file, "a") as f:
                for task_key in tasks:
                    instances = gen_results.get(task_key, [])
                    remaining = [r for r in instances if r["instance_id"] not in completed_ids]

                    if not remaining:
                        continue

                    logger.info(f"    {task_key}: {len(remaining)} instances")

                    for idx, inst in enumerate(remaining):
                        try:
                            # Build verification prompt
                            prompt = VERIFICATION_PROMPT.format(
                                prompt=inst["prompt_sent"],
                                response=inst["model_response"],
                            )

                            # Query verifier
                            start = time.perf_counter()
                            response, latency = client.query(
                                prompt,
                                system_prompt="You are a careful reasoning evaluator.",
                                max_tokens=1024,
                            )
                            actual_latency = (time.perf_counter() - start) * 1000

                            # Extract judgment
                            judgment = extract_verification_judgment(response)

                            # Determine if verification is accurate
                            gen_correct = inst["correct"]
                            if judgment == "Correct":
                                verification_accurate = gen_correct
                            elif judgment == "Incorrect":
                                verification_accurate = not gen_correct
                            else:
                                verification_accurate = False  # extraction failure

                            result = VerificationResult(
                                instance_id=inst["instance_id"],
                                task=inst["task"],
                                difficulty=inst["difficulty"],
                                generator_model=gen_model,
                                generator_answer=inst["extracted_answer"],
                                generator_correct=gen_correct,
                                verifier_model=ver_model,
                                verifier_response=response[:500],  # truncate for storage
                                verifier_judgment=judgment,
                                verification_accurate=verification_accurate,
                                ground_truth=inst["ground_truth"],
                                vc_class=VC_CLASS.get(task_key, "?"),
                                latency_ms=actual_latency,
                            )

                            f.write(json.dumps(asdict(result)) + "\n")
                            f.flush()

                            if (idx + 1) % 10 == 0 or idx == 0:
                                status = "accurate" if verification_accurate else "wrong"
                                logger.info(
                                    f"      [{idx+1}/{len(remaining)}] {status} "
                                    f"gen={inst['extracted_answer']} "
                                    f"verdict={judgment}"
                                )

                        except Exception as e:
                            logger.error(f"      [{idx+1}] {inst['instance_id']}: {e}")
                            continue

            logger.info(f"    Done → {output_file}")

    logger.info("\nAll verification complete.")


if __name__ == "__main__":
    main()
