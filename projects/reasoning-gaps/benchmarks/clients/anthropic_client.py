"""Anthropic API client for ReasonGap evaluation."""

from __future__ import annotations

import logging
import os
import threading
import time
from typing import Any

import anthropic
from tenacity import (
    retry,
    retry_if_exception,
    stop_after_attempt,
    wait_exponential,
)

# Resolve the evaluate module's ModelClient via relative import
from evaluate import ModelClient

logger = logging.getLogger(__name__)

# Pricing per 1M tokens (USD)
ANTHROPIC_PRICING: dict[str, dict[str, float]] = {
    "claude-haiku-4-5-20251001": {"input": 0.80, "output": 4.00},
    "claude-sonnet-4-6-20250514": {"input": 3.00, "output": 15.00},
    "claude-opus-4-6-20250514": {"input": 15.00, "output": 75.00},
}


def _is_retryable(exc: BaseException) -> bool:
    """Check if an Anthropic error is retryable (429, 500, 529)."""
    if isinstance(exc, anthropic.RateLimitError):
        return True
    if isinstance(exc, anthropic.InternalServerError):
        return True
    if isinstance(exc, anthropic.APIStatusError) and exc.status_code == 529:
        return True
    return False


class AnthropicClient(ModelClient):
    """Anthropic Claude API client with rate limiting, retry, and cost tracking.

    Thread-safe: all mutable state is protected by locks.
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
        super().__init__(model_name, **kwargs)
        key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not key:
            raise ValueError(
                "Anthropic API key required. Set ANTHROPIC_API_KEY env var "
                "or pass api_key parameter."
            )
        self._client = anthropic.Anthropic(api_key=key, timeout=timeout)
        self._max_rpm = max_rpm
        self._timeout = timeout

        # Cost tracking (protected by lock)
        self._lock = threading.Lock()
        self._total_input_tokens = 0
        self._total_output_tokens = 0
        self._total_cost = 0.0

        # Token-bucket rate limiter
        self._rate_lock = threading.Lock()
        self._tokens = float(max_rpm)
        self._max_tokens_bucket = float(max_rpm)
        self._last_refill = time.monotonic()
        self._refill_rate = max_rpm / 60.0  # tokens per second

    # -- Rate limiter --------------------------------------------------

    def _wait_for_rate_limit(self) -> None:
        """Block until a rate-limit token is available."""
        while True:
            with self._rate_lock:
                now = time.monotonic()
                elapsed = now - self._last_refill
                self._tokens = min(
                    self._max_tokens_bucket,
                    self._tokens + elapsed * self._refill_rate,
                )
                self._last_refill = now

                if self._tokens >= 1.0:
                    self._tokens -= 1.0
                    return

            # Sleep briefly before retrying
            time.sleep(0.05)

    # -- Cost helpers --------------------------------------------------

    def _compute_cost(self, input_tokens: int, output_tokens: int) -> float:
        pricing = ANTHROPIC_PRICING.get(self.model_name)
        if not pricing:
            logger.warning(
                "No pricing info for model %s; cost will be estimated at 0",
                self.model_name,
            )
            return 0.0
        return (
            input_tokens * pricing["input"] / 1_000_000
            + output_tokens * pricing["output"] / 1_000_000
        )

    @property
    def total_tokens(self) -> int:
        with self._lock:
            return self._total_input_tokens + self._total_output_tokens

    @property
    def total_cost_usd(self) -> float:
        with self._lock:
            return self._total_cost

    def get_cost(self) -> float:
        """Return cumulative USD spent."""
        return self.total_cost_usd

    # -- Query ---------------------------------------------------------

    def query(
        self,
        prompt: str,
        system_prompt: str = "",
        max_tokens: int = 512,
    ) -> tuple[str, float]:
        """Send prompt to Anthropic Claude and return (response_text, latency_ms)."""
        self._wait_for_rate_limit()
        return self._query_with_retry(prompt, system_prompt, max_tokens)

    @retry(
        retry=retry_if_exception(_is_retryable),
        wait=wait_exponential(multiplier=1, min=1, max=60),
        stop=stop_after_attempt(5),
        reraise=True,
    )
    def _query_with_retry(
        self,
        prompt: str,
        system_prompt: str,
        max_tokens: int,
    ) -> tuple[str, float]:
        """Inner query with tenacity retry on transient errors."""
        messages = [{"role": "user", "content": prompt}]

        kwargs: dict[str, Any] = {
            "model": self.model_name,
            "max_tokens": max_tokens,
            "messages": messages,
        }
        if system_prompt:
            kwargs["system"] = system_prompt

        start = time.perf_counter()
        response = self._client.messages.create(**kwargs)
        latency_ms = (time.perf_counter() - start) * 1000

        # Extract text
        text_parts = []
        for block in response.content:
            if block.type == "text":
                text_parts.append(block.text)
        response_text = "\n".join(text_parts)

        # Track tokens and cost
        input_tokens = response.usage.input_tokens
        output_tokens = response.usage.output_tokens
        cost = self._compute_cost(input_tokens, output_tokens)

        with self._lock:
            self._total_input_tokens += input_tokens
            self._total_output_tokens += output_tokens
            self._total_cost += cost

        return response_text, latency_ms
