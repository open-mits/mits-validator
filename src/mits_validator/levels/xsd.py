from __future__ import annotations

import time
from pathlib import Path

import lxml.etree as ET
from lxml import etree

from mits_validator.models import Finding, FindingLevel, ValidationLevel, ValidationResult


class XSDValidator:
    """Validates XML against XSD schemas."""

    def __init__(self, schema_path: Path | None = None):
        self.schema_path = schema_path
        self._schema: etree.XMLSchema | None = None
        self._load_schema()

    def _load_schema(self) -> None:
        """Load XSD schema if available."""
        if not self.schema_path or not self.schema_path.exists():
            return

        try:
            schema_doc = etree.parse(str(self.schema_path))
            self._schema = etree.XMLSchema(schema_doc)
        except Exception:
            # Schema loading failed - will be reported as missing
            self._schema = None

    def validate(self, content: bytes, content_type: str) -> ValidationResult:
        """Validate XML against XSD schema."""
        start_time = time.time()
        findings: list[Finding] = []

        # Check if schema is available
        if not self._schema:
            findings.append(
                Finding(
                    level=FindingLevel.WARNING,
                    code="XSD:SCHEMA_MISSING",
                    message="XSD schema not available for validation",
                    rule_ref="internal://XSD",
                )
            )
        else:
            try:
                # Parse XML
                xml_doc = ET.fromstring(content)

                # Validate against schema
                self._schema.assertValid(xml_doc)

            except etree.DocumentInvalid as e:
                # XSD validation failed
                findings.append(
                    Finding(
                        level=FindingLevel.ERROR,
                        code="XSD:VALIDATION_ERROR",
                        message=f"XSD validation failed: {str(e)}",
                        rule_ref="internal://XSD",
                    )
                )
            except Exception as e:
                # Unexpected error during XSD validation
                findings.append(
                    Finding(
                        level=FindingLevel.ERROR,
                        code="ENGINE:LEVEL_CRASH",
                        message=f"XSD validation crashed: {str(e)}",
                        rule_ref="internal://XSD",
                    )
                )

        duration_ms = int((time.time() - start_time) * 1000)
        return ValidationResult(
            level=ValidationLevel.XSD, findings=findings, duration_ms=duration_ms
        )
