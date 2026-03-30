"""Checkpoint management for crash-resistant experiments."""

import json
from pathlib import Path
from typing import Any, Dict, Optional, Set


class CheckpointManager:
    """Manage experiment checkpoints for crash recovery.

    Example:
        checkpoint = CheckpointManager("experiments/pilot/checkpoints")

        for instance_id in range(180):
            if checkpoint.is_completed(instance_id):
                print(f"Skipping completed instance {instance_id}")
                continue

            result = run_instance(instance_id)
            checkpoint.save(instance_id, result)
    """

    def __init__(self, checkpoint_dir: Path | str):
        """Initialize checkpoint manager.

        Args:
            checkpoint_dir: Directory to store checkpoint files
        """
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)

        # Index file tracks which instances are completed
        self.index_file = self.checkpoint_dir / "index.json"
        self._completed_instances: Set[int] = set()
        self._load_index()

    def _load_index(self) -> None:
        """Load the index of completed instances."""
        if self.index_file.exists():
            with open(self.index_file, "r") as f:
                data = json.load(f)
                self._completed_instances = set(data.get("completed", []))

    def _save_index(self) -> None:
        """Save the index of completed instances."""
        with open(self.index_file, "w") as f:
            json.dump(
                {
                    "completed": sorted(list(self._completed_instances)),
                    "total": len(self._completed_instances),
                },
                f,
                indent=2,
            )

    def is_completed(self, instance_id: int) -> bool:
        """Check if an instance has been completed.

        Args:
            instance_id: Instance ID to check

        Returns:
            True if instance has a checkpoint
        """
        return instance_id in self._completed_instances

    def save(self, instance_id: int, result: Dict[str, Any]) -> None:
        """Save a checkpoint for an instance.

        Args:
            instance_id: Instance ID
            result: Result dictionary to save
        """
        checkpoint_file = self.checkpoint_dir / f"instance_{instance_id:05d}.json"

        with open(checkpoint_file, "w") as f:
            json.dump(result, f, indent=2)

        # Mark as completed
        self._completed_instances.add(instance_id)
        self._save_index()

    def load(self, instance_id: int) -> Optional[Dict[str, Any]]:
        """Load a checkpoint for an instance.

        Args:
            instance_id: Instance ID to load

        Returns:
            Result dictionary if checkpoint exists, None otherwise
        """
        checkpoint_file = self.checkpoint_dir / f"instance_{instance_id:05d}.json"

        if not checkpoint_file.exists():
            return None

        with open(checkpoint_file, "r") as f:
            return json.load(f)

    def get_completed_count(self) -> int:
        """Get the number of completed instances.

        Returns:
            Number of completed instances
        """
        return len(self._completed_instances)

    def get_completed_ids(self) -> list[int]:
        """Get list of completed instance IDs.

        Returns:
            Sorted list of completed instance IDs
        """
        return sorted(list(self._completed_instances))

    def clear(self) -> None:
        """Clear all checkpoints (use with caution!)."""
        import shutil

        if self.checkpoint_dir.exists():
            shutil.rmtree(self.checkpoint_dir)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        self._completed_instances = set()
        self._save_index()

    def summary(self) -> str:
        """Generate a summary report.

        Returns:
            Human-readable checkpoint summary
        """
        completed_ids = self.get_completed_ids()
        if not completed_ids:
            return "No checkpoints saved yet."

        return (
            f"Checkpoint Summary:\n"
            f"  Completed instances: {len(completed_ids)}\n"
            f"  Range: {min(completed_ids)} - {max(completed_ids)}\n"
            f"  Checkpoint dir: {self.checkpoint_dir}"
        )
