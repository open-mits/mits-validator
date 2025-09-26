from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


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

    level: str
    findings: list[Finding]
    duration_ms: int


@dataclass
class ValidationRequest:
    """Request for validation."""

    content: bytes
    content_type: str
    source: str  # "file" or "url"
    url: str | None = None
    filename: str | None = None
    size_bytes: int | None = None


@dataclass
class ValidationResponse:
    """Response envelope for validation results."""

    api_version: str = "1.0"
    validator: dict[str, Any] | None = None
    input: dict[str, Any] | None = None
    summary: dict[str, Any] | None = None
    findings: list[dict[str, Any]] | None = None
    derived: dict[str, Any] | None = None
    metadata: dict[str, Any] | None = None
