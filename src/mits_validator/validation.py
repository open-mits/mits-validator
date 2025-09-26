from __future__ import annotations

import time
import uuid
from datetime import UTC
from pathlib import Path
from typing import Any, Protocol
from xml.etree.ElementTree import ParseError

import lxml.etree as ET

from mits_validator.levels import SchematronValidator, XSDValidator
from mits_validator.models import (
    Finding,
    FindingLevel,
    Location,
    ValidationLevel,
    ValidationRequest,
    ValidationResult,
)
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


def build_v1_envelope(
    request: ValidationRequest,
    results: list[ValidationResult],
    profile_name: str = "default",
    duration_ms: int = 0,
) -> dict[str, Any]:
    """Build a v1 response envelope from validation results."""
    from datetime import datetime

    import fastapi
    import lxml

    # Collect all findings
    all_findings = []
    levels_executed = []

    for result in results:
        levels_executed.append(result.level.value)
        for finding in result.findings:
            finding_dict: dict[str, Any] = {
                "level": finding.level.value,
                "code": finding.code,
                "message": finding.message,
                "rule_ref": finding.rule_ref,
            }
            if finding.location:
                finding_dict["location"] = {
                    "line": finding.location.line,
                    "column": finding.location.column,
                    "xpath": finding.location.xpath,
                }
            all_findings.append(finding_dict)

    # Count errors and warnings
    errors = sum(1 for f in all_findings if f["level"] == "error")
    warnings = sum(1 for f in all_findings if f["level"] == "warning")

    return {
        "api_version": "1.0",
        "validator": {
            "name": "mits-validator",
            "spec_version": "unversioned",
            "profile": profile_name,
            "levels_available": ["WellFormed", "XSD", "Schematron"],
            "levels_executed": levels_executed,
        },
        "input": {
            "source": request.source,
            "url": request.url,
            "filename": request.filename,
            "size_bytes": request.size_bytes,
            "content_type": request.content_type,
        },
        "summary": {
            "valid": errors == 0,
            "errors": errors,
            "warnings": warnings,
            "duration_ms": duration_ms,
        },
        "findings": all_findings,
        "derived": {},
        "metadata": {
            "request_id": str(uuid.uuid4()),
            "timestamp": datetime.now(UTC).isoformat(),
            "engine": {
                "fastapi": fastapi.__version__,
                "lxml": lxml.__version__,
            },
        },
    }
