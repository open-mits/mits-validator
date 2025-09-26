from __future__ import annotations

import time
import uuid
from datetime import UTC
from pathlib import Path
from typing import Any, Protocol
from xml.etree.ElementTree import ParseError

import lxml.etree as ET
from pydantic import BaseModel, Field

from mits_validator.levels import SchematronValidator, XSDValidator
from mits_validator.models import Finding, FindingLevel, Location, ValidationLevel, ValidationResult
from mits_validator.profiles import get_profile


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

    def __init__(self, profile: str | None = None, rules_dir: Path | None = None) -> None:
        self._levels: dict[ValidationLevel, ValidationLevelProtocol] = {}
        self._profile = get_profile(profile)
        self._rules_dir = rules_dir or Path("rules")
        self._register_levels()

    def _register_levels(self) -> None:
        """Register validation levels based on profile."""
        # Always register WellFormed
        self._levels[ValidationLevel.WELLFORMED] = WellFormedValidator()

        # Register XSD if in profile
        if ValidationLevel.XSD in self._profile.levels:
            xsd_schema_path = self._rules_dir / "xsd" / "schema.xsd" if self._rules_dir else None
            self._levels[ValidationLevel.XSD] = XSDValidator(xsd_schema_path)

        # Register Schematron if in profile
        if ValidationLevel.SCHEMATRON in self._profile.levels:
            schematron_rules_path = (
                self._rules_dir / "schematron" / "rules.sch" if self._rules_dir else None
            )
            self._levels[ValidationLevel.SCHEMATRON] = SchematronValidator(schematron_rules_path)

    def validate(
        self, content: bytes, content_type: str, levels: list[ValidationLevel] | None = None
    ) -> list[ValidationResult]:
        """Validate content using specified levels with defensive error handling."""
        if levels is None:
            levels = self._profile.levels

        results = []
        for level in levels:
            if level in self._levels:
                try:
                    validator = self._levels[level]
                    result = validator.validate(content, content_type)
                    results.append(result)
                except Exception as e:
                    # Defensive: capture level crashes as findings
                    crash_result = ValidationResult(
                        level=level,
                        findings=[
                            Finding(
                                level=FindingLevel.ERROR,
                                code="ENGINE:LEVEL_CRASH",
                                message=f"Validation level {level.value} crashed: {str(e)}",
                                rule_ref=f"internal://{level.value}",
                            )
                        ],
                        duration_ms=0,
                    )
                    results.append(crash_result)
            else:
                # Level not available - report as missing
                missing_result = ValidationResult(
                    level=level,
                    findings=[
                        Finding(
                            level=FindingLevel.WARNING,
                            code="ENGINE:RULES_MISSING",
                            message=f"Validation level {level.value} not available",
                            rule_ref=f"internal://{level.value}",
                        )
                    ],
                    duration_ms=0,
                )
                results.append(missing_result)

        return results

    def get_available_levels(self) -> list[str]:
        """Get list of available validation levels."""
        return [level.value for level in self._levels.keys()]

    def get_profile_info(self) -> dict[str, Any]:
        """Get current profile information."""
        return {
            "name": self._profile.name,
            "description": self._profile.description,
            "levels": [level.value for level in self._profile.levels],
            "max_size_mb": self._profile.max_size_mb,
            "timeout_seconds": self._profile.timeout_seconds,
            "allowed_content_types": self._profile.allowed_content_types,
        }


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
            "levels_available": ["WellFormed"],
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
