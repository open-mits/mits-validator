from __future__ import annotations

import time
from pathlib import Path

import lxml.etree as ET

from mits_validator.models import Finding, FindingLevel, ValidationResult


class SchematronValidator:
    """Validates XML against Schematron rules."""

    def __init__(self, rules_dir: Path | None = None, version: str = "mits-5.0"):
        self.rules_dir = rules_dir or Path("rules")
        self.version = version
        self.rules_path = self.rules_dir / version / "schematron"
        self._rules_available = False
        self._check_rules()

    def _check_rules(self) -> None:
        """Check if Schematron rules are available."""
        if not self.rules_path.exists():
            return
        
        # Check for any .sch files in the schematron directory
        if any(self.rules_path.glob("*.sch")):
            self._rules_available = True

    def _load_rules(self) -> list[Path]:
        """Load available Schematron rule files."""
        if not self.rules_path.exists():
            return []
        
        return list(self.rules_path.glob("*.sch"))

    def validate(self, content: bytes) -> ValidationResult:
        """Validate XML against Schematron rules."""
        start_time = time.time()
        findings: list[Finding] = []

        try:
            # Check if rules are available
            if not self._rules_available:
                findings.append(
                    Finding(
                        level=FindingLevel.INFO,
                        code="SCHEMATRON:NO_RULES_LOADED",
                        message="No Schematron rules available for validation",
                        rule_ref="internal://Schematron",
                    )
                )
            else:
                try:
                    # Parse XML (placeholder for future rule execution)
                    _ = ET.fromstring(content)

                    # For this milestone, we'll simulate rule execution
                    # In a full implementation, this would run the compiled Schematron rules
                    # and report any failures as findings

                    # Simulate a rule check (placeholder)
                    # This would be replaced with actual Schematron execution
                    rule_files = self._load_rules()
                    if rule_files:
                        # Placeholder: in the future, this would validate against the rules
                        pass

                except ET.XMLSyntaxError as e:
                    # XML parsing error - this should be caught by WellFormed level
                    # but we'll handle it gracefully here too
                    findings.append(
                        Finding(
                            level=FindingLevel.ERROR,
                            code="SCHEMATRON:RULE_FAILURE",
                            message=f"XML parsing failed during Schematron validation: {str(e)}",
                            rule_ref="internal://Schematron",
                        )
                    )

        except Exception as e:
            # Unexpected error during Schematron validation
            findings.append(
                Finding(
                    level=FindingLevel.ERROR,
                    code="ENGINE:RESOURCE_LOAD_FAILED",
                    message=f"Failed to load Schematron rules: {str(e)}",
                    rule_ref="internal://Schematron",
                )
            )

        duration_ms = int((time.time() - start_time) * 1000)
        return ValidationResult(
            level=self.get_name(), findings=findings, duration_ms=duration_ms
        )

    def get_name(self) -> str:
        """Get the name of this validation level."""
        return "Schematron"
