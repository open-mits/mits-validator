"""Test Semantic validation level."""

from pathlib import Path

import pytest

from mits_validator.levels.semantic import SemanticValidator


class TestSemanticValidation:
    """Test Semantic validation level."""

    @pytest.fixture
    def semantic_validator(self) -> SemanticValidator:
        """Create semantic validator for testing."""
        return SemanticValidator()

    def test_validate_invalid_charge_classification(self, semantic_validator: SemanticValidator):
        """Test validation of invalid charge classification against catalog."""
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
        <ChargeClassification>InvalidChargeClass</ChargeClassification>
        <Requirement>Mandatory</Requirement>
        <PaymentFrequency>Monthly</PaymentFrequency>
        <Refundability>NonRefundable</Refundability>
        <TermBasis>LeaseTerm</TermBasis>
        <Amount>1500.00</Amount>
        <Description>Invalid charge class</Description>
      </ChargeOfferItem>
    </ChargeOffer>
  </Property>
</PropertyMarketing>"""

        result = semantic_validator.validate(xml_content.encode("utf-8"))

        assert result.level == "Semantic"
        # Should find invalid charge classification
        assert len(result.findings) > 0
        assert any(finding.code == "SEMANTIC:INVALID_CHARGE_CLASS" for finding in result.findings)

    def test_validate_invalid_payment_frequency(self, semantic_validator: SemanticValidator):
        """Test validation of invalid payment frequency against catalog."""
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

        result = semantic_validator.validate(xml_content.encode("utf-8"))

        assert result.level == "Semantic"
        # Should find invalid payment frequency
        assert len(result.findings) > 0
        assert any(
            finding.code == "SEMANTIC:INVALID_PAYMENT_FREQUENCY" for finding in result.findings
        )

    def test_validate_invalid_refundability(self, semantic_validator: SemanticValidator):
        """Test validation of invalid refundability against catalog."""
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

        result = semantic_validator.validate(xml_content.encode("utf-8"))

        assert result.level == "Semantic"
        # Should find invalid refundability
        assert len(result.findings) > 0
        assert any(finding.code == "SEMANTIC:INVALID_REFUNDABILITY" for finding in result.findings)

    def test_validate_invalid_term_basis(self, semantic_validator: SemanticValidator):
        """Test validation of invalid term basis against catalog."""
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

        result = semantic_validator.validate(xml_content.encode("utf-8"))

        assert result.level == "Semantic"
        # Should find invalid term basis
        assert len(result.findings) > 0
        assert any(finding.code == "SEMANTIC:INVALID_TERM_BASIS" for finding in result.findings)

    def test_validate_business_logic_consistency(self, semantic_validator: SemanticValidator):
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

        result = semantic_validator.validate(xml_content.encode("utf-8"))

        assert result.level == "Semantic"
        # Should find inconsistent rent requirement
        assert len(result.findings) > 0
        assert any(
            finding.code == "SEMANTIC:INCONSISTENT_RENT_REQUIREMENT" for finding in result.findings
        )

    def test_validate_deposit_frequency_consistency(self, semantic_validator: SemanticValidator):
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

        result = semantic_validator.validate(xml_content.encode("utf-8"))

        assert result.level == "Semantic"
        # Should find inconsistent deposit frequency
        assert len(result.findings) > 0
        assert any(
            finding.code == "SEMANTIC:INCONSISTENT_DEPOSIT_FREQUENCY" for finding in result.findings
        )

    def test_validate_valid_xml_passes(self, semantic_validator: SemanticValidator):
        """Test that valid XML passes semantic validation."""
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
        <ChargeClassification>RENT</ChargeClassification>
        <Requirement>Mandatory</Requirement>
        <PaymentFrequency>MONTHLY</PaymentFrequency>
        <Refundability>NON_REFUNDABLE</Refundability>
        <TermBasis>LEASE_TERM</TermBasis>
        <Amount>1500.00</Amount>
        <Description>Valid rent charge</Description>
      </ChargeOfferItem>
      <ChargeOfferItem>
        <ChargeClassification>DEPOSIT</ChargeClassification>
        <Requirement>Mandatory</Requirement>
        <PaymentFrequency>ONE_TIME</PaymentFrequency>
        <Refundability>FULLY_REFUNDABLE</Refundability>
        <TermBasis>LEASE_TERM</TermBasis>
        <Amount>1500.00</Amount>
        <Description>Valid deposit charge</Description>
      </ChargeOfferItem>
    </ChargeOffer>
  </Property>
</PropertyMarketing>"""

        result = semantic_validator.validate(xml_content.encode("utf-8"))

        assert result.level == "Semantic"
        # Should have no findings for valid XML
        assert len(result.findings) == 0

    def test_validate_malformed_xml(self, semantic_validator: SemanticValidator):
        """Test validation with malformed XML."""
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
    <UnclosedTag>
</PropertyMarketing>"""

        result = semantic_validator.validate(xml_content.encode("utf-8"))

        assert result.level == "Semantic"
        # Should find XML parse error
        assert len(result.findings) > 0
        assert any(finding.code == "SEMANTIC:XML_PARSE_ERROR" for finding in result.findings)

    def test_validate_with_missing_catalogs(self, semantic_validator: SemanticValidator):
        """Test validation when catalogs are not available."""
        # Create validator with non-existent rules directory
        validator = SemanticValidator(rules_dir=Path("/nonexistent/rules"))

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
        <Amount>1500.00</Amount>
        <Description>Test charge</Description>
      </ChargeOfferItem>
    </ChargeOffer>
  </Property>
</PropertyMarketing>"""

        result = validator.validate(xml_content.encode("utf-8"))

        assert result.level == "Semantic"
        # Should find resource load failure
        assert len(result.findings) > 0
        assert any(
            finding.code in ["ENGINE:RESOURCE_LOAD_FAILED", "CATALOG:VERSION_NOT_FOUND"]
            for finding in result.findings
        )
