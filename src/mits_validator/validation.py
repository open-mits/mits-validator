from __future__ import annotations

import time
import uuid
from dataclasses import dataclass
from datetime import UTC
from enum import Enum
from typing import Any, Protocol
from xml.etree.ElementTree import ParseError

import lxml.etree as ET
from pydantic import BaseModel, Field


class FindingLevel(str, Enum):
    """Severity levels for validation findings."""

    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class ValidationLevel(str, Enum):
    """Available validation levels."""

    WELLFORMED = "WellFormed"
    XSD = "XSD"
    SCHEMATRON = "Schematron"
    SEMANTIC = "Semantic"


@dataclass
class Location:
    """Location information for a finding."""

    line: int | None = None
    column: int | None = None
    xpath: str | None = None


@dataclass
class Finding:
    """A single validation finding."""

    level: FindingLevel
    code: str
    message: str
    location: Location | None = None
    rule_ref: str = "internal://WellFormed"


@dataclass
class ValidationResult:
    """Result of a validation level execution."""

    level: ValidationLevel
    findings: list[Finding]
    duration_ms: int


class ValidationLevelProtocol(Protocol):
    """Protocol for validation levels."""

    def validate(self, content: bytes, content_type: str) -> ValidationResult:
        """Validate content and return findings."""
        ...


class WellFormedValidator:
    """Validates XML well-formedness."""

    def validate(self, content: bytes, content_type: str) -> ValidationResult:
        """Validate XML well-formedness."""
        start_time = time.time()
        findings: list[Finding] = []

        try:
            # Parse XML to check well-formedness
            ET.fromstring(content)

            # Check for suspicious content types
            if content_type and not any(
                ct in content_type.lower() for ct in ["xml", "text/xml", "application/xml"]
            ):
                findings.append(
                    Finding(
                        level=FindingLevel.WARNING,
                        code="WELLFORMED:SUSPICIOUS_CONTENT_TYPE",
                        message=f"Content type '{content_type}' may not be XML",
                        rule_ref="internal://WellFormed",
                    )
                )

        except (ParseError, ET.XMLSyntaxError) as e:
            # Extract line/column if available
            line = getattr(e, "lineno", None)
            column = getattr(e, "offset", None)

            findings.append(
                Finding(
                    level=FindingLevel.ERROR,
                    code="WELLFORMED:PARSE_ERROR",
                    message=f"XML parsing failed: {str(e)}",
                    location=Location(line=line, column=column) if line else None,
                    rule_ref="internal://WellFormed",
                )
            )
        except Exception as e:
            findings.append(
                Finding(
                    level=FindingLevel.ERROR,
                    code="WELLFORMED:UNEXPECTED_ERROR",
                    message=f"Unexpected error during XML parsing: {str(e)}",
                    rule_ref="internal://WellFormed",
                )
            )

        duration_ms = int((time.time() - start_time) * 1000)
        return ValidationResult(
            level=ValidationLevel.WELLFORMED, findings=findings, duration_ms=duration_ms
        )


class ValidationEngine:
    """Main validation engine with level registry."""

    def __init__(self) -> None:
        self._levels: dict[ValidationLevel, ValidationLevelProtocol] = {}
        self._register_default_levels()

    def _register_default_levels(self) -> None:
        """Register default validation levels."""
        self._levels[ValidationLevel.WELLFORMED] = WellFormedValidator()

    def validate(
        self, content: bytes, content_type: str, levels: list[ValidationLevel] | None = None
    ) -> list[ValidationResult]:
        """Validate content using specified levels."""
        if levels is None:
            levels = [ValidationLevel.WELLFORMED]

        results = []
        for level in levels:
            if level in self._levels:
                validator = self._levels[level]
                result = validator.validate(content, content_type)
                results.append(result)

        return results


class ValidationRequest(BaseModel):
    """Request model for validation."""

    source: str = Field(..., description="Source type: 'file' or 'url'")
    url: str | None = Field(None, description="URL if source is 'url'")
    filename: str | None = Field(None, description="Filename if source is 'file'")
    size_bytes: int = Field(..., description="Size in bytes")
    content_type: str = Field(..., description="Content type")


class ValidationResponse(BaseModel):
    """Structured validation response envelope."""

    api_version: str = "1.0"
    validator: dict[str, Any] = Field(
        default_factory=lambda: {
            "name": "mits-validator",
            "spec_version": "unversioned",
            "profile": "default",
            "levels_executed": ["WellFormed"],
        }
    )
    input: ValidationRequest
    summary: dict[str, Any] = Field(
        default_factory=lambda: {"valid": True, "errors": 0, "warnings": 0, "duration_ms": 0}
    )
    findings: list[dict[str, Any]] = Field(default_factory=list)
    derived: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(
        default_factory=lambda: {"request_id": str(uuid.uuid4()), "timestamp": "", "engine": {}}
    )

    def model_post_init(self, __context: Any) -> None:
        """Post-initialization to set computed fields."""
        from datetime import datetime

        import fastapi
        import lxml

        # Set timestamp
        self.metadata["timestamp"] = datetime.now(UTC).isoformat()

        # Set engine versions
        self.metadata["engine"] = {"fastapi": fastapi.__version__, "lxml": lxml.__version__}

        # Set levels executed
        self.validator["levels_executed"] = ["WellFormed"]

        # Compute summary from findings
        errors = sum(1 for f in self.findings if f.get("level") == "error")
        warnings = sum(1 for f in self.findings if f.get("level") == "warning")

        self.summary.update({"valid": errors == 0, "errors": errors, "warnings": warnings})
