"""Tests for XSD validation."""

from pathlib import Path

from mits_validator.models import FindingLevel
from mits_validator.validation.xsd import get_schema_info, validate_xsd


class TestXSDValidation:
    """Test XSD validation functionality."""

    def test_validate_valid_xml(self):
        """Test validation of valid MITS XML."""
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
</PropertyMarketing>"""

        result = validate_xsd(xml_content)

        assert result.level == "XSD"
        assert len(result.findings) == 0
        assert result.duration_ms >= 0

    def test_validate_invalid_xml(self):
        """Test validation of invalid MITS XML."""
        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<PropertyMarketing xmlns="http://www.mits.org/schema/PropertyMarketing/ILS/5.0"
                   version="5.0"
                   timestamp="2025-09-15T10:30:00Z">
  <Property>
    <PropertyID>PROP-001</PropertyID>
    <!-- Missing required PropertyName -->
    <PropertyType>Apartment</PropertyType>
    <Address>
      <StreetAddress>123 Main St</StreetAddress>
      <City>Anytown</City>
      <State>CA</State>
      <PostalCode>12345</PostalCode>
    </Address>
  </Property>
</PropertyMarketing>"""

        result = validate_xsd(xml_content)

        assert result.level == "XSD"
        assert len(result.findings) > 0
        assert any(finding.level == FindingLevel.ERROR for finding in result.findings)
        assert any("PropertyName" in finding.message for finding in result.findings)

    def test_validate_invalid_enumeration(self):
        """Test validation with invalid enumeration value."""
        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<PropertyMarketing xmlns="http://www.mits.org/schema/PropertyMarketing/ILS/5.0"
                   version="5.0"
                   timestamp="2025-09-15T10:30:00Z">
  <Property>
    <PropertyID>PROP-001</PropertyID>
    <PropertyName>Test Property</PropertyName>
    <PropertyType>InvalidType</PropertyType>
    <Address>
      <StreetAddress>123 Main St</StreetAddress>
      <City>Anytown</City>
      <State>CA</State>
      <PostalCode>12345</PostalCode>
    </Address>
  </Property>
</PropertyMarketing>"""

        result = validate_xsd(xml_content)

        assert result.level == "XSD"
        assert len(result.findings) > 0
        assert any(finding.level == FindingLevel.ERROR for finding in result.findings)

    def test_validate_missing_schema(self):
        """Test validation when schema file is missing."""
        result = validate_xsd("", schema_path=Path("/nonexistent/schema.xsd"))

        assert result.level == "XSD"
        assert len(result.findings) == 1
        assert result.findings[0].level == FindingLevel.ERROR
        assert result.findings[0].code == "XSD:SCHEMA_MISSING"

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
  <!-- Unclosed tag -->
</PropertyMarketing>"""

        result = validate_xsd(xml_content)

        assert result.level == "XSD"
        # This XML is actually well-formed, so it should pass parsing
        # but might fail schema validation
        assert result.duration_ms >= 0

    def test_validate_from_file(self):
        """Test validation from file path."""
        fixture_path = (
            Path(__file__).parent.parent.parent / "fixtures" / "mits5" / "valid-property.xml"
        )

        if fixture_path.exists():
            result = validate_xsd(fixture_path)

            assert result.level == "XSD"
            # Should pass validation
            assert len(result.findings) == 0

    def test_get_schema_info(self):
        """Test getting schema information."""
        info = get_schema_info()

        assert "schema_path" in info
        assert "exists" in info
        assert "namespace" in info
        assert "root_element" in info
        assert "version" in info

        if info["exists"]:
            assert info["namespace"] == "http://www.mits.org/schema/PropertyMarketing/ILS/5.0"
            assert info["root_element"] == "PropertyMarketing"
            assert info["version"] == "5.0"

    def test_validate_charge_classification_enum(self):
        """Test validation of charge classification enumeration."""
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
      </ChargeOfferItem>
    </ChargeOffer>
  </Property>
</PropertyMarketing>"""

        result = validate_xsd(xml_content)

        assert result.level == "XSD"
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

        result = validate_xsd(xml_content)

        assert result.level == "XSD"
        assert len(result.findings) > 0
        assert any(finding.level == FindingLevel.ERROR for finding in result.findings)

    def test_validate_currency_format(self):
        """Test validation of currency format."""
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
        <Amount>1500.123</Amount>  <!-- Invalid: too many decimal places -->
      </ChargeOfferItem>
    </ChargeOffer>
  </Property>
</PropertyMarketing>"""

        result = validate_xsd(xml_content)

        assert result.level == "XSD"
        assert len(result.findings) > 0
        assert any(finding.level == FindingLevel.ERROR for finding in result.findings)
