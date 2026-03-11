"""vLLM (OpenAI-compatible) API client for ReasonGap evaluation."""

from __future__ import annotations

import logging
import os
import threading
import time
from typing import Any

import httpx
from tenacity import (
    retry,
    retry_if_exception,
    stop_after_attempt,
    wait_exponential,
)

from evaluate import ModelClient

logger = logging.getLogger(__name__)


def _is_retryable(exc: BaseException) -> bool:
    """Check if an HTTP error is retryable (429, 500, 529)."""
    if isinstance(exc, httpx.HTTPStatusError):
        return exc.response.status_code in (429, 500, 529)
    if isinstance(exc, (httpx.ConnectError, httpx.ReadTimeout)):
        return True
    return False


class VLLMClient(ModelClient):
    """vLLM OpenAI-compatible API client.

    Connects to a local or remote vLLM server that exposes an
    OpenAI-compatible ``/v1/chat/completions`` endpoint.

    No cost tracking (local inference).
    Thread-safe.
    """

    def __init__(
        self,
        model_name: str,
        *,
        base_url: str | None = None,
        timeout: float = 300.0,
        max_rpm: int = 60,
        **kwargs: Any,
    ) -> None:
        super().__init__(model_name, **kwargs)
        self._base_url = (
            base_url
            or os.environ.get("VLLM_BASE_URL")
            or "http://localhost:8000/v1"
        )
        # Strip trailing slash for consistent URL building
        self._base_url = self._base_url.rstrip("/")
        self._timeout = timeout
        self._client = httpx.Client(timeout=timeout)

        # Token tracking (protected by lock)
        self._lock = threading.Lock()
        self._total_input_tokens = 0
        self._total_output_tokens = 0

        # Token-bucket rate limiter
        self._rate_lock = threading.Lock()
        self._tokens = float(max_rpm)
        self._max_tokens_bucket = float(max_rpm)
        self._last_refill = time.monotonic()
        self._refill_rate = max_rpm / 60.0

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

            time.sleep(0.05)

    # -- Properties ----------------------------------------------------

    @property
    def total_tokens(self) -> int:
        with self._lock:
            return self._total_input_tokens + self._total_output_tokens

    @property
    def total_cost_usd(self) -> float:
        """vLLM is local inference; cost is always 0."""
        return 0.0

    def get_cost(self) -> float:
        """Return cumulative USD spent (always 0 for local inference)."""
        return 0.0

    # -- Query ---------------------------------------------------------

    def query(
        self,
        prompt: str,
        system_prompt: str = "",
        max_tokens: int = 512,
    ) -> tuple[str, float]:
        """Send prompt to vLLM server and return (response_text, latency_ms)."""
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
        messages: list[dict[str, str]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model_name,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": 0,
            "top_p": 1.0,
            "seed": 42,
        }

        start = time.perf_counter()
        resp = self._client.post(
            f"{self._base_url}/chat/completions",
            json=payload,
        )
        resp.raise_for_status()
        latency_ms = (time.perf_counter() - start) * 1000

        data = resp.json()

        # Extract text
        response_text = data["choices"][0]["message"]["content"] or ""

        # Track tokens if available
        usage = data.get("usage", {})
        input_tokens = usage.get("prompt_tokens", 0)
        output_tokens = usage.get("completion_tokens", 0)

        with self._lock:
            self._total_input_tokens += input_tokens
            self._total_output_tokens += output_tokens

        return response_text, latency_ms
