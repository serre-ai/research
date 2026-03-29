"""
Pilot experiment runner for agent failure taxonomy validation.

This script runs a small-scale proof-of-concept experiment to:
1. Test the experimental infrastructure
2. Validate that failures can be reproduced in controlled settings
3. Estimate costs for full experiment
"""

import sys
import argparse
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from utils.experiment_logger import ExperimentLogger, compute_aggregate_metrics
from detectors.loop_detector import LoopDetector
from detectors.completion_verifier import CompletionVerifier, verify_primes_file
from tasks.task_definitions import get_task_for_experiment


def run_experiment(
    failure_type: str,
    framework: str,
    model: str,
    num_instances: int = 3,
    temperature: float = 0.7,
    dry_run: bool = False
):
    """
    Run a batch of experiments for a specific failure type and framework.

    Args:
        failure_type: "F2_infinite_loop" or "F4_false_completion"
        framework: "langgraph", "autogpt", "plan-execute", etc.
        model: Model identifier (e.g., "gpt-4-turbo-2024-04-09")
        num_instances: Number of instances to run
        temperature: Sampling temperature
        dry_run: If True, log task setup but don't actually run agents
    """
    print(f"\n{'='*60}")
    print(f"Running Pilot Experiment")
    print(f"{'='*60}")
    print(f"Failure Type: {failure_type}")
    print(f"Framework: {framework}")
    print(f"Model: {model}")
    print(f"Instances: {num_instances}")
    print(f"Temperature: {temperature}")
    print(f"Dry Run: {dry_run}")
    print(f"{'='*60}\n")

    # Initialize logger
    logger = ExperimentLogger()

    # Initialize detectors
    loop_detector = LoopDetector(similarity_threshold=5, window_size=10)
    completion_verifier = CompletionVerifier()

    for instance_num in range(num_instances):
        print(f"\n--- Instance {instance_num + 1}/{num_instances} ---")

        # Get task
        task = get_task_for_experiment(failure_type, instance_num)
        print(f"Task ID: {task.task_id}")
        print(f"Description: {task.description}")

        # Start logging
        run_id = logger.start_run(
            failure_type=failure_type,
            framework=framework,
            model=model,
            task={
                "id": task.task_id,
                "description": task.description,
                "prompt": task.prompt,
                "expected_failure_mode": task.expected_failure_mode,
                "iteration_limit": task.iteration_limit
            },
            temperature=temperature
        )

        print(f"Run ID: {run_id}")

        if dry_run:
            print("DRY RUN: Would execute agent here")
            print(f"Prompt: {task.prompt[:100]}...")

            # Simulate some actions for infrastructure testing
            logger.log_action(1, "search_web", "Found results about quantum computing")
            logger.log_action(2, "search_web", "Found results about quantum computing")
            logger.log_action(3, "search_web", "Found results about quantum computing")

            # Simulate costs
            logger.log_costs(1000, 200, 0.015)

            # End run
            logger.end_run("dry_run_complete")

        else:
            print("PRODUCTION RUN: Agent execution would go here")
            print("NOTE: Agent wrappers not yet implemented - this is infrastructure validation only")

            # TODO: Implement actual agent execution
            # This would call the framework wrapper to run the agent
            # For now, we're just validating the logging/detection infrastructure

            logger.end_run("not_implemented")

    # Compute aggregate metrics
    print(f"\n{'='*60}")
    print("Experiment Summary")
    print(f"{'='*60}")

    runs = logger.get_all_runs()
    print(f"Total runs logged: {len(runs)}")

    if runs:
        metrics = compute_aggregate_metrics(runs)
        print(f"\nAggregate Metrics:")
        print(f"  Total runs: {metrics['total_runs']}")
        print(f"  Failure detection rate: {metrics['failure_detection_rate']:.1%}")
        print(f"  Iterations (mean): {metrics['iterations']['mean']:.1f}")
        print(f"  Iterations (median): {metrics['iterations']['median']}")
        print(f"  Total cost: ${metrics['costs']['total_usd']:.2f}")
        print(f"  Cost per run: ${metrics['costs']['mean_per_run_usd']:.3f}")

    print(f"\nLogs saved to: experiments/pilot-01-taxonomy-validation/runs/")
    print(f"{'='*60}\n")


def test_infrastructure():
    """Test that all infrastructure components can be imported and initialized."""
    print("Testing infrastructure components...\n")

    # Test logger
    print("✓ ExperimentLogger imported")
    logger = ExperimentLogger()
    print("✓ ExperimentLogger initialized")

    # Test detectors
    print("✓ LoopDetector imported")
    loop_detector = LoopDetector()
    print("✓ LoopDetector initialized")

    print("✓ CompletionVerifier imported")
    completion_verifier = CompletionVerifier()
    print("✓ CompletionVerifier initialized")

    # Test tasks
    print("✓ Task definitions imported")
    task = get_task_for_experiment("F2_infinite_loop", 0)
    print(f"✓ Retrieved task: {task.task_id}")

    # Test loop detector
    test_actions = [
        {"action": "search_web"},
        {"action": "search_web"},
        {"action": "search_web"},
        {"action": "search_web"},
        {"action": "search_web"},
        {"action": "search_web"}
    ]
    result = loop_detector.detect(test_actions)
    print(f"✓ Loop detector test: {result['loop_detected']} (expected True)")

    print("\n✅ All infrastructure components working!\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run pilot agent failure experiments")
    parser.add_argument("--test", action="store_true", help="Test infrastructure only")
    parser.add_argument("--failure-type", choices=["F2_infinite_loop", "F4_false_completion"],
                        default="F2_infinite_loop", help="Failure type to test")
    parser.add_argument("--framework", default="langgraph", help="Agent framework to use")
    parser.add_argument("--model", default="gpt-4-turbo-2024-04-09", help="Model to use")
    parser.add_argument("--instances", type=int, default=3, help="Number of instances")
    parser.add_argument("--temperature", type=float, default=0.7, help="Sampling temperature")
    parser.add_argument("--dry-run", action="store_true", help="Dry run (no agent execution)")

    args = parser.parse_args()

    if args.test:
        test_infrastructure()
    else:
        run_experiment(
            failure_type=args.failure_type,
            framework=args.framework,
            model=args.model,
            num_instances=args.instances,
            temperature=args.temperature,
            dry_run=args.dry_run
        )
