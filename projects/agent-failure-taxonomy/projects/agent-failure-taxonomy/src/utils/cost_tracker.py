"""Cost tracking utilities for experiment budget management."""

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class CostRecord:
    """A single cost record."""

    timestamp: float
    model: str
    input_tokens: int
    output_tokens: int
    cost_usd: float
    context: str  # e.g., "instance_42_react_gpt4o"


class CostTracker:
    """Track API costs and enforce budget limits.

    Example:
        tracker = CostTracker(max_budget_usd=2.50)
        tracker.record(model="gpt-4o-mini", input_tokens=100, output_tokens=50,
                      context="instance_1_react")
        if tracker.is_over_budget():
            raise BudgetExceededError()
        print(f"Spent: ${tracker.total_cost_usd():.4f}")
    """

    def __init__(
        self,
        max_budget_usd: float,
        checkpoint_file: Optional[Path] = None,
    ):
        """Initialize cost tracker.

        Args:
            max_budget_usd: Maximum allowed spending
            checkpoint_file: Optional file to persist cost records
        """
        self.max_budget_usd = max_budget_usd
        self.checkpoint_file = checkpoint_file
        self.records: list[CostRecord] = []

        # Load existing records if checkpoint exists
        if checkpoint_file and checkpoint_file.exists():
            self.load()

    def record(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
        cost_usd: float,
        context: str = "",
        timestamp: Optional[float] = None,
    ) -> None:
        """Record a cost entry.

        Args:
            model: Model identifier
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            cost_usd: Cost in USD
            context: Optional context string
            timestamp: Optional timestamp (defaults to current time)
        """
        import time

        if timestamp is None:
            timestamp = time.time()

        record = CostRecord(
            timestamp=timestamp,
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=cost_usd,
            context=context,
        )
        self.records.append(record)

        # Auto-save if checkpoint file is set
        if self.checkpoint_file:
            self.save()

    def total_cost_usd(self) -> float:
        """Get total cost so far.

        Returns:
            Total cost in USD
        """
        return sum(r.cost_usd for r in self.records)

    def is_over_budget(self) -> bool:
        """Check if over budget.

        Returns:
            True if total cost exceeds max budget
        """
        return self.total_cost_usd() > self.max_budget_usd

    def remaining_budget_usd(self) -> float:
        """Get remaining budget.

        Returns:
            Remaining budget in USD (negative if over budget)
        """
        return self.max_budget_usd - self.total_cost_usd()

    def cost_by_model(self) -> dict[str, float]:
        """Get cost breakdown by model.

        Returns:
            Dictionary mapping model name to total cost
        """
        breakdown = {}
        for record in self.records:
            breakdown[record.model] = breakdown.get(record.model, 0.0) + record.cost_usd
        return breakdown

    def save(self) -> None:
        """Save cost records to checkpoint file."""
        if not self.checkpoint_file:
            return

        self.checkpoint_file.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "max_budget_usd": self.max_budget_usd,
            "records": [
                {
                    "timestamp": r.timestamp,
                    "model": r.model,
                    "input_tokens": r.input_tokens,
                    "output_tokens": r.output_tokens,
                    "cost_usd": r.cost_usd,
                    "context": r.context,
                }
                for r in self.records
            ],
        }

        with open(self.checkpoint_file, "w") as f:
            json.dump(data, f, indent=2)

    def load(self) -> None:
        """Load cost records from checkpoint file."""
        if not self.checkpoint_file or not self.checkpoint_file.exists():
            return

        with open(self.checkpoint_file, "r") as f:
            data = json.load(f)

        self.max_budget_usd = data.get("max_budget_usd", self.max_budget_usd)
        self.records = [
            CostRecord(
                timestamp=r["timestamp"],
                model=r["model"],
                input_tokens=r["input_tokens"],
                output_tokens=r["output_tokens"],
                cost_usd=r["cost_usd"],
                context=r["context"],
            )
            for r in data.get("records", [])
        ]

    def summary(self) -> str:
        """Generate a summary report.

        Returns:
            Human-readable cost summary
        """
        total = self.total_cost_usd()
        remaining = self.remaining_budget_usd()
        by_model = self.cost_by_model()

        lines = [
            f"Cost Summary:",
            f"  Total: ${total:.4f} / ${self.max_budget_usd:.2f}",
            f"  Remaining: ${remaining:.4f}",
            f"  Number of calls: {len(self.records)}",
            f"",
            f"By model:",
        ]

        for model, cost in sorted(by_model.items(), key=lambda x: -x[1]):
            lines.append(f"  {model}: ${cost:.4f}")

        return "\n".join(lines)


class BudgetExceededError(Exception):
    """Raised when experiment exceeds budget."""

    pass
