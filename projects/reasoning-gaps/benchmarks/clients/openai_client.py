"""OpenAI API client for ReasonGap evaluation."""

from __future__ import annotations

import logging
import os
import threading
import time
from typing import Any

import openai
from tenacity import (
    retry,
    retry_if_exception,
    stop_after_attempt,
    wait_exponential,
)

from evaluate import ModelClient

logger = logging.getLogger(__name__)

# Pricing per 1M tokens (USD)
OPENAI_PRICING: dict[str, dict[str, float]] = {
    "gpt-4o-mini": {"input": 0.15, "output": 0.60},
    "gpt-4o": {"input": 2.50, "output": 10.00},
    "o3": {"input": 10.00, "output": 40.00},
}

# Models that use the "reasoning" API style (no system prompt, different params)
REASONING_MODELS = {"o3"}


def _is_retryable(exc: BaseException) -> bool:
    """Check if an OpenAI error is retryable (429, 500, 529)."""
    if isinstance(exc, openai.RateLimitError):
        return True
    if isinstance(exc, openai.InternalServerError):
        return True
    if isinstance(exc, openai.APIStatusError) and getattr(exc, "status_code", 0) == 529:
        return True
    return False


class OpenAIClient(ModelClient):
    """OpenAI API client with rate limiting, retry, and cost tracking.

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
        key = api_key or os.environ.get("OPENAI_API_KEY")
        if not key:
            raise ValueError(
                "OpenAI API key required. Set OPENAI_API_KEY env var "
                "or pass api_key parameter."
            )
        self._client = openai.OpenAI(api_key=key, timeout=timeout)
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
        pricing = OPENAI_PRICING.get(self.model_name)
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
        """Send prompt to OpenAI and return (response_text, latency_ms)."""
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
        is_reasoning = self.model_name in REASONING_MODELS

        if is_reasoning:
            # Reasoning models (o3) don't support system messages;
            # fold the system prompt into the user message.
            combined = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
            messages = [{"role": "user", "content": combined}]
            kwargs: dict[str, Any] = {
                "model": self.model_name,
                "messages": messages,
                "max_completion_tokens": max_tokens,
            }
        else:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            kwargs = {
                "model": self.model_name,
                "messages": messages,
                "max_tokens": max_tokens,
            }

        start = time.perf_counter()
        response = self._client.chat.completions.create(**kwargs)
        latency_ms = (time.perf_counter() - start) * 1000

        # Extract text
        choice = response.choices[0]
        response_text = choice.message.content or ""

        # Track tokens and cost
        usage = response.usage
        input_tokens = usage.prompt_tokens if usage else 0
        output_tokens = usage.completion_tokens if usage else 0
        cost = self._compute_cost(input_tokens, output_tokens)

        with self._lock:
            self._total_input_tokens += input_tokens
            self._total_output_tokens += output_tokens
            self._total_cost += cost

        return response_text, latency_ms
