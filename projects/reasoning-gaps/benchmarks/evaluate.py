#!/usr/bin/env python3
"""ReasonGap Benchmark Suite -- Evaluation Skeleton.

Runs inference on benchmark instances and scores results.

Usage:
    python evaluate.py --benchmark data/b1_B1_masked_majority.json \
                       --model openai:gpt-4o \
                       --condition direct \
                       --output results/b1_gpt4o_direct.json

Conditions:
    direct      -- No chain-of-thought; force immediate answer.
    short_cot   -- "Think step by step" prompt prefix (unconstrained).
    budget_cot  -- Fixed CoT token budget (log n, n, n^2).
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

CONDITION_PROMPTS: dict[str, str] = {
    "direct": (
        "Answer immediately with just the final answer. "
        "Do not explain your reasoning."
    ),
    "short_cot": (
        "Think step by step, then provide your final answer on the last line."
    ),
    "budget_cot": (
        "Think step by step (using at most {budget} words), "
        "then provide your final answer on the last line."
    ),
}

BUDGET_COT_MULTIPLIERS: dict[str, int] = {
    "log": 1,    # log(n) tokens
    "linear": 2, # n tokens
    "quadratic": 3, # n^2 tokens
}


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class EvalResult:
    """Result for a single evaluation instance."""
    instance_id: str
    task: str
    difficulty: int
    condition: str
    model: str
    prompt_sent: str
    model_response: str
    extracted_answer: str
    ground_truth: str
    correct: bool
    latency_ms: float
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class EvalSummary:
    """Aggregated evaluation summary."""
    task: str
    model: str
    condition: str
    total_instances: int
    correct: int
    accuracy: float
    accuracy_by_difficulty: dict[int, float]
    mean_latency_ms: float


# ---------------------------------------------------------------------------
# Model interface (abstract -- to be implemented per provider)
# ---------------------------------------------------------------------------

class ModelClient:
    """Abstract base for model API clients.

    Subclass this to implement specific API providers (OpenAI, Anthropic,
    local models via vLLM, etc.).
    """

    def __init__(self, model_name: str, **kwargs: Any) -> None:
        self.model_name = model_name

    def query(
        self,
        prompt: str,
        system_prompt: str = "",
        max_tokens: int = 512,
    ) -> tuple[str, float]:
        """Send a prompt to the model and return (response_text, latency_ms).

        Must be implemented by subclasses.
        """
        raise NotImplementedError(
            f"ModelClient.query() not implemented. "
            f"Implement a subclass for your model provider. "
            f"Model: {self.model_name}"
        )


class DummyClient(ModelClient):
    """Placeholder client that returns empty responses.

    Useful for testing the evaluation pipeline structure.
    """

    def query(
        self,
        prompt: str,
        system_prompt: str = "",
        max_tokens: int = 512,
    ) -> tuple[str, float]:
        return ("[DUMMY RESPONSE -- implement ModelClient]", 0.0)


# ---------------------------------------------------------------------------
# Answer extraction
# ---------------------------------------------------------------------------

def extract_answer(response: str, task: str) -> str:
    """Extract the final answer from a model response.

    For CoT responses, takes the last line. For direct responses,
    takes the whole response. Strips whitespace and common prefixes.
    """
    if not response.strip():
        return ""

    # Take the last non-empty line
    lines = [line.strip() for line in response.strip().split("\n") if line.strip()]
    if not lines:
        return ""

    last_line = lines[-1]

    # Remove common prefixes
    for prefix in [
        "Answer:", "The answer is", "Final answer:", "Result:",
        "answer:", "the answer is", "final answer:", "result:",
    ]:
        if last_line.lower().startswith(prefix.lower()):
            last_line = last_line[len(prefix):].strip()

    # Remove trailing punctuation
    last_line = last_line.rstrip(".")

    return last_line.strip()


# ---------------------------------------------------------------------------
# Evaluation logic
# ---------------------------------------------------------------------------

def evaluate_instance(
    instance: dict[str, Any],
    client: ModelClient,
    condition: str,
    budget: int | None = None,
) -> EvalResult:
    """Evaluate a single benchmark instance.

    Args:
        instance: Benchmark instance dict (from generated JSON).
        client: Model client to use for inference.
        condition: One of 'direct', 'short_cot', 'budget_cot'.
        budget: Token budget for budget_cot condition.

    Returns:
        EvalResult with scoring.
    """
    base_prompt = instance["prompt"]

    # Build condition-specific prompt
    if condition == "direct":
        system_prompt = CONDITION_PROMPTS["direct"]
        full_prompt = base_prompt
        max_tokens = 64
    elif condition == "short_cot":
        system_prompt = CONDITION_PROMPTS["short_cot"]
        full_prompt = base_prompt
        max_tokens = 1024
    elif condition == "budget_cot":
        budget_val = budget or 100
        system_prompt = CONDITION_PROMPTS["budget_cot"].format(budget=budget_val)
        full_prompt = base_prompt
        max_tokens = budget_val * 2  # rough token-to-word ratio
    else:
        raise ValueError(f"Unknown condition: {condition}")

    # Query the model
    response, latency = client.query(
        prompt=full_prompt,
        system_prompt=system_prompt,
        max_tokens=max_tokens,
    )

    # Extract and score
    extracted = extract_answer(response, instance["task"])
    ground_truth = str(instance["answer"])
    correct = extracted.strip().lower() == ground_truth.strip().lower()

    return EvalResult(
        instance_id=instance["id"],
        task=instance["task"],
        difficulty=instance["difficulty"],
        condition=condition,
        model=client.model_name,
        prompt_sent=full_prompt,
        model_response=response,
        extracted_answer=extracted,
        ground_truth=ground_truth,
        correct=correct,
        latency_ms=latency,
    )


def compute_summary(results: list[EvalResult]) -> EvalSummary:
    """Compute aggregated evaluation metrics.

    Args:
        results: List of individual evaluation results.

    Returns:
        EvalSummary with accuracy breakdowns.
    """
    if not results:
        return EvalSummary(
            task="", model="", condition="",
            total_instances=0, correct=0, accuracy=0.0,
            accuracy_by_difficulty={}, mean_latency_ms=0.0,
        )

    total = len(results)
    correct = sum(1 for r in results if r.correct)
    accuracy = correct / total if total > 0 else 0.0

    # Group by difficulty
    by_difficulty: dict[int, list[EvalResult]] = {}
    for r in results:
        by_difficulty.setdefault(r.difficulty, []).append(r)

    accuracy_by_difficulty: dict[int, float] = {}
    for diff, diff_results in sorted(by_difficulty.items()):
        n_correct = sum(1 for r in diff_results if r.correct)
        accuracy_by_difficulty[diff] = n_correct / len(diff_results)

    mean_latency = sum(r.latency_ms for r in results) / total

    return EvalSummary(
        task=results[0].task,
        model=results[0].model,
        condition=results[0].condition,
        total_instances=total,
        correct=correct,
        accuracy=accuracy,
        accuracy_by_difficulty=accuracy_by_difficulty,
        mean_latency_ms=mean_latency,
    )


# ---------------------------------------------------------------------------
# CLI entrypoint
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Evaluate models on ReasonGap benchmarks.",
    )
    parser.add_argument(
        "--benchmark",
        type=str,
        required=True,
        help="Path to benchmark JSON file (from generate.py).",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="dummy",
        help="Model identifier (e.g., 'openai:gpt-4o', 'anthropic:claude-3-opus'). "
             "Default: 'dummy' (placeholder).",
    )
    parser.add_argument(
        "--condition",
        type=str,
        choices=["direct", "short_cot", "budget_cot"],
        default="direct",
        help="Evaluation condition (default: direct).",
    )
    parser.add_argument(
        "--budget",
        type=int,
        default=None,
        help="Word budget for budget_cot condition.",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output JSON file for results.",
    )
    parser.add_argument(
        "--max-instances",
        type=int,
        default=None,
        help="Maximum number of instances to evaluate (for testing).",
    )

    args = parser.parse_args()

    # Load benchmark
    benchmark_path = Path(args.benchmark)
    if not benchmark_path.exists():
        print(f"Error: Benchmark file not found: {benchmark_path}", file=sys.stderr)
        sys.exit(1)

    with open(benchmark_path) as f:
        benchmark = json.load(f)

    instances = benchmark["instances"]
    if args.max_instances:
        instances = instances[:args.max_instances]

    print(f"Loaded {len(instances)} instances from {benchmark_path}")
    print(f"Task: {benchmark['task_name']}")
    print(f"Model: {args.model}")
    print(f"Condition: {args.condition}")

    # Initialize client
    if args.model == "dummy":
        client = DummyClient("dummy")
        print("\nWARNING: Using dummy client. Implement ModelClient subclass "
              "for actual evaluation.\n")
    else:
        # Parse model spec and create client
        from clients import create_client

        try:
            client = create_client(args.model)
        except ValueError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            sys.exit(1)

    # Run evaluation
    results: list[EvalResult] = []
    for idx, instance in enumerate(instances):
        if (idx + 1) % 10 == 0 or idx == 0:
            print(f"  Evaluating {idx + 1}/{len(instances)}...", flush=True)

        result = evaluate_instance(instance, client, args.condition, args.budget)
        results.append(result)

    # Compute summary
    summary = compute_summary(results)

    print(f"\n{'='*60}")
    print(f"Results: {summary.task}")
    print(f"{'='*60}")
    print(f"Model: {summary.model}")
    print(f"Condition: {summary.condition}")
    print(f"Total: {summary.total_instances}")
    print(f"Correct: {summary.correct}")
    print(f"Accuracy: {summary.accuracy:.2%}")
    print(f"\nAccuracy by difficulty:")
    for diff, acc in sorted(summary.accuracy_by_difficulty.items()):
        print(f"  Level {diff}: {acc:.2%}")
    print(f"\nMean latency: {summary.mean_latency_ms:.1f} ms")

    # Save results
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        output_data = {
            "summary": asdict(summary),
            "results": [asdict(r) for r in results],
        }

        with open(output_path, "w") as f:
            json.dump(output_data, f, indent=2)

        print(f"\nResults saved to {output_path}")


if __name__ == "__main__":
    main()
