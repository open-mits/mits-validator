"""Tests for metrics functionality."""

import time

from mits_validator.metrics import (
    MetricsCollector,
    ValidationTimer,
    get_metrics_collector,
    record_cache_operation,
    record_validation_error,
)


class TestMetricsCollector:
    """Test metrics collector functionality."""

    def test_metrics_collector_initialization(self):
        """Test metrics collector initialization."""
        collector = MetricsCollector()
        assert collector._start_time > 0
        assert collector._active_validations == 0

    def test_record_request(self):
        """Test request recording."""
        collector = MetricsCollector()
        collector.record_request("POST", "/v1/validate", 200, 1.5)
        # Metrics are recorded but we can't easily test the values
        # without accessing the internal prometheus metrics

    def test_validation_tracking(self):
        """Test validation tracking."""
        collector = MetricsCollector()

        # Start validation
        collector.start_validation("test-validation-1")
        assert collector._active_validations == 1

        # End validation
        collector.end_validation("test-validation-1", "XSD", "default", "valid", 2.0)
        assert collector._active_validations == 0

    def test_validation_error_recording(self):
        """Test validation error recording."""
        collector = MetricsCollector()
        collector.record_validation_error("XSD:VALIDATION_ERROR", "XSD")
        # Error is recorded but we can't easily test the values

    def test_cache_operations(self):
        """Test cache operation recording."""
        collector = MetricsCollector()
        collector.record_cache_hit("xsd_schema")
        collector.record_cache_miss("schematron_rules")
        # Operations are recorded but we can't easily test the values

    def test_uptime(self):
        """Test uptime calculation."""
        collector = MetricsCollector()
        uptime = collector.get_uptime()
        assert uptime >= 0
        assert uptime < 1  # Should be very small for new collector

    def test_metrics_generation(self):
        """Test metrics generation."""
        collector = MetricsCollector()
        metrics = collector.get_metrics()
        assert isinstance(metrics, str)
        assert len(metrics) > 0


class TestValidationTimer:
    """Test validation timer context manager."""

    def test_validation_timer_success(self):
        """Test validation timer with successful validation."""
        timer = ValidationTimer("test-validation", "XSD", "default")

        with timer:
            time.sleep(0.01)  # Small delay to test timing

        # Timer should have recorded the validation
        assert timer.metrics is not None

    def test_validation_timer_error(self):
        """Test validation timer with error."""
        timer = ValidationTimer("test-validation", "XSD", "default")

        try:
            with timer:
                raise ValueError("Test error")
        except ValueError:
            pass

        # Timer should have recorded the validation even with error
        assert timer.metrics is not None


class TestGlobalFunctions:
    """Test global metric functions."""

    def test_get_metrics_collector(self):
        """Test getting metrics collector."""
        collector = get_metrics_collector()
        assert isinstance(collector, MetricsCollector)

    def test_record_validation_error(self):
        """Test recording validation error."""
        # Should not raise exception
        record_validation_error("TEST_ERROR", "XSD")

    def test_record_cache_operation(self):
        """Test recording cache operation."""
        # Should not raise exception
        record_cache_operation("xsd_schema", True)
        record_cache_operation("schematron_rules", False)
