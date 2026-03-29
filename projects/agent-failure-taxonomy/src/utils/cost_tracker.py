"""
Cost tracking and circuit breaker.

Monitors API costs and halts execution if budget limits are exceeded.
"""

from typing import Optional


class CostTracker:
    """
    Tracks cumulative API costs and enforces budget limits.

    Provides circuit breaker functionality to halt experiments
    before budget overruns.
    """

    # Pricing per 1M tokens (as of 2024)
    PRICING = {
        "claude-3-5-sonnet-20241022": {
            "input": 3.00,   # $3 per 1M input tokens
            "output": 15.00  # $15 per 1M output tokens
        },
        "claude-3-opus-20240229": {
            "input": 15.00,
            "output": 75.00
        },
        "gpt-4-turbo": {
            "input": 10.00,
            "output": 30.00
        }
    }

    def __init__(self, max_budget_usd: float, warning_threshold: float = 0.8):
        """
        Initialize cost tracker.

        Args:
            max_budget_usd: Maximum allowed budget in USD
            warning_threshold: Fraction of budget at which to warn (0.0-1.0)
        """
        self.max_budget_usd = max_budget_usd
        self.warning_threshold = warning_threshold
        self.cumulative_cost_usd = 0.0
        self.warning_issued = False

    def add_usage(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int
    ) -> float:
        """
        Add API usage and compute cost.

        Args:
            model: Model identifier
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens

        Returns:
            Cost in USD for this usage
        """
        if model not in self.PRICING:
            # Default to Sonnet pricing if unknown
            model = "claude-3-5-sonnet-20241022"

        pricing = self.PRICING[model]
        cost = (input_tokens * pricing["input"] / 1_000_000) + \
               (output_tokens * pricing["output"] / 1_000_000)

        self.cumulative_cost_usd += cost

        # Check for warning threshold
        if not self.warning_issued and self.cumulative_cost_usd >= (self.max_budget_usd * self.warning_threshold):
            self.warning_issued = True
            print(f"⚠️  WARNING: {self.get_budget_used_percent():.1f}% of budget used (${self.cumulative_cost_usd:.2f} / ${self.max_budget_usd:.2f})")

        return cost

    def check_budget(self) -> bool:
        """
        Check if budget limit has been exceeded.

        Returns:
            True if within budget, False if exceeded
        """
        return self.cumulative_cost_usd < self.max_budget_usd

    def get_remaining_budget(self) -> float:
        """Get remaining budget in USD."""
        return max(0.0, self.max_budget_usd - self.cumulative_cost_usd)

    def get_budget_used_percent(self) -> float:
        """Get percentage of budget used."""
        return (self.cumulative_cost_usd / self.max_budget_usd) * 100

    def get_cumulative_cost(self) -> float:
        """Get total cost so far."""
        return self.cumulative_cost_usd

    def estimate_cost(
        self,
        model: str,
        estimated_input_tokens: int,
        estimated_output_tokens: int
    ) -> float:
        """
        Estimate cost without adding to tracker.

        Args:
            model: Model identifier
            estimated_input_tokens: Estimated input tokens
            estimated_output_tokens: Estimated output tokens

        Returns:
            Estimated cost in USD
        """
        if model not in self.PRICING:
            model = "claude-3-5-sonnet-20241022"

        pricing = self.PRICING[model]
        return (estimated_input_tokens * pricing["input"] / 1_000_000) + \
               (estimated_output_tokens * pricing["output"] / 1_000_000)

    def can_afford(
        self,
        model: str,
        estimated_input_tokens: int,
        estimated_output_tokens: int
    ) -> bool:
        """
        Check if we can afford an upcoming API call.

        Args:
            model: Model identifier
            estimated_input_tokens: Estimated input tokens
            estimated_output_tokens: Estimated output tokens

        Returns:
            True if cost would be within budget, False otherwise
        """
        estimated_cost = self.estimate_cost(model, estimated_input_tokens, estimated_output_tokens)
        return (self.cumulative_cost_usd + estimated_cost) <= self.max_budget_usd
