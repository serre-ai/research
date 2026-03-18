"""Parallel evaluation support for ReasonGap benchmarks.

Provides async batch evaluation using asyncio with configurable concurrency.
Wraps synchronous model client calls in a thread pool executor for
parallelism without rewriting the client interfaces.
"""

from __future__ import annotations

import asyncio
import logging
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Any

logger = logging.getLogger(__name__)


async def evaluate_batch(
    instances: list[dict[str, Any]],
    client: Any,
    condition: str,
    budget: int | None,
    checkpoint: Any | None = None,
    concurrency: int = 5,
    evaluate_fn: Any = None,
    budget_multiplier: float | None = None,
) -> list[Any]:
    """Evaluate a batch of instances concurrently.

    Uses asyncio.Semaphore to limit concurrency and a ThreadPoolExecutor
    to run synchronous client.query() calls in parallel.

    Args:
        instances: List of benchmark instance dicts.
        client: ModelClient instance (synchronous query interface).
        condition: Evaluation condition (direct, short_cot, budget_cot, tool_use).
        budget: Word budget for budget_cot (None for dynamic).
        checkpoint: Optional CheckpointManager for incremental saves.
        concurrency: Maximum number of concurrent evaluations.
        evaluate_fn: The evaluate_instance function to call. Must be provided.
        budget_multiplier: Optional multiplier for budget_cot word budget.

    Returns:
        List of EvalResult objects for all successfully evaluated instances.
    """
    if evaluate_fn is None:
        raise ValueError("evaluate_fn must be provided")

    semaphore = asyncio.Semaphore(concurrency)
    results: list[Any] = []
    results_lock = asyncio.Lock()
    completed_count = 0
    error_count = 0
    total = len(instances)
    start_time = time.monotonic()

    # Use a thread pool sized to match concurrency
    executor = ThreadPoolExecutor(max_workers=concurrency)
    loop = asyncio.get_event_loop()

    async def _evaluate_one(instance: dict[str, Any]) -> None:
        nonlocal completed_count, error_count

        instance_id = instance.get("id", "unknown")
        async with semaphore:
            try:
                # Run sync evaluate_instance in thread pool
                import functools
                _eval_call = functools.partial(
                    evaluate_fn,
                    instance,
                    client,
                    condition,
                    budget,
                    budget_multiplier=budget_multiplier,
                )
                result = await loop.run_in_executor(
                    executor,
                    _eval_call,
                )

                # Save checkpoint immediately
                if checkpoint is not None:
                    try:
                        checkpoint.save(result)
                    except Exception as ckpt_err:
                        logger.error(
                            "Failed to save checkpoint for %s: %s",
                            instance_id,
                            ckpt_err,
                        )

                async with results_lock:
                    results.append(result)
                    completed_count += 1

                    # Progress reporting every 10 completions
                    if completed_count % 10 == 0 or completed_count == total:
                        elapsed = time.monotonic() - start_time
                        rate = completed_count / elapsed if elapsed > 0 else 0
                        logger.info(
                            "Progress: %d/%d completed (%.1f/s), %d errors",
                            completed_count,
                            total,
                            rate,
                            error_count,
                        )

            except Exception as exc:
                async with results_lock:
                    error_count += 1
                logger.error(
                    "Error evaluating instance %s: %s", instance_id, exc
                )

    # Create tasks for all instances
    tasks = [asyncio.create_task(_evaluate_one(inst)) for inst in instances]

    # Wait for all tasks to complete
    await asyncio.gather(*tasks, return_exceptions=True)

    executor.shutdown(wait=False)

    elapsed = time.monotonic() - start_time
    logger.info(
        "Batch complete: %d/%d succeeded, %d errors, %.1f seconds",
        completed_count,
        total,
        error_count,
        elapsed,
    )

    return results
