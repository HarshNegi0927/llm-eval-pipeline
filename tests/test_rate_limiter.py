"""Tests for RateLimiter. Uses small window_seconds so tests stay fast —
logic is identical at a real 60s window, we just don't want to wait 60s.
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
            await limiter.reserve(estimated_tokens=10)
        return time.monotonic() - start

    elapsed = asyncio.run(_run())
    assert elapsed < 0.2


def test_reserve_blocks_once_request_budget_is_exhausted():
    async def _run():
        limiter = RateLimiter(
            max_requests_per_minute=2, max_tokens_per_minute=1_000_000, window_seconds=0.3
        )
        await limiter.reserve(estimated_tokens=10)
        await limiter.reserve(estimated_tokens=10)
        start = time.monotonic()
        await limiter.reserve(estimated_tokens=10)  # 3rd call must wait
        return time.monotonic() - start

    elapsed = asyncio.run(_run())
    assert elapsed >= 0.2


def test_reserve_blocks_once_token_budget_would_be_exceeded():
    async def _run():
        limiter = RateLimiter(
            max_requests_per_minute=1_000, max_tokens_per_minute=100, window_seconds=0.3
        )
        await limiter.reserve(estimated_tokens=60)
        start = time.monotonic()
        await limiter.reserve(estimated_tokens=60)  # 60+60=120 > 100 — must wait
        return time.monotonic() - start

    elapsed = asyncio.run(_run())
    assert elapsed >= 0.2


def test_concurrent_reservations_cannot_jointly_exceed_token_budget():
    """Regression test for the exact bug that broke a real run: two
    concurrent reserve() calls both checking against the same *recorded*
    (pre-reservation) total could both pass at once and jointly overshoot
    the real limit. Each reserve() must charge its estimate immediately so
    the other concurrent caller sees the updated total and waits."""
    async def _run():
        limiter = RateLimiter(
            max_requests_per_minute=1_000, max_tokens_per_minute=100, window_seconds=0.3
        )
        start = time.monotonic()
        await asyncio.gather(
            limiter.reserve(estimated_tokens=60),
            limiter.reserve(estimated_tokens=60),  # combined 120 > 100
        )
        return time.monotonic() - start

    elapsed = asyncio.run(_run())
    # If both slipped through instantly (the bug), elapsed would be ~0.
    assert elapsed >= 0.2


def test_record_trues_up_the_estimate_to_the_real_count():
    async def _run():
        limiter = RateLimiter(
            max_requests_per_minute=1_000, max_tokens_per_minute=100, window_seconds=0.3
        )
        entry = await limiter.reserve(estimated_tokens=10)  # placeholder guess
        await limiter.record(entry, actual_tokens=90)  # real usage was much higher

        start = time.monotonic()
        await limiter.reserve(estimated_tokens=20)  # 90+20=110 > 100 — must wait
        return time.monotonic() - start

    elapsed = asyncio.run(_run())
    assert elapsed >= 0.2


def test_old_events_are_pruned_outside_the_window():
    async def _run():
        limiter = RateLimiter(
            max_requests_per_minute=1, max_tokens_per_minute=1_000_000, window_seconds=0.2
        )
        await limiter.reserve(estimated_tokens=10)
        await asyncio.sleep(0.25)  # let the window fully clear
        start = time.monotonic()
        await limiter.reserve(estimated_tokens=10)  # should be immediate
        return time.monotonic() - start

    elapsed = asyncio.run(_run())
    assert elapsed < 0.1
