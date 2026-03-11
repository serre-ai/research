"""Cost estimation for ReasonGap evaluation runs.

Estimates API costs based on model pricing, average prompt lengths per task,
and expected output lengths per condition. Provides a clear summary before
committing to a long-running evaluation.
"""

from __future__ import annotations

from typing import Any

# Pricing per 1M tokens (USD) -- input and output
MODEL_PRICING: dict[str, dict[str, float]] = {
    # Anthropic
    "anthropic:claude-haiku-4-5-20251001": {"input": 0.80, "output": 4.00},
    "anthropic:claude-sonnet-4-6-20250514": {"input": 3.00, "output": 15.00},
    "anthropic:claude-opus-4-6-20250514": {"input": 15.00, "output": 75.00},
    "claude-haiku-4-5-20251001": {"input": 0.80, "output": 4.00},
    "claude-sonnet-4-6-20250514": {"input": 3.00, "output": 15.00},
    "claude-opus-4-6-20250514": {"input": 15.00, "output": 75.00},
    # OpenAI
    "openai:gpt-4o": {"input": 2.50, "output": 10.00},
    "openai:gpt-4o-mini": {"input": 0.15, "output": 0.60},
    "openai:gpt-4.1": {"input": 2.00, "output": 8.00},
    "openai:gpt-4.1-mini": {"input": 0.40, "output": 1.60},
    "openai:gpt-4.1-nano": {"input": 0.10, "output": 0.40},
    "openai:o1": {"input": 15.00, "output": 60.00},
    "openai:o3": {"input": 10.00, "output": 40.00},
    "openai:o3-mini": {"input": 1.10, "output": 4.40},
    "gpt-4o": {"input": 2.50, "output": 10.00},
    "gpt-4o-mini": {"input": 0.15, "output": 0.60},
    "o3": {"input": 10.00, "output": 40.00},
    # vLLM (self-hosted: ~$0 per token, but track compute cost separately)
    "vllm:*": {"input": 0.0, "output": 0.0},
    # Dummy
    "dummy": {"input": 0.0, "output": 0.0},
}

# Average input tokens per task (estimated from prompt lengths)
AVG_INPUT_TOKENS: dict[str, dict[int, int]] = {
    "B1": {1: 80, 2: 100, 3: 150, 4: 250, 5: 450},
    "B2": {1: 100, 2: 130, 3: 200, 4: 300, 5: 500},
    "B3": {1: 150, 2: 200, 3: 350, 4: 600, 5: 1100},
    "B4": {1: 150, 2: 180, 3: 250, 4: 400, 5: 800},
    "B5": {1: 120, 2: 250, 3: 500, 4: 1500, 5: 4000},
    "B6": {1: 120, 2: 150, 3: 220, 4: 400, 5: 700},
    "B7": {1: 150, 2: 250, 3: 450, 4: 800, 5: 1500},
    "B8": {1: 120, 2: 180, 3: 300, 4: 550, 5: 1200},
    "B9": {1: 100, 2: 110, 3: 130, 4: 150, 5: 180},
}

# Average output tokens per condition
AVG_OUTPUT_TOKENS: dict[str, int] = {
    "direct": 15,
    "short_cot": 300,
    "budget_cot": 200,
}

# Default difficulty distribution (instances per difficulty level)
DEFAULT_DIFFICULTIES = [1, 2, 3, 4, 5]


def _get_pricing(model: str) -> dict[str, float]:
    """Look up pricing for a model, falling back to vLLM wildcard."""
    if model in MODEL_PRICING:
        return MODEL_PRICING[model]

    # Check if it matches a vLLM model
    if model.startswith("vllm:"):
        return MODEL_PRICING["vllm:*"]

    # Unknown model -- use a conservative estimate
    return {"input": 5.00, "output": 20.00}


def _resolve_task_key(task: str) -> str:
    """Resolve task name to B1-B9 key."""
    task_upper = task.upper()
    for key in AVG_INPUT_TOKENS:
        if task_upper.startswith(key):
            return key
    return task_upper


def estimate_cost(
    models: list[str],
    tasks: list[str],
    conditions: list[str],
    instances_per_task: int,
    difficulties: list[int] | None = None,
) -> dict[str, Any]:
    """Estimate the total cost for an evaluation run.

    Args:
        models: List of model identifiers.
        tasks: List of task identifiers (e.g., ["B1", "B2", ...]).
        conditions: List of conditions (e.g., ["direct", "short_cot"]).
        instances_per_task: Number of instances per (task, difficulty) pair.
        difficulties: Difficulty levels to include (default: [1,2,3,4,5]).

    Returns:
        Dict with 'by_model', 'by_task', 'total_cost', 'total_instances',
        and 'total_tokens' fields.
    """
    if difficulties is None:
        difficulties = DEFAULT_DIFFICULTIES

    by_model: dict[str, float] = {}
    by_task: dict[str, float] = {}
    total_cost = 0.0
    total_input_tokens = 0
    total_output_tokens = 0
    total_instances = 0

    for model in models:
        pricing = _get_pricing(model)
        model_cost = 0.0

        for task in tasks:
            task_key = _resolve_task_key(task)
            task_input_tokens = AVG_INPUT_TOKENS.get(task_key, {})

            for condition in conditions:
                avg_output = AVG_OUTPUT_TOKENS.get(condition, 100)

                for diff in difficulties:
                    avg_input = task_input_tokens.get(diff, 200)

                    # System prompt adds ~30 tokens
                    instance_input_tokens = avg_input + 30
                    instance_output_tokens = avg_output
                    n_instances = instances_per_task

                    batch_input = instance_input_tokens * n_instances
                    batch_output = instance_output_tokens * n_instances

                    batch_cost = (
                        batch_input * pricing["input"] / 1_000_000
                        + batch_output * pricing["output"] / 1_000_000
                    )

                    model_cost += batch_cost
                    by_task[task_key] = by_task.get(task_key, 0.0) + batch_cost
                    total_input_tokens += batch_input
                    total_output_tokens += batch_output
                    total_instances += n_instances

        by_model[model] = model_cost
        total_cost += model_cost

    return {
        "by_model": by_model,
        "by_task": by_task,
        "total_cost": total_cost,
        "total_instances": total_instances,
        "total_input_tokens": total_input_tokens,
        "total_output_tokens": total_output_tokens,
    }


def format_estimate(estimate: dict[str, Any]) -> str:
    """Format a cost estimate as a human-readable summary string."""
    lines = []
    lines.append("=" * 60)
    lines.append("COST ESTIMATE")
    lines.append("=" * 60)
    lines.append(f"Total instances: {estimate['total_instances']:,}")
    lines.append(
        f"Total tokens:    {estimate['total_input_tokens'] + estimate['total_output_tokens']:,} "
        f"({estimate['total_input_tokens']:,} input + {estimate['total_output_tokens']:,} output)"
    )
    lines.append(f"Estimated cost:  ${estimate['total_cost']:.2f}")
    lines.append("")

    lines.append("By model:")
    for model, cost in sorted(estimate["by_model"].items(), key=lambda x: -x[1]):
        lines.append(f"  {model:45s}  ${cost:.2f}")
    lines.append("")

    lines.append("By task:")
    for task, cost in sorted(estimate["by_task"].items()):
        lines.append(f"  {task:10s}  ${cost:.2f}")

    lines.append("=" * 60)
    return "\n".join(lines)
