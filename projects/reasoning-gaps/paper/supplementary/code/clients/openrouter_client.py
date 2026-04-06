"""OpenRouter API client for ReasonGap evaluation.

Thin wrapper over OpenAIClient pointing at OpenRouter's API.
Supports all models available on OpenRouter (Llama, Mistral, Qwen, etc.)
via a single API key.
"""

from __future__ import annotations

import logging
import os
from typing import Any

from .openai_client import OpenAIClient

logger = logging.getLogger(__name__)

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# Pricing per 1M tokens (USD) — OpenRouter prices as of 2026-03.
# Used for cost tracking only; actual billing is via OpenRouter dashboard.
OPENROUTER_PRICING: dict[str, dict[str, float]] = {
    "meta-llama/llama-3.1-8b-instruct": {"input": 0.06, "output": 0.06},
    "meta-llama/llama-3.1-70b-instruct": {"input": 0.52, "output": 0.75},
    "mistralai/mistral-7b-instruct-v0.3": {"input": 0.06, "output": 0.06},
    "mistralai/mistral-small-24b-instruct-2501": {"input": 0.14, "output": 0.14},
    "qwen/qwen-2.5-7b-instruct": {"input": 0.10, "output": 0.10},
    "qwen/qwen-2.5-72b-instruct": {"input": 0.31, "output": 0.31},
}


class OpenRouterClient(OpenAIClient):
    """OpenRouter client — routes to open-source models via openrouter.ai.

    Uses the same OpenAI-compatible chat completions API.
    """

    def __init__(
        self,
        model_name: str,
        *,
        api_key: str | None = None,
        max_rpm: int = 60,
        timeout: float = 120.0,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            model_name,
            api_key=api_key,
            base_url=OPENROUTER_BASE_URL,
            api_key_env="OPENROUTER_API_KEY",
            max_rpm=max_rpm,
            timeout=timeout,
            **kwargs,
        )

    def _compute_cost(self, input_tokens: int, output_tokens: int) -> float:
        pricing = OPENROUTER_PRICING.get(self.model_name)
        if not pricing:
            logger.warning(
                "No pricing info for OpenRouter model %s; cost will be estimated at 0",
                self.model_name,
            )
            return 0.0
        return (
            input_tokens * pricing["input"] / 1_000_000
            + output_tokens * pricing["output"] / 1_000_000
        )
