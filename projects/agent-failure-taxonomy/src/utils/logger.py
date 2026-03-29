"""
Logging utilities for agent experiments.

Logs every action, observation, and internal state to enable:
1. Cost tracking (tokens, API calls)
2. Failure detection
3. Manual review of traces
4. Reproducibility
"""

import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional


class ExperimentLogger:
    """Logs agent execution traces with structured output."""

    def __init__(self, experiment_name: str, instance_id: str, output_dir: str):
        self.experiment_name = experiment_name
        self.instance_id = instance_id
        self.output_dir = output_dir
        self.trace: List[Dict[str, Any]] = []
        self.metadata: Dict[str, Any] = {
            "experiment": experiment_name,
            "instance_id": instance_id,
            "start_time": datetime.utcnow().isoformat(),
            "end_time": None,
            "total_steps": 0,
            "total_tokens": 0,
            "total_cost_usd": 0.0,
            "outcome": None,  # success | failure | timeout | error
            "failure_type": None,  # tool_hallucination | infinite_loop | false_completion | etc
        }

        # Create output directory
        os.makedirs(output_dir, exist_ok=True)

    def log_step(
        self,
        step: int,
        action: str,
        action_input: Optional[Dict[str, Any]],
        observation: Optional[str],
        thought: Optional[str] = None,
        tokens_used: int = 0,
        cost_usd: float = 0.0,
    ):
        """Log a single agent step."""
        entry = {
            "step": step,
            "timestamp": datetime.utcnow().isoformat(),
            "thought": thought,
            "action": action,
            "action_input": action_input,
            "observation": observation,
            "tokens": tokens_used,
            "cost_usd": cost_usd,
        }
        self.trace.append(entry)
        self.metadata["total_steps"] = step
        self.metadata["total_tokens"] += tokens_used
        self.metadata["total_cost_usd"] += cost_usd

    def log_completion(
        self,
        outcome: str,
        failure_type: Optional[str] = None,
        final_output: Optional[str] = None,
    ):
        """Log experiment completion."""
        self.metadata["end_time"] = datetime.utcnow().isoformat()
        self.metadata["outcome"] = outcome
        self.metadata["failure_type"] = failure_type
        self.metadata["final_output"] = final_output

    def save(self):
        """Save trace and metadata to disk."""
        filename = f"{self.instance_id}.json"
        filepath = os.path.join(self.output_dir, filename)

        output = {
            "metadata": self.metadata,
            "trace": self.trace,
        }

        with open(filepath, "w") as f:
            json.dump(output, f, indent=2)

        return filepath

    def get_summary(self) -> Dict[str, Any]:
        """Get summary statistics."""
        return {
            "instance_id": self.instance_id,
            "outcome": self.metadata["outcome"],
            "failure_type": self.metadata["failure_type"],
            "steps": self.metadata["total_steps"],
            "tokens": self.metadata["total_tokens"],
            "cost_usd": self.metadata["total_cost_usd"],
        }


class AggregateLogger:
    """Aggregates results across multiple instances."""

    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        self.results: List[Dict[str, Any]] = []

    def add_result(self, summary: Dict[str, Any]):
        """Add a single instance result."""
        self.results.append(summary)

    def compute_statistics(self) -> Dict[str, Any]:
        """Compute aggregate statistics."""
        if not self.results:
            return {}

        total = len(self.results)
        outcomes = {}
        failure_types = {}
        total_cost = 0.0
        total_tokens = 0
        total_steps = 0

        for result in self.results:
            # Count outcomes
            outcome = result["outcome"]
            outcomes[outcome] = outcomes.get(outcome, 0) + 1

            # Count failure types
            if result["failure_type"]:
                ft = result["failure_type"]
                failure_types[ft] = failure_types.get(ft, 0) + 1

            # Sum metrics
            total_cost += result.get("cost_usd", 0.0)
            total_tokens += result.get("tokens", 0)
            total_steps += result.get("steps", 0)

        return {
            "total_instances": total,
            "outcomes": outcomes,
            "failure_types": failure_types,
            "total_cost_usd": round(total_cost, 2),
            "total_tokens": total_tokens,
            "total_steps": total_steps,
            "avg_cost_per_instance": round(total_cost / total, 4) if total > 0 else 0,
            "avg_tokens_per_instance": round(total_tokens / total, 1) if total > 0 else 0,
            "avg_steps_per_instance": round(total_steps / total, 1) if total > 0 else 0,
        }

    def save_summary(self, filename: str = "summary_stats.json"):
        """Save aggregate summary."""
        filepath = os.path.join(self.output_dir, filename)
        stats = self.compute_statistics()

        with open(filepath, "w") as f:
            json.dump(stats, f, indent=2)

        return filepath
