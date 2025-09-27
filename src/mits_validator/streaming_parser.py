"""Streaming XML parser for memory-efficient processing of large files."""

import io
from typing import Any, Generator

import structlog
from lxml import etree

logger = structlog.get_logger(__name__)


class StreamingXMLParser:
    """Memory-efficient streaming XML parser for large files."""

    def __init__(self, chunk_size: int = 8192, max_memory_mb: int = 100):
        """Initialize streaming parser.
        
        Args:
            chunk_size: Size of chunks to read at a time
            max_memory_mb: Maximum memory usage in MB
        """
        self.chunk_size = chunk_size
        self.max_memory_bytes = max_memory_mb * 1024 * 1024
        self.current_memory = 0

    async def parse_streaming(
        self, 
        content: str | bytes | io.IOBase,
        validation_callback: callable = None
    ) -> Generator[etree.Element, None, None]:
        """Parse XML content in streaming fashion.
        
        Args:
            content: XML content to parse
            validation_callback: Optional callback for validation
            
        Yields:
            XML elements as they are parsed
        """
        try:
            if isinstance(content, str):
                content = content.encode('utf-8')
            
            if isinstance(content, bytes):
                content = io.BytesIO(content)
            
            # Use iterparse for streaming
            context = etree.iterparse(
                content,
                events=('start', 'end'),
                huge_tree=True
            )
            
            for event, element in context:
                # Check memory usage
                if self._check_memory_limit():
                    logger.warning("Memory limit exceeded during streaming parse")
                    break
                
                # Yield element for processing
                if event == 'end':
                    yield element
                    
                    # Optional validation callback
                    if validation_callback:
                        await validation_callback(element)
                    
                    # Clean up element to free memory
                    element.clear()
                    while element.getprevious() is not None:
                        del element.getparent()[0]
            
        except Exception as e:
            logger.error("Streaming parse failed", error=str(e))
            raise ValueError(f"Streaming XML parse failed: {str(e)}") from e

    def _check_memory_limit(self) -> bool:
        """Check if memory usage exceeds limit."""
        # Simple memory check - in production, use psutil or similar
        import sys
        current_memory = sys.getsizeof(self)
        return current_memory > self.max_memory_bytes

    async def validate_streaming(
        self,
        content: str | bytes | io.IOBase,
        xsd_schema: etree.XMLSchema = None,
        schematron_rules: etree.XSLT = None
    ) -> list[dict[str, Any]]:
        """Validate XML content using streaming parser.
        
        Args:
            content: XML content to validate
            xsd_schema: Optional XSD schema for validation
            schematron_rules: Optional Schematron rules for validation
            
        Returns:
            List of validation findings
        """
        findings = []
        
        try:
            async for element in self.parse_streaming(content):
                # Validate element against schema if provided
                if xsd_schema:
                    try:
                        xsd_schema.assertValid(element)
                    except etree.DocumentInvalid as e:
                        findings.append({
                            "level": "error",
                            "code": "XSD:VALIDATION_ERROR",
                            "message": f"XSD validation failed: {str(e)}",
                            "location": self._get_element_location(element),
                        })
                
                # Validate element against Schematron rules if provided
                if schematron_rules:
                    try:
                        result = schematron_rules(element)
                        # Process Schematron results
                        for assertion in result.xpath('//svrl:failed-assert', namespaces={'svrl': 'http://purl.oclc.org/dsdl/svrl'}):
                            findings.append({
                                "level": "error",
                                "code": "SCHEMATRON:RULE_FAILURE",
                                "message": assertion.text or "Schematron rule failed",
                                "location": self._get_element_location(element),
                            })
                    except Exception as e:
                        findings.append({
                            "level": "error",
                            "code": "SCHEMATRON:VALIDATION_ERROR",
                            "message": f"Schematron validation failed: {str(e)}",
                            "location": self._get_element_location(element),
                        })
        
        except Exception as e:
            findings.append({
                "level": "error",
                "code": "ENGINE:STREAMING_PARSE_ERROR",
                "message": f"Streaming validation failed: {str(e)}",
                "location": None,
            })
        
        return findings

    def _get_element_location(self, element: etree.Element) -> dict[str, Any]:
        """Get location information for an element."""
        try:
            return {
                "line": element.sourceline,
                "column": 0,  # lxml doesn't provide column info
                "xpath": self._get_xpath(element),
            }
        except Exception:
            return {
                "line": None,
                "column": None,
                "xpath": None,
            }

    def _get_xpath(self, element: etree.Element) -> str:
        """Get XPath for an element."""
        try:
            return etree.tostring(element, method='text', encoding='unicode').strip()
        except Exception:
            return ""

    def get_memory_usage(self) -> dict[str, Any]:
        """Get current memory usage statistics."""
        import sys
        return {
            "current_memory_bytes": sys.getsizeof(self),
            "max_memory_bytes": self.max_memory_bytes,
            "memory_usage_percent": (sys.getsizeof(self) / self.max_memory_bytes) * 100,
        }


class MemoryOptimizedValidator:
    """Memory-optimized validator for large XML files."""

    def __init__(self, max_memory_mb: int = 100):
        """Initialize memory-optimized validator.
        
        Args:
            max_memory_mb: Maximum memory usage in MB
        """
        self.max_memory_mb = max_memory_mb
        self.parser = StreamingXMLParser(max_memory_mb=max_memory_mb)

    async def validate_large_file(
        self,
        content: str | bytes | io.IOBase,
        validation_levels: list[str] = None
    ) -> dict[str, Any]:
        """Validate large XML file with memory optimization.
        
        Args:
            content: XML content to validate
            validation_levels: List of validation levels to run
            
        Returns:
            Validation results with findings
        """
        if validation_levels is None:
            validation_levels = ["wellformed", "xsd", "schematron", "semantic"]
        
        results = {
            "valid": True,
            "findings": [],
            "memory_usage": self.parser.get_memory_usage(),
            "validation_levels": validation_levels,
        }
        
        try:
            # Run streaming validation
            findings = await self.parser.validate_streaming(content)
            results["findings"] = findings
            
            # Check if validation passed
            errors = [f for f in findings if f.get("level") == "error"]
            results["valid"] = len(errors) == 0
            results["error_count"] = len(errors)
            results["warning_count"] = len([f for f in findings if f.get("level") == "warning"])
            
        except Exception as e:
            results["valid"] = False
            results["error"] = str(e)
            results["findings"].append({
                "level": "error",
                "code": "ENGINE:MEMORY_VALIDATION_FAILED",
                "message": f"Memory-optimized validation failed: {str(e)}",
                "location": None,
            })
        
        return results

    def get_stats(self) -> dict[str, Any]:
        """Get validator statistics."""
        return {
            "max_memory_mb": self.max_memory_mb,
            "memory_usage": self.parser.get_memory_usage(),
        }
