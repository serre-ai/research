"""Structured logging utilities for agent traces."""

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, Optional


class TraceLogger:
    """Log agent execution traces in structured format.

    Logs are written as JSON Lines (one JSON object per line) for easy
    parsing and analysis.

    Example:
        logger = TraceLogger("experiments/pilot/logs/tool_fabrication.jsonl")
        logger.log_action(instance_id=1, action="search", params={"query": "foo"})
        logger.log_observation(instance_id=1, content="Found 3 results", success=True)
        logger.log_completion(instance_id=1, completed=True, cost_usd=0.005)
    """

    def __init__(self, log_file: Path | str):
        """Initialize trace logger.

        Args:
            log_file: Path to log file (will be created if doesn't exist)
        """
        self.log_file = Path(log_file)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

        # Create file if it doesn't exist
        if not self.log_file.exists():
            self.log_file.touch()

    def _write_entry(self, entry: Dict[str, Any]) -> None:
        """Write a log entry.

        Args:
            entry: Dictionary to write as JSON
        """
        with open(self.log_file, "a") as f:
            json.dump(entry, f)
            f.write("\n")

    def log_action(
        self,
        instance_id: int,
        action_type: str,
        action_name: str,
        parameters: Dict[str, Any],
        thought: Optional[str] = None,
        timestamp: Optional[float] = None,
        **metadata,
    ) -> None:
        """Log an action taken by the agent.

        Args:
            instance_id: Task instance ID
            action_type: Type of action (e.g., "tool_call", "finish")
            action_name: Name of action (e.g., tool name)
            parameters: Action parameters
            thought: Agent's reasoning before action
            timestamp: Optional timestamp
            **metadata: Additional metadata
        """
        import time

        if timestamp is None:
            timestamp = time.time()

        entry = {
            "type": "action",
            "instance_id": instance_id,
            "timestamp": timestamp,
            "action_type": action_type,
            "action_name": action_name,
            "parameters": parameters,
            "thought": thought,
            **metadata,
        }
        self._write_entry(entry)

    def log_observation(
        self,
        instance_id: int,
        content: Any,
        success: bool = True,
        error: Optional[str] = None,
        timestamp: Optional[float] = None,
        **metadata,
    ) -> None:
        """Log an observation received after an action.

        Args:
            instance_id: Task instance ID
            content: Observation content
            success: Whether action succeeded
            error: Error message if failed
            timestamp: Optional timestamp
            **metadata: Additional metadata
        """
        import time

        if timestamp is None:
            timestamp = time.time()

        entry = {
            "type": "observation",
            "instance_id": instance_id,
            "timestamp": timestamp,
            "content": str(content),  # Convert to string for JSON serialization
            "success": success,
            "error": error,
            **metadata,
        }
        self._write_entry(entry)

    def log_completion(
        self,
        instance_id: int,
        completed: bool,
        final_answer: Optional[str] = None,
        cost_usd: float = 0.0,
        iterations: int = 0,
        timed_out: bool = False,
        timestamp: Optional[float] = None,
        **metadata,
    ) -> None:
        """Log task completion.

        Args:
            instance_id: Task instance ID
            completed: Whether agent claimed completion
            final_answer: Agent's final answer
            cost_usd: Total API cost
            iterations: Number of iterations
            timed_out: Whether agent hit iteration limit
            timestamp: Optional timestamp
            **metadata: Additional metadata
        """
        import time

        if timestamp is None:
            timestamp = time.time()

        entry = {
            "type": "completion",
            "instance_id": instance_id,
            "timestamp": timestamp,
            "completed": completed,
            "final_answer": final_answer,
            "cost_usd": cost_usd,
            "iterations": iterations,
            "timed_out": timed_out,
            **metadata,
        }
        self._write_entry(entry)

    def log_error(
        self,
        instance_id: int,
        error_type: str,
        error_message: str,
        timestamp: Optional[float] = None,
        **metadata,
    ) -> None:
        """Log an error during execution.

        Args:
            instance_id: Task instance ID
            error_type: Type of error
            error_message: Error message
            timestamp: Optional timestamp
            **metadata: Additional metadata
        """
        import time

        if timestamp is None:
            timestamp = time.time()

        entry = {
            "type": "error",
            "instance_id": instance_id,
            "timestamp": timestamp,
            "error_type": error_type,
            "error_message": error_message,
            **metadata,
        }
        self._write_entry(entry)

    def read_logs(self, instance_id: Optional[int] = None) -> list[Dict[str, Any]]:
        """Read logs, optionally filtered by instance ID.

        Args:
            instance_id: Optional instance ID to filter by

        Returns:
            List of log entries
        """
        logs = []
        if not self.log_file.exists():
            return logs

        with open(self.log_file, "r") as f:
            for line in f:
                if line.strip():
                    entry = json.loads(line)
                    if instance_id is None or entry.get("instance_id") == instance_id:
                        logs.append(entry)

        return logs

    def get_instance_trace(self, instance_id: int) -> Dict[str, Any]:
        """Get complete trace for a specific instance.

        Args:
            instance_id: Instance ID to retrieve

        Returns:
            Dictionary with actions, observations, and completion info
        """
        logs = self.read_logs(instance_id=instance_id)

        actions = [log for log in logs if log["type"] == "action"]
        observations = [log for log in logs if log["type"] == "observation"]
        completions = [log for log in logs if log["type"] == "completion"]
        errors = [log for log in logs if log["type"] == "error"]

        return {
            "instance_id": instance_id,
            "actions": actions,
            "observations": observations,
            "completion": completions[0] if completions else None,
            "errors": errors,
            "total_actions": len(actions),
        }
