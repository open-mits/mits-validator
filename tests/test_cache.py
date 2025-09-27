"""Tests for caching functionality."""

from pathlib import Path

import pytest
from mits_validator.cache import CacheManager, SchemaCache


class TestCacheManager:
    """Test cache manager functionality."""

    @pytest.mark.asyncio
    async def test_memory_cache_basic_operations(self):
        """Test basic cache operations with memory cache."""
        cache = CacheManager()
        await cache.initialize()

        # Test set and get
        await cache.set("test", "key1", {"data": "value1"})
        result = await cache.get("test", "key1")
        assert result == {"data": "value1"}

        # Test delete
        await cache.delete("test", "key1")
        result = await cache.get("test", "key1")
        assert result is None

        await cache.close()

    @pytest.mark.asyncio
    async def test_cache_stats(self):
        """Test cache statistics."""
        cache = CacheManager()
        await cache.initialize()

        stats = cache.get_cache_stats()
        assert "redis_connected" in stats
        assert "memory_items" in stats
        assert "memory_usage_mb" in stats

        await cache.close()

    @pytest.mark.asyncio
    async def test_cache_clear(self):
        """Test cache clearing."""
        cache = CacheManager()
        await cache.initialize()

        # Add some data
        await cache.set("test", "key1", {"data": "value1"})
        await cache.set("test", "key2", {"data": "value2"})

        # Clear specific prefix
        await cache.clear("test")

        # Verify cleared
        assert await cache.get("test", "key1") is None
        assert await cache.get("test", "key2") is None

        await cache.close()


class TestSchemaCache:
    """Test schema cache functionality."""

    @pytest.mark.asyncio
    async def test_schema_cache_initialization(self):
        """Test schema cache initialization."""
        cache_manager = CacheManager()
        await cache_manager.initialize()

        schema_cache = SchemaCache(cache_manager)
        assert schema_cache.cache is cache_manager

        await cache_manager.close()

    @pytest.mark.asyncio
    async def test_schema_key_generation(self):
        """Test schema key generation."""
        cache_manager = CacheManager()
        await cache_manager.initialize()

        schema_cache = SchemaCache(cache_manager)

        # Create a temporary file for testing
        test_path = Path("test_schema.xsd")
        test_path.write_text('<?xml version="1.0"?><schema></schema>')

        try:
            key1 = schema_cache._get_schema_key(test_path, "xsd")
            key2 = schema_cache._get_schema_key(test_path, "xsd")

            # Same file should generate same key
            assert key1 == key2

            # Different file should generate different key
            test_path2 = Path("test_schema2.xsd")
            test_path2.write_text('<?xml version="1.0"?><schema></schema>')
            key3 = schema_cache._get_schema_key(test_path2, "xsd")
            assert key1 != key3

        finally:
            # Cleanup
            if test_path.exists():
                test_path.unlink()
            if test_path2.exists():
                test_path2.unlink()

        await cache_manager.close()
