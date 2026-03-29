"""
Basic tests for experiment infrastructure.

Run with: python test_infrastructure.py
"""

import sys
from pathlib import Path

# Add parent directory to path to enable imports
src_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(src_dir.parent))
sys.path.insert(0, str(src_dir))

from tasks.tool_fabrication import ToolFabricationGenerator, generate_tool_count_conditions
from detectors.tool_fabrication_detector import ToolFabricationDetector
from frameworks.base import AgentResult, Action, ActionType
from utils.checkpoint import CheckpointManager
from utils.cost_tracker import CostTracker


def test_task_generation():
    """Test that task generator produces valid tasks."""
    print("Testing task generation...")

    gen = ToolFabricationGenerator(seed=42)

    # Generate single task
    task = gen.generate(task_id="test_1", difficulty=1, num_decoy_tools=10)

    assert task.task_id == "test_1"
    assert task.task_type == "tool_fabrication"
    assert len(task.tools) == 11  # 1 real + 10 decoys
    assert task.ground_truth["correct_tool"] == "calculator"
    assert "calculator" in [t["name"] for t in task.tools]

    print(f"  ✓ Generated task with {len(task.tools)} tools")
    print(f"  ✓ Problem: {task.metadata['problem']}")
    print(f"  ✓ Answer: {task.metadata['answer']}")

    # Test batch generation
    conditions = generate_tool_count_conditions(seed=42)
    assert len(conditions) == 4  # 3, 10, 30, 100 tool conditions
    assert all(len(tasks) == 10 for tasks in conditions.values())

    print(f"  ✓ Generated {len(conditions)} conditions with 10 instances each")


def test_detector():
    """Test that failure detector works correctly."""
    print("\nTesting failure detector...")

    detector = ToolFabricationDetector()

    # Create a mock task
    gen = ToolFabricationGenerator(seed=42)
    task = gen.generate(task_id="test_detector", difficulty=1, num_decoy_tools=5)

    # Test case 1: Agent uses correct tool (no failure)
    result_correct = AgentResult(
        success=True,
        output="42",
        trace=[
            Action(type=ActionType.TOOL_CALL, content="calculator", parameters={"expression": "40 + 2"})
        ],
        cost=0.001,
        token_counts={"input": 100, "output": 50, "total": 150},
        metadata={}
    )
    assert not detector.detect(result_correct, task)
    print("  ✓ Correctly identifies no failure when correct tool used")

    # Test case 2: Agent fabricates non-existent tool (failure)
    result_fabricated = AgentResult(
        success=False,
        output="Error",
        trace=[
            Action(type=ActionType.TOOL_CALL, content="super_calculator_9000", parameters={})
        ],
        cost=0.001,
        token_counts={"input": 100, "output": 50, "total": 150},
        metadata={}
    )
    assert detector.detect(result_fabricated, task)
    details = detector.get_failure_details(result_fabricated, task)
    assert "super_calculator_9000" in details["fabricated_tools"]
    print("  ✓ Correctly detects fabricated tool")

    # Test case 3: Agent uses wrong but existing tool (failure)
    wrong_tool_name = [t["name"] for t in task.tools if t["name"] != "calculator"][0]
    result_wrong = AgentResult(
        success=False,
        output="Error",
        trace=[
            Action(type=ActionType.TOOL_CALL, content=wrong_tool_name, parameters={})
        ],
        cost=0.001,
        token_counts={"input": 100, "output": 50, "total": 150},
        metadata={}
    )
    assert detector.detect(result_wrong, task)
    details = detector.get_failure_details(result_wrong, task)
    assert wrong_tool_name in details["wrong_tools"]
    print("  ✓ Correctly detects wrong tool selection")


def test_checkpoint():
    """Test checkpoint system."""
    print("\nTesting checkpoint system...")

    import tempfile
    import shutil

    # Create temp directory for checkpoints
    temp_dir = tempfile.mkdtemp()

    try:
        manager = CheckpointManager("test_experiment", checkpoint_dir=temp_dir)

        assert manager.get_completed_count() == 0
        assert manager.get_cumulative_cost() == 0.0

        # Mark task as completed
        manager.mark_task_completed("task_1", {"result": "success"}, 0.05)
        assert manager.get_completed_count() == 1
        assert manager.get_cumulative_cost() == 0.05
        assert manager.is_task_completed("task_1")
        assert not manager.is_task_completed("task_2")

        # Test persistence
        manager2 = CheckpointManager("test_experiment", checkpoint_dir=temp_dir)
        assert manager2.get_completed_count() == 1
        assert manager2.get_cumulative_cost() == 0.05

        print("  ✓ Checkpoint save/load works")
        print("  ✓ Tracks completed tasks and cost")

    finally:
        shutil.rmtree(temp_dir)


def test_cost_tracker():
    """Test cost tracking and budget enforcement."""
    print("\nTesting cost tracker...")

    tracker = CostTracker(max_budget_usd=10.0)

    # Add some usage
    cost1 = tracker.add_usage("claude-3-5-sonnet-20241022", input_tokens=1000, output_tokens=500)
    assert cost1 > 0
    assert tracker.check_budget()

    print(f"  ✓ Cost calculation works: ${cost1:.4f} for 1000 in + 500 out tokens")

    # Test budget exceeded
    cost2 = tracker.add_usage("claude-3-5-sonnet-20241022", input_tokens=10_000_000, output_tokens=1_000_000)
    assert not tracker.check_budget()  # Should exceed $10 budget

    print(f"  ✓ Budget enforcement works (used ${tracker.get_cumulative_cost():.2f} / $10.00)")

    # Test estimation
    estimated = tracker.estimate_cost("claude-3-5-sonnet-20241022", 1000, 500)
    assert abs(estimated - cost1) < 0.0001  # Should match actual cost

    print("  ✓ Cost estimation works")


def main():
    """Run all tests."""
    print("=" * 60)
    print("Infrastructure Validation Tests")
    print("=" * 60)

    try:
        test_task_generation()
        test_detector()
        test_checkpoint()
        test_cost_tracker()

        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED")
        print("=" * 60)
        print("\nInfrastructure is ready for pilot experiments!")

    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
