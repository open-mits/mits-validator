"""Alerting system for MITS Validator."""

import asyncio
import time
from typing import Any

import structlog
from fastapi import HTTPException, status

logger = structlog.get_logger(__name__)


class AlertManager:
    """Manages alerts and notifications for the validation system."""

    def __init__(self, alert_thresholds: dict[str, Any] = None):
        """Initialize alert manager.
        
        Args:
            alert_thresholds: Dictionary of alert thresholds
        """
        self.alert_thresholds = alert_thresholds or {
            "error_rate_percent": 10.0,
            "response_time_seconds": 5.0,
            "memory_usage_percent": 90.0,
            "disk_usage_percent": 90.0,
            "consecutive_failures": 5,
        }
        self.active_alerts: dict[str, dict[str, Any]] = {}
        self.alert_history: list[dict[str, Any]] = []
        self.alert_cooldown = 300  # 5 minutes cooldown between same alerts

    async def check_alerts(self, metrics: dict[str, Any]) -> list[dict[str, Any]]:
        """Check metrics against alert thresholds.
        
        Args:
            metrics: Current system metrics
            
        Returns:
            List of triggered alerts
        """
        triggered_alerts = []
        
        # Check error rate
        if "error_rate_percent" in metrics:
            if metrics["error_rate_percent"] > self.alert_thresholds["error_rate_percent"]:
                alert = await self._create_alert(
                    "HIGH_ERROR_RATE",
                    f"Error rate is {metrics['error_rate_percent']:.1f}% (threshold: {self.alert_thresholds['error_rate_percent']}%)",
                    "error",
                    metrics
                )
                triggered_alerts.append(alert)
        
        # Check response time
        if "avg_response_time_seconds" in metrics:
            if metrics["avg_response_time_seconds"] > self.alert_thresholds["response_time_seconds"]:
                alert = await self._create_alert(
                    "HIGH_RESPONSE_TIME",
                    f"Average response time is {metrics['avg_response_time_seconds']:.2f}s (threshold: {self.alert_thresholds['response_time_seconds']}s)",
                    "warning",
                    metrics
                )
                triggered_alerts.append(alert)
        
        # Check memory usage
        if "memory_usage_percent" in metrics:
            if metrics["memory_usage_percent"] > self.alert_thresholds["memory_usage_percent"]:
                alert = await self._create_alert(
                    "HIGH_MEMORY_USAGE",
                    f"Memory usage is {metrics['memory_usage_percent']:.1f}% (threshold: {self.alert_thresholds['memory_usage_percent']}%)",
                    "warning",
                    metrics
                )
                triggered_alerts.append(alert)
        
        # Check disk usage
        if "disk_usage_percent" in metrics:
            if metrics["disk_usage_percent"] > self.alert_thresholds["disk_usage_percent"]:
                alert = await self._create_alert(
                    "HIGH_DISK_USAGE",
                    f"Disk usage is {metrics['disk_usage_percent']:.1f}% (threshold: {self.alert_thresholds['disk_usage_percent']}%)",
                    "warning",
                    metrics
                )
                triggered_alerts.append(alert)
        
        # Check consecutive failures
        if "consecutive_failures" in metrics:
            if metrics["consecutive_failures"] > self.alert_thresholds["consecutive_failures"]:
                alert = await self._create_alert(
                    "CONSECUTIVE_FAILURES",
                    f"Consecutive failures: {metrics['consecutive_failures']} (threshold: {self.alert_thresholds['consecutive_failures']})",
                    "critical",
                    metrics
                )
                triggered_alerts.append(alert)
        
        return triggered_alerts

    async def _create_alert(
        self, 
        alert_type: str, 
        message: str, 
        severity: str, 
        metrics: dict[str, Any]
    ) -> dict[str, Any]:
        """Create an alert.
        
        Args:
            alert_type: Type of alert
            message: Alert message
            severity: Alert severity (info, warning, error, critical)
            metrics: Current metrics
            
        Returns:
            Alert dictionary
        """
        alert = {
            "alert_type": alert_type,
            "message": message,
            "severity": severity,
            "timestamp": time.time(),
            "metrics": metrics,
            "resolved": False,
        }
        
        # Check if this alert is already active
        if alert_type in self.active_alerts:
            existing_alert = self.active_alerts[alert_type]
            # Check cooldown
            if time.time() - existing_alert["timestamp"] < self.alert_cooldown:
                return existing_alert
        
        # Store active alert
        self.active_alerts[alert_type] = alert
        
        # Add to history
        self.alert_history.append(alert)
        
        # Log alert
        logger.warning("Alert triggered", alert_type=alert_type, message=message, severity=severity)
        
        return alert

    async def resolve_alert(self, alert_type: str) -> bool:
        """Resolve an alert.
        
        Args:
            alert_type: Type of alert to resolve
            
        Returns:
            True if alert was resolved, False if not found
        """
        if alert_type in self.active_alerts:
            alert = self.active_alerts[alert_type]
            alert["resolved"] = True
            alert["resolved_at"] = time.time()
            del self.active_alerts[alert_type]
            
            logger.info("Alert resolved", alert_type=alert_type)
            return True
        return False

    def get_active_alerts(self) -> list[dict[str, Any]]:
        """Get list of active alerts."""
        return list(self.active_alerts.values())

    def get_alert_history(self, limit: int = 100) -> list[dict[str, Any]]:
        """Get alert history.
        
        Args:
            limit: Maximum number of alerts to return
            
        Returns:
            List of recent alerts
        """
        return self.alert_history[-limit:]

    def get_alert_stats(self) -> dict[str, Any]:
        """Get alert statistics."""
        total_alerts = len(self.alert_history)
        active_alerts = len(self.active_alerts)
        resolved_alerts = total_alerts - active_alerts
        
        # Count by severity
        severity_counts = {}
        for alert in self.alert_history:
            severity = alert.get("severity", "unknown")
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        return {
            "total_alerts": total_alerts,
            "active_alerts": active_alerts,
            "resolved_alerts": resolved_alerts,
            "severity_counts": severity_counts,
        }

    def update_thresholds(self, new_thresholds: dict[str, Any]) -> None:
        """Update alert thresholds.
        
        Args:
            new_thresholds: New threshold values
        """
        self.alert_thresholds.update(new_thresholds)
        logger.info("Alert thresholds updated", thresholds=new_thresholds)


class AlertNotifier:
    """Handles alert notifications."""

    def __init__(self):
        """Initialize alert notifier."""
        self.notification_handlers: list[callable] = []

    def register_handler(self, handler: callable) -> None:
        """Register a notification handler.
        
        Args:
            handler: Async function that handles notifications
        """
        self.notification_handlers.append(handler)

    async def send_notification(self, alert: dict[str, Any]) -> None:
        """Send notification for an alert.
        
        Args:
            alert: Alert to notify about
        """
        for handler in self.notification_handlers:
            try:
                await handler(alert)
            except Exception as e:
                logger.error("Notification handler failed", error=str(e))

    async def send_email_notification(self, alert: dict[str, Any]) -> None:
        """Send email notification (placeholder).
        
        Args:
            alert: Alert to notify about
        """
        # TODO: Implement actual email sending
        logger.info("Email notification sent", alert_type=alert["alert_type"])

    async def send_webhook_notification(self, alert: dict[str, Any]) -> None:
        """Send webhook notification (placeholder).
        
        Args:
            alert: Alert to notify about
        """
        # TODO: Implement actual webhook sending
        logger.info("Webhook notification sent", alert_type=alert["alert_type"])

    async def send_slack_notification(self, alert: dict[str, Any]) -> None:
        """Send Slack notification (placeholder).
        
        Args:
            alert: Alert to notify about
        """
        # TODO: Implement actual Slack sending
        logger.info("Slack notification sent", alert_type=alert["alert_type"])


# Global alert manager and notifier
_alert_manager: AlertManager | None = None
_alert_notifier: AlertNotifier | None = None


def get_alert_manager() -> AlertManager:
    """Get or create global alert manager."""
    global _alert_manager
    if _alert_manager is None:
        _alert_manager = AlertManager()
    return _alert_manager


def get_alert_notifier() -> AlertNotifier:
    """Get or create global alert notifier."""
    global _alert_notifier
    if _alert_notifier is None:
        _alert_notifier = AlertNotifier()
        # Register default handlers
        _alert_notifier.register_handler(_alert_notifier.send_email_notification)
        _alert_notifier.register_handler(_alert_notifier.send_webhook_notification)
    return _alert_notifier


async def check_and_alert(metrics: dict[str, Any]) -> list[dict[str, Any]]:
    """Check metrics and send alerts if needed.
    
    Args:
        metrics: Current system metrics
        
    Returns:
        List of triggered alerts
    """
    alert_manager = get_alert_manager()
    notifier = get_alert_notifier()
    
    # Check for alerts
    triggered_alerts = await alert_manager.check_alerts(metrics)
    
    # Send notifications for new alerts
    for alert in triggered_alerts:
        await notifier.send_notification(alert)
    
    return triggered_alerts
