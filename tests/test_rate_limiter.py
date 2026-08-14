"""Tests for RateLimiter. Uses a small window_seconds so tests stay fast —
the logic is identical at 60s, we just don't want to actually wait 60s here.
"""
import asyncio
import time

from src.rate_limiter import RateLimiter


def test_reserve_allows_calls_under_the_request_cap():
    async def _run():
        limiter = RateLimiter(
            max_requests_per_minute=5, max_tokens_per_minute=1_000_000, window_seconds=1.0
        )
        start = time.monotonic()
        for _ in range(5):
            await limiter.reserve()
        return time.monotonic() - start

    elapsed = asyncio.run(_run())
    assert elapsed < 0.2  # all 5 fit in budget, should return near-instantly


def test_reserve_blocks_once_request_budget_is_exhausted():
    async def _run():
        limiter = RateLimiter(
            max_requests_per_minute=2, max_tokens_per_minute=1_000_000, window_seconds=0.3
        )
        await limiter.reserve()
        await limiter.reserve()
        start = time.monotonic()
        await limiter.reserve()  # 3rd call must wait for the window to clear
        return time.monotonic() - start

    elapsed = asyncio.run(_run())
    assert elapsed >= 0.2


def test_record_charges_token_budget_and_reserve_blocks_when_exhausted():
    async def _run():
        limiter = RateLimiter(
            max_requests_per_minute=1_000, max_tokens_per_minute=100, window_seconds=0.3
        )
        await limiter.reserve()
        await limiter.record(95)  # nearly exhausts the 100-token budget

        await limiter.reserve()  # still allowed: 95 < 100
        await limiter.record(20)  # now 115 > 100, budget exceeded

        start = time.monotonic()
        await limiter.reserve()  # must wait for the window to clear
        return time.monotonic() - start

    elapsed = asyncio.run(_run())
    assert elapsed >= 0.2


def test_old_events_are_pruned_outside_the_window():
    async def _run():
        limiter = RateLimiter(
            max_requests_per_minute=1, max_tokens_per_minute=1_000_000, window_seconds=0.2
        )
        await limiter.reserve()
        await asyncio.sleep(0.25)  # let the window fully clear
        start = time.monotonic()
        await limiter.reserve()  # should be immediate — old event is pruned
        return time.monotonic() - start

    elapsed = asyncio.run(_run())
    assert elapsed < 0.1
