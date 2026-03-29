"""
Structured logging for agent experiments.

Logs all experimental runs in JSON format with:
- Run metadata (ID, failure type, framework, model)
- Task specification
- Execution trace (actions, observations, timing)
- Failure detection results
- Metrics and costs
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


class ExperimentLogger:
    """Structured logger for agent experiment runs."""

    def __init__(self, output_dir: str = "experiments/pilot-01-taxonomy-validation/runs"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.current_run: Optional[Dict[str, Any]] = None

    def start_run(
        self,
        failure_type: str,
        framework: str,
        model: str,
        task: Dict[str, Any],
        temperature: float = 0.7
    ) -> str:
        """Start a new experimental run and return the run ID."""
        run_id = str(uuid.uuid4())

        self.current_run = {
            "run_id": run_id,
            "failure_type": failure_type,
            "framework": framework,
            "model": model,
            "temperature": temperature,
            "task": task,
            "execution": {
                "start_time": datetime.utcnow().isoformat() + "Z",
                "end_time": None,
                "iterations": 0,
                "actions": [],
                "termination_reason": None
            },
            "failure_detection": {},
            "metrics": {},
            "costs": {
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_cost_usd": 0.0
            }
        }

        return run_id

    def log_action(
        self,
        step: int,
        action: str,
        observation: Optional[str] = None,
        reasoning: Optional[str] = None
    ):
        """Log a single agent action-observation pair."""
        if self.current_run is None:
            raise ValueError("No active run. Call start_run() first.")

        action_data = {
            "step": step,
            "action": action,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

        if observation is not None:
            action_data["observation"] = observation
        if reasoning is not None:
            action_data["reasoning"] = reasoning

        self.current_run["execution"]["actions"].append(action_data)
        self.current_run["execution"]["iterations"] = step

    def log_failure_detection(self, detection_results: Dict[str, Any]):
        """Log failure detection results."""
        if self.current_run is None:
            raise ValueError("No active run. Call start_run() first.")

        self.current_run["failure_detection"].update(detection_results)

    def log_metrics(self, metrics: Dict[str, Any]):
        """Log computed metrics."""
        if self.current_run is None:
            raise ValueError("No active run. Call start_run() first.")

        self.current_run["metrics"].update(metrics)

    def log_costs(
        self,
        prompt_tokens: int,
        completion_tokens: int,
        cost_usd: float
    ):
        """Log API costs for this run."""
        if self.current_run is None:
            raise ValueError("No active run. Call start_run() first.")

        self.current_run["costs"]["prompt_tokens"] += prompt_tokens
        self.current_run["costs"]["completion_tokens"] += completion_tokens
        self.current_run["costs"]["total_cost_usd"] += cost_usd

    def end_run(self, termination_reason: str) -> str:
        """End the current run and save to disk."""
        if self.current_run is None:
            raise ValueError("No active run. Call start_run() first.")

        self.current_run["execution"]["end_time"] = datetime.utcnow().isoformat() + "Z"
        self.current_run["execution"]["termination_reason"] = termination_reason

        # Save to file
        run_id = self.current_run["run_id"]
        output_file = self.output_dir / f"{run_id}.json"

        with open(output_file, 'w') as f:
            json.dump(self.current_run, f, indent=2)

        # Clear current run
        self.current_run = None

        return str(output_file)

    def get_all_runs(self) -> List[Dict[str, Any]]:
        """Load all run logs from disk."""
        runs = []
        for log_file in self.output_dir.glob("*.json"):
            with open(log_file) as f:
                runs.append(json.load(f))
        return runs


def compute_aggregate_metrics(runs: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Compute aggregate metrics across multiple runs.

    Returns:
        Dictionary with failure rates, iteration statistics, cost statistics
    """
    if not runs:
        return {}

    total_runs = len(runs)
    failure_detected = sum(1 for r in runs if r["metrics"].get("failure_occurred", False))

    iterations = [r["execution"]["iterations"] for r in runs]
    costs = [r["costs"]["total_cost_usd"] for r in runs]

    metrics = {
        "total_runs": total_runs,
        "failure_detection_rate": failure_detected / total_runs if total_runs > 0 else 0,
        "iterations": {
            "mean": sum(iterations) / len(iterations) if iterations else 0,
            "min": min(iterations) if iterations else 0,
            "max": max(iterations) if iterations else 0,
            "median": sorted(iterations)[len(iterations) // 2] if iterations else 0
        },
        "costs": {
            "total_usd": sum(costs),
            "mean_per_run_usd": sum(costs) / len(costs) if costs else 0,
            "min_usd": min(costs) if costs else 0,
            "max_usd": max(costs) if costs else 0
        }
    }

    return metrics
