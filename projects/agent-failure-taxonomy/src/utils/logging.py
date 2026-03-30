"""
Logging utilities for experiment execution.

Provides structured logging for agent execution traces, costs, and metrics.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional
from datetime import datetime


class ExperimentLogger:
    """Logger for experimental runs."""

    def __init__(self, experiment_name: str, output_dir: str = "experiments"):
        """
        Initialize logger.

        Args:
            experiment_name: Name of the experiment (e.g., "pilot")
            output_dir: Base directory for experiment outputs
        """
        self.experiment_name = experiment_name
        self.output_dir = Path(output_dir) / experiment_name / "results"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.log_file = self.output_dir / "execution.log"
        self.results_file = self.output_dir / "results.jsonl"

    def log_execution(self, result: Dict[str, Any]) -> None:
        """
        Log an agent execution result.

        Args:
            result: AgentResult dictionary to log
        """
        # Append to JSONL file (one JSON object per line)
        with open(self.results_file, "a") as f:
            f.write(json.dumps(result) + "\n")

        # Log summary to text file
        with open(self.log_file, "a") as f:
            timestamp = datetime.now().isoformat()
            f.write(f"\n[{timestamp}] Task: {result['task_id']}\n")
            f.write(f"  Framework: {result['framework']}\n")
            f.write(f"  Model: {result['model']}\n")
            f.write(f"  Steps: {len(result['steps'])}\n")
            f.write(f"  Success: {result['success']}\n")
            f.write(f"  Completion claimed: {result['completion_claimed']}\n")
            f.write(f"  Cost: ${result['total_cost']:.4f}\n")
            if result.get("error"):
                f.write(f"  Error: {result['error']}\n")

    def log_cost(self, task_id: str, cost: float, tokens: int) -> None:
        """Log cost information."""
        cost_file = self.output_dir / "costs.jsonl"
        with open(cost_file, "a") as f:
            entry = {
                "timestamp": datetime.now().isoformat(),
                "task_id": task_id,
                "cost": cost,
                "tokens": tokens,
            }
            f.write(json.dumps(entry) + "\n")

    def save_checkpoint(self, checkpoint_data: Dict[str, Any]) -> None:
        """Save checkpoint for crash recovery."""
        checkpoint_file = self.output_dir / "checkpoint.json"
        with open(checkpoint_file, "w") as f:
            json.dump(checkpoint_data, f, indent=2)

    def load_checkpoint(self) -> Optional[Dict[str, Any]]:
        """Load checkpoint if it exists."""
        checkpoint_file = self.output_dir / "checkpoint.json"
        if checkpoint_file.exists():
            with open(checkpoint_file) as f:
                return json.load(f)
        return None

    def get_completed_tasks(self) -> set:
        """Get set of completed task IDs from results file."""
        completed = set()
        if self.results_file.exists():
            with open(self.results_file) as f:
                for line in f:
                    result = json.loads(line)
                    completed.add(result["task_id"])
        return completed

    def get_total_cost(self) -> float:
        """Calculate total cost from logged results."""
        total = 0.0
        if self.results_file.exists():
            with open(self.results_file) as f:
                for line in f:
                    result = json.loads(line)
                    total += result.get("total_cost", 0.0)
        return total

    def summary(self) -> Dict[str, Any]:
        """Generate summary statistics from logged results."""
        if not self.results_file.exists():
            return {"total_executions": 0}

        results = []
        with open(self.results_file) as f:
            for line in f:
                results.append(json.loads(line))

        total_cost = sum(r.get("total_cost", 0.0) for r in results)
        total_tokens = sum(r.get("total_tokens", 0) for r in results)
        total_steps = sum(len(r.get("steps", [])) for r in results)
        successes = sum(1 for r in results if r.get("success"))
        completions_claimed = sum(1 for r in results if r.get("completion_claimed"))
        errors = sum(1 for r in results if r.get("error"))

        frameworks = {}
        for r in results:
            fw = r.get("framework", "unknown")
            if fw not in frameworks:
                frameworks[fw] = 0
            frameworks[fw] += 1

        return {
            "experiment": self.experiment_name,
            "total_executions": len(results),
            "total_cost_usd": round(total_cost, 2),
            "total_tokens": total_tokens,
            "total_steps": total_steps,
            "avg_steps_per_execution": round(total_steps / len(results), 1) if results else 0,
            "avg_cost_per_execution": round(total_cost / len(results), 4) if results else 0,
            "success_rate": round(successes / len(results), 2) if results else 0,
            "completion_claim_rate": round(completions_claimed / len(results), 2) if results else 0,
            "error_rate": round(errors / len(results), 2) if results else 0,
            "by_framework": frameworks,
        }


def estimate_cost(
    num_tokens_input: int,
    num_tokens_output: int,
    model: str = "claude-haiku-4-5-20251001",
) -> float:
    """
    Estimate cost for an LLM API call.

    Args:
        num_tokens_input: Number of input tokens
        num_tokens_output: Number of output tokens
        model: Model identifier

    Returns:
        Estimated cost in USD
    """
    # Pricing as of March 2026 (approximate)
    pricing = {
        "claude-haiku-4-5-20251001": {"input": 0.80 / 1e6, "output": 4.00 / 1e6},
        "claude-sonnet-4-5-20250929": {"input": 3.00 / 1e6, "output": 15.00 / 1e6},
        "gpt-4o-mini": {"input": 0.15 / 1e6, "output": 0.60 / 1e6},
        "gpt-4o": {"input": 2.50 / 1e6, "output": 10.00 / 1e6},
    }

    if model not in pricing:
        # Default to Haiku pricing if model unknown
        rates = pricing["claude-haiku-4-5-20251001"]
    else:
        rates = pricing[model]

    return num_tokens_input * rates["input"] + num_tokens_output * rates["output"]
