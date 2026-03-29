"""Cost tracking utilities for API calls.

Tracks cumulative costs and enforces budget limits.
"""

from typing import Optional


class CostTracker:
    """Track API costs and enforce budget limits."""

    # Pricing per 1M tokens (as of 2026-03-29)
    PRICING = {
        "gpt-4o-mini-2024-07-18": {"input": 0.15, "output": 0.60},
        "gpt-4o-2024-11-20": {"input": 2.50, "output": 10.00},
        "claude-3-5-sonnet-20241022": {"input": 3.00, "output": 15.00},
        "claude-3-5-haiku-20241022": {"input": 1.00, "output": 5.00},
    }

    def __init__(self, budget_limit_usd: float):
        """Initialize cost tracker.

        Args:
            budget_limit_usd: Maximum allowed spend in USD
        """
        self.budget_limit_usd = budget_limit_usd
        self.cumulative_cost_usd = 0.0
        self.call_count = 0

    def add_call(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Record an API call and return its cost.

        Args:
            model: Model identifier
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens

        Returns:
            Cost in USD for this call

        Raises:
            ValueError: If budget limit exceeded
        """
        if model not in self.PRICING:
            raise ValueError(f"Unknown model: {model}. Add pricing to CostTracker.PRICING")

        pricing = self.PRICING[model]
        cost = (input_tokens / 1_000_000) * pricing["input"] + (
            output_tokens / 1_000_000
        ) * pricing["output"]

        self.cumulative_cost_usd += cost
        self.call_count += 1

        if self.cumulative_cost_usd > self.budget_limit_usd:
            raise ValueError(
                f"Budget limit exceeded: ${self.cumulative_cost_usd:.2f} > "
                f"${self.budget_limit_usd:.2f}"
            )

        return cost

    def get_summary(self) -> dict:
        """Get cost tracking summary.

        Returns:
            Dictionary with cumulative_cost_usd, call_count, budget_remaining_usd
        """
        return {
            "cumulative_cost_usd": self.cumulative_cost_usd,
            "call_count": self.call_count,
            "budget_remaining_usd": self.budget_limit_usd - self.cumulative_cost_usd,
            "budget_limit_usd": self.budget_limit_usd,
        }

    def reset(self):
        """Reset cumulative cost and call count."""
        self.cumulative_cost_usd = 0.0
        self.call_count = 0
