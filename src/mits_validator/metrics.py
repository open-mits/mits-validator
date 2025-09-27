"""Metrics and monitoring for MITS Validator."""

import time

import structlog
from prometheus_client import (
    Counter,
    Gauge,
    Histogram,
    Info,
    generate_latest,
)

logger = structlog.get_logger(__name__)

# Request metrics
REQUEST_COUNT = Counter(
    "mits_validator_requests_total",
    "Total number of validation requests",
    ["method", "endpoint", "status_code"],
)

REQUEST_DURATION = Histogram(
    "mits_validator_request_duration_seconds", "Request duration in seconds", ["method", "endpoint"]
)

VALIDATION_DURATION = Histogram(
    "mits_validator_validation_duration_seconds",
    "Validation duration in seconds",
    ["validation_level", "profile"],
)

# Validation metrics
VALIDATION_COUNT = Counter(
    "mits_validator_validations_total",
    "Total number of validations",
    ["level", "result"],  # result: valid, invalid, error
)

VALIDATION_ERRORS = Counter(
    "mits_validator_validation_errors_total",
    "Total number of validation errors",
    ["error_code", "level"],
)

# Cache metrics
CACHE_HITS = Counter(
    "mits_validator_cache_hits_total", "Total number of cache hits", ["cache_type"]
)

CACHE_MISSES = Counter(
    "mits_validator_cache_misses_total", "Total number of cache misses", ["cache_type"]
)

CACHE_SIZE = Gauge("mits_validator_cache_size_bytes", "Current cache size in bytes", ["cache_type"])

# System metrics
ACTIVE_VALIDATIONS = Gauge(
    "mits_validator_active_validations", "Number of currently active validations"
)

MEMORY_USAGE = Gauge("mits_validator_memory_usage_bytes", "Current memory usage in bytes")

# Application info
APP_INFO = Info("mits_validator_info", "Application information")


class MetricsCollector:
    """Collects and manages metrics for the MITS Validator."""

    def __init__(self):
        """Initialize metrics collector."""
        self._start_time = time.time()
        self._active_validations = 0
        self._validation_start_times: dict[str, float] = {}

    def record_request(self, method: str, endpoint: str, status_code: int, duration: float) -> None:
        """Record request metrics."""
        REQUEST_COUNT.labels(method=method, endpoint=endpoint, status_code=status_code).inc()
        REQUEST_DURATION.labels(method=method, endpoint=endpoint).observe(duration)

    def start_validation(self, validation_id: str) -> None:
        """Start tracking a validation."""
        self._active_validations += 1
        self._validation_start_times[validation_id] = time.time()
        ACTIVE_VALIDATIONS.set(self._active_validations)

    def end_validation(
        self,
        validation_id: str,
        level: str,
        profile: str,
        result: str,
        duration: float | None = None,
    ) -> None:
        """End tracking a validation."""
        self._active_validations = max(0, self._active_validations - 1)
        ACTIVE_VALIDATIONS.set(self._active_validations)

        if validation_id in self._validation_start_times:
            if duration is None:
                duration = time.time() - self._validation_start_times[validation_id]
            del self._validation_start_times[validation_id]

        VALIDATION_COUNT.labels(level=level, result=result).inc()
        VALIDATION_DURATION.labels(validation_level=level, profile=profile).observe(duration)

    def record_validation_error(self, error_code: str, level: str) -> None:
        """Record a validation error."""
        VALIDATION_ERRORS.labels(error_code=error_code, level=level).inc()

    def record_cache_hit(self, cache_type: str) -> None:
        """Record a cache hit."""
        CACHE_HITS.labels(cache_type=cache_type).inc()

    def record_cache_miss(self, cache_type: str) -> None:
        """Record a cache miss."""
        CACHE_MISSES.labels(cache_type=cache_type).inc()

    def update_cache_size(self, cache_type: str, size_bytes: int) -> None:
        """Update cache size metric."""
        CACHE_SIZE.labels(cache_type=cache_type).set(size_bytes)

    def update_memory_usage(self, memory_bytes: int) -> None:
        """Update memory usage metric."""
        MEMORY_USAGE.set(memory_bytes)

    def get_uptime(self) -> float:
        """Get application uptime in seconds."""
        return time.time() - self._start_time

    def get_metrics(self) -> str:
        """Get Prometheus metrics in text format."""
        return generate_latest().decode("utf-8")


# Global metrics collector
_metrics_collector: MetricsCollector | None = None


def get_metrics_collector() -> MetricsCollector:
    """Get or create global metrics collector."""
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector()
        # Set application info
        APP_INFO.info(
            {
                "version": "0.1.0",
                "name": "mits-validator",
                "description": "Open-source validator for MITS XML feeds",
            }
        )
    return _metrics_collector


class ValidationTimer:
    """Context manager for timing validations."""

    def __init__(self, validation_id: str, level: str, profile: str):
        """Initialize validation timer."""
        self.validation_id = validation_id
        self.level = level
        self.profile = profile
        self.start_time = None
        self.metrics = get_metrics_collector()

    def __enter__(self):
        """Start timing."""
        self.start_time = time.time()
        self.metrics.start_validation(self.validation_id)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """End timing and record metrics."""
        if self.start_time:
            duration = time.time() - self.start_time
            result = "error" if exc_type else "valid"  # Simplified for now
            self.metrics.end_validation(
                self.validation_id, self.level, self.profile, result, duration
            )


def record_validation_error(error_code: str, level: str) -> None:
    """Record a validation error."""
    get_metrics_collector().record_validation_error(error_code, level)


def record_cache_operation(cache_type: str, hit: bool) -> None:
    """Record a cache operation."""
    metrics = get_metrics_collector()
    if hit:
        metrics.record_cache_hit(cache_type)
    else:
        metrics.record_cache_miss(cache_type)


def update_cache_size(cache_type: str, size_bytes: int) -> None:
    """Update cache size metric."""
    get_metrics_collector().update_cache_size(cache_type, size_bytes)


def update_memory_usage(memory_bytes: int) -> None:
    """Update memory usage metric."""
    get_metrics_collector().update_memory_usage(memory_bytes)
