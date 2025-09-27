"""Async validation engine for large XML files."""

import asyncio
import io
import time
from typing import Any

import structlog
from lxml import etree

from mits_validator.cache import get_schema_cache
from mits_validator.logging_config import create_validation_logger
from mits_validator.metrics import ValidationTimer, record_validation_error
from mits_validator.models import Finding, FindingLevel, Location, ValidationRequest, ValidationResult

logger = structlog.get_logger(__name__)


class AsyncValidationEngine:
    """Async validation engine for processing large XML files efficiently."""

    def __init__(self, max_concurrent_validations: int = 10):
        """Initialize async validation engine.
        
        Args:
            max_concurrent_validations: Maximum number of concurrent validations
        """
        self.max_concurrent_validations = max_concurrent_validations
        self.semaphore = asyncio.Semaphore(max_concurrent_validations)
        self.active_validations: dict[str, asyncio.Task] = {}

    async def validate_async(
        self,
        request: ValidationRequest,
        validation_id: str,
        profile: str = "default",
    ) -> ValidationResult:
        """Validate XML content asynchronously.
        
        Args:
            request: Validation request containing XML content
            validation_id: Unique identifier for this validation
            profile: Validation profile to use
            
        Returns:
            ValidationResult with findings and metadata
        """
        start_time = time.time()
        async with self.semaphore:
            try:
                # Create validation logger
                validation_logger = create_validation_logger(validation_id, "Async", profile)
                
                # Start validation timing
                with ValidationTimer(validation_id, "Async", profile):
                    validation_logger.start_validation(
                        len(request.content), 
                        getattr(request, 'content_type', 'application/xml')
                    )
                    
                    # Parse XML asynchronously
                    xml_doc = await self._parse_xml_async(request.content)
                    
                    # Run validation levels asynchronously
                    findings = await self._run_validation_levels_async(xml_doc, profile)
                    
                    # Determine if validation passed
                    errors = [f for f in findings if f.level == FindingLevel.ERROR]
                    warnings = [f for f in findings if f.level == FindingLevel.WARNING]
                    valid = len(errors) == 0
                    
                    # Log completion
                    validation_logger.end_validation(valid, len(errors), len(warnings), findings)
                    
                    duration_ms = int((time.time() - start_time) * 1000)
                    return ValidationResult(
                        level="Async",
                        findings=findings,
                        duration_ms=duration_ms,
                    )
                    
            except Exception as e:
                logger.error("Async validation failed", validation_id=validation_id, error=str(e))
                record_validation_error("ENGINE:ASYNC_VALIDATION_FAILED", "Async")
                
                # Return error result
                error_finding = Finding(
                    level=FindingLevel.ERROR,
                    code="ENGINE:ASYNC_VALIDATION_FAILED",
                    message=f"Async validation failed: {str(e)}",
                    location=None,
                )
                
                return ValidationResult(
                    level="Async",
                    findings=[error_finding],
                    duration_ms=0,
                )

    async def _parse_xml_async(self, content: str | bytes) -> etree.Element:
        """Parse XML content asynchronously.
        
        Args:
            content: XML content to parse
            
        Returns:
            Parsed XML element
            
        Raises:
            ValueError: If XML parsing fails
        """
        try:
            # Run XML parsing in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            xml_doc = await loop.run_in_executor(
                None, 
                self._parse_xml_sync, 
                content
            )
            return xml_doc
        except Exception as e:
            raise ValueError(f"Failed to parse XML: {str(e)}") from e

    def _parse_xml_sync(self, content: str | bytes) -> etree.Element:
        """Synchronous XML parsing (runs in thread pool).
        
        Args:
            content: XML content to parse
            
        Returns:
            Parsed XML element
        """
        if isinstance(content, str):
            content = content.encode('utf-8')
        
        try:
            return etree.fromstring(content)
        except etree.XMLSyntaxError as e:
            raise ValueError(f"Invalid XML syntax: {str(e)}") from e

    async def _run_validation_levels_async(
        self, 
        xml_doc: etree.Element, 
        profile: str
    ) -> list[Finding]:
        """Run validation levels asynchronously.
        
        Args:
            xml_doc: Parsed XML document
            profile: Validation profile
            
        Returns:
            List of validation findings
        """
        findings = []
        
        # Run validation levels concurrently
        tasks = [
            self._validate_wellformed_async(xml_doc),
            self._validate_xsd_async(xml_doc, profile),
            self._validate_schematron_async(xml_doc, profile),
            self._validate_semantic_async(xml_doc, profile),
        ]
        
        # Wait for all validations to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Collect findings from all levels
        for result in results:
            if isinstance(result, Exception):
                logger.error("Validation level failed", error=str(result))
                error_finding = Finding(
                    level=FindingLevel.ERROR,
                    code="ENGINE:LEVEL_CRASH",
                    message=f"Validation level failed: {str(result)}",
                    location=None,
                )
                findings.append(error_finding)
            elif isinstance(result, list):
                findings.extend(result)
        
        return findings

    async def _validate_wellformed_async(self, xml_doc: etree.Element) -> list[Finding]:
        """Validate XML well-formedness asynchronously."""
        try:
            # XML is already parsed, so it's well-formed
            return []
        except Exception as e:
            return [Finding(
                level=FindingLevel.ERROR,
                code="WELLFORMED:PARSE_ERROR",
                message=f"XML parsing failed: {str(e)}",
                location=None,
            )]

    async def _validate_xsd_async(self, xml_doc: etree.Element, profile: str) -> list[Finding]:
        """Validate XML against XSD schema asynchronously."""
        try:
            # TODO: Implement XSD validation with caching
            # For now, return empty findings
            return []
        except Exception as e:
            return [Finding(
                level=FindingLevel.ERROR,
                code="XSD:VALIDATION_ERROR",
                message=f"XSD validation failed: {str(e)}",
                location=None,
            )]

    async def _validate_schematron_async(self, xml_doc: etree.Element, profile: str) -> list[Finding]:
        """Validate XML against Schematron rules asynchronously."""
        try:
            # TODO: Implement Schematron validation with caching
            # For now, return empty findings
            return []
        except Exception as e:
            return [Finding(
                level=FindingLevel.ERROR,
                code="SCHEMATRON:VALIDATION_ERROR",
                message=f"Schematron validation failed: {str(e)}",
                location=None,
            )]

    async def _validate_semantic_async(self, xml_doc: etree.Element, profile: str) -> list[Finding]:
        """Validate XML semantics asynchronously."""
        try:
            # TODO: Implement semantic validation
            # For now, return empty findings
            return []
        except Exception as e:
            return [Finding(
                level=FindingLevel.ERROR,
                code="SEMANTIC:VALIDATION_ERROR",
                message=f"Semantic validation failed: {str(e)}",
                location=None,
            )]

    async def cancel_validation(self, validation_id: str) -> bool:
        """Cancel a running validation.
        
        Args:
            validation_id: ID of validation to cancel
            
        Returns:
            True if validation was cancelled, False if not found
        """
        if validation_id in self.active_validations:
            task = self.active_validations[validation_id]
            task.cancel()
            del self.active_validations[validation_id]
            return True
        return False

    def get_active_validations(self) -> list[str]:
        """Get list of active validation IDs."""
        return list(self.active_validations.keys())

    def get_stats(self) -> dict[str, Any]:
        """Get validation engine statistics."""
        return {
            "max_concurrent_validations": self.max_concurrent_validations,
            "active_validations": len(self.active_validations),
            "available_slots": self.semaphore._value,
        }


# Global async validation engine
_async_engine: AsyncValidationEngine | None = None


def get_async_validation_engine() -> AsyncValidationEngine:
    """Get or create global async validation engine."""
    global _async_engine
    if _async_engine is None:
        _async_engine = AsyncValidationEngine()
    return _async_engine
