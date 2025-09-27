"""Tests for rate limiting functionality."""

import pytest
from mits_validator.rate_limiter import (
    ClientRateLimiter,
    RateLimiter,
    RequestThrottler,
    get_rate_limiter,
    get_throttler,
)


class TestRateLimiter:
    """Test basic rate limiter functionality."""

    @pytest.mark.asyncio
    async def test_rate_limiter_initialization(self):
        """Test rate limiter initialization."""
        limiter = RateLimiter(max_requests=10, time_window=60)
        assert limiter.max_requests == 10
        assert limiter.time_window == 60
        assert limiter.tokens == 10

    @pytest.mark.asyncio
    async def test_rate_limiter_allows_requests(self):
        """Test that rate limiter allows requests within limit."""
        limiter = RateLimiter(max_requests=5, time_window=60)

        # Should allow first few requests
        for i in range(5):
            allowed, info = await limiter.is_allowed("client1")
            assert allowed
            assert info["remaining"] == 4 - i

    @pytest.mark.asyncio
    async def test_rate_limiter_blocks_excess_requests(self):
        """Test that rate limiter blocks excess requests."""
        limiter = RateLimiter(max_requests=2, time_window=60)

        # Allow first 2 requests
        allowed1, _ = await limiter.is_allowed("client1")
        allowed2, _ = await limiter.is_allowed("client1")
        assert allowed1 and allowed2

        # Block third request
        allowed3, info = await limiter.is_allowed("client1")
        assert not allowed3
        assert info["remaining"] == 0


class TestClientRateLimiter:
    """Test client-specific rate limiter."""

    @pytest.mark.asyncio
    async def test_client_rate_limiter_initialization(self):
        """Test client rate limiter initialization."""
        limiter = ClientRateLimiter(max_requests=10, time_window=60)
        assert limiter.max_requests == 10
        assert limiter.time_window == 60
        assert len(limiter.clients) == 0

    @pytest.mark.asyncio
    async def test_client_rate_limiter_tracks_clients(self):
        """Test that rate limiter tracks different clients separately."""
        limiter = ClientRateLimiter(max_requests=2, time_window=60)

        # Client 1 should be allowed
        allowed1, _ = await limiter.is_allowed("client1")
        assert allowed1

        # Client 2 should also be allowed (separate limit)
        allowed2, _ = await limiter.is_allowed("client2")
        assert allowed2

        # Both clients should have separate limits
        assert len(limiter.clients) == 2

    @pytest.mark.asyncio
    async def test_client_rate_limiter_stats(self):
        """Test client rate limiter statistics."""
        limiter = ClientRateLimiter(max_requests=10, time_window=60)

        stats = limiter.get_stats()
        assert "active_clients" in stats
        assert "max_clients" in stats
        assert "max_requests_per_window" in stats
        assert "time_window_seconds" in stats


class TestRequestThrottler:
    """Test request throttler functionality."""

    @pytest.mark.asyncio
    async def test_request_throttler_initialization(self):
        """Test request throttler initialization."""
        throttler = RequestThrottler(max_concurrent=5, max_queue_size=10)
        assert throttler.max_concurrent == 5
        assert throttler.max_queue_size == 10
        assert throttler.active_requests == 0

    @pytest.mark.asyncio
    async def test_request_throttler_allows_requests(self):
        """Test that throttler allows requests within limit."""
        throttler = RequestThrottler(max_concurrent=3, max_queue_size=5)

        # Should allow requests up to max_concurrent
        for i in range(3):
            allowed = await throttler.acquire(f"request-{i}")
            assert allowed
            assert throttler.active_requests == i + 1

    @pytest.mark.asyncio
    async def test_request_throttler_releases_requests(self):
        """Test that throttler properly releases requests."""
        throttler = RequestThrottler(max_concurrent=2, max_queue_size=5)

        # Acquire requests
        await throttler.acquire("request-1")
        await throttler.acquire("request-2")
        assert throttler.active_requests == 2

        # Release one request
        await throttler.release("request-1")
        assert throttler.active_requests == 1

    @pytest.mark.asyncio
    async def test_request_throttler_stats(self):
        """Test request throttler statistics."""
        throttler = RequestThrottler(max_concurrent=5, max_queue_size=10)

        stats = throttler.get_stats()
        assert "active_requests" in stats
        assert "max_concurrent" in stats
        assert "queue_size" in stats
        assert "max_queue_size" in stats


class TestGlobalFunctions:
    """Test global rate limiter functions."""

    def test_get_rate_limiter(self):
        """Test getting rate limiter."""
        limiter = get_rate_limiter()
        assert isinstance(limiter, ClientRateLimiter)

    def test_get_throttler(self):
        """Test getting throttler."""
        throttler = get_throttler()
        assert isinstance(throttler, RequestThrottler)
