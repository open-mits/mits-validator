"""Test enhanced Schematron validation rules."""

import pytest
from pathlib import Path

from mits_validator.models import FindingLevel
from mits_validator.validation.schematron import validate_schematron


class TestEnhancedSchematronValidation:
    """Test enhanced Schematron validation rules."""

    def test_validate_amount_validation(self):
        """Test amount validation rules."""
        # Test negative amount
        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<PropertyMarketing xmlns="http://www.mits.org/schema/PropertyMarketing/ILS/5.0"
                   version="5.0"
                   timestamp="2025-01-15T10:30:00Z">
  <Property>
    <PropertyID>TEST-001</PropertyID>
    <PropertyName>Test Property</PropertyName>
    <PropertyType>Apartment</PropertyType>
    <Address>
      <StreetAddress>123 Test St</StreetAddress>
      <City>TestCity</City>
      <State>TC</State>
      <PostalCode>12345</PostalCode>
    </Address>
    <ChargeOffer>
      <ChargeOfferItem>
        <ChargeClassification>Rent</ChargeClassification>
        <Requirement>Mandatory</Requirement>
        <PaymentFrequency>Monthly</PaymentFrequency>
        <Refundability>NonRefundable</Refundability>
        <TermBasis>LeaseTerm</TermBasis>
        <Amount>-100.00</Amount>
        <Description>Invalid negative amount</Description>
      </ChargeOfferItem>
    </ChargeOffer>
  </Property>
</PropertyMarketing>"""
        
        result = validate_schematron(xml_content)
        
        assert result.level == "Schematron"
        assert len(result.findings) > 0
        assert any(finding.level == FindingLevel.ERROR for finding in result.findings)
        assert any("Rule validation failed" in finding.message for finding in result.findings)

    def test_validate_payment_frequency_validation(self):
        """Test payment frequency validation."""
        # Test invalid payment frequency
        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<PropertyMarketing xmlns="http://www.mits.org/schema/PropertyMarketing/ILS/5.0"
                   version="5.0"
                   timestamp="2025-01-15T10:30:00Z">
  <Property>
    <PropertyID>TEST-001</PropertyID>
    <PropertyName>Test Property</PropertyName>
    <PropertyType>Apartment</PropertyType>
    <Address>
      <StreetAddress>123 Test St</StreetAddress>
      <City>TestCity</City>
      <State>TC</State>
      <PostalCode>12345</PostalCode>
    </Address>
    <ChargeOffer>
      <ChargeOfferItem>
        <ChargeClassification>Rent</ChargeClassification>
        <Requirement>Mandatory</Requirement>
        <PaymentFrequency>InvalidFrequency</PaymentFrequency>
        <Refundability>NonRefundable</Refundability>
        <TermBasis>LeaseTerm</TermBasis>
        <Amount>1500.00</Amount>
        <Description>Invalid payment frequency</Description>
      </ChargeOfferItem>
    </ChargeOffer>
  </Property>
</PropertyMarketing>"""
        
        result = validate_schematron(xml_content)
        
        assert result.level == "Schematron"
        assert len(result.findings) > 0
        assert any(finding.level == FindingLevel.ERROR for finding in result.findings)
        assert any("Rule validation failed" in finding.message for finding in result.findings)

    def test_validate_refundability_validation(self):
        """Test refundability validation."""
        # Test invalid refundability
        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<PropertyMarketing xmlns="http://www.mits.org/schema/PropertyMarketing/ILS/5.0"
                   version="5.0"
                   timestamp="2025-01-15T10:30:00Z">
  <Property>
    <PropertyID>TEST-001</PropertyID>
    <PropertyName>Test Property</PropertyName>
    <PropertyType>Apartment</PropertyType>
    <Address>
      <StreetAddress>123 Test St</StreetAddress>
      <City>TestCity</City>
      <State>TC</State>
      <PostalCode>12345</PostalCode>
    </Address>
    <ChargeOffer>
      <ChargeOfferItem>
        <ChargeClassification>Rent</ChargeClassification>
        <Requirement>Mandatory</Requirement>
        <PaymentFrequency>Monthly</PaymentFrequency>
        <Refundability>InvalidRefundability</Refundability>
        <TermBasis>LeaseTerm</TermBasis>
        <Amount>1500.00</Amount>
        <Description>Invalid refundability</Description>
      </ChargeOfferItem>
    </ChargeOffer>
  </Property>
</PropertyMarketing>"""
        
        result = validate_schematron(xml_content)
        
        assert result.level == "Schematron"
        assert len(result.findings) > 0
        assert any(finding.level == FindingLevel.ERROR for finding in result.findings)
        assert any("Rule validation failed" in finding.message for finding in result.findings)

    def test_validate_term_basis_validation(self):
        """Test term basis validation."""
        # Test invalid term basis
        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<PropertyMarketing xmlns="http://www.mits.org/schema/PropertyMarketing/ILS/5.0"
                   version="5.0"
                   timestamp="2025-01-15T10:30:00Z">
  <Property>
    <PropertyID>TEST-001</PropertyID>
    <PropertyName>Test Property</PropertyName>
    <PropertyType>Apartment</PropertyType>
    <Address>
      <StreetAddress>123 Test St</StreetAddress>
      <City>TestCity</City>
      <State>TC</State>
      <PostalCode>12345</PostalCode>
    </Address>
    <ChargeOffer>
      <ChargeOfferItem>
        <ChargeClassification>Rent</ChargeClassification>
        <Requirement>Mandatory</Requirement>
        <PaymentFrequency>Monthly</PaymentFrequency>
        <Refundability>NonRefundable</Refundability>
        <TermBasis>InvalidTermBasis</TermBasis>
        <Amount>1500.00</Amount>
        <Description>Invalid term basis</Description>
      </ChargeOfferItem>
    </ChargeOffer>
  </Property>
</PropertyMarketing>"""
        
        result = validate_schematron(xml_content)
        
        assert result.level == "Schematron"
        assert len(result.findings) > 0
        assert any(finding.level == FindingLevel.ERROR for finding in result.findings)
        assert any("Rule validation failed" in finding.message for finding in result.findings)

    def test_validate_address_completeness(self):
        """Test address completeness validation."""
        # Test incomplete address
        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<PropertyMarketing xmlns="http://www.mits.org/schema/PropertyMarketing/ILS/5.0"
                   version="5.0"
                   timestamp="2025-01-15T10:30:00Z">
  <Property>
    <PropertyID>TEST-001</PropertyID>
    <PropertyName>Test Property</PropertyName>
    <PropertyType>Apartment</PropertyType>
    <Address>
      <!-- Missing StreetAddress -->
      <City>TestCity</City>
      <State>TC</State>
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
        <Description>Incomplete address</Description>
      </ChargeOfferItem>
    </ChargeOffer>
  </Property>
</PropertyMarketing>"""
        
        result = validate_schematron(xml_content)
        
        assert result.level == "Schematron"
        assert len(result.findings) > 0
        assert any(finding.level == FindingLevel.ERROR for finding in result.findings)
        assert any("Rule validation failed" in finding.message for finding in result.findings)

    def test_validate_property_type_validation(self):
        """Test property type validation."""
        # Test invalid property type
        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<PropertyMarketing xmlns="http://www.mits.org/schema/PropertyMarketing/ILS/5.0"
                   version="5.0"
                   timestamp="2025-01-15T10:30:00Z">
  <Property>
    <PropertyID>TEST-001</PropertyID>
    <PropertyName>Test Property</PropertyName>
    <PropertyType>InvalidType</PropertyType>
    <Address>
      <StreetAddress>123 Test St</StreetAddress>
      <City>TestCity</City>
      <State>TC</State>
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
        <Description>Invalid property type</Description>
      </ChargeOfferItem>
    </ChargeOffer>
  </Property>
</PropertyMarketing>"""
        
        result = validate_schematron(xml_content)
        
        assert result.level == "Schematron"
        assert len(result.findings) > 0
        assert any(finding.level == FindingLevel.ERROR for finding in result.findings)
        assert any("Rule validation failed" in finding.message for finding in result.findings)

    def test_validate_business_logic_consistency(self):
        """Test business logic consistency validation."""
        # Test rent charge marked as optional (should be mandatory)
        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<PropertyMarketing xmlns="http://www.mits.org/schema/PropertyMarketing/ILS/5.0"
                   version="5.0"
                   timestamp="2025-01-15T10:30:00Z">
  <Property>
    <PropertyID>TEST-001</PropertyID>
    <PropertyName>Test Property</PropertyName>
    <PropertyType>Apartment</PropertyType>
    <Address>
      <StreetAddress>123 Test St</StreetAddress>
      <City>TestCity</City>
      <State>TC</State>
      <PostalCode>12345</PostalCode>
    </Address>
    <ChargeOffer>
      <ChargeOfferItem>
        <ChargeClassification>Rent</ChargeClassification>
        <Requirement>Optional</Requirement>  <!-- Should be Mandatory -->
        <PaymentFrequency>Monthly</PaymentFrequency>
        <Refundability>NonRefundable</Refundability>
        <TermBasis>LeaseTerm</TermBasis>
        <Amount>1500.00</Amount>
        <Description>Rent marked as optional</Description>
      </ChargeOfferItem>
    </ChargeOffer>
  </Property>
</PropertyMarketing>"""
        
        result = validate_schematron(xml_content)
        
        assert result.level == "Schematron"
        assert len(result.findings) > 0
        assert any(finding.level == FindingLevel.ERROR for finding in result.findings)
        assert any("Rule validation failed" in finding.message for finding in result.findings)

    def test_validate_deposit_frequency_consistency(self):
        """Test deposit frequency consistency validation."""
        # Test deposit charge with non-OneTime frequency
        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<PropertyMarketing xmlns="http://www.mits.org/schema/PropertyMarketing/ILS/5.0"
                   version="5.0"
                   timestamp="2025-01-15T10:30:00Z">
  <Property>
    <PropertyID>TEST-001</PropertyID>
    <PropertyName>Test Property</PropertyName>
    <PropertyType>Apartment</PropertyType>
    <Address>
      <StreetAddress>123 Test St</StreetAddress>
      <City>TestCity</City>
      <State>TC</State>
      <PostalCode>12345</PostalCode>
    </Address>
    <ChargeOffer>
      <ChargeOfferItem>
        <ChargeClassification>Deposit</ChargeClassification>
        <Requirement>Mandatory</Requirement>
        <PaymentFrequency>Monthly</PaymentFrequency>  <!-- Should be OneTime -->
        <Refundability>Deposit</Refundability>
        <TermBasis>LeaseTerm</TermBasis>
        <Amount>1500.00</Amount>
        <Description>Deposit with monthly frequency</Description>
      </ChargeOfferItem>
    </ChargeOffer>
  </Property>
</PropertyMarketing>"""
        
        result = validate_schematron(xml_content)
        
        assert result.level == "Schematron"
        assert len(result.findings) > 0
        assert any(finding.level == FindingLevel.ERROR for finding in result.findings)
        assert any("Rule validation failed" in finding.message for finding in result.findings)

    def test_validate_valid_xml_passes(self):
        """Test that valid XML passes all enhanced rules."""
        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<PropertyMarketing xmlns="http://www.mits.org/schema/PropertyMarketing/ILS/5.0"
                   version="5.0"
                   timestamp="2025-01-15T10:30:00Z">
  <Property>
    <PropertyID>VALID-001</PropertyID>
    <PropertyName>Valid Property</PropertyName>
    <PropertyType>Apartment</PropertyType>
    <Address>
      <StreetAddress>123 Valid St</StreetAddress>
      <City>ValidCity</City>
      <State>VC</State>
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
        <Description>Valid rent charge</Description>
      </ChargeOfferItem>
      <ChargeOfferItem>
        <ChargeClassification>Deposit</ChargeClassification>
        <Requirement>Mandatory</Requirement>
        <PaymentFrequency>OneTime</PaymentFrequency>
        <Refundability>Deposit</Refundability>
        <TermBasis>LeaseTerm</TermBasis>
        <Amount>1500.00</Amount>
        <Description>Valid deposit charge</Description>
      </ChargeOfferItem>
    </ChargeOffer>
  </Property>
</PropertyMarketing>"""
        
        result = validate_schematron(xml_content)
        
        assert result.level == "Schematron"
        # Should have no findings for valid XML
        assert len(result.findings) == 0
