"""
Checkpoint utilities for crash recovery in experiments.
Enables resuming experiments from last completed run.
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional


class CheckpointManager:
    """Manages experiment checkpoints for crash recovery."""

    def __init__(self, experiment_name: str, checkpoint_dir: str = "experiments/checkpoints"):
        self.experiment_name = experiment_name
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        self.checkpoint_file = self.checkpoint_dir / f"{experiment_name}.json"

    def save_checkpoint(self,
                       completed_runs: List[str],
                       pending_runs: List[Dict[str, Any]],
                       metadata: Optional[Dict[str, Any]] = None) -> None:
        """Save checkpoint with completed and pending runs."""
        checkpoint_data = {
            "experiment_name": self.experiment_name,
            "completed_runs": completed_runs,
            "pending_runs": pending_runs,
            "metadata": metadata or {}
        }

        with open(self.checkpoint_file, 'w') as f:
            json.dump(checkpoint_data, f, indent=2)

    def load_checkpoint(self) -> Optional[Dict[str, Any]]:
        """Load checkpoint if it exists."""
        if not self.checkpoint_file.exists():
            return None

        with open(self.checkpoint_file, 'r') as f:
            return json.load(f)

    def has_checkpoint(self) -> bool:
        """Check if checkpoint exists."""
        return self.checkpoint_file.exists()

    def clear_checkpoint(self) -> None:
        """Delete checkpoint file."""
        if self.checkpoint_file.exists():
            self.checkpoint_file.unlink()

    def get_completed_count(self) -> int:
        """Get number of completed runs from checkpoint."""
        checkpoint = self.load_checkpoint()
        if not checkpoint:
            return 0
        return len(checkpoint.get("completed_runs", []))

    def get_pending_count(self) -> int:
        """Get number of pending runs from checkpoint."""
        checkpoint = self.load_checkpoint()
        if not checkpoint:
            return 0
        return len(checkpoint.get("pending_runs", []))


class ExperimentQueue:
    """Manages a queue of experiment runs with checkpoint support."""

    def __init__(self, experiment_name: str):
        self.experiment_name = experiment_name
        self.checkpoint_manager = CheckpointManager(experiment_name)
        self.completed_runs: List[str] = []
        self.pending_runs: List[Dict[str, Any]] = []

        # Try to resume from checkpoint
        self._resume_from_checkpoint()

    def _resume_from_checkpoint(self) -> None:
        """Resume from checkpoint if available."""
        checkpoint = self.checkpoint_manager.load_checkpoint()
        if checkpoint:
            self.completed_runs = checkpoint.get("completed_runs", [])
            self.pending_runs = checkpoint.get("pending_runs", [])
            print(f"Resumed from checkpoint: {len(self.completed_runs)} completed, {len(self.pending_runs)} pending")

    def add_runs(self, runs: List[Dict[str, Any]]) -> None:
        """Add runs to the queue."""
        self.pending_runs.extend(runs)
        self._save_checkpoint()

    def get_next_run(self) -> Optional[Dict[str, Any]]:
        """Get next run from queue."""
        if not self.pending_runs:
            return None
        return self.pending_runs[0]

    def mark_completed(self, run_id: str) -> None:
        """Mark a run as completed and remove from pending."""
        if self.pending_runs:
            self.pending_runs.pop(0)
        self.completed_runs.append(run_id)
        self._save_checkpoint()

    def _save_checkpoint(self) -> None:
        """Save current state to checkpoint."""
        self.checkpoint_manager.save_checkpoint(
            self.completed_runs,
            self.pending_runs,
            {"total_runs": len(self.completed_runs) + len(self.pending_runs)}
        )

    def is_complete(self) -> bool:
        """Check if all runs are completed."""
        return len(self.pending_runs) == 0

    def get_progress(self) -> Dict[str, Any]:
        """Get progress statistics."""
        total = len(self.completed_runs) + len(self.pending_runs)
        return {
            "completed": len(self.completed_runs),
            "pending": len(self.pending_runs),
            "total": total,
            "progress_pct": (len(self.completed_runs) / total * 100) if total > 0 else 0
        }

    def print_progress(self) -> None:
        """Print progress status."""
        progress = self.get_progress()
        print(f"\nExperiment Progress: {self.experiment_name}")
        print(f"  Completed: {progress['completed']}/{progress['total']}")
        print(f"  Pending: {progress['pending']}")
        print(f"  Progress: {progress['progress_pct']:.1f}%")
        print()


def create_run_plan(failure_instance: str,
                   framework: str,
                   model: str,
                   task: str,
                   num_runs: int) -> List[Dict[str, Any]]:
    """Create a plan for multiple runs of the same configuration."""
    runs = []
    for i in range(1, num_runs + 1):
        run_id = f"{failure_instance.lower()}_{framework}_run{i:03d}"
        runs.append({
            "run_id": run_id,
            "failure_instance": failure_instance,
            "framework": framework,
            "model": model,
            "task": task
        })
    return runs


if __name__ == "__main__":
    # Example usage
    queue = ExperimentQueue("pilot_experiment")

    # Add some runs
    runs = create_run_plan("FI-014", "react", "gpt-4-turbo", "laptop_research", 5)
    queue.add_runs(runs)

    queue.print_progress()

    # Simulate completing runs
    while not queue.is_complete():
        run = queue.get_next_run()
        if run:
            print(f"Processing: {run['run_id']}")
            # ... run experiment ...
            queue.mark_completed(run['run_id'])
            queue.print_progress()
