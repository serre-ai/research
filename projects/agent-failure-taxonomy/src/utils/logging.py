"""
Logging and cost tracking utilities for agent experiments.
"""

import json
import time
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class APICall:
    """Record of a single API call."""
    timestamp: str
    framework: str
    model: str
    test_id: str
    instance_id: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    cost_usd: float
    latency_seconds: float
    response_preview: str  # First 200 chars

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class TestResult:
    """Result of a single test instance."""
    test_name: str
    framework: str
    instance_id: str
    success: bool
    failure_occurred: bool
    failure_type: Optional[str]
    metadata: Dict[str, Any]
    api_calls: list[APICall]
    total_cost_usd: float
    total_time_seconds: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "test_name": self.test_name,
            "framework": self.framework,
            "instance_id": self.instance_id,
            "success": self.success,
            "failure_occurred": self.failure_occurred,
            "failure_type": self.failure_type,
            "metadata": self.metadata,
            "api_calls": [call.to_dict() for call in self.api_calls],
            "total_cost_usd": self.total_cost_usd,
            "total_time_seconds": self.total_time_seconds,
        }


class ExperimentLogger:
    """Logger for experiment runs with cost tracking."""

    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.run_id = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Cost tracking
        self.total_cost = 0.0
        self.api_calls = []
        self.results = []

    def log_api_call(self, call: APICall):
        """Log a single API call."""
        self.api_calls.append(call)
        self.total_cost += call.cost_usd

    def log_result(self, result: TestResult):
        """Log a test result."""
        self.results.append(result)
        self.total_cost += result.total_cost_usd

        # Save incrementally
        self._save_checkpoint()

    def _save_checkpoint(self):
        """Save current state to disk."""
        checkpoint_file = self.output_dir / f"checkpoint_{self.run_id}.json"

        data = {
            "run_id": self.run_id,
            "timestamp": datetime.now().isoformat(),
            "total_cost_usd": self.total_cost,
            "num_results": len(self.results),
            "results": [r.to_dict() for r in self.results],
        }

        with open(checkpoint_file, 'w') as f:
            json.dump(data, f, indent=2)

    def get_summary(self) -> Dict[str, Any]:
        """Get summary statistics."""
        if not self.results:
            return {"error": "No results logged"}

        failure_count = sum(1 for r in self.results if r.failure_occurred)

        return {
            "run_id": self.run_id,
            "total_instances": len(self.results),
            "failures_observed": failure_count,
            "failure_rate": failure_count / len(self.results) if self.results else 0,
            "total_cost_usd": self.total_cost,
            "avg_cost_per_instance": self.total_cost / len(self.results) if self.results else 0,
        }

    def save_final_report(self):
        """Save final experiment report."""
        report_file = self.output_dir / f"report_{self.run_id}.json"

        report = {
            "run_id": self.run_id,
            "timestamp": datetime.now().isoformat(),
            "summary": self.get_summary(),
            "results": [r.to_dict() for r in self.results],
        }

        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"\n{'='*60}")
        print(f"Experiment Complete: {self.run_id}")
        print(f"{'='*60}")
        print(f"Total instances: {len(self.results)}")
        print(f"Failures observed: {report['summary']['failures_observed']}")
        print(f"Failure rate: {report['summary']['failure_rate']:.2%}")
        print(f"Total cost: ${self.total_cost:.4f}")
        print(f"Report saved: {report_file}")
        print(f"{'='*60}\n")

        return report


def estimate_cost(prompt_tokens: int, completion_tokens: int, model: str = "claude-3-5-sonnet-20241022") -> float:
    """
    Estimate API call cost in USD.

    Pricing (as of 2026-03):
    - Claude 3.5 Sonnet: $3/MTok input, $15/MTok output
    - Claude 3.5 Haiku: $1/MTok input, $5/MTok output
    """
    pricing = {
        "claude-3-5-sonnet-20241022": {"input": 3.0, "output": 15.0},
        "claude-3-5-haiku-20241022": {"input": 1.0, "output": 5.0},
    }

    if model not in pricing:
        # Default to Sonnet pricing
        model = "claude-3-5-sonnet-20241022"

    input_cost = (prompt_tokens / 1_000_000) * pricing[model]["input"]
    output_cost = (completion_tokens / 1_000_000) * pricing[model]["output"]

    return input_cost + output_cost
