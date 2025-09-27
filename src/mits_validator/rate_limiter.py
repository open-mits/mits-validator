"""Rate limiting and request throttling for MITS Validator."""

import asyncio
import time

import structlog
from fastapi import HTTPException, Request, status

logger = structlog.get_logger(__name__)


class RateLimiter:
    """Token bucket rate limiter implementation."""

    def __init__(
        self,
        max_requests: int = 100,
        time_window: int = 60,  # seconds
        burst_limit: int = 10,
    ):
        """Initialize rate limiter.

        Args:
            max_requests: Maximum requests per time window
            time_window: Time window in seconds
            burst_limit: Maximum burst requests
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.burst_limit = burst_limit
        self.tokens = max_requests
        self.last_update = time.time()
        self._lock = asyncio.Lock()

    async def is_allowed(self, client_id: str) -> tuple[bool, dict[str, int]]:
        """Check if request is allowed for client.

        Returns:
            Tuple of (is_allowed, rate_limit_info)
        """
        async with self._lock:
            now = time.time()
            time_passed = now - self.last_update

            # Add tokens based on time passed
            tokens_to_add = time_passed * (self.max_requests / self.time_window)
            self.tokens = min(self.max_requests, self.tokens + tokens_to_add)
            self.last_update = now

            # Check if request is allowed
            if self.tokens >= 1:
                self.tokens -= 1
                return True, {
                    "limit": self.max_requests,
                    "remaining": int(self.tokens),
                    "reset_time": int(now + self.time_window),
                }
            else:
                return False, {
                    "limit": self.max_requests,
                    "remaining": 0,
                    "reset_time": int(now + self.time_window),
                }


class ClientRateLimiter:
    """Rate limiter that tracks individual clients."""

    def __init__(
        self,
        max_requests: int = 100,
        time_window: int = 60,
        max_clients: int = 1000,
        cleanup_interval: int = 300,  # 5 minutes
    ):
        """Initialize client rate limiter.

        Args:
            max_requests: Maximum requests per time window per client
            time_window: Time window in seconds
            max_clients: Maximum number of clients to track
            cleanup_interval: Cleanup interval for old clients in seconds
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.max_clients = max_clients
        self.cleanup_interval = cleanup_interval
        self.clients: dict[str, RateLimiter] = {}
        self.last_cleanup = time.time()
        self._lock = asyncio.Lock()

    async def is_allowed(self, client_id: str) -> tuple[bool, dict[str, int]]:
        """Check if request is allowed for client."""
        async with self._lock:
            # Cleanup old clients if needed
            await self._cleanup_if_needed()

            # Get or create rate limiter for client
            if client_id not in self.clients:
                if len(self.clients) >= self.max_clients:
                    # Remove oldest client (simple FIFO)
                    oldest_client = next(iter(self.clients))
                    del self.clients[oldest_client]

                self.clients[client_id] = RateLimiter(
                    max_requests=self.max_requests, time_window=self.time_window
                )

            return await self.clients[client_id].is_allowed(client_id)

    async def _cleanup_if_needed(self) -> None:
        """Cleanup old clients if cleanup interval has passed."""
        now = time.time()
        if now - self.last_cleanup > self.cleanup_interval:
            # Remove clients that haven't been active
            clients_to_remove = []
            for client_id, limiter in self.clients.items():
                if now - limiter.last_update > self.time_window * 2:
                    clients_to_remove.append(client_id)

            for client_id in clients_to_remove:
                del self.clients[client_id]

            self.last_cleanup = now
            logger.debug("Cleaned up inactive clients", removed_count=len(clients_to_remove))

    def get_stats(self) -> dict[str, int]:
        """Get rate limiter statistics."""
        return {
            "active_clients": len(self.clients),
            "max_clients": self.max_clients,
            "max_requests_per_window": self.max_requests,
            "time_window_seconds": self.time_window,
        }


class RequestThrottler:
    """Request throttler to prevent system overload."""

    def __init__(
        self,
        max_concurrent: int = 50,
        max_queue_size: int = 100,
        queue_timeout: int = 30,  # seconds
    ):
        """Initialize request throttler.

        Args:
            max_concurrent: Maximum concurrent requests
            max_queue_size: Maximum queue size
            queue_timeout: Queue timeout in seconds
        """
        self.max_concurrent = max_concurrent
        self.max_queue_size = max_queue_size
        self.queue_timeout = queue_timeout
        self.active_requests = 0
        self.request_queue = asyncio.Queue(maxsize=max_queue_size)
        self._lock = asyncio.Lock()

    async def acquire(self, request_id: str) -> bool:
        """Acquire permission to process request.

        Returns:
            True if request can be processed, False if throttled
        """
        async with self._lock:
            if self.active_requests < self.max_concurrent:
                self.active_requests += 1
                logger.debug(
                    "Request acquired", request_id=request_id, active_requests=self.active_requests
                )
                return True
            else:
                # Try to queue request
                try:
                    await asyncio.wait_for(
                        self.request_queue.put(request_id), timeout=self.queue_timeout
                    )
                    logger.debug(
                        "Request queued",
                        request_id=request_id,
                        queue_size=self.request_queue.qsize(),
                    )
                    return True
                except TimeoutError:
                    logger.warning("Request throttled - queue timeout", request_id=request_id)
                    return False

    async def release(self, request_id: str) -> None:
        """Release request and process next queued request."""
        async with self._lock:
            self.active_requests = max(0, self.active_requests - 1)

            # Process next queued request if any
            if not self.request_queue.empty():
                try:
                    next_request_id = self.request_queue.get_nowait()
                    self.active_requests += 1
                    logger.debug("Next request processed from queue", request_id=next_request_id)
                except asyncio.QueueEmpty:
                    pass

            logger.debug(
                "Request released", request_id=request_id, active_requests=self.active_requests
            )

    def get_stats(self) -> dict[str, int]:
        """Get throttler statistics."""
        return {
            "active_requests": self.active_requests,
            "max_concurrent": self.max_concurrent,
            "queue_size": self.request_queue.qsize(),
            "max_queue_size": self.max_queue_size,
        }


# Global instances
_rate_limiter: ClientRateLimiter | None = None
_throttler: RequestThrottler | None = None


def get_rate_limiter() -> ClientRateLimiter:
    """Get or create global rate limiter."""
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = ClientRateLimiter()
    return _rate_limiter


def get_throttler() -> RequestThrottler:
    """Get or create global request throttler."""
    global _throttler
    if _throttler is None:
        _throttler = RequestThrottler()
    return _throttler


async def check_rate_limit(request: Request) -> None:
    """Check rate limit for request and raise exception if exceeded."""
    # Get client identifier (IP address for now)
    client_ip = request.client.host if request.client else "unknown"

    rate_limiter = get_rate_limiter()
    is_allowed, rate_info = await rate_limiter.is_allowed(client_ip)

    if not is_allowed:
        logger.warning("Rate limit exceeded", client_ip=client_ip, rate_info=rate_info)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "error": "Rate limit exceeded",
                "retry_after": rate_info["reset_time"],
                "limit": rate_info["limit"],
                "remaining": rate_info["remaining"],
            },
        )


async def check_throttle_limit(request_id: str) -> bool:
    """Check throttle limit for request.

    Returns:
        True if request can be processed, False if throttled
    """
    throttler = get_throttler()
    return await throttler.acquire(request_id)


async def release_throttle_limit(request_id: str) -> None:
    """Release throttle limit for request."""
    throttler = get_throttler()
    await throttler.release(request_id)
