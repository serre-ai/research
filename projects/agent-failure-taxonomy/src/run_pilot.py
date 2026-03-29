"""Run pilot experiment: Tool Fabrication (F1).

Tests infrastructure before full experiment run.
"""

import os
import sys
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from tasks.tool_fabrication import ToolFabricationTask
from frameworks.react_agent import ReActAgent
from utils.logging import ExperimentLogger, extract_metrics


def run_pilot_f1(num_instances: int = 5, difficulty: str = "medium", output_dir: Path = None):
    """Run pilot for Tool Fabrication failure (F1).

    Args:
        num_instances: Number of instances to run
        difficulty: Task difficulty level
        output_dir: Where to save logs and results
    """
    if output_dir is None:
        output_dir = Path("projects/agent-failure-taxonomy/experiments/pilot/results/f1_tool_fabrication")

    output_dir.mkdir(parents=True, exist_ok=True)
    logs_dir = output_dir / "logs"
    logs_dir.mkdir(exist_ok=True)

    print(f"Running Tool Fabrication pilot: {num_instances} instances, difficulty={difficulty}")
    print(f"Output: {output_dir}")
    print(f"Mock mode: {os.getenv('AGENT_FAILURE_MOCK', '1')}")
    print()

    # Generate tasks
    task_gen = ToolFabricationTask(seed=42)
    results = []

    for i in range(num_instances):
        instance = task_gen.generate_instance(i, difficulty)
        instance_id = instance["instance_id"]

        print(f"[{i+1}/{num_instances}] Running {instance_id}...")
        print(f"  Tools available: {len(instance['available_tools'])}")
        print(f"  Required tools: {instance['required_tools']}")

        # Create logger
        logger = ExperimentLogger(logs_dir, instance_id)

        # Create agent
        agent = ReActAgent(
            tools=instance["available_tools"],
            max_iterations=instance["max_iterations"]
        )

        # Run task
        success, reason, answer = agent.run(instance["task_description"], logger)

        print(f"  Result: success={success}, reason={reason}")

        # Extract metrics
        log_file = logs_dir / f"{instance_id}.jsonl"
        metrics = extract_metrics(log_file)

        print(f"  Metrics: {metrics['total_tool_calls']} tool calls, {metrics['invalid_tool_calls']} fabricated")
        print()

        results.append({
            "instance": instance,
            "metrics": metrics
        })

    # Aggregate results
    summary = aggregate_results(results)

    # Save summary
    summary_file = output_dir / "summary.json"
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)

    print("="*60)
    print("PILOT SUMMARY:")
    print(f"  Total instances: {summary['total_instances']}")
    print(f"  Successful completions: {summary['successful_completions']}")
    print(f"  Tool fabrication detected: {summary['fabrication_detected']} ({summary['fabrication_rate']:.1%})")
    print(f"  Avg tool calls/instance: {summary['avg_tool_calls']:.1f}")
    print(f"  Avg fabricated calls/instance: {summary['avg_fabricated_calls']:.1f}")
    print(f"  Total cost: ${summary['total_cost_usd']:.4f}")
    print(f"  Summary saved to: {summary_file}")
    print("="*60)

    return summary


def aggregate_results(results: list) -> dict:
    """Aggregate metrics across instances."""
    total = len(results)

    if total == 0:
        return {"total_instances": 0}

    fabrication_detected = sum(1 for r in results if r["metrics"]["invalid_tool_calls"] > 0)
    total_tool_calls = sum(r["metrics"]["total_tool_calls"] for r in results)
    total_fabricated = sum(r["metrics"]["invalid_tool_calls"] for r in results)
    total_cost = sum(r["metrics"]["total_cost_usd"] for r in results)
    successful = sum(1 for r in results if r["metrics"]["success"])

    return {
        "total_instances": total,
        "successful_completions": successful,
        "completion_rate": successful / total,
        "fabrication_detected": fabrication_detected,
        "fabrication_rate": fabrication_detected / total,
        "total_tool_calls": total_tool_calls,
        "total_fabricated_calls": total_fabricated,
        "avg_tool_calls": total_tool_calls / total,
        "avg_fabricated_calls": total_fabricated / total,
        "total_cost_usd": total_cost,
        "avg_cost_per_instance": total_cost / total
    }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run Tool Fabrication pilot")
    parser.add_argument("--instances", type=int, default=5, help="Number of instances")
    parser.add_argument("--difficulty", type=str, default="medium", choices=["easy", "medium", "hard"])
    parser.add_argument("--output", type=str, default=None, help="Output directory")

    args = parser.parse_args()

    output = Path(args.output) if args.output else None
    run_pilot_f1(args.instances, args.difficulty, output)
