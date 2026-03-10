#!/usr/bin/env python3
"""ReasonGap Benchmark Suite -- Evaluation Pipeline.

Runs inference on benchmark instances and scores results.
Production-ready with checkpoint/resume, structured logging,
dynamic budgets, cost estimation, and parallel evaluation.

Usage:
    python evaluate.py --benchmark data/b1_B1_masked_majority.json \
                       --model openai:gpt-4o \
                       --condition direct \
                       --output results/b1_gpt4o_direct.json

    # Resume interrupted run
    python evaluate.py --benchmark data/b1_B1_masked_majority.json \
                       --model openai:gpt-4o --resume

    # Cost estimation only
    python evaluate.py --benchmark data/b1_B1_masked_majority.json \
                       --model openai:gpt-4o --estimate-only

    # Parallel evaluation
    python evaluate.py --benchmark data/b1_B1_masked_majority.json \
                       --model openai:gpt-4o --parallel 5

Conditions:
    direct      -- No chain-of-thought; force immediate answer.
    short_cot   -- "Think step by step" prompt prefix (unconstrained).
    budget_cot  -- Dynamic CoT token budget based on task complexity.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import sys
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any

logger = logging.getLogger("reasongap.evaluate")


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
# Answer extraction (delegated to answer_extraction module)
# ---------------------------------------------------------------------------

from answer_extraction import extract_answer, is_refusal  # noqa: E402


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
        budget: Token budget for budget_cot condition. If None and
                condition is budget_cot, compute dynamically.

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
        if budget is not None:
            budget_val = budget
        else:
            # Dynamic budget based on task type and instance metadata
            from budget_calculator import compute_budget
            task_id = instance.get("task", "")
            budget_val = compute_budget(task_id, instance)
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
    ground_truth = str(instance["answer"])
    extracted = extract_answer(response, instance["task"], expected=ground_truth)
    refusal = is_refusal(response)
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
        metadata={"is_refusal": refusal},
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
# Logging setup
# ---------------------------------------------------------------------------

def setup_logging(verbose: bool = False) -> None:
    """Configure structured logging for the evaluation pipeline."""
    level = logging.DEBUG if verbose else logging.INFO
    fmt = "%(asctime)s %(levelname)s %(message)s"
    logging.basicConfig(level=level, format=fmt, force=True)


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
        help="Word budget for budget_cot condition. "
             "If not set, computed dynamically per instance.",
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
    # Checkpoint/resume flags
    parser.add_argument(
        "--resume",
        action="store_true",
        default=True,
        help="Resume from checkpoint if available (default: True).",
    )
    parser.add_argument(
        "--no-resume",
        action="store_true",
        default=False,
        help="Disable checkpoint resume (start fresh).",
    )
    parser.add_argument(
        "--checkpoint-dir",
        type=str,
        default=None,
        help="Directory for checkpoint files (default: results/checkpoints/).",
    )
    # Logging
    parser.add_argument(
        "--verbose",
        action="store_true",
        default=False,
        help="Enable DEBUG-level logging.",
    )
    # Cost estimation
    parser.add_argument(
        "--estimate-only",
        action="store_true",
        default=False,
        help="Estimate cost and exit without running evaluation.",
    )
    # Parallel evaluation
    parser.add_argument(
        "--parallel",
        type=int,
        default=None,
        help="Enable parallel evaluation with N concurrent workers.",
    )

    args = parser.parse_args()

    # Set up logging
    setup_logging(verbose=args.verbose)

    # Handle --no-resume overriding --resume
    resume = args.resume and not args.no_resume

    # Load benchmark
    benchmark_path = Path(args.benchmark)
    if not benchmark_path.exists():
        logger.error("Benchmark file not found: %s", benchmark_path)
        sys.exit(1)

    with open(benchmark_path) as f:
        benchmark = json.load(f)

    instances = benchmark["instances"]
    if args.max_instances:
        instances = instances[:args.max_instances]

    task_name = benchmark.get("task_name", benchmark.get("task", "unknown"))
    task_key = benchmark.get("task", task_name)

    logger.info("Loaded %d instances from %s", len(instances), benchmark_path)
    logger.info("Task: %s", task_name)
    logger.info("Model: %s", args.model)
    logger.info("Condition: %s", args.condition)

    # Cost estimation
    if args.estimate_only:
        from cost_estimator import estimate_cost, format_estimate
        estimate = estimate_cost(
            models=[args.model],
            tasks=[task_key],
            conditions=[args.condition],
            instances_per_task=len(instances),
        )
        logger.info("\n%s", format_estimate(estimate))
        sys.exit(0)

    # Initialize client
    if args.model == "dummy":
        client: ModelClient = DummyClient("dummy")
        logger.warning("Using dummy client -- responses will be placeholders")
    else:
        from clients import create_client
        try:
            client = create_client(args.model)
        except ValueError as exc:
            logger.error("Failed to create client: %s", exc)
            sys.exit(1)

    # Set up checkpoint manager
    checkpoint_dir = args.checkpoint_dir or str(
        Path(args.benchmark).resolve().parent.parent / "results" / "checkpoints"
    )
    from checkpoint import CheckpointManager
    checkpoint = CheckpointManager(checkpoint_dir)
    logger.info("Checkpoint directory: %s", checkpoint_dir)

    # Filter out already-completed instances if resuming
    if resume:
        completed_ids = checkpoint.get_completed_ids(
            args.model, task_name, args.condition
        )
        if completed_ids:
            remaining = [
                inst for inst in instances if inst["id"] not in completed_ids
            ]
            logger.info(
                "Resuming: %d/%d already complete, %d remaining",
                len(completed_ids),
                len(instances),
                len(remaining),
            )
            instances_to_eval = remaining
        else:
            instances_to_eval = instances
    else:
        instances_to_eval = instances

    if not instances_to_eval:
        logger.info("All instances already complete. Nothing to do.")
        # Load existing results for summary
        existing = checkpoint.load(args.model, task_name, args.condition)
        results = [
            EvalResult(**{k: v for k, v in r.items() if k in EvalResult.__dataclass_fields__})
            for r in existing
        ]
    elif args.parallel and args.parallel > 1:
        # Parallel evaluation
        logger.info(
            "Starting parallel evaluation: %d instances, concurrency=%d",
            len(instances_to_eval),
            args.parallel,
        )
        from batch_evaluate import evaluate_batch
        results = asyncio.run(
            evaluate_batch(
                instances=instances_to_eval,
                client=client,
                condition=args.condition,
                budget=args.budget,
                checkpoint=checkpoint,
                concurrency=args.parallel,
                evaluate_fn=evaluate_instance,
            )
        )
    else:
        # Sequential evaluation
        results: list[EvalResult] = []
        total = len(instances_to_eval)
        for idx, instance in enumerate(instances_to_eval):
            instance_id = instance["id"]
            logger.debug("Evaluating instance %s (%d/%d)", instance_id, idx + 1, total)

            try:
                result = evaluate_instance(
                    instance, client, args.condition, args.budget
                )
                # Checkpoint immediately
                checkpoint.save(result)
                results.append(result)

                logger.info(
                    "%s | correct=%s | latency=%.0fms | extracted=\"%s\"",
                    instance_id,
                    result.correct,
                    result.latency_ms,
                    result.extracted_answer,
                )
            except Exception as exc:
                logger.error(
                    "Failed to evaluate %s: %s", instance_id, exc
                )
                continue

            if (idx + 1) % 10 == 0:
                logger.info(
                    "Progress: %d/%d completed", idx + 1, total
                )

    # If we resumed, include the previously completed results in the summary
    if resume and results:
        all_results_data = checkpoint.load(args.model, task_name, args.condition)
        all_results = [
            EvalResult(**{k: v for k, v in r.items() if k in EvalResult.__dataclass_fields__})
            for r in all_results_data
        ]
    else:
        all_results = results

    # Compute summary
    summary = compute_summary(all_results)

    logger.info("=" * 60)
    logger.info("Results: %s", summary.task)
    logger.info("=" * 60)
    logger.info("Model: %s", summary.model)
    logger.info("Condition: %s", summary.condition)
    logger.info("Total: %d", summary.total_instances)
    logger.info("Correct: %d", summary.correct)
    logger.info("Accuracy: %.2f%%", summary.accuracy * 100)
    for diff, acc in sorted(summary.accuracy_by_difficulty.items()):
        logger.info("  Level %s: %.2f%%", diff, acc * 100)
    logger.info("Mean latency: %.1f ms", summary.mean_latency_ms)

    # Save results
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        output_data = {
            "summary": asdict(summary),
            "results": [asdict(r) for r in all_results],
        }

        with open(output_path, "w") as f:
            json.dump(output_data, f, indent=2)

        logger.info("Results saved to %s", output_path)


if __name__ == "__main__":
    main()
