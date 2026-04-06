"""Thread-safe token-bucket rate limiter mixin for API clients."""

from __future__ import annotations

import threading
import time


class RateLimiterMixin:
    """Mixin that adds a token-bucket rate limiter to an API client.

    Call ``_init_rate_limiter(max_rpm)`` in your ``__init__`` and then
    call ``_wait_for_rate_limit()`` before each API request.

    Thread-safe: all mutable state is protected by a lock.
    """

    def _init_rate_limiter(self, max_rpm: int) -> None:
        """Initialise the token-bucket state.

        Args:
            max_rpm: Maximum requests per minute.
        """
        self._rate_lock = threading.Lock()
        self._tokens = float(max_rpm)
        self._max_tokens_bucket = float(max_rpm)
        self._last_refill = time.monotonic()
        self._refill_rate = max_rpm / 60.0  # tokens per second

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
