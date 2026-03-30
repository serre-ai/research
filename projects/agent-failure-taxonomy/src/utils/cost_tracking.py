"""
Cost tracking utilities for agent experiments.
Monitors API usage and enforces budget limits.
"""

from typing import Dict, Optional
from pathlib import Path
import json


# Pricing per 1M tokens (as of 2026-03)
# Source: OpenAI, Anthropic pricing pages
MODEL_PRICING = {
    "gpt-4-turbo": {"input": 10.0, "output": 30.0},
    "gpt-4": {"input": 30.0, "output": 60.0},
    "gpt-3.5-turbo": {"input": 0.5, "output": 1.5},
    "claude-3-5-sonnet-20241022": {"input": 3.0, "output": 15.0},
    "claude-3-opus-20240229": {"input": 15.0, "output": 75.0},
    "claude-3-sonnet-20240229": {"input": 3.0, "output": 15.0},
}


class CostTracker:
    """Tracks API costs and enforces budget limits."""

    def __init__(self, budget_usd: float = 200.0, checkpoint_file: Optional[str] = None):
        self.budget_usd = budget_usd
        self.total_spent = 0.0
        self.checkpoint_file = checkpoint_file

        # Load from checkpoint if exists
        if checkpoint_file and Path(checkpoint_file).exists():
            self.load_checkpoint()

    def calculate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost for a single API call."""
        if model not in MODEL_PRICING:
            # Default to GPT-4 pricing as conservative estimate
            pricing = MODEL_PRICING["gpt-4"]
        else:
            pricing = MODEL_PRICING[model]

        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]

        return input_cost + output_cost

    def add_cost(self, cost: float) -> None:
        """Add cost to running total."""
        self.total_spent += cost

        if self.checkpoint_file:
            self.save_checkpoint()

    def check_budget(self) -> bool:
        """Check if we're still within budget."""
        return self.total_spent < self.budget_usd

    def get_remaining_budget(self) -> float:
        """Get remaining budget."""
        return max(0.0, self.budget_usd - self.total_spent)

    def get_budget_usage_pct(self) -> float:
        """Get percentage of budget used."""
        return (self.total_spent / self.budget_usd) * 100 if self.budget_usd > 0 else 0.0

    def save_checkpoint(self) -> None:
        """Save cost state to checkpoint file."""
        if not self.checkpoint_file:
            return

        checkpoint_path = Path(self.checkpoint_file)
        checkpoint_path.parent.mkdir(parents=True, exist_ok=True)

        with open(checkpoint_path, 'w') as f:
            json.dump({
                "budget_usd": self.budget_usd,
                "total_spent": self.total_spent
            }, f, indent=2)

    def load_checkpoint(self) -> None:
        """Load cost state from checkpoint file."""
        if not self.checkpoint_file:
            return

        checkpoint_path = Path(self.checkpoint_file)
        if not checkpoint_path.exists():
            return

        with open(checkpoint_path, 'r') as f:
            data = json.load(f)
            self.budget_usd = data.get("budget_usd", self.budget_usd)
            self.total_spent = data.get("total_spent", 0.0)

    def print_status(self) -> None:
        """Print budget status."""
        print(f"\nBudget Status:")
        print(f"  Budget: ${self.budget_usd:.2f}")
        print(f"  Spent: ${self.total_spent:.2f}")
        print(f"  Remaining: ${self.get_remaining_budget():.2f}")
        print(f"  Usage: {self.get_budget_usage_pct():.1f}%")
        print()


class EstimateCost:
    """Estimate costs for planned experiments."""

    @staticmethod
    def estimate_run_cost(model: str,
                         avg_turns: int,
                         tokens_per_turn_input: int = 1000,
                         tokens_per_turn_output: int = 500) -> float:
        """Estimate cost for a single run."""
        tracker = CostTracker()
        total_input = avg_turns * tokens_per_turn_input
        total_output = avg_turns * tokens_per_turn_output

        return tracker.calculate_cost(model, total_input, total_output)

    @staticmethod
    def estimate_experiment_cost(model: str,
                                 num_runs: int,
                                 avg_turns_per_run: int,
                                 tokens_per_turn_input: int = 1000,
                                 tokens_per_turn_output: int = 500) -> float:
        """Estimate total cost for an experiment."""
        cost_per_run = EstimateCost.estimate_run_cost(
            model, avg_turns_per_run, tokens_per_turn_input, tokens_per_turn_output
        )
        return cost_per_run * num_runs

    @staticmethod
    def print_estimates() -> None:
        """Print example cost estimates."""
        print("\nCost Estimates (per run):")
        print(f"{'Model':<30} {'5 turns':<12} {'10 turns':<12} {'20 turns':<12}")
        print("-" * 66)

        for model in ["gpt-4-turbo", "gpt-3.5-turbo", "claude-3-5-sonnet-20241022"]:
            costs = [
                EstimateCost.estimate_run_cost(model, turns)
                for turns in [5, 10, 20]
            ]
            print(f"{model:<30} ${costs[0]:<11.3f} ${costs[1]:<11.3f} ${costs[2]:<11.3f}")

        print()


if __name__ == "__main__":
    # Print cost estimates
    EstimateCost.print_estimates()

    # Example usage
    tracker = CostTracker(budget_usd=50.0)
    tracker.print_status()

    # Simulate some API calls
    cost1 = tracker.calculate_cost("gpt-4-turbo", 1000, 500)
    print(f"Call 1 cost: ${cost1:.3f}")
    tracker.add_cost(cost1)

    cost2 = tracker.calculate_cost("gpt-4-turbo", 1500, 800)
    print(f"Call 2 cost: ${cost2:.3f}")
    tracker.add_cost(cost2)

    tracker.print_status()
    print(f"Within budget: {tracker.check_budget()}")
