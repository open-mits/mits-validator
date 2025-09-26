"""Tests for Schematron validation."""

import pytest
from pathlib import Path

from mits_validator.models import FindingLevel
from mits_validator.validation.schematron import validate_schematron, get_rules_info


class TestSchematronValidation:
    """Test Schematron validation functionality."""

    def test_validate_valid_xml(self):
        """Test validation of valid MITS XML with business rules."""
        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<PropertyMarketing xmlns="http://www.mits.org/schema/PropertyMarketing/ILS/5.0"
                   version="5.0"
                   timestamp="2025-09-15T10:30:00Z">
  <Property>
    <PropertyID>PROP-001</PropertyID>
    <PropertyName>Test Property</PropertyName>
    <PropertyType>Apartment</PropertyType>
    <Address>
      <StreetAddress>123 Main St</StreetAddress>
      <City>Anytown</City>
      <State>CA</State>
      <PostalCode>12345</PostalCode>
    </Address>
    <ChargeOffer>
      <ChargeOfferItem>
        <ChargeClassification>Rent</ChargeClassification>
        <Requirement>Mandatory</Requirement>
        <PaymentFrequency>Monthly</PaymentFrequency>
        <Refundability>NonRefundable</Refundability>
        <TermBasis>LeaseTerm</TermBasis>
        <Amount>1500.00</Amount>
        <Description>Monthly rent</Description>
      </ChargeOfferItem>
    </ChargeOffer>
  </Property>
</PropertyMarketing>"""
        
        result = validate_schematron(xml_content)
        
        assert result.level == "Schematron"
        # Should pass business rule validation
        assert len(result.findings) == 0

    def test_validate_invalid_charge_classification(self):
        """Test validation with invalid charge classification."""
        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<PropertyMarketing xmlns="http://www.mits.org/schema/PropertyMarketing/ILS/5.0"
                   version="5.0"
                   timestamp="2025-09-15T10:30:00Z">
  <Property>
    <PropertyID>PROP-001</PropertyID>
    <PropertyName>Test Property</PropertyName>
    <PropertyType>Apartment</PropertyType>
    <Address>
      <StreetAddress>123 Main St</StreetAddress>
      <City>Anytown</City>
      <State>CA</State>
      <PostalCode>12345</PostalCode>
    </Address>
    <ChargeOffer>
      <ChargeOfferItem>
        <ChargeClassification>InvalidCharge</ChargeClassification>
        <Requirement>Mandatory</Requirement>
        <PaymentFrequency>Monthly</PaymentFrequency>
        <Refundability>NonRefundable</Refundability>
        <TermBasis>LeaseTerm</TermBasis>
        <Amount>1500.00</Amount>
      </ChargeOfferItem>
    </ChargeOffer>
  </Property>
</PropertyMarketing>"""
        
        result = validate_schematron(xml_content)
        
        assert result.level == "Schematron"
        assert len(result.findings) > 0
        assert any(finding.level == FindingLevel.ERROR for finding in result.findings)
        assert any("Rule validation failed" in finding.message for finding in result.findings)

    def test_validate_missing_payment_frequency(self):
        """Test validation with missing payment frequency for mandatory charge."""
        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<PropertyMarketing xmlns="http://www.mits.org/schema/PropertyMarketing/ILS/5.0"
                   version="5.0"
                   timestamp="2025-09-15T10:30:00Z">
  <Property>
    <PropertyID>PROP-001</PropertyID>
    <PropertyName>Test Property</PropertyName>
    <PropertyType>Apartment</PropertyType>
    <Address>
      <StreetAddress>123 Main St</StreetAddress>
      <City>Anytown</City>
      <State>CA</State>
      <PostalCode>12345</PostalCode>
    </Address>
    <ChargeOffer>
      <ChargeOfferItem>
        <ChargeClassification>Rent</ChargeClassification>
        <Requirement>Mandatory</Requirement>
        <!-- Missing PaymentFrequency - should trigger rule -->
        <Refundability>NonRefundable</Refundability>
        <TermBasis>LeaseTerm</TermBasis>
        <Amount>1500.00</Amount>
      </ChargeOfferItem>
    </ChargeOffer>
  </Property>
</PropertyMarketing>"""
        
        result = validate_schematron(xml_content)
        
        assert result.level == "Schematron"
        assert len(result.findings) > 0
        assert any(finding.level == FindingLevel.ERROR for finding in result.findings)
        assert any("Rule validation failed" in finding.message for finding in result.findings)

    def test_validate_deposit_without_description(self):
        """Test validation of deposit charge without description or amount."""
        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<PropertyMarketing xmlns="http://www.mits.org/schema/PropertyMarketing/ILS/5.0"
                   version="5.0"
                   timestamp="2025-09-15T10:30:00Z">
  <Property>
    <PropertyID>PROP-001</PropertyID>
    <PropertyName>Test Property</PropertyName>
    <PropertyType>Apartment</PropertyType>
    <Address>
      <StreetAddress>123 Main St</StreetAddress>
      <City>Anytown</City>
      <State>CA</State>
      <PostalCode>12345</PostalCode>
    </Address>
    <ChargeOffer>
      <ChargeOfferItem>
        <ChargeClassification>Deposit</ChargeClassification>
        <Requirement>Mandatory</Requirement>
        <PaymentFrequency>OneTime</PaymentFrequency>
        <Refundability>Deposit</Refundability>
        <TermBasis>LeaseTerm</TermBasis>
        <!-- Missing both Description and Amount - should trigger rule -->
      </ChargeOfferItem>
    </ChargeOffer>
  </Property>
</PropertyMarketing>"""
        
        result = validate_schematron(xml_content)
        
        assert result.level == "Schematron"
        assert len(result.findings) > 0
        assert any(finding.level == FindingLevel.ERROR for finding in result.findings)
        assert any("Rule validation failed" in finding.message for finding in result.findings)

    def test_validate_missing_rules(self):
        """Test validation when rules file is missing."""
        result = validate_schematron("", rules_path=Path("/nonexistent/rules.sch"))
        
        assert result.level == "Schematron"
        assert len(result.findings) == 1
        assert result.findings[0].level == FindingLevel.INFO
        assert result.findings[0].code == "SCHEMATRON:NO_RULES_LOADED"

    def test_validate_malformed_xml(self):
        """Test validation with malformed XML."""
        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<PropertyMarketing xmlns="http://www.mits.org/schema/PropertyMarketing/ILS/5.0"
                   version="5.0"
                   timestamp="2025-09-15T10:30:00Z">
  <Property>
    <PropertyID>PROP-001</PropertyID>
    <PropertyName>Test Property</PropertyName>
    <PropertyType>Apartment</PropertyType>
    <Address>
      <StreetAddress>123 Main St</StreetAddress>
      <City>Anytown</City>
      <State>CA</State>
      <PostalCode>12345</PostalCode>
    </Address>
  </Property>
  <UnclosedTag>
</PropertyMarketing>"""
        
        result = validate_schematron(xml_content)
        
        assert result.level == "Schematron"
        assert len(result.findings) > 0
        assert any(finding.level == FindingLevel.ERROR for finding in result.findings)
        assert any("XML parsing failed" in finding.message for finding in result.findings)

    def test_validate_from_file(self):
        """Test validation from file path."""
        fixture_path = Path(__file__).parent.parent.parent / "fixtures" / "mits5" / "valid-property.xml"
        
        if fixture_path.exists():
            result = validate_schematron(fixture_path)
            
            assert result.level == "Schematron"
            # Should pass business rule validation
            assert len(result.findings) == 0

    def test_get_rules_info(self):
        """Test getting rules information."""
        info = get_rules_info()
        
        assert "rules_path" in info
        assert "exists" in info
        assert "title" in info
        assert "description" in info
        assert "patterns" in info
        assert "rules_count" in info
        
        if info["exists"]:
            assert len(info["patterns"]) > 0
            assert info["rules_count"] > 0

    def test_validate_optional_charge_without_frequency(self):
        """Test validation of optional charge without payment frequency."""
        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<PropertyMarketing xmlns="http://www.mits.org/schema/PropertyMarketing/ILS/5.0"
                   version="5.0"
                   timestamp="2025-09-15T10:30:00Z">
  <Property>
    <PropertyID>PROP-001</PropertyID>
    <PropertyName>Test Property</PropertyName>
    <PropertyType>Apartment</PropertyType>
    <Address>
      <StreetAddress>123 Main St</StreetAddress>
      <City>Anytown</City>
      <State>CA</State>
      <PostalCode>12345</PostalCode>
    </Address>
    <ChargeOffer>
      <ChargeOfferItem>
        <ChargeClassification>Pet</ChargeClassification>
        <Requirement>Mandatory</Requirement>
        <!-- Missing PaymentFrequency - should trigger rule -->
        <Refundability>NonRefundable</Refundability>
        <TermBasis>Rolling</TermBasis>
        <Amount>50.00</Amount>
        <Description>Pet fee</Description>
      </ChargeOfferItem>
    </ChargeOffer>
  </Property>
</PropertyMarketing>"""
        
        result = validate_schematron(xml_content)
        
        assert result.level == "Schematron"
        assert len(result.findings) > 0
        assert any(finding.level == FindingLevel.ERROR for finding in result.findings)
        assert any("Rule validation failed" in finding.message for finding in result.findings)

    def test_validate_property_completeness(self):
        """Test validation of property information completeness."""
        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<PropertyMarketing xmlns="http://www.mits.org/schema/PropertyMarketing/ILS/5.0"
                   version="5.0"
                   timestamp="2025-09-15T10:30:00Z">
  <Property>
    <!-- Missing PropertyID - should trigger rule -->
    <PropertyName>Test Property</PropertyName>
    <PropertyType>Apartment</PropertyType>
    <Address>
      <StreetAddress>123 Main St</StreetAddress>
      <City>Anytown</City>
      <State>CA</State>
      <PostalCode>12345</PostalCode>
    </Address>
  </Property>
</PropertyMarketing>"""
        
        result = validate_schematron(xml_content)
        
        assert result.level == "Schematron"
        assert len(result.findings) > 0
        assert any(finding.level == FindingLevel.ERROR for finding in result.findings)
        assert any("Rule validation failed" in finding.message for finding in result.findings)
