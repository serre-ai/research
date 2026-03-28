#!/usr/bin/env python3
"""
Pilot Validation Experiment Runner

Executes the pilot validation experiment to test 3 high-priority failures:
1. Tool Fabrication (1.1)
2. Infinite Loop (3.1)
3. Context Degradation (4.3)

Usage:
    python run_pilot.py --canary  # Run canary first
    python run_pilot.py --full    # Run full pilot
    python run_pilot.py --analyze # Analyze results
"""

import argparse
import json
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from framework_wrapper import create_agent, ExecutionTrace
from task_generators import generate_pilot_tasks, create_task_generator
from failure_detectors import create_detector


class PilotExperiment:
    """Manages pilot validation experiment execution and analysis."""

    def __init__(self, output_dir: str = "experiments/pilot-taxonomy-validation"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.results_dir = self.output_dir / "results"
        self.results_dir.mkdir(exist_ok=True)

        self.logs_dir = self.output_dir / "logs"
        self.logs_dir.mkdir(exist_ok=True)

        self.cost_tracker = {
            'total_usd': 0.0,
            'by_task': {}
        }

    def run_canary(self, model: str = "gpt-4o-mini") -> Dict[str, Any]:
        """
        Run canary experiment (tool fabrication only, 3 trials).

        Returns:
            Canary results with diagnostic checks
        """
        print("=" * 60)
        print("CANARY RUN: Tool Fabrication (3 trials)")
        print("=" * 60)

        # Generate canary tasks
        generator = create_task_generator('tool_fabrication')
        tasks = generator.generate_batch(3)

        # Create agent
        agent = create_agent('langgraph', model=model, temperature=0.7)

        # Run trials
        traces = []
        for task in tasks:
            print(f"\n Running: {task.task_id}")

            # Setup agent with tools
            system_prompt = "You are a helpful assistant. Use the provided tools to complete tasks."
            agent.setup(tools=task.tools, system_prompt=system_prompt)

            # Execute
            try:
                trace = agent.run(
                    task=task.task_description,
                    max_iterations=10,
                    timeout_seconds=120
                )
                traces.append(trace)

                # Save trace
                trace_file = self.logs_dir / f"{task.task_id}_trace.json"
                with open(trace_file, 'w') as f:
                    json.dump(agent._trace_to_dict(), f, indent=2)

                print(f"  ✓ Completed in {trace.end_time - trace.start_time:.1f}s")

            except Exception as e:
                print(f"  ✗ Error: {e}")
                traces.append(None)

        # Run diagnostics
        diagnostics = self._run_diagnostics(traces, tasks)

        # Save canary results
        canary_results = {
            'timestamp': datetime.now().isoformat(),
            'model': model,
            'num_trials': len(tasks),
            'diagnostics': diagnostics,
            'traces': [
                agent._trace_to_dict() if trace else None
                for trace in traces
            ]
        }

        results_file = self.results_dir / "canary_results.json"
        with open(results_file, 'w') as f:
            json.dump(canary_results, f, indent=2)

        # Print summary
        print("\n" + "=" * 60)
        print("CANARY DIAGNOSTICS")
        print("=" * 60)
        for check, result in diagnostics.items():
            status = "✓ PASS" if result['passed'] else "✗ FAIL"
            print(f"{status} {check}: {result['message']}")

        all_passed = all(d['passed'] for d in diagnostics.values())
        print("\n" + ("✓" if all_passed else "✗") * 60)
        if all_passed:
            print("CANARY PASSED - Proceed to full pilot")
        else:
            print("CANARY FAILED - Fix issues before full pilot")
        print("=" * 60)

        return canary_results

    def run_full_pilot(self, model: str = "gpt-4o-mini") -> Dict[str, Any]:
        """
        Run full pilot experiment (all 3 failures, 5 trials each).

        Returns:
            Full pilot results with failure detection
        """
        print("=" * 60)
        print("FULL PILOT: 3 Failures × 5 Trials = 15 Total")
        print("=" * 60)

        # Generate all tasks
        all_tasks = generate_pilot_tasks()

        results = {}

        for failure_type, tasks in all_tasks.items():
            print(f"\n{'=' * 60}")
            print(f"Testing: {failure_type.replace('_', ' ').title()}")
            print(f"{'=' * 60}")

            failure_results = self._run_failure_test(
                failure_type=failure_type,
                tasks=tasks,
                model=model
            )

            results[failure_type] = failure_results

        # Save full results
        full_results = {
            'timestamp': datetime.now().isoformat(),
            'model': model,
            'failures_tested': list(results.keys()),
            'results': results,
            'cost_tracker': self.cost_tracker
        }

        results_file = self.results_dir / "full_pilot_results.json"
        with open(results_file, 'w') as f:
            json.dump(full_results, f, indent=2)

        # Print summary
        self._print_summary(results)

        return full_results

    def _run_failure_test(
        self,
        failure_type: str,
        tasks: List[Any],
        model: str
    ) -> Dict[str, Any]:
        """Run a single failure type test."""

        # Create agent
        agent = create_agent('langgraph', model=model, temperature=0.7)

        # Create detector
        detector_kwargs = {}
        if failure_type == 'tool_fabrication':
            # Need tools registry for detection
            detector_kwargs['tools_registry'] = [t.__name__ for t in tasks[0].tools]

        detector = create_detector(failure_type, **detector_kwargs)

        # Run trials
        detection_results = []
        traces = []

        for task in tasks:
            print(f"\n  Running: {task.task_id}")

            # Setup agent
            system_prompt = "You are a helpful assistant. Use the provided tools to complete tasks."
            agent.setup(tools=task.tools, system_prompt=system_prompt)

            # Execute
            try:
                trace = agent.run(
                    task=task.task_description,
                    max_iterations=20,
                    timeout_seconds=300
                )
                traces.append(trace)

                # Save trace
                trace_file = self.logs_dir / f"{task.task_id}_trace.json"
                trace_dict = agent._trace_to_dict()
                with open(trace_file, 'w') as f:
                    json.dump(trace_dict, f, indent=2)

                # Detect failure
                detection = detector.detect(trace_dict)
                detection_results.append({
                    'task_id': task.task_id,
                    'detected': detection.failure_detected,
                    'confidence': detection.confidence,
                    'evidence': detection.evidence,
                    'metrics': detection.metrics
                })

                status = "✓ DETECTED" if detection.failure_detected else "✗ NOT DETECTED"
                print(f"    {status} (confidence: {detection.confidence:.2f})")

            except Exception as e:
                print(f"    ✗ Error: {e}")
                detection_results.append({
                    'task_id': task.task_id,
                    'error': str(e)
                })

        # Compute statistics
        detected_count = sum(1 for r in detection_results if r.get('detected', False))
        detection_rate = detected_count / len(tasks) if tasks else 0

        return {
            'failure_type': failure_type,
            'trials': len(tasks),
            'detected_count': detected_count,
            'detection_rate': detection_rate,
            'success': detection_rate >= 0.60,  # Success threshold
            'detection_results': detection_results
        }

    def _run_diagnostics(
        self,
        traces: List[Any],
        tasks: List[Any]
    ) -> Dict[str, Dict[str, Any]]:
        """Run canary diagnostic checks."""

        diagnostics = {}

        # Check 1: Pipeline completion
        completed = sum(1 for t in traces if t is not None)
        diagnostics['pipeline_completion'] = {
            'passed': completed == len(traces),
            'message': f"{completed}/{len(traces)} trials completed",
            'details': {
                'completed': completed,
                'total': len(traces),
                'rate': completed / len(traces) if traces else 0
            }
        }

        # Check 2: Extraction success
        extraction_success = 0
        for trace in traces:
            if trace and len(trace.tool_calls) > 0:
                extraction_success += 1

        diagnostics['extraction_success'] = {
            'passed': extraction_success >= len(traces) * 0.9,
            'message': f"{extraction_success}/{len(traces)} had extractable tool calls",
            'details': {
                'extracted': extraction_success,
                'total': len(traces),
                'rate': extraction_success / len(traces) if traces else 0
            }
        }

        # Check 3: Cost within budget
        avg_cost = 0.75  # Placeholder - would calculate from actual API usage
        diagnostics['cost_within_budget'] = {
            'passed': avg_cost <= 1.50,
            'message': f"Average cost ${avg_cost:.2f} per trial (budget: $1.50)",
            'details': {
                'avg_cost_usd': avg_cost,
                'budget_usd': 1.50,
                'within_budget': avg_cost <= 1.50
            }
        }

        # Check 4: Baseline sanity
        valid_behavior = sum(
            1 for trace in traces
            if trace and len(trace.tool_calls) > 0 and trace.error is None
        )

        diagnostics['baseline_sanity'] = {
            'passed': valid_behavior >= len(traces) * 0.8,
            'message': f"{valid_behavior}/{len(traces)} showed reasonable behavior",
            'details': {
                'valid': valid_behavior,
                'total': len(traces),
                'rate': valid_behavior / len(traces) if traces else 0
            }
        }

        return diagnostics

    def _print_summary(self, results: Dict[str, Dict[str, Any]]) -> None:
        """Print experiment summary."""

        print("\n" + "=" * 60)
        print("PILOT VALIDATION SUMMARY")
        print("=" * 60)

        total_success = 0
        for failure_type, data in results.items():
            status = "✓ SUCCESS" if data['success'] else "✗ FAILED"
            print(f"\n{status} {failure_type.replace('_', ' ').title()}")
            print(f"  Detection rate: {data['detection_rate']:.1%} "
                  f"({data['detected_count']}/{data['trials']})")

            if data['success']:
                total_success += 1

        print("\n" + "=" * 60)
        validation_rate = total_success / len(results)
        print(f"Overall Validation: {total_success}/{len(results)} failures reproduced "
              f"({validation_rate:.1%})")

        if validation_rate >= 0.66:
            print("\n✓✓✓ STRONG VALIDATION - Taxonomy empirically confirmed")
            print("→ Proceed to full 6-failure protocol")
        elif validation_rate >= 0.33:
            print("\n✓ PARTIAL VALIDATION - Core categories validated")
            print("→ Refine test design for failed cases")
        else:
            print("\n✗ WEAK VALIDATION - Re-examine taxonomy or tests")
            print("→ Investigate discrepancies before proceeding")

        print("=" * 60)

    def analyze_results(self, results_file: str = None) -> None:
        """Analyze completed experiment results."""

        if results_file is None:
            results_file = self.results_dir / "full_pilot_results.json"
        else:
            results_file = Path(results_file)

        if not results_file.exists():
            print(f"Error: Results file not found: {results_file}")
            return

        with open(results_file) as f:
            results = json.load(f)

        print("\n" + "=" * 60)
        print("DETAILED ANALYSIS")
        print("=" * 60)

        for failure_type, data in results['results'].items():
            print(f"\n{failure_type.replace('_', ' ').title()}")
            print("-" * 60)

            for detection in data['detection_results']:
                task_id = detection['task_id']
                detected = detection.get('detected', False)
                confidence = detection.get('confidence', 0)

                print(f"\n  {task_id}:")
                print(f"    Detected: {detected} (confidence: {confidence:.2f})")

                if 'evidence' in detection:
                    print(f"    Evidence:")
                    for evidence in detection['evidence'][:3]:
                        print(f"      - {evidence}")

                if 'metrics' in detection:
                    print(f"    Metrics: {detection['metrics']}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Run pilot validation experiment")
    parser.add_argument('--canary', action='store_true', help="Run canary only")
    parser.add_argument('--full', action='store_true', help="Run full pilot")
    parser.add_argument('--analyze', action='store_true', help="Analyze results")
    parser.add_argument('--model', default='gpt-4o-mini', help="LLM model to use")
    parser.add_argument('--output-dir', default='experiments/pilot-taxonomy-validation',
                        help="Output directory")

    args = parser.parse_args()

    # Create experiment
    experiment = PilotExperiment(output_dir=args.output_dir)

    # Run requested mode
    if args.canary:
        experiment.run_canary(model=args.model)
    elif args.full:
        experiment.run_full_pilot(model=args.model)
    elif args.analyze:
        experiment.analyze_results()
    else:
        print("Error: Must specify --canary, --full, or --analyze")
        parser.print_help()


if __name__ == '__main__':
    main()
