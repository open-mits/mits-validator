"""Tests for health check functionality."""

import pytest
from fastapi import HTTPException
from mits_validator.health_checks import HealthChecker, check_system_health, get_health_checker


class TestHealthChecker:
    """Test health checker functionality."""

    def test_health_checker_initialization(self):
        """Test health checker initialization."""
        checker = HealthChecker()
        assert len(checker.checks) > 0
        assert "filesystem" in checker.checks
        assert "rules_directory" in checker.checks

    @pytest.mark.asyncio
    async def test_check_health_all(self):
        """Test checking all health checks."""
        checker = HealthChecker()
        results = await checker.check_health()

        assert "status" in results
        assert "timestamp" in results
        assert "checks" in results
        assert "overall_healthy" in results
        assert len(results["checks"]) > 0

    @pytest.mark.asyncio
    async def test_check_health_specific(self):
        """Test checking specific health checks."""
        checker = HealthChecker()
        results = await checker.check_health(["filesystem", "memory"])

        assert "filesystem" in results["checks"]
        assert "memory" in results["checks"]
        assert "rules_directory" not in results["checks"]

    @pytest.mark.asyncio
    async def test_check_filesystem(self):
        """Test filesystem health check."""
        checker = HealthChecker()
        result = await checker._check_filesystem()

        assert "healthy" in result
        assert "timestamp" in result

    @pytest.mark.asyncio
    async def test_check_rules_directory(self):
        """Test rules directory health check."""
        checker = HealthChecker()
        result = await checker._check_rules_directory()

        assert "healthy" in result
        assert "timestamp" in result

    @pytest.mark.asyncio
    async def test_check_memory(self):
        """Test memory health check."""
        checker = HealthChecker()
        result = await checker._check_memory()

        assert "healthy" in result
        assert "timestamp" in result

    @pytest.mark.asyncio
    async def test_check_disk_space(self):
        """Test disk space health check."""
        checker = HealthChecker()
        result = await checker._check_disk_space()

        assert "healthy" in result
        assert "timestamp" in result

    def test_register_custom_check(self):
        """Test registering custom health check."""
        checker = HealthChecker()

        async def custom_check():
            return {"healthy": True, "message": "Custom check passed"}

        checker.register_check("custom", custom_check)
        assert "custom" in checker.checks

    def test_get_available_checks(self):
        """Test getting available checks."""
        checker = HealthChecker()
        checks = checker.get_available_checks()

        assert isinstance(checks, list)
        assert len(checks) > 0
        assert "filesystem" in checks


class TestGlobalFunctions:
    """Test global health check functions."""

    def test_get_health_checker(self):
        """Test getting health checker."""
        checker = get_health_checker()
        assert isinstance(checker, HealthChecker)

        # Should return the same instance
        checker2 = get_health_checker()
        assert checker is checker2

    @pytest.mark.asyncio
    async def test_check_system_health_healthy(self):
        """Test system health check when healthy."""
        # This should not raise an exception
        results = await check_system_health(["filesystem"])
        assert "status" in results

    @pytest.mark.asyncio
    async def test_check_system_health_with_custom_check(self):
        """Test system health check with custom check."""
        checker = get_health_checker()

        async def failing_check():
            return {"healthy": False, "error": "Test failure"}

        checker.register_check("failing", failing_check)

        # This should raise HTTPException
        with pytest.raises(HTTPException):  # Should raise HTTPException for unhealthy check
            await check_system_health(["failing"])
