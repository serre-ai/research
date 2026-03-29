"""Structured logging utilities for agent failure experiments.

All experiment runs produce structured JSON logs that can be analyzed programmatically.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional


class ExperimentLogger:
    """Structured logger for experiment runs."""

    def __init__(self, experiment_name: str, output_dir: Path):
        """Initialize experiment logger.

        Args:
            experiment_name: Name of experiment (e.g., "pilot-validation")
            output_dir: Directory to write log files
        """
        self.experiment_name = experiment_name
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Create timestamped log file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = self.output_dir / f"{experiment_name}_{timestamp}.jsonl"

        # Set up Python logger for console output
        self.logger = logging.getLogger(f"experiment.{experiment_name}")
        self.logger.setLevel(logging.INFO)

        # Console handler
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        console.setFormatter(formatter)
        self.logger.addHandler(console)

    def log_instance(
        self,
        instance_id: str,
        framework: str,
        task_type: str,
        ground_truth: Any,
        agent_trajectory: list,
        completion_status: str,
        failure_detected: bool,
        failure_type: Optional[str],
        cost_usd: float,
        latency_seconds: float,
        token_counts: Dict[str, int],
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """Log a single experiment instance.

        Args:
            instance_id: Unique identifier for this instance
            framework: Framework name (langgraph, react_direct, anthropic_mcp)
            task_type: Task type (tool_fabrication_n5, infinite_loops_ambiguous, etc.)
            ground_truth: Ground truth answer/state
            agent_trajectory: List of steps with observations, reasoning, actions, results
            completion_status: success | failure | timeout
            failure_detected: Whether target failure mode was detected
            failure_type: Type of failure if detected
            cost_usd: API cost in USD
            latency_seconds: Wall-clock time
            token_counts: {"input": int, "output": int}
            metadata: Additional metadata
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "instance_id": instance_id,
            "framework": framework,
            "task_type": task_type,
            "ground_truth": ground_truth,
            "agent_trajectory": agent_trajectory,
            "metrics": {
                "completion_status": completion_status,
                "failure_detected": failure_detected,
                "failure_type": failure_type,
                "cost_usd": cost_usd,
                "latency_seconds": latency_seconds,
                "tokens": token_counts,
            },
            "metadata": metadata or {},
        }

        # Write to JSONL file
        with open(self.log_file, "a") as f:
            f.write(json.dumps(log_entry) + "\n")

        # Console summary
        status_emoji = "✓" if completion_status == "success" else "✗"
        failure_emoji = "🔥" if failure_detected else "○"
        self.logger.info(
            f"{status_emoji} {failure_emoji} {instance_id} | {framework} | {task_type} | "
            f"{completion_status} | ${cost_usd:.4f} | {latency_seconds:.1f}s"
        )

    def log_canary_diagnostic(
        self, diagnostic_name: str, passed: bool, value: Any, threshold: Any, message: str
    ):
        """Log a canary diagnostic check result.

        Args:
            diagnostic_name: Name of diagnostic check
            passed: Whether check passed
            value: Actual measured value
            threshold: Expected threshold
            message: Explanation message
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "canary_diagnostic",
            "diagnostic": diagnostic_name,
            "passed": passed,
            "value": value,
            "threshold": threshold,
            "message": message,
        }

        with open(self.log_file, "a") as f:
            f.write(json.dumps(log_entry) + "\n")

        emoji = "✓" if passed else "✗"
        level = logging.INFO if passed else logging.WARNING
        self.logger.log(level, f"{emoji} {diagnostic_name}: {message}")

    def log_experiment_start(self, spec: Dict[str, Any]):
        """Log experiment start with full spec."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "experiment_start",
            "experiment_name": self.experiment_name,
            "spec": spec,
        }

        with open(self.log_file, "a") as f:
            f.write(json.dumps(log_entry) + "\n")

        self.logger.info(f"Starting experiment: {self.experiment_name}")

    def log_experiment_complete(self, summary: Dict[str, Any]):
        """Log experiment completion with summary stats."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "experiment_complete",
            "experiment_name": self.experiment_name,
            "summary": summary,
        }

        with open(self.log_file, "a") as f:
            f.write(json.dumps(log_entry) + "\n")

        self.logger.info(
            f"Experiment complete: {summary.get('total_instances', 0)} instances, "
            f"${summary.get('total_cost_usd', 0):.2f}, "
            f"{summary.get('total_time_seconds', 0):.1f}s"
        )


def load_experiment_logs(log_file: Path) -> list:
    """Load all log entries from a JSONL file.

    Args:
        log_file: Path to .jsonl log file

    Returns:
        List of log entry dictionaries
    """
    entries = []
    with open(log_file) as f:
        for line in f:
            entries.append(json.loads(line))
    return entries


def filter_instance_logs(log_entries: list) -> list:
    """Filter log entries to only instance results (exclude diagnostics, metadata).

    Args:
        log_entries: All log entries

    Returns:
        List of instance log entries only
    """
    return [e for e in log_entries if "instance_id" in e and "type" not in e]
