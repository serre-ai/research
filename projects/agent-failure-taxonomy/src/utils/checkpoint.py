"""
Checkpoint system for crash recovery.

Enables experiments to resume from the last completed instance after crashes.
"""

import json
import os
from typing import Any, Dict, List, Optional
from pathlib import Path
from datetime import datetime


class CheckpointManager:
    """
    Manages experiment checkpoints for crash recovery.

    Checkpoints store:
    - Completed task IDs
    - Cumulative cost
    - Results so far
    - Timestamp of last update
    """

    def __init__(self, experiment_name: str, checkpoint_dir: str = "checkpoints"):
        """
        Initialize checkpoint manager.

        Args:
            experiment_name: Name of the experiment
            checkpoint_dir: Directory to store checkpoint files
        """
        self.experiment_name = experiment_name
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        self.checkpoint_file = self.checkpoint_dir / f"{experiment_name}.json"

        # Initialize or load checkpoint
        self.checkpoint = self._load_checkpoint()

    def _load_checkpoint(self) -> Dict[str, Any]:
        """Load checkpoint from disk if exists, otherwise create new."""
        if self.checkpoint_file.exists():
            with open(self.checkpoint_file, 'r') as f:
                return json.load(f)
        else:
            return {
                "experiment_name": self.experiment_name,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "completed_tasks": [],
                "results": [],
                "cumulative_cost_usd": 0.0,
                "status": "running"
            }

    def save(self):
        """Save checkpoint to disk."""
        self.checkpoint["updated_at"] = datetime.utcnow().isoformat()
        with open(self.checkpoint_file, 'w') as f:
            json.dump(self.checkpoint, f, indent=2)

    def is_task_completed(self, task_id: str) -> bool:
        """Check if a task has already been completed."""
        return task_id in self.checkpoint["completed_tasks"]

    def mark_task_completed(self, task_id: str, result: Dict[str, Any], cost: float):
        """
        Mark a task as completed and save result.

        Args:
            task_id: Task identifier
            result: Task result dictionary
            cost: Cost in USD for this task
        """
        if task_id not in self.checkpoint["completed_tasks"]:
            self.checkpoint["completed_tasks"].append(task_id)
            self.checkpoint["results"].append(result)
            self.checkpoint["cumulative_cost_usd"] += cost
            self.save()

    def get_cumulative_cost(self) -> float:
        """Get total cost so far."""
        return self.checkpoint["cumulative_cost_usd"]

    def get_completed_count(self) -> int:
        """Get number of completed tasks."""
        return len(self.checkpoint["completed_tasks"])

    def get_results(self) -> List[Dict[str, Any]]:
        """Get all completed results."""
        return self.checkpoint["results"]

    def mark_complete(self):
        """Mark experiment as complete."""
        self.checkpoint["status"] = "complete"
        self.checkpoint["completed_at"] = datetime.utcnow().isoformat()
        self.save()

    def mark_failed(self, error: str):
        """Mark experiment as failed."""
        self.checkpoint["status"] = "failed"
        self.checkpoint["error"] = error
        self.checkpoint["failed_at"] = datetime.utcnow().isoformat()
        self.save()

    def get_status(self) -> str:
        """Get current experiment status."""
        return self.checkpoint["status"]

    def reset(self):
        """Reset checkpoint (use with caution - deletes all progress)."""
        if self.checkpoint_file.exists():
            self.checkpoint_file.unlink()
        self.checkpoint = self._load_checkpoint()
