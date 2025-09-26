"""Semantic validation level."""

from __future__ import annotations

import time
from pathlib import Path

from mits_validator.catalogs import get_catalog_loader
from mits_validator.models import Finding, FindingLevel, ValidationResult


class SemanticValidator:
    """Semantic validation level that uses catalogs for business logic validation."""

    def __init__(self, rules_dir: Path | None = None, version: str = "mits-5.0"):
        self.rules_dir = rules_dir or Path("rules")
        self.version = version
        self.catalog_loader = get_catalog_loader(self.rules_dir)
        self._catalogs_loaded = False
        self._catalog_registry = None

    def _load_catalogs(self) -> None:
        """Load catalogs for semantic validation."""
        if self._catalogs_loaded:
            return

        try:
            self._catalog_registry, findings = self.catalog_loader.load_catalogs(self.version)
            self._catalogs_loaded = True
        except Exception:
            # Catalogs failed to load - this will be handled in validate()
            self._catalog_registry = None
            self._catalogs_loaded = False

    def validate(self, content: bytes) -> ValidationResult:
        """Validate content using semantic rules and catalogs."""
        start_time = time.time()
        findings: list[Finding] = []

        try:
            # Load catalogs
            self._load_catalogs()

            if not self._catalogs_loaded or not self._catalog_registry:
                findings.append(
                    Finding(
                        level=FindingLevel.WARNING,
                        code="ENGINE:RESOURCE_LOAD_FAILED",
                        message="Failed to load catalogs for semantic validation",
                        rule_ref="internal://Semantic",
                    )
                )
                duration_ms = int((time.time() - start_time) * 1000)
                return ValidationResult(
                    level=self.get_name(), findings=findings, duration_ms=duration_ms
                )

            # TODO: Implement semantic validation checks
            # For now, this is a scaffold that demonstrates the interface
            
            # Future semantic checks could include:
            # - Enum validation against catalogs
            # - Charge class validation
            # - Business rule consistency
            # - Cross-field validation
            # - Totals consistency
            
            # Placeholder: Count available catalogs as a basic check
            catalog_count = (
                len(self._catalog_registry.charge_classes) +
                len(self._catalog_registry.enums) +
                len(self._catalog_registry.specializations)
            )
            
            if catalog_count == 0:
                findings.append(
                    Finding(
                        level=FindingLevel.INFO,
                        code="SEMANTIC:ENUM_UNKNOWN",
                        message="No catalogs available for semantic validation",
                        rule_ref="internal://Semantic",
                    )
                )

        except Exception as e:
            findings.append(
                Finding(
                    level=FindingLevel.ERROR,
                    code="ENGINE:LEVEL_CRASH",
                    message=f"Semantic validation crashed: {str(e)}",
                    rule_ref="internal://Semantic",
                )
            )

        duration_ms = int((time.time() - start_time) * 1000)
        return ValidationResult(
            level=self.get_name(), findings=findings, duration_ms=duration_ms
        )

    def get_name(self) -> str:
        """Get the name of this validation level."""
        return "Semantic"
