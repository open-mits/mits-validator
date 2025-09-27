"""XSD validation for MITS 5.0 schemas."""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any

from lxml import etree
from lxml.etree import XMLSchema, XMLSyntaxError

from mits_validator.models import Finding, FindingLevel, ValidationResult


class XSDValidationError(Exception):
    """XSD validation error."""

    pass


def validate_xsd(
    xml_content: str | bytes | Path,
    schema_path: Path | None = None,
) -> ValidationResult:
    """
    Validate XML content against MITS 5.0 XSD schema.

    Args:
        xml_content: XML content to validate (string, bytes, or file path)
        schema_path: Path to XSD schema file (defaults to MITS 5.0 schema)

    Returns:
        ValidationResult with validation findings

    Raises:
        XSDValidationError: If schema loading fails
    """
    start_time = time.time()
    findings: list[Finding] = []

    try:
        # Load schema
        if schema_path is None:
            schema_path = (
                Path(__file__).parent.parent.parent.parent
                / "rules"
                / "xsd"
                / "5.0"
                / "PropertyMarketing-ILS-5.0.xsd"
            )

        if not schema_path.exists():
            findings.append(
                Finding(
                    level=FindingLevel.ERROR,
                    code="XSD:SCHEMA_MISSING",
                    message=f"XSD schema not found at {schema_path}",
                    rule_ref="internal://XSD",
                )
            )
            return ValidationResult(
                level="XSD",
                findings=findings,
                duration_ms=int((time.time() - start_time) * 1000),
            )

        # Parse schema
        try:
            schema_doc = etree.parse(str(schema_path))
            schema = XMLSchema(schema_doc)
        except etree.XMLSyntaxError as e:
            findings.append(
                Finding(
                    level=FindingLevel.ERROR,
                    code="XSD:SCHEMA_PARSE_ERROR",
                    message=f"Failed to parse XSD schema: {e}",
                    rule_ref="internal://XSD",
                )
            )
            return ValidationResult(
                level="XSD",
                findings=findings,
                duration_ms=int((time.time() - start_time) * 1000),
            )

        # Parse XML content
        try:
            if isinstance(xml_content, str | bytes):
                # Parse from string/bytes
                parser = etree.XMLParser(no_network=True, resolve_entities=False)
                if isinstance(xml_content, str):
                    xml_content = xml_content.encode("utf-8")
                xml_doc = etree.fromstring(xml_content, parser=parser)
            else:
                # Parse from file path
                parser = etree.XMLParser(no_network=True, resolve_entities=False)
                xml_doc = etree.parse(str(xml_content), parser=parser)
        except XMLSyntaxError as e:
            findings.append(
                Finding(
                    level=FindingLevel.ERROR,
                    code="XSD:XML_PARSE_ERROR",
                    message=f"XML parsing failed: {e}",
                    rule_ref="internal://XSD",
                )
            )
            return ValidationResult(
                level="XSD",
                findings=findings,
                duration_ms=int((time.time() - start_time) * 1000),
            )

        # Validate against schema
        try:
            schema.assertValid(xml_doc)
        except etree.DocumentInvalid:
            # Parse validation errors
            for error in schema.error_log:
                findings.append(
                    Finding(
                        level=FindingLevel.ERROR,
                        code="XSD:VALIDATION_ERROR",
                        message=f"Schema validation failed: {error.message}",
                        rule_ref="internal://XSD",
                        location={
                            "line": error.line,
                            "column": error.column,
                            "xpath": _get_xpath_from_error(error),
                        },
                    )
                )
        except Exception as e:
            findings.append(
                Finding(
                    level=FindingLevel.ERROR,
                    code="XSD:VALIDATION_ERROR",
                    message=f"Unexpected validation error: {e}",
                    rule_ref="internal://XSD",
                )
            )

    except Exception as e:
        findings.append(
            Finding(
                level=FindingLevel.ERROR,
                code="XSD:VALIDATION_ERROR",
                message=f"XSD validation failed: {e}",
                rule_ref="internal://XSD",
            )
        )

    duration_ms = int((time.time() - start_time) * 1000)
    return ValidationResult(
        level="XSD",
        findings=findings,
        duration_ms=duration_ms,
    )


def _get_xpath_from_error(error: Any) -> str:
    """Extract XPath from validation error."""
    try:
        # Try to get XPath from error context
        if hasattr(error, "path"):
            return error.path
        elif hasattr(error, "xpath"):
            return error.xpath
        else:
            return f"/{error.tag}" if hasattr(error, "tag") else "/"
    except Exception:
        return "/"


def get_schema_info(schema_path: Path | None = None) -> dict[str, Any]:
    """
    Get information about the XSD schema.

    Args:
        schema_path: Path to XSD schema file

    Returns:
        Dictionary with schema information
    """
    if schema_path is None:
        schema_path = (
            Path(__file__).parent.parent.parent.parent
            / "rules"
            / "xsd"
            / "5.0"
            / "PropertyMarketing-ILS-5.0.xsd"
        )

    info = {
        "schema_path": str(schema_path),
        "exists": schema_path.exists(),
        "namespace": None,
        "root_element": None,
        "version": None,
    }

    if schema_path.exists():
        try:
            schema_doc = etree.parse(str(schema_path))
            root = schema_doc.getroot()

            # Extract namespace
            if root.nsmap:
                info["namespace"] = root.nsmap.get(None, "")

            # Extract root element
            for elem in root.iter():
                if str(elem.tag).endswith("element") and elem.get("name"):
                    info["root_element"] = elem.get("name")
                    break

            # If no root element found, try to get the first element
            if not info["root_element"]:
                elements = root.findall(".//{http://www.w3.org/2001/XMLSchema}element")
                if elements:
                    info["root_element"] = elements[0].get("name")

            # Extract version
            info["version"] = root.get("version", "5.0")

        except Exception as e:
            info["error"] = str(e)

    return info
