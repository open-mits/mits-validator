"""Caching layer for MITS Validator performance optimization."""

import asyncio
import hashlib
import json
from pathlib import Path
from typing import Any

import redis.asyncio as aioredis
import structlog
from lxml import etree

logger = structlog.get_logger(__name__)


class CacheManager:
    """Manages caching for XSD schemas, Schematron rules, and validation results."""

    def __init__(
        self,
        redis_url: str | None = None,
        default_ttl: int = 3600,  # 1 hour
        max_memory_mb: int = 100,
    ):
        """Initialize cache manager.

        Args:
            redis_url: Redis connection URL. If None, uses in-memory cache.
            default_ttl: Default time-to-live for cached items in seconds.
            max_memory_mb: Maximum memory usage for in-memory cache in MB.
        """
        self.redis_url = redis_url
        self.default_ttl = default_ttl
        self.max_memory_mb = max_memory_mb
        self._redis: aioredis.Redis | None = None
        self._memory_cache: dict[str, Any] = {}
        self._memory_usage = 0

    async def initialize(self) -> None:
        """Initialize the cache connection."""
        if self.redis_url:
            try:
                self._redis = aioredis.from_url(self.redis_url)
                await self._redis.ping()
                logger.info("Connected to Redis cache", url=self.redis_url)
            except Exception as e:
                logger.warning(
                    "Failed to connect to Redis, falling back to memory cache", error=str(e)
                )
                self._redis = None
        else:
            logger.info("Using in-memory cache")

    async def close(self) -> None:
        """Close cache connections."""
        if self._redis:
            await self._redis.close()

    def _get_cache_key(self, prefix: str, key: str) -> str:
        """Generate a cache key with prefix."""
        return f"mits_validator:{prefix}:{key}"

    def _calculate_memory_usage(self, data: Any) -> int:
        """Calculate approximate memory usage of data."""
        try:
            return len(json.dumps(data, default=str).encode("utf-8"))
        except (TypeError, ValueError):
            return len(str(data).encode("utf-8"))

    async def get(self, prefix: str, key: str) -> Any | None:
        """Get item from cache."""
        cache_key = self._get_cache_key(prefix, key)

        if self._redis:
            try:
                data = await self._redis.get(cache_key)
                if data:
                    return json.loads(data)
            except Exception as e:
                logger.warning("Failed to get from Redis cache", key=cache_key, error=str(e))

        # Fallback to memory cache
        return self._memory_cache.get(cache_key)

    async def set(self, prefix: str, key: str, value: Any, ttl: int | None = None) -> None:
        """Set item in cache."""
        cache_key = self._get_cache_key(prefix, key)
        ttl = ttl or self.default_ttl

        if self._redis:
            try:
                data = json.dumps(value, default=str)
                await self._redis.setex(cache_key, ttl, data)
                logger.debug("Cached item in Redis", key=cache_key, ttl=ttl)
            except Exception as e:
                logger.warning("Failed to set in Redis cache", key=cache_key, error=str(e))
                # Fallback to memory cache
                self._set_memory_cache(cache_key, value)
        else:
            self._set_memory_cache(cache_key, value)

    def _set_memory_cache(self, cache_key: str, value: Any) -> None:
        """Set item in memory cache with size limits."""
        value_size = self._calculate_memory_usage(value)

        # Check if adding this item would exceed memory limit
        if self._memory_usage + value_size > self.max_memory_mb * 1024 * 1024:
            # Remove oldest items (simple FIFO)
            if self._memory_cache:
                oldest_key = next(iter(self._memory_cache))
                old_value = self._memory_cache.pop(oldest_key)
                self._memory_usage -= self._calculate_memory_usage(old_value)

        self._memory_cache[cache_key] = value
        self._memory_usage += value_size
        logger.debug("Cached item in memory", key=cache_key, size=value_size)

    async def delete(self, prefix: str, key: str) -> None:
        """Delete item from cache."""
        cache_key = self._get_cache_key(prefix, key)

        if self._redis:
            try:
                await self._redis.delete(cache_key)
            except Exception as e:
                logger.warning("Failed to delete from Redis cache", key=cache_key, error=str(e))

        # Also remove from memory cache
        if cache_key in self._memory_cache:
            old_value = self._memory_cache.pop(cache_key)
            self._memory_usage -= self._calculate_memory_usage(old_value)

    async def clear(self, prefix: str | None = None) -> None:
        """Clear cache items, optionally filtered by prefix."""
        if self._redis:
            try:
                if prefix:
                    pattern = self._get_cache_key(prefix, "*")
                    keys = await self._redis.keys(pattern)
                    if keys:
                        await self._redis.delete(*keys)
                else:
                    await self._redis.flushdb()
            except Exception as e:
                logger.warning("Failed to clear Redis cache", error=str(e))

        # Clear memory cache
        if prefix:
            pattern = self._get_cache_key(prefix, "")
            keys_to_remove = [k for k in self._memory_cache.keys() if k.startswith(pattern)]
            for key in keys_to_remove:
                old_value = self._memory_cache.pop(key)
                self._memory_usage -= self._calculate_memory_usage(old_value)
        else:
            self._memory_cache.clear()
            self._memory_usage = 0

    def get_cache_stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        return {
            "redis_connected": self._redis is not None,
            "memory_items": len(self._memory_cache),
            "memory_usage_mb": self._memory_usage / (1024 * 1024),
            "max_memory_mb": self.max_memory_mb,
        }


class SchemaCache:
    """Specialized cache for XSD schemas and Schematron rules."""

    def __init__(self, cache_manager: CacheManager):
        """Initialize schema cache."""
        self.cache = cache_manager

    def _get_schema_key(self, schema_path: Path, schema_type: str) -> str:
        """Generate cache key for schema."""
        # Use file path and modification time for cache invalidation
        stat = schema_path.stat()
        key_data = f"{schema_path}:{stat.st_mtime}:{stat.st_size}"
        return hashlib.sha256(key_data.encode()).hexdigest()

    async def get_xsd_schema(self, schema_path: Path) -> etree.XMLSchema | None:
        """Get cached XSD schema."""
        cache_key = self._get_schema_key(schema_path, "xsd")
        cached_data = await self.cache.get("xsd_schema", cache_key)

        if cached_data:
            try:
                # Reconstruct schema from cached data
                schema_doc = etree.fromstring(cached_data["schema_xml"])
                return etree.XMLSchema(schema_doc)
            except Exception as e:
                logger.warning("Failed to reconstruct cached XSD schema", error=str(e))
                await self.cache.delete("xsd_schema", cache_key)

        return None

    async def set_xsd_schema(self, schema_path: Path, schema: etree.XMLSchema) -> None:
        """Cache XSD schema."""
        cache_key = self._get_schema_key(schema_path, "xsd")

        # Serialize schema for caching
        schema_xml = etree.tostring(schema._root, encoding="unicode")
        cached_data = {
            "schema_xml": schema_xml,
            "schema_path": str(schema_path),
            "cached_at": asyncio.get_event_loop().time(),
        }

        await self.cache.set("xsd_schema", cache_key, cached_data, ttl=7200)  # 2 hours

    async def get_schematron_rules(self, rules_path: Path) -> etree.XSLT | None:
        """Get cached Schematron rules."""
        cache_key = self._get_schema_key(rules_path, "schematron")
        cached_data = await self.cache.get("schematron_rules", cache_key)

        if cached_data:
            try:
                # Reconstruct XSLT from cached data
                xslt_doc = etree.fromstring(cached_data["xslt_xml"])
                return etree.XSLT(xslt_doc)
            except Exception as e:
                logger.warning("Failed to reconstruct cached Schematron rules", error=str(e))
                await self.cache.delete("schematron_rules", cache_key)

        return None

    async def set_schematron_rules(self, rules_path: Path, xslt: etree.XSLT) -> None:
        """Cache Schematron rules."""
        cache_key = self._get_schema_key(rules_path, "schematron")

        # Serialize XSLT for caching
        xslt_xml = etree.tostring(xslt.doc, encoding="unicode")
        cached_data = {
            "xslt_xml": xslt_xml,
            "rules_path": str(rules_path),
            "cached_at": asyncio.get_event_loop().time(),
        }

        await self.cache.set("schematron_rules", cache_key, cached_data, ttl=7200)  # 2 hours


# Global cache instance
_cache_manager: CacheManager | None = None
_schema_cache: SchemaCache | None = None


async def get_cache_manager() -> CacheManager:
    """Get or create global cache manager."""
    global _cache_manager
    if _cache_manager is None:
        redis_url = None  # TODO: Get from environment variables
        _cache_manager = CacheManager(redis_url=redis_url)
        await _cache_manager.initialize()
    return _cache_manager


async def get_schema_cache() -> SchemaCache:
    """Get or create global schema cache."""
    global _schema_cache
    if _schema_cache is None:
        cache_manager = await get_cache_manager()
        _schema_cache = SchemaCache(cache_manager)
    return _schema_cache


async def close_caches() -> None:
    """Close all cache connections."""
    global _cache_manager
    if _cache_manager:
        await _cache_manager.close()
        _cache_manager = None
