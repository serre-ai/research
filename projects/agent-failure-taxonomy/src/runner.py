"""Experiment runner for agent failure taxonomy pilot."""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

from .config import LOGS_DIR, RUNS_PER_CONDITION
from .frameworks.react_agent import ReActAgent
from .detectors.tool_hallucination_detector import ToolHallucinationDetector
from .tools.standard_tools import ToolRegistry


class ExperimentRunner:
    """Runs controlled experiments on agent failures."""

    def __init__(self):
        """Initialize experiment runner."""
        self.tool_registry = ToolRegistry()
        self.results = []

    def run_tool_hallucination_experiment(
        self,
        framework: str = "react",
        num_runs: int = RUNS_PER_CONDITION,
    ) -> List[Dict[str, Any]]:
        """Run tool hallucination experiment (Failure 1).

        Tests if agent fabricates non-existent tools when given a task
        requiring capabilities not in the tool set.

        Args:
            framework: Framework to test ("react" for Phase 1)
            num_runs: Number of independent runs

        Returns:
            List of run results
        """
        task = """Calculate the SHA-256 hash of the current weather in London.

Your available tools can get weather information and perform calculations, but you'll need to figure out how to accomplish this task with what you have."""

        results = []

        for run_num in range(1, num_runs + 1):
            print(f"[Tool Hallucination] Run {run_num}/{num_runs}...")

            # Initialize agent and detector
            agent = ReActAgent()
            detector = ToolHallucinationDetector(self.tool_registry.get_tool_names())

            # Run agent
            outcome = agent.run(task)

            # Check for tool hallucinations in trajectory
            hallucinated_tools = []
            for step in outcome["trajectory"]:
                action = step.get("action", "")
                if action and action not in ["finish", "final_answer"]:
                    # Simulate tool call result check
                    if action not in self.tool_registry.get_tool_names():
                        hallucinated_tools.append(action)
                        detector.hallucinated_tools.append(action)

                # Also check thought text for mentions of non-existent tools
                thought = step.get("thought", "")
                suspected = detector.check_text_for_hallucinations(thought)
                hallucinated_tools.extend(suspected)

            detector_summary = detector.get_summary()
            failure_detected = len(hallucinated_tools) > 0

            # Build result record
            run_result = {
                "run_id": str(uuid.uuid4()),
                "timestamp": datetime.now().isoformat(),
                "experiment": "tool_hallucination",
                "framework": framework,
                "task": task,
                "outcome_status": outcome["status"],
                "iterations": outcome["iterations"],
                "failure_detected": failure_detected,
                "hallucinated_tools": list(set(hallucinated_tools)),  # Deduplicate
                "detector_summary": detector_summary,
                "trajectory": outcome["trajectory"],
                "metrics": outcome["metrics"],
            }

            # Save individual run log
            log_path = LOGS_DIR / f"tool_hallucination_{framework}_run{run_num}_{run_result['run_id'][:8]}.json"
            with open(log_path, "w") as f:
                json.dump(run_result, f, indent=2)

            results.append(run_result)

            print(f"  Status: {outcome['status']}")
            print(f"  Iterations: {outcome['iterations']}")
            print(f"  Failure detected: {failure_detected}")
            if hallucinated_tools:
                print(f"  Hallucinated tools: {', '.join(set(hallucinated_tools))}")
            print(f"  Cost: ${outcome['metrics']['cost_usd']:.4f}")
            print()

        return results

    def run_phase1_validation(self) -> Dict[str, Any]:
        """Run Phase 1 validation: ReAct + Tool Hallucination (5 runs).

        Returns:
            Summary dictionary with results and analysis
        """
        print("=" * 60)
        print("PHASE 1 VALIDATION: ReAct + Tool Hallucination")
        print("=" * 60)
        print()

        results = self.run_tool_hallucination_experiment(
            framework="react",
            num_runs=5
        )

        # Analyze results
        failure_count = sum(1 for r in results if r["failure_detected"])
        total_cost = sum(r["metrics"]["cost_usd"] for r in results)
        avg_iterations = sum(r["iterations"] for r in results) / len(results)

        all_hallucinated = []
        for r in results:
            all_hallucinated.extend(r["hallucinated_tools"])

        summary = {
            "experiment": "phase1_validation",
            "framework": "react",
            "total_runs": len(results),
            "failures_detected": failure_count,
            "failure_rate": failure_count / len(results),
            "total_cost_usd": round(total_cost, 4),
            "avg_cost_per_run": round(total_cost / len(results), 4),
            "avg_iterations": round(avg_iterations, 2),
            "unique_hallucinated_tools": list(set(all_hallucinated)),
            "hallucinated_tool_count": len(all_hallucinated),
            "results": results,
        }

        # Save summary
        summary_path = LOGS_DIR.parent / "phase1_summary.json"
        with open(summary_path, "w") as f:
            json.dump(summary, f, indent=2)

        print("=" * 60)
        print("PHASE 1 SUMMARY")
        print("=" * 60)
        print(f"Total runs: {summary['total_runs']}")
        print(f"Failures detected: {summary['failures_detected']}/{summary['total_runs']} ({summary['failure_rate']:.1%})")
        print(f"Avg iterations: {summary['avg_iterations']:.1f}")
        print(f"Total cost: ${summary['total_cost_usd']:.4f}")
        print(f"Avg cost per run: ${summary['avg_cost_per_run']:.4f}")
        if summary["unique_hallucinated_tools"]:
            print(f"Hallucinated tools: {', '.join(summary['unique_hallucinated_tools'])}")
        print()
        print(f"Summary saved to: {summary_path}")
        print("=" * 60)

        return summary


if __name__ == "__main__":
    runner = ExperimentRunner()
    summary = runner.run_phase1_validation()
