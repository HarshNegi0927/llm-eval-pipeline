"""A rate limiter that respects BOTH requests-per-minute AND
tokens-per-minute, and does so SAFELY under concurrency.

Token cost isn't known until a call completes — so naively checking "is
recorded usage under budget?" and only recording AFTER the call finishes
has a race: several concurrent callers can all see the same (stale, lower)
recorded total, all judge themselves safe, and all fire together, jointly
overshooting the provider's real limit before any of them has recorded
anything. This bit a real run at ~5895/6000 tokens used.

The fix: reserve() charges a conservative ESTIMATE against the budget the
moment it's granted, inside the same lock — so the very next concurrent
caller sees the updated running total, not the stale one. Once the real
response comes back, record() trues the estimate up to the actual count.
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
        # Each entry is a mutable [timestamp, tokens] pair (not a tuple) so
        # record() can true up the estimate to the real count in place,
        # without disturbing its position in the window.
        self._token_events: deque[list] = deque()
        self._lock = asyncio.Lock()

    def _prune(self, now: float) -> None:
        cutoff = now - self._window
        while self._request_times and self._request_times[0] < cutoff:
            self._request_times.popleft()
        while self._token_events and self._token_events[0][0] < cutoff:
            self._token_events.popleft()

    async def reserve(self, estimated_tokens: int) -> list:
        """Blocks until issuing one more request — counting
        `estimated_tokens` as a conservative placeholder — would stay under
        both budgets, then immediately reserves a request slot AND a
        provisional token slot. Returns the token-event entry; pass it to
        record() once the real token count is known."""
        while True:
            sleep_for = 0.0
            async with self._lock:
                now = time.monotonic()
                self._prune(now)
                tokens_used = sum(t for _, t in self._token_events)
                requests_used = len(self._request_times)

                if (
                    requests_used < self._max_requests
                    and tokens_used + estimated_tokens <= self._max_tokens
                ):
                    self._request_times.append(now)
                    entry = [now, estimated_tokens]
                    self._token_events.append(entry)
                    return entry

                candidates = []
                if self._request_times:
                    candidates.append(self._request_times[0] + self._window - now)
                if self._token_events:
                    candidates.append(self._token_events[0][0] + self._window - now)
                sleep_for = max(0.05, min(candidates) if candidates else 0.5)
            await asyncio.sleep(sleep_for)

    async def record(self, entry: list, actual_tokens: int) -> None:
        """Trues up a reservation with the real token count once known.
        If the call failed and this never gets called, the conservative
        estimate just ages out of the window on its own — safer than
        under-counting a call that might have partially consumed quota."""
        async with self._lock:
            entry[1] = actual_tokens
