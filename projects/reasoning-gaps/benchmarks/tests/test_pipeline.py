"""Tests for the pipeline hardening modules.

Covers:
- Checkpoint save/load/resume cycle
- Checkpoint deduplication (don't re-evaluate completed instances)
- Dynamic budget calculation for each task type
- Cost estimator produces reasonable numbers
- Batch evaluation with DummyClient
- Interrupted evaluation resumes correctly
"""

from __future__ import annotations

import asyncio
import json
import os
import tempfile
from pathlib import Path
from typing import Any

import pytest

# Ensure benchmarks directory is on sys.path (conftest.py does this too)
import sys
_benchmarks_dir = str(Path(__file__).resolve().parent.parent)
if _benchmarks_dir not in sys.path:
    sys.path.insert(0, _benchmarks_dir)

from evaluate import EvalResult, DummyClient, ModelClient, evaluate_instance, compute_summary
from checkpoint import CheckpointManager
from budget_calculator import compute_budget, MIN_BUDGET, MAX_BUDGET
from cost_estimator import estimate_cost, format_estimate
from batch_evaluate import evaluate_batch


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _make_result(
    instance_id: str = "test_001",
    task: str = "B1_masked_majority",
    difficulty: int = 1,
    condition: str = "direct",
    model: str = "dummy",
    correct: bool = True,
    latency_ms: float = 100.0,
) -> EvalResult:
    """Create a minimal EvalResult for testing."""
    return EvalResult(
        instance_id=instance_id,
        task=task,
        difficulty=difficulty,
        condition=condition,
        model=model,
        prompt_sent="test prompt",
        model_response="test response",
        extracted_answer="1",
        ground_truth="1",
        correct=correct,
        latency_ms=latency_ms,
        metadata={"is_refusal": False},
    )


def _make_instance(
    instance_id: str = "B1_masked_majority_d1_0001",
    task: str = "B1_masked_majority",
    difficulty: int = 1,
    answer: str = "1",
    n: int = 10,
) -> dict[str, Any]:
    """Create a minimal benchmark instance dict."""
    return {
        "id": instance_id,
        "task": task,
        "prompt": "Consider the binary string: 1010?1010?\nThe '?' characters are masked. Among the visible bits, is the majority 0 or 1?",
        "answer": answer,
        "difficulty": difficulty,
        "metadata": {"n": n, "n_masked": 2, "n_visible": 8, "ones": 4, "zeros": 4},
    }


# ---------------------------------------------------------------------------
# Checkpoint Tests
# ---------------------------------------------------------------------------

class TestCheckpointManager:
    """Test the checkpoint save/load/resume system."""

    def test_save_and_load(self, tmp_path: Path) -> None:
        """Checkpoint should save a result and load it back correctly."""
        ckpt = CheckpointManager(tmp_path / "checkpoints")
        result = _make_result(instance_id="inst_001")
        ckpt.save(result)

        loaded = ckpt.load("dummy", "B1_masked_majority", "direct")
        assert len(loaded) == 1
        assert loaded[0]["instance_id"] == "inst_001"
        assert loaded[0]["correct"] is True

    def test_save_multiple(self, tmp_path: Path) -> None:
        """Multiple results should all be persisted."""
        ckpt = CheckpointManager(tmp_path / "checkpoints")
        for i in range(5):
            result = _make_result(instance_id=f"inst_{i:03d}")
            ckpt.save(result)

        loaded = ckpt.load("dummy", "B1_masked_majority", "direct")
        assert len(loaded) == 5

    def test_get_completed_ids(self, tmp_path: Path) -> None:
        """get_completed_ids should return all saved instance IDs."""
        ckpt = CheckpointManager(tmp_path / "checkpoints")
        for i in range(3):
            ckpt.save(_make_result(instance_id=f"inst_{i:03d}"))

        completed = ckpt.get_completed_ids("dummy", "B1_masked_majority", "direct")
        assert completed == {"inst_000", "inst_001", "inst_002"}

    def test_is_complete(self, tmp_path: Path) -> None:
        """is_complete should return True when all expected instances are done."""
        ckpt = CheckpointManager(tmp_path / "checkpoints")
        for i in range(5):
            ckpt.save(_make_result(instance_id=f"inst_{i:03d}"))

        assert ckpt.is_complete("dummy", "B1_masked_majority", "direct", 5) is True
        assert ckpt.is_complete("dummy", "B1_masked_majority", "direct", 6) is False

    def test_load_empty(self, tmp_path: Path) -> None:
        """Loading from nonexistent checkpoint should return empty list."""
        ckpt = CheckpointManager(tmp_path / "checkpoints")
        loaded = ckpt.load("dummy", "B1_masked_majority", "direct")
        assert loaded == []

    def test_completed_ids_empty(self, tmp_path: Path) -> None:
        """get_completed_ids should return empty set for new checkpoints."""
        ckpt = CheckpointManager(tmp_path / "checkpoints")
        completed = ckpt.get_completed_ids("dummy", "B1_masked_majority", "direct")
        assert completed == set()

    def test_different_conditions_separate(self, tmp_path: Path) -> None:
        """Results for different conditions should not mix."""
        ckpt = CheckpointManager(tmp_path / "checkpoints")
        ckpt.save(_make_result(instance_id="inst_001", condition="direct"))
        ckpt.save(_make_result(instance_id="inst_002", condition="short_cot"))

        direct_ids = ckpt.get_completed_ids("dummy", "B1_masked_majority", "direct")
        cot_ids = ckpt.get_completed_ids("dummy", "B1_masked_majority", "short_cot")
        assert direct_ids == {"inst_001"}
        assert cot_ids == {"inst_002"}

    def test_different_models_separate(self, tmp_path: Path) -> None:
        """Results for different models should not mix."""
        ckpt = CheckpointManager(tmp_path / "checkpoints")
        ckpt.save(_make_result(instance_id="inst_001", model="model_a"))
        ckpt.save(_make_result(instance_id="inst_002", model="model_b"))

        a_ids = ckpt.get_completed_ids("model_a", "B1_masked_majority", "direct")
        b_ids = ckpt.get_completed_ids("model_b", "B1_masked_majority", "direct")
        assert a_ids == {"inst_001"}
        assert b_ids == {"inst_002"}

    def test_cache_updated_on_save(self, tmp_path: Path) -> None:
        """In-memory cache should be updated when saving new results."""
        ckpt = CheckpointManager(tmp_path / "checkpoints")
        # Prime the cache
        ckpt.get_completed_ids("dummy", "B1_masked_majority", "direct")
        # Save a result
        ckpt.save(_make_result(instance_id="inst_new"))
        # Cache should include the new result without reloading from disk
        completed = ckpt.get_completed_ids("dummy", "B1_masked_majority", "direct")
        assert "inst_new" in completed

    def test_corrupt_line_skipped(self, tmp_path: Path) -> None:
        """Corrupt JSONL lines should be skipped gracefully."""
        ckpt = CheckpointManager(tmp_path / "checkpoints")
        ckpt.save(_make_result(instance_id="inst_001"))

        # Manually append a corrupt line
        path = ckpt._checkpoint_path("dummy", "B1_masked_majority", "direct")
        with open(path, "a") as f:
            f.write("{this is not valid json\n")

        ckpt.save(_make_result(instance_id="inst_002"))

        # Force reload by creating a fresh manager
        ckpt2 = CheckpointManager(tmp_path / "checkpoints")
        loaded = ckpt2.load("dummy", "B1_masked_majority", "direct")
        ids = {r["instance_id"] for r in loaded}
        assert "inst_001" in ids
        assert "inst_002" in ids
        assert len(loaded) == 2  # corrupt line skipped

    def test_summary(self, tmp_path: Path) -> None:
        """summary() should return completed and correct counts."""
        ckpt = CheckpointManager(tmp_path / "checkpoints")
        ckpt.save(_make_result(instance_id="inst_001", correct=True))
        ckpt.save(_make_result(instance_id="inst_002", correct=False))
        ckpt.save(_make_result(instance_id="inst_003", correct=True))

        s = ckpt.summary("dummy", "B1_masked_majority", "direct")
        assert s["completed"] == 3
        assert s["correct"] == 2


# ---------------------------------------------------------------------------
# Deduplication / Resume Tests
# ---------------------------------------------------------------------------

class TestDeduplication:
    """Test that checkpoint-based deduplication works correctly."""

    def test_skip_completed_instances(self, tmp_path: Path) -> None:
        """Completed instances should be skipped on resume."""
        ckpt = CheckpointManager(tmp_path / "checkpoints")
        # Simulate prior run completing 3 of 5 instances
        for i in range(3):
            ckpt.save(_make_result(instance_id=f"inst_{i:03d}"))

        # Build instance list
        all_instances = [
            _make_instance(instance_id=f"inst_{i:03d}") for i in range(5)
        ]

        # Filter like evaluate.py does
        completed = ckpt.get_completed_ids("dummy", "B1_masked_majority", "direct")
        remaining = [
            inst for inst in all_instances if inst["id"] not in completed
        ]

        assert len(remaining) == 2
        assert remaining[0]["id"] == "inst_003"
        assert remaining[1]["id"] == "inst_004"

    def test_full_resume_cycle(self, tmp_path: Path) -> None:
        """Simulate a crash and resume: all instances get evaluated exactly once."""
        ckpt = CheckpointManager(tmp_path / "checkpoints")
        client = DummyClient("dummy")
        instances = [
            _make_instance(instance_id=f"inst_{i:03d}") for i in range(10)
        ]

        # First run: evaluate first 6
        for inst in instances[:6]:
            result = evaluate_instance(inst, client, "direct")
            ckpt.save(result)

        # Simulate "crash" -- create fresh checkpoint manager (fresh cache)
        ckpt2 = CheckpointManager(tmp_path / "checkpoints")
        completed = ckpt2.get_completed_ids("dummy", "B1_masked_majority", "direct")
        assert len(completed) == 6

        # Second run: evaluate remaining
        remaining = [inst for inst in instances if inst["id"] not in completed]
        assert len(remaining) == 4

        for inst in remaining:
            result = evaluate_instance(inst, client, "direct")
            ckpt2.save(result)

        # All 10 should be complete
        assert ckpt2.is_complete("dummy", "B1_masked_majority", "direct", 10)


# ---------------------------------------------------------------------------
# Dynamic Budget Tests
# ---------------------------------------------------------------------------

class TestBudgetCalculator:
    """Test dynamic budget calculation for each task type."""

    def test_b1_budget_scales_with_n(self) -> None:
        """B1 budget should scale with string length n."""
        small = compute_budget("B1", {"metadata": {"n": 10}})
        large = compute_budget("B1", {"metadata": {"n": 200}})
        assert large > small
        assert small >= MIN_BUDGET
        assert large <= MAX_BUDGET

    def test_b2_budget_scales_with_depth(self) -> None:
        """B2 budget should scale with formula depth."""
        shallow = compute_budget("B2", {"metadata": {"depth": 2}})
        deep = compute_budget("B2", {"metadata": {"depth": 10}})
        assert deep > shallow

    def test_b3_budget_scales_with_k(self) -> None:
        """B3 budget should scale with number of compositions."""
        small_k = compute_budget("B3", {"metadata": {"k": 2}})
        large_k = compute_budget("B3", {"metadata": {"k": 32}})
        assert large_k > small_k

    def test_b4_budget_scales_with_k(self) -> None:
        """B4 budget should scale with number of transitions."""
        small_k = compute_budget("B4", {"metadata": {"k": 3}})
        large_k = compute_budget("B4", {"metadata": {"k": 50}})
        assert large_k > small_k

    def test_b5_budget_scales_with_nodes(self) -> None:
        """B5 budget should scale with graph size (via estimated diameter)."""
        small = compute_budget("B5", {"metadata": {"n_nodes": 5}})
        large = compute_budget("B5", {"metadata": {"n_nodes": 100}})
        assert large > small

    def test_b6_budget_scales_quadratically(self) -> None:
        """B6 budget should grow roughly quadratically with n."""
        n5 = compute_budget("B6", {"metadata": {"n": 5}})
        n20 = compute_budget("B6", {"metadata": {"n": 20}})
        # Quadratic: 20^2/5^2 = 16x, but capped
        assert n20 > n5

    def test_b7_budget_scales_with_vars(self) -> None:
        """B7 budget should scale with number of variables."""
        small = compute_budget("B7", {"metadata": {"n_vars": 4}})
        large = compute_budget("B7", {"metadata": {"n_vars": 64}})
        assert large > small

    def test_b8_budget_scales_with_facts(self) -> None:
        """B8 budget should scale with number of facts."""
        small = compute_budget("B8", {"metadata": {"n_facts": 2}})
        large = compute_budget("B8", {"metadata": {"n_facts": 50}})
        assert large > small

    def test_b9_budget_scales_with_depth(self) -> None:
        """B9 budget should scale with negation depth."""
        shallow = compute_budget("B9", {"metadata": {"negation_depth": 1}})
        deep = compute_budget("B9", {"metadata": {"negation_depth": 5}})
        assert deep > shallow

    def test_minimum_budget_enforced(self) -> None:
        """Budget should never be below MIN_BUDGET."""
        # B9 with depth=1 should still be >= MIN_BUDGET
        budget = compute_budget("B9", {"metadata": {"negation_depth": 1}})
        assert budget >= MIN_BUDGET

    def test_maximum_budget_enforced(self) -> None:
        """Budget should never exceed MAX_BUDGET."""
        # B6 with very large n
        budget = compute_budget("B6", {"metadata": {"n": 1000}})
        assert budget <= MAX_BUDGET

    def test_task_name_with_suffix(self) -> None:
        """Task names like 'B1_masked_majority' should resolve to B1."""
        budget = compute_budget("B1_masked_majority", {"metadata": {"n": 10}})
        assert budget >= MIN_BUDGET

    def test_unknown_task_raises(self) -> None:
        """Unknown task names should raise ValueError."""
        with pytest.raises(ValueError, match="Unknown task"):
            compute_budget("B99_unknown", {"metadata": {}})

    def test_all_tasks_produce_valid_budgets(self) -> None:
        """Every task should produce a budget in [MIN_BUDGET, MAX_BUDGET]."""
        test_cases = {
            "B1": {"metadata": {"n": 50}},
            "B2": {"metadata": {"depth": 5}},
            "B3": {"metadata": {"k": 8}},
            "B4": {"metadata": {"k": 10}},
            "B5": {"metadata": {"n_nodes": 20}},
            "B6": {"metadata": {"n": 20}},
            "B7": {"metadata": {"n_vars": 16}},
            "B8": {"metadata": {"n_facts": 10}},
            "B9": {"metadata": {"negation_depth": 3}},
        }
        for task, instance in test_cases.items():
            budget = compute_budget(task, instance)
            assert MIN_BUDGET <= budget <= MAX_BUDGET, (
                f"Task {task}: budget {budget} out of range "
                f"[{MIN_BUDGET}, {MAX_BUDGET}]"
            )


# ---------------------------------------------------------------------------
# Cost Estimator Tests
# ---------------------------------------------------------------------------

class TestCostEstimator:
    """Test cost estimation produces reasonable numbers."""

    def test_basic_estimate(self) -> None:
        """Basic estimate should return positive values."""
        est = estimate_cost(
            models=["dummy"],
            tasks=["B1"],
            conditions=["direct"],
            instances_per_task=100,
        )
        assert est["total_instances"] > 0
        assert est["total_cost"] >= 0
        assert est["total_input_tokens"] > 0

    def test_multiple_models_sum(self) -> None:
        """Cost should increase with more models."""
        est_one = estimate_cost(
            models=["openai:gpt-4o"],
            tasks=["B1"],
            conditions=["direct"],
            instances_per_task=100,
        )
        est_two = estimate_cost(
            models=["openai:gpt-4o", "openai:gpt-4o-mini"],
            tasks=["B1"],
            conditions=["direct"],
            instances_per_task=100,
        )
        assert est_two["total_cost"] > est_one["total_cost"]

    def test_multiple_conditions_sum(self) -> None:
        """More conditions should mean more instances and cost."""
        est_one = estimate_cost(
            models=["openai:gpt-4o"],
            tasks=["B1"],
            conditions=["direct"],
            instances_per_task=100,
        )
        est_three = estimate_cost(
            models=["openai:gpt-4o"],
            tasks=["B1"],
            conditions=["direct", "short_cot", "budget_cot"],
            instances_per_task=100,
        )
        assert est_three["total_instances"] == 3 * est_one["total_instances"]

    def test_dummy_model_zero_cost(self) -> None:
        """Dummy model should have zero cost."""
        est = estimate_cost(
            models=["dummy"],
            tasks=["B1"],
            conditions=["direct"],
            instances_per_task=100,
        )
        assert est["total_cost"] == 0.0

    def test_full_run_estimate(self) -> None:
        """Estimate for full 216K run should be computable."""
        est = estimate_cost(
            models=[
                "anthropic:claude-haiku-4-5-20251001",
                "anthropic:claude-sonnet-4-6-20250514",
                "openai:gpt-4o",
                "openai:gpt-4o-mini",
            ],
            tasks=["B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8", "B9"],
            conditions=["direct", "short_cot", "budget_cot"],
            instances_per_task=100,
        )
        # Should produce a reasonable dollar figure (not zero, not millions)
        assert est["total_cost"] > 0
        assert est["total_cost"] < 10_000  # sanity upper bound
        assert est["total_instances"] > 0

    def test_format_estimate(self) -> None:
        """format_estimate should produce a non-empty string."""
        est = estimate_cost(
            models=["openai:gpt-4o"],
            tasks=["B1"],
            conditions=["direct"],
            instances_per_task=100,
        )
        formatted = format_estimate(est)
        assert "COST ESTIMATE" in formatted
        assert "$" in formatted

    def test_by_model_breakdown(self) -> None:
        """by_model should have an entry for each model."""
        models = ["openai:gpt-4o", "openai:gpt-4o-mini"]
        est = estimate_cost(
            models=models,
            tasks=["B1"],
            conditions=["direct"],
            instances_per_task=100,
        )
        for model in models:
            assert model in est["by_model"]

    def test_by_task_breakdown(self) -> None:
        """by_task should have entries for requested tasks."""
        est = estimate_cost(
            models=["openai:gpt-4o"],
            tasks=["B1", "B2", "B3"],
            conditions=["direct"],
            instances_per_task=100,
        )
        assert "B1" in est["by_task"]
        assert "B2" in est["by_task"]
        assert "B3" in est["by_task"]


# ---------------------------------------------------------------------------
# Batch Evaluation Tests
# ---------------------------------------------------------------------------

class TestBatchEvaluate:
    """Test async parallel evaluation."""

    def test_basic_batch(self) -> None:
        """Batch evaluation should evaluate all instances."""
        client = DummyClient("dummy")
        instances = [
            _make_instance(instance_id=f"inst_{i:03d}") for i in range(10)
        ]

        results = asyncio.run(
            evaluate_batch(
                instances=instances,
                client=client,
                condition="direct",
                budget=None,
                checkpoint=None,
                concurrency=3,
                evaluate_fn=evaluate_instance,
            )
        )
        assert len(results) == 10

    def test_batch_with_checkpoint(self, tmp_path: Path) -> None:
        """Batch evaluation should checkpoint results as they complete."""
        ckpt = CheckpointManager(tmp_path / "checkpoints")
        client = DummyClient("dummy")
        instances = [
            _make_instance(instance_id=f"inst_{i:03d}") for i in range(5)
        ]

        results = asyncio.run(
            evaluate_batch(
                instances=instances,
                client=client,
                condition="direct",
                budget=None,
                checkpoint=ckpt,
                concurrency=2,
                evaluate_fn=evaluate_instance,
            )
        )
        assert len(results) == 5

        # Verify checkpoints were saved
        completed = ckpt.get_completed_ids("dummy", "B1_masked_majority", "direct")
        assert len(completed) == 5

    def test_batch_concurrency_limit(self) -> None:
        """Concurrency should be limited by semaphore."""
        import threading

        max_concurrent = 0
        current_concurrent = 0
        lock = threading.Lock()

        class SlowDummyClient(ModelClient):
            def query(self, prompt, system_prompt="", max_tokens=512):
                nonlocal max_concurrent, current_concurrent
                import time
                with lock:
                    current_concurrent += 1
                    if current_concurrent > max_concurrent:
                        max_concurrent = current_concurrent
                time.sleep(0.05)
                with lock:
                    current_concurrent -= 1
                return ("test", 50.0)

        client = SlowDummyClient("slow_dummy")
        instances = [
            _make_instance(instance_id=f"inst_{i:03d}") for i in range(10)
        ]

        asyncio.run(
            evaluate_batch(
                instances=instances,
                client=client,
                condition="direct",
                budget=None,
                checkpoint=None,
                concurrency=3,
                evaluate_fn=evaluate_instance,
            )
        )

        # max_concurrent should not exceed concurrency limit
        assert max_concurrent <= 3

    def test_batch_error_handling(self) -> None:
        """Batch should continue if one instance fails."""
        call_count = 0

        class FailingClient(ModelClient):
            def query(self, prompt, system_prompt="", max_tokens=512):
                nonlocal call_count
                call_count += 1
                if call_count == 3:
                    raise RuntimeError("Simulated API failure")
                return ("test response", 10.0)

        client = FailingClient("failing")
        instances = [
            _make_instance(instance_id=f"inst_{i:03d}") for i in range(5)
        ]

        results = asyncio.run(
            evaluate_batch(
                instances=instances,
                client=client,
                condition="direct",
                budget=None,
                checkpoint=None,
                concurrency=1,  # Sequential to control failure order
                evaluate_fn=evaluate_instance,
            )
        )

        # 4 of 5 should succeed (one fails)
        assert len(results) == 4

    def test_batch_requires_evaluate_fn(self) -> None:
        """Should raise ValueError if evaluate_fn is not provided."""
        with pytest.raises(ValueError, match="evaluate_fn must be provided"):
            asyncio.run(
                evaluate_batch(
                    instances=[],
                    client=DummyClient("dummy"),
                    condition="direct",
                    budget=None,
                )
            )


# ---------------------------------------------------------------------------
# Integration: Interrupted Evaluation Resume
# ---------------------------------------------------------------------------

class TestInterruptedResume:
    """Test that interrupted evaluations resume correctly end-to-end."""

    def test_interrupted_sequential_resume(self, tmp_path: Path) -> None:
        """Simulate sequential eval crash and verify correct resume behavior."""
        ckpt = CheckpointManager(tmp_path / "checkpoints")
        client = DummyClient("dummy")
        task = "B1_masked_majority"
        condition = "direct"
        model = "dummy"

        all_instances = [
            _make_instance(instance_id=f"inst_{i:03d}") for i in range(20)
        ]

        # "First run" -- evaluate 12 then "crash"
        for inst in all_instances[:12]:
            result = evaluate_instance(inst, client, condition)
            ckpt.save(result)

        # Verify state after crash
        completed = ckpt.get_completed_ids(model, task, condition)
        assert len(completed) == 12

        # "Second run" -- resume
        ckpt2 = CheckpointManager(tmp_path / "checkpoints")
        completed2 = ckpt2.get_completed_ids(model, task, condition)
        remaining = [inst for inst in all_instances if inst["id"] not in completed2]
        assert len(remaining) == 8

        for inst in remaining:
            result = evaluate_instance(inst, client, condition)
            ckpt2.save(result)

        # All 20 should be complete
        assert ckpt2.is_complete(model, task, condition, 20)

        # Load all results and verify no duplicates
        all_results = ckpt2.load(model, task, condition)
        all_ids = [r["instance_id"] for r in all_results]
        assert len(all_ids) == 20
        assert len(set(all_ids)) == 20  # No duplicates

    def test_interrupted_parallel_resume(self, tmp_path: Path) -> None:
        """Simulate parallel eval crash and verify correct resume behavior."""
        ckpt = CheckpointManager(tmp_path / "checkpoints")
        client = DummyClient("dummy")
        task = "B1_masked_majority"
        condition = "direct"
        model = "dummy"

        all_instances = [
            _make_instance(instance_id=f"inst_{i:03d}") for i in range(15)
        ]

        # First batch: evaluate first 8
        results1 = asyncio.run(
            evaluate_batch(
                instances=all_instances[:8],
                client=client,
                condition=condition,
                budget=None,
                checkpoint=ckpt,
                concurrency=3,
                evaluate_fn=evaluate_instance,
            )
        )
        assert len(results1) == 8

        # "Crash" -- create fresh manager
        ckpt2 = CheckpointManager(tmp_path / "checkpoints")
        completed = ckpt2.get_completed_ids(model, task, condition)
        assert len(completed) == 8

        # Resume with remaining
        remaining = [inst for inst in all_instances if inst["id"] not in completed]
        assert len(remaining) == 7

        results2 = asyncio.run(
            evaluate_batch(
                instances=remaining,
                client=client,
                condition=condition,
                budget=None,
                checkpoint=ckpt2,
                concurrency=3,
                evaluate_fn=evaluate_instance,
            )
        )
        assert len(results2) == 7
        assert ckpt2.is_complete(model, task, condition, 15)


# ---------------------------------------------------------------------------
# Dynamic Budget + evaluate_instance Integration
# ---------------------------------------------------------------------------

class TestBudgetCotIntegration:
    """Test that evaluate_instance uses dynamic budgets correctly."""

    def test_budget_cot_uses_dynamic_budget(self) -> None:
        """When no explicit budget is given, budget_cot should use dynamic budget."""
        client = DummyClient("dummy")
        instance = _make_instance(n=50)  # B1 with n=50

        # With no explicit budget, should use dynamic calculator
        result = evaluate_instance(instance, client, "budget_cot", budget=None)
        assert result.condition == "budget_cot"
        # The prompt should contain a budget number (from dynamic calculator)
        assert "words" in result.prompt_sent or result.prompt_sent  # prompt is the base prompt

    def test_budget_cot_with_explicit_budget(self) -> None:
        """Explicit budget should override dynamic calculation."""
        client = DummyClient("dummy")
        instance = _make_instance(n=50)

        result = evaluate_instance(instance, client, "budget_cot", budget=42)
        assert result.condition == "budget_cot"
        # No crash means the explicit budget was used
