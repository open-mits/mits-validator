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
    "XSD:PARSE_ERROR": ErrorDefinition(
        code="XSD:PARSE_ERROR",
        severity=FindingLevel.ERROR,
        title="XML parsing failed",
        description="XML content could not be parsed",
        remediation="Fix XML syntax errors",
        level="XSD",
    ),
    "XSD:XML_PARSE_ERROR": ErrorDefinition(
        code="XSD:XML_PARSE_ERROR",
        severity=FindingLevel.ERROR,
        title="XML parse error in XSD",
        description="Failed to parse XML for XSD validation",
        remediation="Check XML syntax and structure",
        level="XSD",
    ),
    "XSD:SCHEMA_PARSE_ERROR": ErrorDefinition(
        code="XSD:SCHEMA_PARSE_ERROR",
        severity=FindingLevel.ERROR,
        title="XSD schema parse error",
        description="Failed to parse XSD schema file",
        remediation="Check XSD schema syntax",
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
    "NETWORK:DNS_ERROR": ErrorDefinition(
        code="NETWORK:DNS_ERROR",
        severity=FindingLevel.ERROR,
        title="DNS resolution error",
        description="Failed to resolve domain name",
        remediation="Check URL and DNS configuration",
        level="network",
    ),
    "NETWORK:TOO_LARGE_DURING_STREAM": ErrorDefinition(
        code="NETWORK:TOO_LARGE_DURING_STREAM",
        severity=FindingLevel.ERROR,
        title="Content too large",
        description="Content exceeded size limit during streaming",
        remediation="Reduce content size or increase limit",
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
    # Catalog errors
    "CATALOG:VERSION_NOT_FOUND": ErrorDefinition(
        code="CATALOG:VERSION_NOT_FOUND",
        severity=FindingLevel.ERROR,
        title="Catalog version not found",
        description="The specified MITS catalog version directory was not found",
        remediation="Check that the version directory exists in rules/",
        level="catalog",
    ),
    "CATALOG:FILE_MISSING": ErrorDefinition(
        code="CATALOG:FILE_MISSING",
        severity=FindingLevel.WARNING,
        title="Catalog file missing",
        description="A required catalog file was not found",
        remediation="Ensure all required catalog files are present",
        level="catalog",
    ),
    "CATALOG:DIRECTORY_MISSING": ErrorDefinition(
        code="CATALOG:DIRECTORY_MISSING",
        severity=FindingLevel.WARNING,
        title="Catalog directory missing",
        description="A required catalog directory was not found",
        remediation="Ensure all required catalog directories are present",
        level="catalog",
    ),
    "CATALOG:INVALID_JSON": ErrorDefinition(
        code="CATALOG:INVALID_JSON",
        severity=FindingLevel.ERROR,
        title="Invalid JSON in catalog",
        description="Catalog file contains invalid JSON syntax",
        remediation="Fix JSON syntax errors in the catalog file",
        level="catalog",
    ),
    "CATALOG:SCHEMA_VALIDATION_ERROR": ErrorDefinition(
        code="CATALOG:SCHEMA_VALIDATION_ERROR",
        severity=FindingLevel.ERROR,
        title="Catalog schema validation failed",
        description="Catalog file does not conform to its JSON schema",
        remediation="Fix catalog file to match the required schema",
        level="catalog",
    ),
    "CATALOG:DUPLICATE_CODE": ErrorDefinition(
        code="CATALOG:DUPLICATE_CODE",
        severity=FindingLevel.ERROR,
        title="Duplicate catalog code",
        description="Duplicate code found within a catalog file",
        remediation="Ensure all codes are unique within each catalog file",
        level="catalog",
    ),
    "CATALOG:NO_ENUMS": ErrorDefinition(
        code="CATALOG:NO_ENUMS",
        severity=FindingLevel.INFO,
        title="No enum files found",
        description="No enumeration files found in the enums directory",
        remediation="Add enum files to the enums directory if needed",
        level="catalog",
    ),
    "CATALOG:NO_SPECIALIZATIONS": ErrorDefinition(
        code="CATALOG:NO_SPECIALIZATIONS",
        severity=FindingLevel.INFO,
        title="No specialization files found",
        description="No item specialization files found in the specializations directory",
        remediation="Add specialization files to the specializations directory if needed",
        level="catalog",
    ),
    # Schematron errors
    "SCHEMATRON:NO_RULES_LOADED": ErrorDefinition(
        code="SCHEMATRON:NO_RULES_LOADED",
        severity=FindingLevel.INFO,
        title="Schematron rules not loaded",
        description="No Schematron rules available for validation",
        remediation="Add Schematron rules to rules/schematron/ for cross-field validation",
        level="schematron",
    ),
    "SCHEMATRON:RULE_FAILURE": ErrorDefinition(
        code="SCHEMATRON:RULE_FAILURE",
        severity=FindingLevel.ERROR,
        title="Schematron rule failed",
        description="XML failed Schematron business rule validation",
        remediation="Review and fix the business rule violation",
        level="schematron",
    ),
    "SCHEMATRON:VALIDATION_ERROR": ErrorDefinition(
        code="SCHEMATRON:VALIDATION_ERROR",
        severity=FindingLevel.ERROR,
        title="Schematron validation error",
        description="Schematron validation process failed",
        remediation="Check Schematron rules and XML content",
        level="schematron",
    ),
    "SCHEMATRON:XML_PARSE_ERROR": ErrorDefinition(
        code="SCHEMATRON:XML_PARSE_ERROR",
        severity=FindingLevel.ERROR,
        title="XML parse error in Schematron",
        description="Failed to parse XML for Schematron validation",
        remediation="Check XML syntax and structure",
        level="schematron",
    ),
    "SCHEMATRON:RULES_PARSE_ERROR": ErrorDefinition(
        code="SCHEMATRON:RULES_PARSE_ERROR",
        severity=FindingLevel.ERROR,
        title="Schematron rules parse error",
        description="Failed to parse Schematron rules file",
        remediation="Check Schematron rules syntax",
        level="schematron",
    ),
    # Semantic errors
    "SEMANTIC:ENUM_UNKNOWN": ErrorDefinition(
        code="SEMANTIC:ENUM_UNKNOWN",
        severity=FindingLevel.ERROR,
        title="Unknown enumeration value",
        description="Value not found in the enumeration catalog",
        remediation="Use a valid enumeration value from the catalog",
        level="semantic",
    ),
    "SEMANTIC:LIMIT_EXCEEDED": ErrorDefinition(
        code="SEMANTIC:LIMIT_EXCEEDED",
        severity=FindingLevel.ERROR,
        title="Limit exceeded",
        description="Value exceeds the configured limit",
        remediation="Reduce the value to within the allowed limit",
        level="semantic",
    ),
    "SEMANTIC:INCONSISTENT_TOTALS": ErrorDefinition(
        code="SEMANTIC:INCONSISTENT_TOTALS",
        severity=FindingLevel.ERROR,
        title="Inconsistent totals",
        description="Calculated totals do not match expected values",
        remediation="Review and correct the calculation or input values",
        level="semantic",
    ),
    "SEMANTIC:INVALID_CHARGE_CLASS": ErrorDefinition(
        code="SEMANTIC:INVALID_CHARGE_CLASS",
        severity=FindingLevel.ERROR,
        title="Invalid charge classification",
        description="Charge classification is not valid according to catalog",
        remediation="Use a valid charge classification from the catalog",
        level="semantic",
    ),
    "SEMANTIC:INVALID_PAYMENT_FREQUENCY": ErrorDefinition(
        code="SEMANTIC:INVALID_PAYMENT_FREQUENCY",
        severity=FindingLevel.ERROR,
        title="Invalid payment frequency",
        description="Payment frequency is not valid according to catalog",
        remediation="Use a valid payment frequency from the catalog",
        level="semantic",
    ),
    "SEMANTIC:INVALID_REFUNDABILITY": ErrorDefinition(
        code="SEMANTIC:INVALID_REFUNDABILITY",
        severity=FindingLevel.ERROR,
        title="Invalid refundability",
        description="Refundability value is not valid according to catalog",
        remediation="Use a valid refundability value from the catalog",
        level="semantic",
    ),
    "SEMANTIC:INVALID_TERM_BASIS": ErrorDefinition(
        code="SEMANTIC:INVALID_TERM_BASIS",
        severity=FindingLevel.ERROR,
        title="Invalid term basis",
        description="Term basis is not valid according to catalog",
        remediation="Use a valid term basis from the catalog",
        level="semantic",
    ),
    "SEMANTIC:INCONSISTENT_RENT_REQUIREMENT": ErrorDefinition(
        code="SEMANTIC:INCONSISTENT_RENT_REQUIREMENT",
        severity=FindingLevel.WARNING,
        title="Inconsistent rent requirement",
        description="Rent charges should typically be Mandatory, not Optional",
        remediation="Consider making rent charges Mandatory",
        level="semantic",
    ),
    "SEMANTIC:INCONSISTENT_DEPOSIT_FREQUENCY": ErrorDefinition(
        code="SEMANTIC:INCONSISTENT_DEPOSIT_FREQUENCY",
        severity=FindingLevel.WARNING,
        title="Inconsistent deposit frequency",
        description="Deposit charges should typically be OneTime payments",
        remediation="Consider making deposit charges OneTime payments",
        level="semantic",
    ),
    "SEMANTIC:XML_PARSE_ERROR": ErrorDefinition(
        code="SEMANTIC:XML_PARSE_ERROR",
        severity=FindingLevel.ERROR,
        title="XML parse error in semantic validation",
        description="Failed to parse XML for semantic validation",
        remediation="Check XML syntax and structure",
        level="semantic",
    ),
    # Engine errors
    "ENGINE:RESOURCE_LOAD_FAILED": ErrorDefinition(
        code="ENGINE:RESOURCE_LOAD_FAILED",
        severity=FindingLevel.ERROR,
        title="Resource load failed",
        description="Failed to load a required resource",
        remediation="Check that the resource exists and is accessible",
        level="engine",
    ),
}


def get_error_definition(code: str) -> ErrorDefinition | None:
    """Get error definition by code."""
    return ERROR_CATALOG.get(code)
