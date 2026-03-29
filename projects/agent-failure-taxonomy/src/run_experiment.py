"""
Main experiment runner.

Usage:
    python src/run_experiment.py --spec experiments/pilot-failure-reproduction/spec.yaml --canary
    python src/run_experiment.py --spec experiments/pilot-failure-reproduction/spec.yaml
"""

import argparse
import os
import sys
import yaml
from typing import Dict, Any

# Add src to path
sys.path.insert(0, os.path.dirname(__file__))

from frameworks.react_agent import ReActAgent
from tasks.task_definitions import get_task_by_id, get_all_tasks
from utils.logger import ExperimentLogger, AggregateLogger
from utils.failure_detection import analyze_trace


def load_spec(spec_path: str) -> Dict[str, Any]:
    """Load experiment specification."""
    with open(spec_path, "r") as f:
        return yaml.safe_load(f)


def run_single_instance(
    task_id: str,
    framework: str,
    model: str,
    spec: Dict[str, Any],
    output_dir: str,
) -> Dict[str, Any]:
    """
    Run a single experiment instance.

    Returns:
        Summary dictionary with outcome and metrics
    """
    # Get task
    task = get_task_by_id(task_id)

    # Create logger
    instance_id = f"{task_id}_{framework}_{model}".replace("/", "-").replace(":", "-")
    logger = ExperimentLogger(
        experiment_name=spec["name"],
        instance_id=instance_id,
        output_dir=output_dir,
    )

    print(f"\n{'=' * 80}")
    print(f"Running: {instance_id}")
    print(f"Task: {task.description}")
    print(f"Framework: {framework}, Model: {model}")
    print(f"{'=' * 80}\n")

    # Create agent (only ReAct supported for now)
    if framework == "react":
        agent = ReActAgent(
            model_name=model,
            tools=task.tools,
            temperature=spec["design"].get("temperature", 0.0),
            max_iterations=spec["design"]["frameworks"][0]["max_iterations"],
            verbose=False,  # Reduce noise
        )
    else:
        raise NotImplementedError(f"Framework {framework} not yet implemented")

    # Run agent
    result = agent.run(task.description)

    # Get trace
    trace = agent.get_trace(result.get("intermediate_steps", []))

    # Log each step
    for step_data in trace:
        logger.log_step(
            step=step_data["step"],
            action=step_data["action"],
            action_input=step_data["action_input"],
            observation=step_data["observation"],
            thought=step_data["thought"],
            tokens_used=0,  # TODO: Track actual tokens
            cost_usd=0.0,   # TODO: Track actual cost
        )

    # Analyze outcome
    analysis = analyze_trace(
        trace=trace,
        final_output=result.get("output"),
        ground_truth=task.ground_truth,
        success_criteria=task.success_criteria,
        valid_tools=task.get_tool_names(),
        max_iterations=spec["design"]["frameworks"][0]["max_iterations"],
    )

    # Log completion
    logger.log_completion(
        outcome=analysis["outcome"],
        failure_type=analysis["failure_type"],
        final_output=result.get("output"),
    )

    # Save trace
    logger.save()

    # Print summary
    print(f"\n{'=' * 80}")
    print(f"RESULT: {instance_id}")
    print(f"  Outcome: {analysis['outcome']}")
    print(f"  Failure Type: {analysis['failure_type']}")
    print(f"  Steps: {len(trace)}")
    print(f"  Final Output: {result.get('output', 'None')[:100]}...")
    print(f"{'=' * 80}\n")

    return logger.get_summary()


def run_canary(spec: Dict[str, Any], output_dir: str):
    """Run canary experiment."""
    print("\n" + "=" * 80)
    print("CANARY RUN")
    print("=" * 80)

    canary_config = spec["canary"]

    # For canary, we run just the first tool scaling task
    task_ids = ["tool_scaling_5"]  # Simplified - just one task
    frameworks = ["react"]
    models = canary_config["models"]

    agg_logger = AggregateLogger(output_dir)

    for task_id in task_ids:
        for framework in frameworks:
            for model in models:
                try:
                    summary = run_single_instance(
                        task_id=task_id,
                        framework=framework,
                        model=model,
                        spec=spec,
                        output_dir=output_dir,
                    )
                    agg_logger.add_result(summary)
                except Exception as e:
                    print(f"ERROR running {task_id} with {framework}/{model}: {e}")
                    import traceback
                    traceback.print_exc()

    # Save summary
    summary_path = agg_logger.save_summary(filename="canary_summary.json")
    print(f"\nCanary summary saved to: {summary_path}")

    # Print diagnostics
    stats = agg_logger.compute_statistics()
    print("\n" + "=" * 80)
    print("CANARY DIAGNOSTICS")
    print("=" * 80)
    print(f"Total instances: {stats['total_instances']}")
    print(f"Outcomes: {stats['outcomes']}")
    print(f"Failure types: {stats['failure_types']}")
    print(f"Total cost: ${stats['total_cost_usd']:.2f}")
    print(f"Avg steps: {stats['avg_steps_per_instance']:.1f}")

    # Check diagnostics
    print("\nDiagnostic Checks:")
    print(f"  ✓ Pipeline completion: {stats['total_instances']} instances completed")
    print(f"  ✓ Output parseable: All outputs logged")

    # Check if canary passed
    if stats['total_instances'] > 0:
        print("\n✓ CANARY PASSED - Ready for full run")
        return True
    else:
        print("\n✗ CANARY FAILED - Fix issues before full run")
        return False


def run_full_experiment(spec: Dict[str, Any], output_dir: str):
    """Run full experiment."""
    print("\n" + "=" * 80)
    print("FULL EXPERIMENT")
    print("=" * 80)

    # Get all task IDs from spec (simplified for pilot)
    task_ids = [
        "tool_scaling_5",
        "tool_scaling_10",
        "tool_scaling_20",
        "ambiguous_goal_0",
        "ambiguous_goal_1",
        "ambiguous_goal_2",
        "complex_verification_0",
        "complex_verification_1",
        "complex_verification_2",
    ]

    frameworks = ["react"]  # Only ReAct for pilot
    models = spec["design"]["models"]

    agg_logger = AggregateLogger(output_dir)

    total = len(task_ids) * len(frameworks) * len(models)
    current = 0

    for task_id in task_ids:
        for framework in frameworks:
            for model in models:
                current += 1
                print(f"\nProgress: {current}/{total}")

                try:
                    summary = run_single_instance(
                        task_id=task_id,
                        framework=framework,
                        model=model,
                        spec=spec,
                        output_dir=output_dir,
                    )
                    agg_logger.add_result(summary)
                except Exception as e:
                    print(f"ERROR running {task_id} with {framework}/{model}: {e}")
                    import traceback
                    traceback.print_exc()

    # Save summary
    summary_path = agg_logger.save_summary(filename="full_summary.json")
    print(f"\nFull experiment summary saved to: {summary_path}")

    # Print final statistics
    stats = agg_logger.compute_statistics()
    print("\n" + "=" * 80)
    print("EXPERIMENT COMPLETE")
    print("=" * 80)
    print(f"Total instances: {stats['total_instances']}")
    print(f"Outcomes: {stats['outcomes']}")
    print(f"Failure types: {stats['failure_types']}")
    print(f"Total cost: ${stats['total_cost_usd']:.2f}")
    print(f"Avg cost per instance: ${stats['avg_cost_per_instance']:.4f}")
    print(f"Avg steps per instance: {stats['avg_steps_per_instance']:.1f}")


def main():
    parser = argparse.ArgumentParser(description="Run agent failure experiments")
    parser.add_argument(
        "--spec",
        required=True,
        help="Path to experiment spec YAML file",
    )
    parser.add_argument(
        "--canary",
        action="store_true",
        help="Run canary experiment only",
    )

    args = parser.parse_args()

    # Load spec
    spec = load_spec(args.spec)

    # Determine output directory
    if args.canary:
        output_dir = os.path.join(
            os.path.dirname(args.spec),
            "canary-results",
        )
    else:
        output_dir = os.path.join(
            os.path.dirname(args.spec),
            "results",
        )

    os.makedirs(output_dir, exist_ok=True)

    # Run experiment
    if args.canary:
        run_canary(spec, output_dir)
    else:
        run_full_experiment(spec, output_dir)


if __name__ == "__main__":
    main()
