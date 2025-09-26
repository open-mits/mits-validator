from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from mits_validator.models import FindingLevel


class ErrorCategory(str, Enum):
    """Error categories for taxonomy."""

    INTAKE = "INTAKE"
    WELLFORMED = "WELLFORMED"
    XSD = "XSD"
    SCHEMATRON = "SCHEMATRON"
    ENGINE = "ENGINE"
    NETWORK = "NETWORK"
    URL = "URL"


@dataclass
class ErrorDefinition:
    """Definition of an error code with metadata."""

    code: str
    severity: FindingLevel
    title: str
    description: str
    remediation: str
    level: str


# Central error catalog
ERROR_CATALOG: dict[str, ErrorDefinition] = {
    # Intake errors
    "INTAKE:BOTH_INPUTS": ErrorDefinition(
        code="INTAKE:BOTH_INPUTS",
        severity=FindingLevel.ERROR,
        title="Both file and URL provided",
        description="Cannot provide both file upload and URL in the same request",
        remediation="Provide either a file upload OR a URL, not both",
        level="intake",
    ),
    "INTAKE:NO_INPUTS": ErrorDefinition(
        code="INTAKE:NO_INPUTS",
        severity=FindingLevel.ERROR,
        title="No input provided",
        description="Must provide either a file upload or URL",
        remediation="Provide either a file upload OR a URL",
        level="intake",
    ),
    "INTAKE:TOO_LARGE": ErrorDefinition(
        code="INTAKE:TOO_LARGE",
        severity=FindingLevel.ERROR,
        title="File too large",
        description="Uploaded file exceeds maximum size limit",
        remediation="Reduce file size or contact administrator to increase limits",
        level="intake",
    ),
    "INTAKE:UNACCEPTABLE_CONTENT_TYPE": ErrorDefinition(
        code="INTAKE:UNACCEPTABLE_CONTENT_TYPE",
        severity=FindingLevel.ERROR,
        title="Unacceptable content type",
        description="Content type is not suitable for XML validation",
        remediation="Use application/xml, text/xml, or application/octet-stream",
        level="intake",
    ),
    "INTAKE:INVALID_URL": ErrorDefinition(
        code="INTAKE:INVALID_URL",
        severity=FindingLevel.ERROR,
        title="Invalid URL format",
        description="URL must start with http:// or https://",
        remediation="Provide a valid HTTP or HTTPS URL",
        level="intake",
    ),
    "INTAKE:UNSUPPORTED_MEDIA_TYPE": ErrorDefinition(
        code="INTAKE:UNSUPPORTED_MEDIA_TYPE",
        severity=FindingLevel.ERROR,
        title="Unsupported media type",
        description="Content type is not supported for XML validation",
        remediation="Use application/xml, text/xml, or application/octet-stream content type",
        level="intake",
    ),
    # WellFormed errors
    "WELLFORMED:PARSE_ERROR": ErrorDefinition(
        code="WELLFORMED:PARSE_ERROR",
        severity=FindingLevel.ERROR,
        title="XML parsing failed",
        description="XML document is not well-formed",
        remediation="Fix XML syntax errors and ensure proper nesting",
        level="WellFormed",
    ),
    "WELLFORMED:UNEXPECTED_ERROR": ErrorDefinition(
        code="WELLFORMED:UNEXPECTED_ERROR",
        severity=FindingLevel.ERROR,
        title="Unexpected parsing error",
        description="An unexpected error occurred during XML parsing",
        remediation="Check XML encoding and structure",
        level="WellFormed",
    ),
    "WELLFORMED:SUSPICIOUS_CONTENT_TYPE": ErrorDefinition(
        code="WELLFORMED:SUSPICIOUS_CONTENT_TYPE",
        severity=FindingLevel.WARNING,
        title="Suspicious content type",
        description="Content type may not be XML",
        remediation="Verify content type is application/xml or text/xml",
        level="WellFormed",
    ),
    # XSD errors
    "XSD:SCHEMA_MISSING": ErrorDefinition(
        code="XSD:SCHEMA_MISSING",
        severity=FindingLevel.WARNING,
        title="XSD schema not available",
        description="No XSD schema found for validation",
        remediation="XSD validation skipped - schema not configured",
        level="XSD",
    ),
    "XSD:VALIDATION_ERROR": ErrorDefinition(
        code="XSD:VALIDATION_ERROR",
        severity=FindingLevel.ERROR,
        title="XSD validation failed",
        description="XML does not conform to XSD schema",
        remediation="Fix XML structure to match schema requirements",
        level="XSD",
    ),
    # Schematron errors
    "SCHEMATRON:RULES_MISSING": ErrorDefinition(
        code="SCHEMATRON:RULES_MISSING",
        severity=FindingLevel.WARNING,
        title="Schematron rules not available",
        description="No Schematron rules found for validation",
        remediation="Schematron validation skipped - rules not configured",
        level="Schematron",
    ),
    "SCHEMATRON:RULE_FAILURE": ErrorDefinition(
        code="SCHEMATRON:RULE_FAILURE",
        severity=FindingLevel.ERROR,
        title="Schematron rule failed",
        description="XML failed Schematron business rule validation",
        remediation="Fix XML to satisfy business rules",
        level="Schematron",
    ),
    # Engine errors
    "ENGINE:LEVEL_CRASH": ErrorDefinition(
        code="ENGINE:LEVEL_CRASH",
        severity=FindingLevel.ERROR,
        title="Validation level crashed",
        description="A validation level encountered an unexpected error",
        remediation="Check validation configuration and try again",
        level="engine",
    ),
    "ENGINE:RULES_MISSING": ErrorDefinition(
        code="ENGINE:RULES_MISSING",
        severity=FindingLevel.WARNING,
        title="Validation rules missing",
        description="Some validation rules could not be loaded",
        remediation="Check rule configuration and file paths",
        level="engine",
    ),
    # Network errors
    "NETWORK:TIMEOUT": ErrorDefinition(
        code="NETWORK:TIMEOUT",
        severity=FindingLevel.ERROR,
        title="Network timeout",
        description="Request to fetch URL content timed out",
        remediation="Check network connectivity and try again with a shorter timeout",
        level="network",
    ),
    "NETWORK:CONNECTION_ERROR": ErrorDefinition(
        code="NETWORK:CONNECTION_ERROR",
        severity=FindingLevel.ERROR,
        title="Connection failed",
        description="Failed to establish connection to the URL",
        remediation="Check URL accessibility and network connectivity",
        level="network",
    ),
    "NETWORK:HTTP_STATUS": ErrorDefinition(
        code="NETWORK:HTTP_STATUS",
        severity=FindingLevel.ERROR,
        title="HTTP error status",
        description="URL returned an HTTP error status code",
        remediation="Check if URL is accessible and returns valid content",
        level="network",
    ),
    "NETWORK:REQUEST_ERROR": ErrorDefinition(
        code="NETWORK:REQUEST_ERROR",
        severity=FindingLevel.ERROR,
        title="Request failed",
        description="Network request failed for an unknown reason",
        remediation="Check URL validity and network connectivity",
        level="network",
    ),
    "NETWORK:FETCH_ERROR": ErrorDefinition(
        code="NETWORK:FETCH_ERROR",
        severity=FindingLevel.ERROR,
        title="URL fetch failed",
        description="Failed to fetch content from URL",
        remediation="Check URL accessibility and network connectivity",
        level="network",
    ),
    # URL errors
    "URL:INTAKE_ACKNOWLEDGED": ErrorDefinition(
        code="URL:INTAKE_ACKNOWLEDGED",
        severity=FindingLevel.INFO,
        title="URL intake acknowledged",
        description="URL intake acknowledged but fetching not implemented",
        remediation="URL validation is experimental - use file upload for full validation",
        level="url",
    ),
    # Schematron errors
    "SCHEMATRON:NO_RULES_LOADED": ErrorDefinition(
        code="SCHEMATRON:NO_RULES_LOADED",
        severity=FindingLevel.INFO,
        title="Schematron rules not loaded",
        description="No Schematron rules available for validation",
        remediation=(
            "Add Schematron rules to rules/schematron/ directory for cross-field validation"
        ),
        level="schematron",
    ),
}


def get_error_definition(code: str) -> ErrorDefinition | None:
    """Get error definition by code."""
    return ERROR_CATALOG.get(code)
