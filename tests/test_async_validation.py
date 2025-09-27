"""Tests for async validation functionality."""

import asyncio

import pytest
from mits_validator.async_validation import AsyncValidationEngine, get_async_validation_engine
from mits_validator.models import ValidationRequest


class TestAsyncValidationEngine:
    """Test async validation engine functionality."""

    def test_async_validation_engine_initialization(self):
        """Test async validation engine initialization."""
        engine = AsyncValidationEngine(max_concurrent_validations=5)
        assert engine.max_concurrent_validations == 5
        assert engine.semaphore._value == 5
        assert len(engine.active_validations) == 0

    @pytest.mark.asyncio
    async def test_validate_async_basic(self):
        """Test basic async validation."""
        engine = AsyncValidationEngine()

        # Create a simple validation request
        request = ValidationRequest(
            content=b'<?xml version="1.0"?><root><item>test</item></root>',
            content_type="application/xml",
            source="file",
        )

        result = await engine.validate_async(request, "test-validation-1", "default")

        assert result is not None
        assert hasattr(result, "level")
        assert hasattr(result, "findings")
        assert hasattr(result, "duration_ms")
        assert result.level == "Async"

    @pytest.mark.asyncio
    async def test_validate_async_invalid_xml(self):
        """Test async validation with invalid XML."""
        engine = AsyncValidationEngine()

        # Create request with invalid XML
        request = ValidationRequest(
            content=b'<?xml version="1.0"?><root><item>test</item>',  # Missing closing tag
            content_type="application/xml",
            source="file",
        )

        result = await engine.validate_async(request, "test-validation-2", "default")

        assert result is not None
        # Should have validation errors
        assert len(result.findings) > 0

    @pytest.mark.asyncio
    async def test_cancel_validation(self):
        """Test canceling a validation."""
        engine = AsyncValidationEngine()

        # Start a long-running validation
        request = ValidationRequest(
            content=b'<?xml version="1.0"?><root><item>test</item></root>',
            content_type="application/xml",
            source="file",
        )

        # Cancel before it completes
        cancelled = await engine.cancel_validation("test-validation-3")
        assert not cancelled  # Should not be found since it's not running

        # Test with actual running validation
        task = asyncio.create_task(engine.validate_async(request, "test-validation-4", "default"))
        engine.active_validations["test-validation-4"] = task

        cancelled = await engine.cancel_validation("test-validation-4")
        assert cancelled
        assert "test-validation-4" not in engine.active_validations

    def test_get_active_validations(self):
        """Test getting active validations."""
        engine = AsyncValidationEngine()
        assert engine.get_active_validations() == []

        # Add a mock active validation
        engine.active_validations["test-1"] = None
        assert "test-1" in engine.get_active_validations()

    def test_get_stats(self):
        """Test getting engine statistics."""
        engine = AsyncValidationEngine(max_concurrent_validations=10)
        stats = engine.get_stats()

        assert "max_concurrent_validations" in stats
        assert "active_validations" in stats
        assert "available_slots" in stats
        assert stats["max_concurrent_validations"] == 10


class TestGlobalFunctions:
    """Test global async validation functions."""

    def test_get_async_validation_engine(self):
        """Test getting async validation engine."""
        engine = get_async_validation_engine()
        assert isinstance(engine, AsyncValidationEngine)

        # Should return the same instance
        engine2 = get_async_validation_engine()
        assert engine is engine2
