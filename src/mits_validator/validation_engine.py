from __future__ import annotations

import time
import uuid
from datetime import UTC
from pathlib import Path
from typing import Any, Protocol
from xml.etree.ElementTree import ParseError

import lxml.etree as ET

from mits_validator.levels import SchematronValidator, XSDValidator
from mits_validator.levels.semantic import SemanticValidator
from mits_validator.models import (
    Finding,
    FindingLevel,
    Location,
    ValidationRequest,
    ValidationResult,
)
from mits_validator.profile_loader import get_profile_loader
from mits_validator.profile_models import ProfileConfig


class ValidationLevelProtocol(Protocol):
    """Protocol for validation levels."""

    def validate(self, content: bytes) -> ValidationResult:
        """Validate content and return findings."""
        ...

    def get_name(self) -> str:
        """Get the name of this validation level."""
        ...


class WellFormedValidator:
    """Validates XML well-formedness."""

    def validate(self, content: bytes, content_type: str | None = None) -> ValidationResult:
        """Validate XML well-formedness."""
        start_time = time.time()
        findings: list[Finding] = []

        # Check for suspicious content types
        if content_type and content_type.lower() in ["application/octet-stream", "text/plain"]:
            findings.append(
                Finding(
                    level=FindingLevel.WARNING,
                    code="WELLFORMED:SUSPICIOUS_CONTENT_TYPE",
                    message=f"Content type '{content_type}' may not be XML",
                    rule_ref="internal://WellFormed",
                )
            )

        try:
            # Parse XML to check well-formedness
            ET.fromstring(content)

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
            level="WellFormed", findings=findings, duration_ms=duration_ms
        )

    def get_name(self) -> str:
        """Get the name of this validation level."""
        return "WellFormed"


class ValidationEngine:
    """Main validation engine with level registry."""

    def __init__(
        self, profile: str | None = None, rules_dir: Path | None = None, version: str = "mits-5.0"
    ) -> None:
        self._levels: dict[str, ValidationLevelProtocol] = {}
        self._rules_dir = rules_dir or Path("rules")
        self._version = version
        self._profile_name = profile or "default"
        self._profile_config: ProfileConfig | None = None
        self._profile_loader = get_profile_loader(self._rules_dir)
        self._load_profile()
        self._register_levels()

    def _load_profile(self) -> None:
        """Load profile configuration."""
        self._profile_config = self._profile_loader.load_profile(self._profile_name, self._version)
        if not self._profile_config:
            # Fall back to default profile
            self._profile_config = self._profile_loader.load_profile("default", self._version)
            if not self._profile_config:
                # Create a minimal default profile
                from mits_validator.profile_models import ProfileConfig
                self._profile_config = ProfileConfig(
                    name="default",
                    description="Default profile",
                    enabled_levels=["WellFormed", "XSD", "Schematron", "Semantic"],
                    severity_overrides={}
                )

    def _register_levels(self) -> None:
        """Register validation levels based on profile."""
        # Always register WellFormed
        self._levels["WellFormed"] = WellFormedValidator()

        if not self._profile_config:
            return
            
        # Register XSD if in profile
        if "XSD" in self._profile_config.enabled_levels:
            xsd_schema_path = self._rules_dir / "xsd" / "schema.xsd"
            self._levels["XSD"] = XSDValidator(xsd_schema_path)

        # Register Schematron if in profile
        if "Schematron" in self._profile_config.enabled_levels:
            self._levels["Schematron"] = SchematronValidator(self._rules_dir, self._version)

        # Register Semantic if in profile
        if "Semantic" in self._profile_config.enabled_levels:
            self._levels["Semantic"] = SemanticValidator(self._rules_dir, self._version)

    def validate(
        self, content: bytes, levels: list[str] | None = None, content_type: str | None = None
    ) -> list[ValidationResult]:
        """Validate content using specified levels with defensive error handling."""
        if levels is None:
            levels = self._profile_config.enabled_levels if self._profile_config else []

        results = []
        for level_name in levels:
            if level_name in self._levels:
                try:
                    validator = self._levels[level_name]
                    # Pass content_type to WellFormed validator
                    if level_name == "WellFormed":
                        result = validator.validate(content, content_type)
                    else:
                        result = validator.validate(content)
                    # Apply severity overrides if configured
                    self._apply_severity_overrides(result)
                    results.append(result)
                except Exception as e:
                    # Defensive: capture level crashes as findings
                    crash_result = ValidationResult(
                        level=level_name,
                        findings=[
                            Finding(
                                level=FindingLevel.ERROR,
                                code="ENGINE:LEVEL_CRASH",
                                message=f"Validation level {level_name} crashed: {str(e)}",
                                rule_ref=f"internal://{level_name}",
                            )
                        ],
                        duration_ms=0,
                    )
                    results.append(crash_result)
            else:
                # Level not available - report as missing
                missing_result = ValidationResult(
                    level=level_name,
                    findings=[
                        Finding(
                            level=FindingLevel.WARNING,
                            code="ENGINE:RULES_MISSING",
                            message=f"Validation level {level_name} not available",
                            rule_ref=f"internal://{level_name}",
                        )
                    ],
                    duration_ms=0,
                )
                results.append(missing_result)

        return results

    def _apply_severity_overrides(self, result: ValidationResult) -> None:
        """Apply severity overrides from profile configuration."""
        if not self._profile_config or not self._profile_config.severity_overrides:
            return

        for finding in result.findings:
            if finding.code in self._profile_config.severity_overrides:
                finding.level = self._profile_config.severity_overrides[finding.code]

    def get_available_levels(self) -> list[str]:
        """Get list of available validation levels."""
        return list(self._levels.keys())

    def get_profile_info(self) -> dict[str, Any]:
        """Get current profile information."""
        if not self._profile_config:
            return {
                "name": "default",
                "description": "Default profile",
                "levels": ["WellFormed"],
                "severity_overrides": {},
                "intake_limits": None,
            }
            
        return {
            "name": self._profile_config.name,
            "description": self._profile_config.description,
            "levels": self._profile_config.enabled_levels,
            "severity_overrides": {
                k: v.value for k, v in self._profile_config.severity_overrides.items()
            },
            "intake_limits": (
                self._profile_config.intake_limits.__dict__ 
                if self._profile_config.intake_limits 
                else None
            ),
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
        levels_executed.append(result.level)
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
            "levels_available": ["WellFormed", "XSD", "Schematron", "Semantic"],
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
