"""
Structured logging for experiment runs.

Logs each agent run with full trace, failure detection, and cost tracking.
Supports both individual run logs and aggregated experiment summaries.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from dataclasses import asdict

from ..frameworks.base import AgentResult
from ..tasks.base import Task


class ExperimentLogger:
    """
    Logger for experiment runs with structured output.

    Logs are organized:
    - experiments/runs/{failure_type}/{framework}/{run_id}.json (individual runs)
    - experiments/results/{failure_type}/summary.json (aggregated)
    """

    def __init__(
        self,
        experiment_name: str,
        base_dir: str = "experiments"
    ):
        """
        Initialize logger.

        Args:
            experiment_name: Name of experiment (e.g., 'tool_fabrication')
            base_dir: Base directory for experiments
        """
        self.experiment_name = experiment_name
        self.base_dir = Path(base_dir)

        # Create directory structure
        self.runs_dir = self.base_dir / "runs" / experiment_name
        self.results_dir = self.base_dir / "results" / experiment_name

        self.runs_dir.mkdir(parents=True, exist_ok=True)
        self.results_dir.mkdir(parents=True, exist_ok=True)

        # Track all runs for summary
        self.all_runs: List[Dict[str, Any]] = []
        self.total_cost: float = 0.0

    def log_run(
        self,
        run_id: str,
        framework: str,
        model: str,
        task: Task,
        result: AgentResult,
        failure_detected: bool
    ) -> None:
        """
        Log a single agent run.

        Args:
            run_id: Unique run identifier
            framework: Framework name (e.g., 'langgraph-react')
            model: Model name (e.g., 'gpt-4o')
            task: Task instance
            result: Agent execution result
            failure_detected: Whether target failure was detected
        """
        log_entry = {
            "run_id": run_id,
            "timestamp": datetime.now().isoformat(),
            "experiment": self.experiment_name,
            "framework": framework,
            "model": model,

            # Task details
            "task_id": task.task_id,
            "instance_id": task.instance_id,
            "instruction": task.instruction,
            "tool_count": len(task.tools),
            "tools_available": [t["name"] for t in task.tools],

            # Result
            "success": result.success,
            "final_answer": result.final_answer,
            "error": result.error,

            # Metrics
            "steps": result.steps,
            "tokens_input": result.tokens_input,
            "tokens_output": result.tokens_output,
            "cost_usd": result.cost_usd,
            "duration_seconds": result.duration_seconds,

            # Failure detection
            "failure_detected": failure_detected,
            "tool_fabrication_detected": result.tool_fabrication_detected,
            "fabricated_tools": result.fabricated_tools,
            "infinite_loop_detected": result.infinite_loop_detected,
            "loop_start_step": result.loop_start_step,
            "false_completion_detected": result.false_completion_detected,

            # Trace (can be large)
            "trace": [
                {
                    "step": t.step,
                    "thought": t.thought,
                    "action": t.action,
                    "action_input": t.action_input,
                    "observation": t.observation,
                }
                for t in result.trace
            ],

            # Ground truth
            "ground_truth": task.ground_truth_answer,
            "expected_tools": task.expected_tool_sequence,

            # Task parameters
            "task_parameters": task.parameters,
        }

        # Save individual run
        run_file = self.runs_dir / framework / f"{run_id}.json"
        run_file.parent.mkdir(parents=True, exist_ok=True)

        with open(run_file, 'w') as f:
            json.dump(log_entry, f, indent=2)

        # Add to summary tracking
        self.all_runs.append(log_entry)
        self.total_cost += result.cost_usd

    def save_summary(self) -> None:
        """
        Save aggregated experiment summary.

        Computes statistics across all runs:
        - Failure rates by framework, model, condition
        - Average costs, tokens, duration
        - Success rates
        """
        if not self.all_runs:
            return

        summary = {
            "experiment": self.experiment_name,
            "timestamp": datetime.now().isoformat(),
            "total_runs": len(self.all_runs),
            "total_cost_usd": self.total_cost,

            # Aggregate metrics
            "metrics": self._compute_aggregate_metrics(),

            # Failure rates
            "failure_rates": self._compute_failure_rates(),

            # By framework
            "by_framework": self._group_by("framework"),

            # By model
            "by_model": self._group_by("model"),

            # By tool count (if applicable)
            "by_tool_count": self._group_by_tool_count(),

            # All runs (compact version)
            "runs": [
                {
                    "run_id": r["run_id"],
                    "framework": r["framework"],
                    "model": r["model"],
                    "instance_id": r["instance_id"],
                    "failure_detected": r["failure_detected"],
                    "cost_usd": r["cost_usd"],
                }
                for r in self.all_runs
            ]
        }

        summary_file = self.results_dir / "summary.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)

        print(f"\n✓ Saved summary to {summary_file}")
        print(f"  Total runs: {len(self.all_runs)}")
        print(f"  Total cost: ${self.total_cost:.2f}")
        print(f"  Failure rate: {summary['failure_rates']['overall']:.1%}")

    def _compute_aggregate_metrics(self) -> Dict[str, float]:
        """Compute aggregate metrics across all runs."""
        if not self.all_runs:
            return {}

        return {
            "avg_cost_usd": sum(r["cost_usd"] for r in self.all_runs) / len(self.all_runs),
            "avg_steps": sum(r["steps"] for r in self.all_runs) / len(self.all_runs),
            "avg_tokens_input": sum(r["tokens_input"] for r in self.all_runs) / len(self.all_runs),
            "avg_tokens_output": sum(r["tokens_output"] for r in self.all_runs) / len(self.all_runs),
            "avg_duration_seconds": sum(r["duration_seconds"] for r in self.all_runs) / len(self.all_runs),
            "success_rate": sum(1 for r in self.all_runs if r["success"]) / len(self.all_runs),
        }

    def _compute_failure_rates(self) -> Dict[str, float]:
        """Compute failure detection rates."""
        if not self.all_runs:
            return {}

        total = len(self.all_runs)

        return {
            "overall": sum(1 for r in self.all_runs if r["failure_detected"]) / total,
            "tool_fabrication": sum(1 for r in self.all_runs if r["tool_fabrication_detected"]) / total,
            "infinite_loop": sum(1 for r in self.all_runs if r["infinite_loop_detected"]) / total,
            "false_completion": sum(1 for r in self.all_runs if r["false_completion_detected"]) / total,
        }

    def _group_by(self, key: str) -> Dict[str, Any]:
        """Group runs by a key and compute stats."""
        groups = {}

        for run in self.all_runs:
            group_name = run[key]
            if group_name not in groups:
                groups[group_name] = []
            groups[group_name].append(run)

        # Compute stats per group
        result = {}
        for group_name, runs in groups.items():
            result[group_name] = {
                "count": len(runs),
                "failure_rate": sum(1 for r in runs if r["failure_detected"]) / len(runs),
                "avg_cost": sum(r["cost_usd"] for r in runs) / len(runs),
                "success_rate": sum(1 for r in runs if r["success"]) / len(runs),
            }

        return result

    def _group_by_tool_count(self) -> Dict[int, Any]:
        """Group by tool count (if applicable)."""
        groups = {}

        for run in self.all_runs:
            tool_count = run["tool_count"]
            if tool_count not in groups:
                groups[tool_count] = []
            groups[tool_count].append(run)

        # Compute stats per tool count
        result = {}
        for tool_count, runs in groups.items():
            result[tool_count] = {
                "count": len(runs),
                "failure_rate": sum(1 for r in runs if r["failure_detected"]) / len(runs),
                "fabrication_rate": sum(1 for r in runs if r["tool_fabrication_detected"]) / len(runs),
                "avg_fabricated_tools": sum(len(r["fabricated_tools"]) for r in runs) / len(runs),
            }

        return result
