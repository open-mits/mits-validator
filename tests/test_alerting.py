"""Tests for alerting functionality."""

import pytest
from mits_validator.alerting import (
    AlertManager,
    AlertNotifier,
    check_and_alert,
    get_alert_manager,
    get_alert_notifier,
)


class TestAlertManager:
    """Test alert manager functionality."""

    def test_alert_manager_initialization(self):
        """Test alert manager initialization."""
        manager = AlertManager()
        assert len(manager.alert_thresholds) > 0
        assert "error_rate_percent" in manager.alert_thresholds
        assert "response_time_seconds" in manager.alert_thresholds

    def test_alert_manager_custom_thresholds(self):
        """Test alert manager with custom thresholds."""
        thresholds = {"error_rate_percent": 5.0, "response_time_seconds": 2.0}
        manager = AlertManager(alert_thresholds=thresholds)
        assert manager.alert_thresholds["error_rate_percent"] == 5.0
        assert manager.alert_thresholds["response_time_seconds"] == 2.0

    @pytest.mark.asyncio
    async def test_check_alerts_healthy_metrics(self):
        """Test checking alerts with healthy metrics."""
        manager = AlertManager()
        metrics = {
            "error_rate_percent": 5.0,
            "avg_response_time_seconds": 1.0,
            "memory_usage_percent": 50.0,
            "disk_usage_percent": 60.0,
            "consecutive_failures": 0,
        }

        alerts = await manager.check_alerts(metrics)
        assert len(alerts) == 0

    @pytest.mark.asyncio
    async def test_check_alerts_unhealthy_metrics(self):
        """Test checking alerts with unhealthy metrics."""
        manager = AlertManager()
        metrics = {
            "error_rate_percent": 15.0,  # Above threshold
            "avg_response_time_seconds": 1.0,
            "memory_usage_percent": 50.0,
            "disk_usage_percent": 60.0,
            "consecutive_failures": 0,
        }

        alerts = await manager.check_alerts(metrics)
        assert len(alerts) > 0
        assert any(alert["alert_type"] == "HIGH_ERROR_RATE" for alert in alerts)

    @pytest.mark.asyncio
    async def test_resolve_alert(self):
        """Test resolving an alert."""
        manager = AlertManager()

        # Create an alert first
        metrics = {"error_rate_percent": 15.0}
        alerts = await manager.check_alerts(metrics)
        assert len(alerts) > 0

        # Resolve the alert
        resolved = await manager.resolve_alert("HIGH_ERROR_RATE")
        assert resolved

    @pytest.mark.asyncio
    async def test_resolve_nonexistent_alert(self):
        """Test resolving a non-existent alert."""
        manager = AlertManager()
        resolved = await manager.resolve_alert("NONEXISTENT_ALERT")
        assert not resolved

    def test_get_active_alerts(self):
        """Test getting active alerts."""
        manager = AlertManager()
        active_alerts = manager.get_active_alerts()
        assert isinstance(active_alerts, list)

    def test_get_alert_history(self):
        """Test getting alert history."""
        manager = AlertManager()
        history = manager.get_alert_history(limit=10)
        assert isinstance(history, list)

    def test_get_alert_stats(self):
        """Test getting alert statistics."""
        manager = AlertManager()
        stats = manager.get_alert_stats()

        assert "total_alerts" in stats
        assert "active_alerts" in stats
        assert "resolved_alerts" in stats
        assert "severity_counts" in stats

    def test_update_thresholds(self):
        """Test updating alert thresholds."""
        manager = AlertManager()
        new_thresholds = {"error_rate_percent": 20.0}

        manager.update_thresholds(new_thresholds)
        assert manager.alert_thresholds["error_rate_percent"] == 20.0


class TestAlertNotifier:
    """Test alert notifier functionality."""

    def test_alert_notifier_initialization(self):
        """Test alert notifier initialization."""
        notifier = AlertNotifier()
        assert len(notifier.notification_handlers) == 0

    def test_register_handler(self):
        """Test registering notification handler."""
        notifier = AlertNotifier()

        async def test_handler(alert):
            pass

        notifier.register_handler(test_handler)
        assert len(notifier.notification_handlers) == 1

    @pytest.mark.asyncio
    async def test_send_notification(self):
        """Test sending notification."""
        notifier = AlertNotifier()

        # Register a test handler
        handler_called = False

        async def test_handler(alert):
            nonlocal handler_called
            handler_called = True

        notifier.register_handler(test_handler)

        alert = {"alert_type": "TEST", "message": "Test alert"}
        await notifier.send_notification(alert)

        assert handler_called

    @pytest.mark.asyncio
    async def test_send_email_notification(self):
        """Test sending email notification."""
        notifier = AlertNotifier()
        alert = {"alert_type": "TEST", "message": "Test alert"}

        # Should not raise exception
        await notifier.send_email_notification(alert)

    @pytest.mark.asyncio
    async def test_send_webhook_notification(self):
        """Test sending webhook notification."""
        notifier = AlertNotifier()
        alert = {"alert_type": "TEST", "message": "Test alert"}

        # Should not raise exception
        await notifier.send_webhook_notification(alert)

    @pytest.mark.asyncio
    async def test_send_slack_notification(self):
        """Test sending Slack notification."""
        notifier = AlertNotifier()
        alert = {"alert_type": "TEST", "message": "Test alert"}

        # Should not raise exception
        await notifier.send_slack_notification(alert)


class TestGlobalFunctions:
    """Test global alerting functions."""

    def test_get_alert_manager(self):
        """Test getting alert manager."""
        manager = get_alert_manager()
        assert isinstance(manager, AlertManager)

        # Should return the same instance
        manager2 = get_alert_manager()
        assert manager is manager2

    def test_get_alert_notifier(self):
        """Test getting alert notifier."""
        notifier = get_alert_notifier()
        assert isinstance(notifier, AlertNotifier)

        # Should return the same instance
        notifier2 = get_alert_notifier()
        assert notifier is notifier2

    @pytest.mark.asyncio
    async def test_check_and_alert_healthy(self):
        """Test check and alert with healthy metrics."""
        metrics = {
            "error_rate_percent": 5.0,
            "avg_response_time_seconds": 1.0,
            "memory_usage_percent": 50.0,
        }

        alerts = await check_and_alert(metrics)
        assert len(alerts) == 0

    @pytest.mark.asyncio
    async def test_check_and_alert_unhealthy(self):
        """Test check and alert with unhealthy metrics."""
        metrics = {
            "error_rate_percent": 15.0,  # Above threshold
            "avg_response_time_seconds": 1.0,
            "memory_usage_percent": 50.0,
        }

        alerts = await check_and_alert(metrics)
        assert len(alerts) > 0
