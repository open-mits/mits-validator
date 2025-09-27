"""XSD validation level implementation."""

from __future__ import annotations

import time
from pathlib import Path

from lxml import etree

from mits_validator.models import Finding, FindingLevel, ValidationResult


class XSDValidator:
    """XSD validation level that validates XML against XSD schemas."""

    def __init__(self, schema_path: Path | None = None) -> None:
        self.schema_path = schema_path
        self._schema = None
        self._schema_loaded = False

    def _load_schema(self) -> bool:
        """Load XSD schema if available."""
        if self._schema_loaded:
            return self._schema is not None

        if not self.schema_path or not self.schema_path.exists():
            self._schema_loaded = True
            return False

        try:
            with open(self.schema_path, "rb") as f:
                schema_doc = etree.parse(f)
            self._schema = etree.XMLSchema(schema_doc)
            self._schema_loaded = True
            return True
        except (etree.XMLSyntaxError, etree.XMLSchemaParseError, FileNotFoundError):
            self._schema_loaded = True
            return False

    def validate(self, content: bytes) -> ValidationResult:
        """Validate XML content against XSD schema."""
        start_time = time.time()
        findings: list[Finding] = []

        # Load schema if not already loaded
        schema_available = self._load_schema()

        if not schema_available:
            findings.append(
                Finding(
                    level=FindingLevel.INFO,
                    code="XSD:SCHEMA_MISSING",
                    message="XSD schema not available for validation",
                    rule_ref="internal://XSD",
                )
            )
        else:
            try:
                # Parse XML content
                xml_doc = etree.fromstring(content)

                # Validate against schema
                if not self._schema.validate(xml_doc):
                    # Schema validation failed
                    findings.append(
                        Finding(
                            level=FindingLevel.ERROR,
                            code="XSD:VALIDATION_ERROR",
                            message="XML does not conform to XSD schema",
                            rule_ref="internal://XSD",
                        )
                    )

            except etree.XMLSyntaxError as e:
                findings.append(
                    Finding(
                        level=FindingLevel.ERROR,
                        code="XSD:PARSE_ERROR",
                        message=f"XML parsing failed: {e.msg}",
                        rule_ref="internal://XSD",
                    )
                )
            except etree.DocumentInvalid as e:
                # Schema validation failed
                findings.append(
                    Finding(
                        level=FindingLevel.ERROR,
                        code="XSD:VALIDATION_ERROR",
                        message=f"XSD validation failed: {e.msg}",
                        rule_ref="internal://XSD",
                    )
                )
            except Exception as e:
                findings.append(
                    Finding(
                        level=FindingLevel.ERROR,
                        code="ENGINE:LEVEL_CRASH",
                        message=f"XSD validation level crashed: {e}",
                        rule_ref="internal://XSD",
                    )
                )

        duration_ms = int((time.time() - start_time) * 1000)
        return ValidationResult(
            level="XSD",
            findings=findings,
            duration_ms=duration_ms,
        )

    def get_name(self) -> str:
        """Get the name of this validation level."""
        return "XSD"
