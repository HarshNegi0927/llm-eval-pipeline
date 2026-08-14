"""A rate limiter that respects BOTH requests-per-minute AND
tokens-per-minute — because a provider's free tier (Groq's included) caps
on both axes independently, and you can trip either one first.

An asyncio.Semaphore alone only caps how many calls are in flight at once.
It says nothing about how many requests or tokens you've fired in the
trailing 60 seconds, which is what the provider actually measures. This
class tracks both in a rolling window and blocks new calls until issuing
one more would stay under both budgets.

Token cost isn't known until AFTER a call completes (that's when the API
tells you how many tokens it used) — so the usage is: call reserve()
before making the request, then record(actual_tokens) after, once you have
the real number from the response.
"""
from __future__ import annotations

import asyncio
import time
from collections import deque


class RateLimiter:
    def __init__(
        self,
        max_requests_per_minute: int,
        max_tokens_per_minute: int,
        window_seconds: float = 60.0,
    ):
        self._max_requests = max_requests_per_minute
        self._max_tokens = max_tokens_per_minute
        self._window = window_seconds
        self._request_times: deque[float] = deque()
        self._token_events: deque[tuple[float, int]] = deque()
        self._lock = asyncio.Lock()

    def _prune(self, now: float) -> None:
        cutoff = now - self._window
        while self._request_times and self._request_times[0] < cutoff:
            self._request_times.popleft()
        while self._token_events and self._token_events[0][0] < cutoff:
            self._token_events.popleft()

    async def reserve(self) -> None:
        """Blocks until one more request would stay under both budgets for
        the trailing window, then reserves a request slot."""
        while True:
            sleep_for = 0.0
            async with self._lock:
                now = time.monotonic()
                self._prune(now)
                tokens_used = sum(t for _, t in self._token_events)
                requests_used = len(self._request_times)

                if requests_used < self._max_requests and tokens_used < self._max_tokens:
                    self._request_times.append(now)
                    return

                candidates = []
                if self._request_times:
                    candidates.append(self._request_times[0] + self._window - now)
                if self._token_events:
                    candidates.append(self._token_events[0][0] + self._window - now)
                sleep_for = max(0.05, min(candidates) if candidates else 0.5)
            await asyncio.sleep(sleep_for)

    async def record(self, tokens_used: int) -> None:
        """Charges real token usage against the rolling window once a call
        has completed and the actual count is known."""
        async with self._lock:
            self._token_events.append((time.monotonic(), tokens_used))
