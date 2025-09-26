from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


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
