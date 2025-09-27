"""Structured logging configuration for MITS Validator."""

import logging
import sys
from typing import Any

import structlog
from structlog.types import Processor


def add_correlation_id(logger, method_name, event_dict):
    """Add correlation ID to log events."""
    # Try to get correlation ID from context
    correlation_id = getattr(structlog.contextvars, "correlation_id", None)
    if correlation_id:
        event_dict["correlation_id"] = correlation_id
    return event_dict


def add_timestamp(logger, method_name, event_dict):
    """Add timestamp to log events."""
    import time

    event_dict["timestamp"] = time.time()
    return event_dict


def add_service_info(logger, method_name, event_dict):
    """Add service information to log events."""
    event_dict["service"] = "mits-validator"
    event_dict["version"] = "0.1.0"
    return event_dict


def setup_logging(
    log_level: str = "INFO",
    log_format: str = "json",
    enable_console: bool = True,
    enable_file: bool = False,
    log_file: str | None = None,
) -> None:
    """Setup structured logging for the application.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_format: Log format (json, console)
        enable_console: Enable console logging
        enable_file: Enable file logging
        log_file: Log file path (required if enable_file is True)
    """
    # Configure standard library logging
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(message)s",
        stream=sys.stdout if enable_console else None,
    )

    # Configure structlog processors
    processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        add_correlation_id,
        add_timestamp,
        add_service_info,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    if log_format == "json":
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer(colors=True))

    # Configure structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.BoundLogger:
    """Get a structured logger instance."""
    return structlog.get_logger(name)


class ValidationLogger:
    """Specialized logger for validation operations."""

    def __init__(self, validation_id: str, level: str, profile: str):
        """Initialize validation logger."""
        self.validation_id = validation_id
        self.level = level
        self.profile = profile
        self.logger = get_logger("validation")
        self.start_time = None

    def start_validation(self, xml_size: int, content_type: str) -> None:
        """Log validation start."""
        import time

        self.start_time = time.time()
        self.logger.info(
            "Validation started",
            validation_id=self.validation_id,
            level=self.level,
            profile=self.profile,
            xml_size_bytes=xml_size,
            content_type=content_type,
            event_type="validation_start",
        )

    def end_validation(self, valid: bool, errors: int, warnings: int, findings: list) -> None:
        """Log validation end."""
        import time

        duration = time.time() - self.start_time if self.start_time else 0

        self.logger.info(
            "Validation completed",
            validation_id=self.validation_id,
            level=self.level,
            profile=self.profile,
            valid=valid,
            errors=errors,
            warnings=warnings,
            findings_count=len(findings),
            duration_seconds=duration,
            event_type="validation_end",
        )

    def log_validation_error(
        self, error_code: str, message: str, location: dict[str, Any] | None = None
    ) -> None:
        """Log a validation error."""
        self.logger.error(
            "Validation error",
            validation_id=self.validation_id,
            level=self.level,
            error_code=error_code,
            message=message,
            location=location,
            event_type="validation_error",
        )

    def log_validation_warning(
        self, warning_code: str, message: str, location: dict[str, Any] | None = None
    ) -> None:
        """Log a validation warning."""
        self.logger.warning(
            "Validation warning",
            validation_id=self.validation_id,
            level=self.level,
            warning_code=warning_code,
            message=message,
            location=location,
            event_type="validation_warning",
        )

    def log_cache_operation(self, operation: str, cache_type: str, hit: bool, key: str) -> None:
        """Log a cache operation."""
        self.logger.debug(
            "Cache operation",
            validation_id=self.validation_id,
            operation=operation,
            cache_type=cache_type,
            hit=hit,
            key=key,
            event_type="cache_operation",
        )

    def log_performance_metric(self, metric_name: str, value: float, unit: str = "seconds") -> None:
        """Log a performance metric."""
        self.logger.info(
            "Performance metric",
            validation_id=self.validation_id,
            metric_name=metric_name,
            value=value,
            unit=unit,
            event_type="performance_metric",
        )


class RequestLogger:
    """Specialized logger for HTTP requests."""

    def __init__(self, request_id: str, method: str, path: str):
        """Initialize request logger."""
        self.request_id = request_id
        self.method = method
        self.path = path
        self.logger = get_logger("request")
        self.start_time = None

    def start_request(self, client_ip: str, user_agent: str) -> None:
        """Log request start."""
        import time

        self.start_time = time.time()
        self.logger.info(
            "Request started",
            request_id=self.request_id,
            method=self.method,
            path=self.path,
            client_ip=client_ip,
            user_agent=user_agent,
            event_type="request_start",
        )

    def end_request(self, status_code: int, response_size: int) -> None:
        """Log request end."""
        import time

        duration = time.time() - self.start_time if self.start_time else 0

        self.logger.info(
            "Request completed",
            request_id=self.request_id,
            method=self.method,
            path=self.path,
            status_code=status_code,
            response_size_bytes=response_size,
            duration_seconds=duration,
            event_type="request_end",
        )

    def log_request_error(self, error: str, status_code: int = 500) -> None:
        """Log request error."""
        import time

        duration = time.time() - self.start_time if self.start_time else 0

        self.logger.error(
            "Request error",
            request_id=self.request_id,
            method=self.method,
            path=self.path,
            error=error,
            status_code=status_code,
            duration_seconds=duration,
            event_type="request_error",
        )


def create_validation_logger(validation_id: str, level: str, profile: str) -> ValidationLogger:
    """Create a validation logger instance."""
    return ValidationLogger(validation_id, level, profile)


def create_request_logger(request_id: str, method: str, path: str) -> RequestLogger:
    """Create a request logger instance."""
    return RequestLogger(request_id, method, path)
