"""Tests for streaming XML parser functionality."""

import io
import pytest
from mits_validator.streaming_parser import MemoryOptimizedValidator, StreamingXMLParser


class TestStreamingXMLParser:
    """Test streaming XML parser functionality."""

    def test_streaming_parser_initialization(self):
        """Test streaming parser initialization."""
        parser = StreamingXMLParser(chunk_size=4096, max_memory_mb=50)
        assert parser.chunk_size == 4096
        assert parser.max_memory_bytes == 50 * 1024 * 1024

    @pytest.mark.asyncio
    async def test_parse_streaming_basic(self):
        """Test basic streaming parse."""
        parser = StreamingXMLParser()
        
        xml_content = '<?xml version="1.0"?><root><item>test</item></root>'
        elements = []
        
        async for element in parser.parse_streaming(xml_content):
            elements.append(element)
        
        assert len(elements) > 0

    @pytest.mark.asyncio
    async def test_parse_streaming_with_callback(self):
        """Test streaming parse with validation callback."""
        parser = StreamingXMLParser()
        
        xml_content = '<?xml version="1.0"?><root><item>test</item></root>'
        callback_called = False
        
        async def validation_callback(element):
            nonlocal callback_called
            callback_called = True
        
        async for element in parser.parse_streaming(xml_content, validation_callback):
            pass
        
        assert callback_called

    @pytest.mark.asyncio
    async def test_validate_streaming(self):
        """Test streaming validation."""
        parser = StreamingXMLParser()
        
        xml_content = '<?xml version="1.0"?><root><item>test</item></root>'
        findings = await parser.validate_streaming(xml_content)
        
        assert isinstance(findings, list)

    def test_get_memory_usage(self):
        """Test getting memory usage."""
        parser = StreamingXMLParser()
        usage = parser.get_memory_usage()
        
        assert "current_memory_bytes" in usage
        assert "max_memory_bytes" in usage
        assert "memory_usage_percent" in usage


class TestMemoryOptimizedValidator:
    """Test memory-optimized validator functionality."""

    def test_memory_optimized_validator_initialization(self):
        """Test memory-optimized validator initialization."""
        validator = MemoryOptimizedValidator(max_memory_mb=100)
        assert validator.max_memory_mb == 100
        assert validator.parser.max_memory_bytes == 100 * 1024 * 1024

    @pytest.mark.asyncio
    async def test_validate_large_file(self):
        """Test validating large file."""
        validator = MemoryOptimizedValidator(max_memory_mb=50)
        
        xml_content = '<?xml version="1.0"?><root><item>test</item></root>'
        result = await validator.validate_large_file(xml_content)
        
        assert "valid" in result
        assert "findings" in result
        assert "memory_usage" in result
        assert "validation_levels" in result

    @pytest.mark.asyncio
    async def test_validate_large_file_with_levels(self):
        """Test validating large file with specific levels."""
        validator = MemoryOptimizedValidator(max_memory_mb=50)
        
        xml_content = '<?xml version="1.0"?><root><item>test</item></root>'
        result = await validator.validate_large_file(
            xml_content, 
            validation_levels=["wellformed", "xsd"]
        )
        
        assert "valid" in result
        assert "validation_levels" in result
        assert result["validation_levels"] == ["wellformed", "xsd"]

    def test_get_stats(self):
        """Test getting validator statistics."""
        validator = MemoryOptimizedValidator(max_memory_mb=100)
        stats = validator.get_stats()
        
        assert "max_memory_mb" in stats
        assert "memory_usage" in stats
        assert stats["max_memory_mb"] == 100
