"""Checkpointing utilities for long-running experiments.

Enables crash recovery by saving progress after each instance.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Set


class CheckpointManager:
    """Manage experiment checkpoints for crash recovery."""

    def __init__(self, checkpoint_file: Path):
        """Initialize checkpoint manager.

        Args:
            checkpoint_file: Path to checkpoint file (will be created if doesn't exist)
        """
        self.checkpoint_file = Path(checkpoint_file)
        self.completed_instances: Set[str] = set()
        self.metadata: Dict[str, Any] = {}

        # Load existing checkpoint if present
        if self.checkpoint_file.exists():
            self._load()

    def _load(self):
        """Load checkpoint from disk."""
        with open(self.checkpoint_file) as f:
            data = json.load(f)
            self.completed_instances = set(data.get("completed_instances", []))
            self.metadata = data.get("metadata", {})

    def _save(self):
        """Save checkpoint to disk."""
        data = {
            "completed_instances": list(self.completed_instances),
            "metadata": self.metadata,
        }
        self.checkpoint_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.checkpoint_file, "w") as f:
            json.dump(data, f, indent=2)

    def mark_complete(self, instance_id: str, metadata: Optional[Dict[str, Any]] = None):
        """Mark an instance as completed.

        Args:
            instance_id: Unique instance identifier
            metadata: Optional metadata to store (e.g., cost, status)
        """
        self.completed_instances.add(instance_id)
        if metadata:
            self.metadata[instance_id] = metadata
        self._save()

    def is_complete(self, instance_id: str) -> bool:
        """Check if instance is already completed.

        Args:
            instance_id: Unique instance identifier

        Returns:
            True if instance was already completed
        """
        return instance_id in self.completed_instances

    def get_remaining_instances(self, all_instance_ids: List[str]) -> List[str]:
        """Get list of instances that still need to be run.

        Args:
            all_instance_ids: Complete list of instance IDs for experiment

        Returns:
            List of instance IDs not yet completed
        """
        return [iid for iid in all_instance_ids if not self.is_complete(iid)]

    def get_progress(self, total_instances: int) -> Dict[str, Any]:
        """Get progress summary.

        Args:
            total_instances: Total number of instances in experiment

        Returns:
            Dictionary with completed, remaining, progress_pct
        """
        completed = len(self.completed_instances)
        return {
            "completed": completed,
            "remaining": total_instances - completed,
            "total": total_instances,
            "progress_pct": (completed / total_instances * 100) if total_instances > 0 else 0,
        }

    def reset(self):
        """Clear all checkpoint data and delete file."""
        self.completed_instances.clear()
        self.metadata.clear()
        if self.checkpoint_file.exists():
            self.checkpoint_file.unlink()
