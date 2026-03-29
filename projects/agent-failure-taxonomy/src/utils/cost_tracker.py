"""
Cost tracking utility to prevent budget overruns.

Tracks cumulative costs and enforces budget limits.
"""

from dataclasses import dataclass
from typing import Optional
import json
import os


@dataclass
class CostEntry:
    """Single cost entry."""
    run_id: str
    cost_usd: float
    timestamp: float
    metadata: dict


class CostTracker:
    """
    Tracks experimental costs and enforces budget limits.

    Usage:
        tracker = CostTracker(max_budget_usd=50.0)
        tracker.add_cost(run_id="run_001", cost_usd=0.32)
        if tracker.budget_exceeded():
            raise BudgetExceededError()
    """

    def __init__(
        self,
        max_budget_usd: float,
        checkpoint_file: Optional[str] = None
    ):
        """
        Initialize cost tracker.

        Args:
            max_budget_usd: Maximum allowed spend
            checkpoint_file: Path to save cost log (for recovery)
        """
        self.max_budget_usd = max_budget_usd
        self.checkpoint_file = checkpoint_file
        self.entries: list[CostEntry] = []
        self._load_checkpoint()

    def add_cost(
        self,
        run_id: str,
        cost_usd: float,
        metadata: Optional[dict] = None
    ):
        """
        Add a cost entry.

        Args:
            run_id: Identifier for the run
            cost_usd: Cost in USD
            metadata: Additional information
        """
        import time

        entry = CostEntry(
            run_id=run_id,
            cost_usd=cost_usd,
            timestamp=time.time(),
            metadata=metadata or {}
        )
        self.entries.append(entry)
        self._save_checkpoint()

    def total_cost(self) -> float:
        """Get total cumulative cost."""
        return sum(e.cost_usd for e in self.entries)

    def remaining_budget(self) -> float:
        """Get remaining budget."""
        return self.max_budget_usd - self.total_cost()

    def budget_exceeded(self) -> bool:
        """Check if budget exceeded."""
        return self.total_cost() > self.max_budget_usd

    def can_afford(self, estimated_cost_usd: float) -> bool:
        """Check if can afford estimated cost."""
        return (self.total_cost() + estimated_cost_usd) <= self.max_budget_usd

    def summary(self) -> dict:
        """Get cost summary."""
        return {
            "total_cost_usd": self.total_cost(),
            "max_budget_usd": self.max_budget_usd,
            "remaining_budget_usd": self.remaining_budget(),
            "budget_exceeded": self.budget_exceeded(),
            "num_entries": len(self.entries),
        }

    def _save_checkpoint(self):
        """Save cost log to file."""
        if not self.checkpoint_file:
            return

        data = {
            "max_budget_usd": self.max_budget_usd,
            "entries": [
                {
                    "run_id": e.run_id,
                    "cost_usd": e.cost_usd,
                    "timestamp": e.timestamp,
                    "metadata": e.metadata
                }
                for e in self.entries
            ]
        }

        os.makedirs(os.path.dirname(self.checkpoint_file), exist_ok=True)
        with open(self.checkpoint_file, 'w') as f:
            json.dump(data, f, indent=2)

    def _load_checkpoint(self):
        """Load cost log from file."""
        if not self.checkpoint_file or not os.path.exists(self.checkpoint_file):
            return

        with open(self.checkpoint_file, 'r') as f:
            data = json.load(f)

        self.entries = [
            CostEntry(
                run_id=e["run_id"],
                cost_usd=e["cost_usd"],
                timestamp=e["timestamp"],
                metadata=e["metadata"]
            )
            for e in data["entries"]
        ]


class BudgetExceededError(Exception):
    """Raised when budget is exceeded."""
    pass
