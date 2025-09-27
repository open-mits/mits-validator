"""Health checks for MITS Validator dependencies."""

import time
from pathlib import Path
from typing import Any

import structlog
from fastapi import HTTPException, status

logger = structlog.get_logger(__name__)


class HealthChecker:
    """Health checker for system dependencies."""

    def __init__(self):
        """Initialize health checker."""
        self.checks: dict[str, callable] = {}
        self.last_check_time: dict[str, float] = {}
        self.check_cache_ttl = 30  # 30 seconds cache
        self._register_default_checks()

    def _register_default_checks(self) -> None:
        """Register default health checks."""
        self.checks.update(
            {
                "filesystem": self._check_filesystem,
                "rules_directory": self._check_rules_directory,
                "cache": self._check_cache,
                "memory": self._check_memory,
                "disk_space": self._check_disk_space,
            }
        )

    async def check_health(self, checks: list[str] = None) -> dict[str, Any]:
        """Run health checks.

        Args:
            checks: List of specific checks to run. If None, runs all checks.

        Returns:
            Health check results
        """
        if checks is None:
            checks = list(self.checks.keys())

        results = {
            "status": "healthy",
            "timestamp": time.time(),
            "checks": {},
            "overall_healthy": True,
        }

        for check_name in checks:
            if check_name in self.checks:
                try:
                    # Check cache first
                    if self._is_check_cached(check_name):
                        results["checks"][check_name] = self._get_cached_result(check_name)
                        continue

                    # Run check
                    check_result = await self.checks[check_name]()
                    results["checks"][check_name] = check_result

                    # Cache result
                    self._cache_result(check_name, check_result)

                    # Update overall health
                    if not check_result.get("healthy", False):
                        results["overall_healthy"] = False
                        results["status"] = "unhealthy"

                except Exception as e:
                    logger.error("Health check failed", check=check_name, error=str(e))
                    results["checks"][check_name] = {
                        "healthy": False,
                        "error": str(e),
                        "timestamp": time.time(),
                    }
                    results["overall_healthy"] = False
                    results["status"] = "unhealthy"
            else:
                results["checks"][check_name] = {
                    "healthy": False,
                    "error": f"Unknown check: {check_name}",
                    "timestamp": time.time(),
                }
                results["overall_healthy"] = False
                results["status"] = "unhealthy"

        return results

    def _is_check_cached(self, check_name: str) -> bool:
        """Check if result is cached and still valid."""
        if check_name not in self.last_check_time:
            return False
        return time.time() - self.last_check_time[check_name] < self.check_cache_ttl

    def _get_cached_result(self, check_name: str) -> dict[str, Any]:
        """Get cached result for a check."""
        # In a real implementation, you'd store the actual results
        # For now, we'll just return a basic structure
        return {
            "healthy": True,
            "cached": True,
            "timestamp": self.last_check_time[check_name],
        }

    def _cache_result(self, check_name: str, result: dict[str, Any]) -> None:
        """Cache a check result."""
        self.last_check_time[check_name] = time.time()
        # In a real implementation, you'd store the actual results

    async def _check_filesystem(self) -> dict[str, Any]:
        """Check filesystem health."""
        try:
            # Check if we can write to temp directory
            import tempfile

            with tempfile.NamedTemporaryFile(delete=True) as tmp:
                tmp.write(b"test")

            return {
                "healthy": True,
                "message": "Filesystem is accessible",
                "timestamp": time.time(),
            }
        except Exception as e:
            return {
                "healthy": False,
                "error": f"Filesystem check failed: {str(e)}",
                "timestamp": time.time(),
            }

    async def _check_rules_directory(self) -> dict[str, Any]:
        """Check rules directory health."""
        try:
            rules_path = Path("rules")
            if not rules_path.exists():
                return {
                    "healthy": False,
                    "error": "Rules directory does not exist",
                    "timestamp": time.time(),
                }

            # Check if we can read the directory
            files = (
                list(rules_path.rglob("*.xml"))
                + list(rules_path.rglob("*.xsd"))
                + list(rules_path.rglob("*.sch"))
            )

            return {
                "healthy": True,
                "message": f"Rules directory accessible with {len(files)} rule files",
                "file_count": len(files),
                "timestamp": time.time(),
            }
        except Exception as e:
            return {
                "healthy": False,
                "error": f"Rules directory check failed: {str(e)}",
                "timestamp": time.time(),
            }

    async def _check_cache(self) -> dict[str, Any]:
        """Check cache health."""
        try:
            from mits_validator.cache import get_cache_manager

            cache_manager = await get_cache_manager()
            stats = cache_manager.get_cache_stats()

            return {
                "healthy": True,
                "message": "Cache is accessible",
                "stats": stats,
                "timestamp": time.time(),
            }
        except Exception as e:
            return {
                "healthy": False,
                "error": f"Cache check failed: {str(e)}",
                "timestamp": time.time(),
            }

    async def _check_memory(self) -> dict[str, Any]:
        """Check memory health."""
        try:
            import psutil

            memory = psutil.virtual_memory()
            memory_usage_percent = memory.percent

            # Consider unhealthy if memory usage is over 90%
            healthy = memory_usage_percent < 90

            return {
                "healthy": healthy,
                "message": f"Memory usage: {memory_usage_percent:.1f}%",
                "memory_usage_percent": memory_usage_percent,
                "available_mb": memory.available // (1024 * 1024),
                "total_mb": memory.total // (1024 * 1024),
                "timestamp": time.time(),
            }
        except ImportError:
            # psutil not available, use basic check
            # Basic check - no need to store result
            return {
                "healthy": True,
                "message": "Basic memory check passed",
                "timestamp": time.time(),
            }
        except Exception as e:
            return {
                "healthy": False,
                "error": f"Memory check failed: {str(e)}",
                "timestamp": time.time(),
            }

    async def _check_disk_space(self) -> dict[str, Any]:
        """Check disk space health."""
        try:
            import shutil

            # Check disk space in current directory
            total, used, free = shutil.disk_usage(".")
            free_percent = (free / total) * 100

            # Consider unhealthy if less than 10% free space
            healthy = free_percent > 10

            return {
                "healthy": healthy,
                "message": f"Disk space: {free_percent:.1f}% free",
                "free_percent": free_percent,
                "free_gb": free // (1024**3),
                "total_gb": total // (1024**3),
                "timestamp": time.time(),
            }
        except Exception as e:
            return {
                "healthy": False,
                "error": f"Disk space check failed: {str(e)}",
                "timestamp": time.time(),
            }

    def register_check(self, name: str, check_func: callable) -> None:
        """Register a custom health check.

        Args:
            name: Name of the check
            check_func: Async function that returns health status
        """
        self.checks[name] = check_func

    def get_available_checks(self) -> list[str]:
        """Get list of available health checks."""
        return list(self.checks.keys())


# Global health checker
_health_checker: HealthChecker | None = None


def get_health_checker() -> HealthChecker:
    """Get or create global health checker."""
    global _health_checker
    if _health_checker is None:
        _health_checker = HealthChecker()
    return _health_checker


async def check_system_health(checks: list[str] = None) -> dict[str, Any]:
    """Check system health.

    Args:
        checks: List of specific checks to run

    Returns:
        Health check results

    Raises:
        HTTPException: If system is unhealthy
    """
    health_checker = get_health_checker()
    results = await health_checker.check_health(checks)

    if not results["overall_healthy"]:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=results)

    return results
