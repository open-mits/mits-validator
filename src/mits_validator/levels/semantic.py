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

            # Parse XML content for semantic validation
            try:
                from lxml import etree
                xml_doc = etree.fromstring(content)
                
                # Validate charge classifications against catalog
                findings.extend(self._validate_charge_classifications(xml_doc))
                
                # Validate payment frequencies against catalog
                findings.extend(self._validate_payment_frequencies(xml_doc))
                
                # Validate refundability values against catalog
                findings.extend(self._validate_refundability(xml_doc))
                
                # Validate term basis values against catalog
                findings.extend(self._validate_term_basis(xml_doc))
                
                # Validate business logic consistency
                findings.extend(self._validate_business_logic(xml_doc))
                
            except Exception as parse_error:
                findings.append(
                    Finding(
                        level=FindingLevel.ERROR,
                        code="SEMANTIC:XML_PARSE_ERROR",
                        message=f"Failed to parse XML for semantic validation: {parse_error}",
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

    def _validate_charge_classifications(self, xml_doc) -> list[Finding]:
        """Validate charge classifications against catalog."""
        findings = []
        
        if not self._catalog_registry or not self._catalog_registry.charge_classes:
            return findings
            
        # Get valid charge class codes from catalog
        valid_codes = set(self._catalog_registry.charge_classes)
        
        # Find all charge classifications in the XML
        charge_classifications = xml_doc.xpath("//*[local-name()='ChargeClassification']")
        
        for elem in charge_classifications:
            value = elem.text.strip() if elem.text else ""
            if value and value not in valid_codes:
                findings.append(
                    Finding(
                        level=FindingLevel.ERROR,
                        code="SEMANTIC:INVALID_CHARGE_CLASS",
                        message=f"Charge classification '{value}' is not valid according to catalog",
                        rule_ref="semantic://charge-classification",
                        location={"xpath": self._get_xpath(elem), "value": value}
                    )
                )
        
        return findings

    def _validate_payment_frequencies(self, xml_doc) -> list[Finding]:
        """Validate payment frequencies against catalog."""
        findings = []
        
        if not self._catalog_registry or not self._catalog_registry.enums:
            return findings
            
        # Get valid payment frequency codes from catalog
        payment_freq_enum = self._catalog_registry.enums.get("payment-frequency")
        if not payment_freq_enum:
            return findings
            
        valid_codes = {item.code for item in payment_freq_enum}
        valid_codes.update({alias for item in payment_freq_enum for alias in item.aliases})
        
        # Find all payment frequencies in the XML
        payment_frequencies = xml_doc.xpath("//*[local-name()='PaymentFrequency']")
        
        for elem in payment_frequencies:
            value = elem.text.strip() if elem.text else ""
            if value and value not in valid_codes:
                findings.append(
                    Finding(
                        level=FindingLevel.ERROR,
                        code="SEMANTIC:INVALID_PAYMENT_FREQUENCY",
                        message=f"Payment frequency '{value}' is not valid according to catalog",
                        rule_ref="semantic://payment-frequency",
                        location={"xpath": self._get_xpath(elem), "value": value}
                    )
                )
        
        return findings

    def _validate_refundability(self, xml_doc) -> list[Finding]:
        """Validate refundability values against catalog."""
        findings = []
        
        if not self._catalog_registry or not self._catalog_registry.enums:
            return findings
            
        # Get valid refundability codes from catalog
        refundability_enum = self._catalog_registry.enums.get("refundability")
        if not refundability_enum:
            return findings
            
        valid_codes = {item.code for item in refundability_enum}
        valid_codes.update({alias for item in refundability_enum for alias in item.aliases})
        
        # Find all refundability values in the XML
        refundability_values = xml_doc.xpath("//*[local-name()='Refundability']")
        
        for elem in refundability_values:
            value = elem.text.strip() if elem.text else ""
            if value and value not in valid_codes:
                findings.append(
                    Finding(
                        level=FindingLevel.ERROR,
                        code="SEMANTIC:INVALID_REFUNDABILITY",
                        message=f"Refundability '{value}' is not valid according to catalog",
                        rule_ref="semantic://refundability",
                        location={"xpath": self._get_xpath(elem), "value": value}
                    )
                )
        
        return findings

    def _validate_term_basis(self, xml_doc) -> list[Finding]:
        """Validate term basis values against catalog."""
        findings = []
        
        if not self._catalog_registry or not self._catalog_registry.enums:
            return findings
            
        # Get valid term basis codes from catalog
        term_basis_enum = self._catalog_registry.enums.get("term-basis")
        if not term_basis_enum:
            return findings
            
        valid_codes = {item.code for item in term_basis_enum}
        valid_codes.update({alias for item in term_basis_enum for alias in item.aliases})
        
        # Find all term basis values in the XML
        term_basis_values = xml_doc.xpath("//*[local-name()='TermBasis']")
        
        for elem in term_basis_values:
            value = elem.text.strip() if elem.text else ""
            if value and value not in valid_codes:
                findings.append(
                    Finding(
                        level=FindingLevel.ERROR,
                        code="SEMANTIC:INVALID_TERM_BASIS",
                        message=f"Term basis '{value}' is not valid according to catalog",
                        rule_ref="semantic://term-basis",
                        location={"xpath": self._get_xpath(elem), "value": value}
                    )
                )
        
        return findings

    def _validate_business_logic(self, xml_doc) -> list[Finding]:
        """Validate business logic consistency."""
        findings = []
        
        # Find all charge offer items
        charge_items = xml_doc.xpath("//*[local-name()='ChargeOfferItem']")
        
        for item in charge_items:
            # Check for rent charges that are optional (should typically be mandatory)
            charge_class = item.find(".//*[local-name()='ChargeClassification']")
            requirement = item.find(".//*[local-name()='Requirement']")
            
            if (charge_class is not None and charge_class.text and 
                charge_class.text.strip() in ['Rent', 'RENT'] and
                requirement is not None and requirement.text and
                requirement.text.strip() == 'Optional'):
                findings.append(
                    Finding(
                        level=FindingLevel.WARNING,
                        code="SEMANTIC:INCONSISTENT_RENT_REQUIREMENT",
                        message="Rent charges should typically be Mandatory, not Optional",
                        rule_ref="semantic://business-logic",
                        location={"xpath": self._get_xpath(item)}
                    )
                )
            
            # Check for deposit charges that are not OneTime
            payment_freq = item.find(".//*[local-name()='PaymentFrequency']")
            if (charge_class is not None and charge_class.text and 
                charge_class.text.strip() in ['Deposit', 'DEPOSIT'] and
                payment_freq is not None and payment_freq.text and
                payment_freq.text.strip() != 'OneTime'):
                findings.append(
                    Finding(
                        level=FindingLevel.WARNING,
                        code="SEMANTIC:INCONSISTENT_DEPOSIT_FREQUENCY",
                        message="Deposit charges should typically be OneTime payments",
                        rule_ref="semantic://business-logic",
                        location={"xpath": self._get_xpath(item)}
                    )
                )
        
        return findings

    def _get_xpath(self, element) -> str:
        """Get XPath for an element."""
        try:
            from lxml import etree
            return etree.ElementTree(element).getpath(element)
        except:
            return "unknown"

    def get_name(self) -> str:
        """Get the name of this validation level."""
        return "Semantic"
