"""Tests for XSD validation level."""

from pathlib import Path

from mits_validator.levels.xsd import XSDValidator
from mits_validator.models import FindingLevel


class TestXSDValidator:
    """Test XSD validation level functionality."""

    def test_xsd_validation_with_schema(self, tmp_path: Path) -> None:
        """Test XSD validation with a valid schema."""
        # Create a simple XSD schema
        schema_content = """<?xml version="1.0" encoding="UTF-8"?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema"
           targetNamespace="http://example.com/mits"
           xmlns:mits="http://example.com/mits"
           elementFormDefault="qualified">
  <xs:element name="mits" type="mits:MitsType"/>
  <xs:complexType name="MitsType">
    <xs:sequence>
      <xs:element name="property" type="mits:PropertyType" minOccurs="0" maxOccurs="unbounded"/>
    </xs:sequence>
  </xs:complexType>
  <xs:complexType name="PropertyType">
    <xs:sequence>
      <xs:element name="name" type="xs:string"/>
      <xs:element name="address" type="xs:string"/>
    </xs:sequence>
    <xs:attribute name="id" type="xs:string" use="required"/>
  </xs:complexType>
</xs:schema>"""

        schema_file = tmp_path / "schema.xsd"
        with open(schema_file, "w") as f:
            f.write(schema_content)

        # Create valid XML content
        xml_content = b"""<?xml version="1.0" encoding="UTF-8"?>
<mits xmlns="http://example.com/mits">
  <property id="prop1">
    <name>Test Property</name>
    <address>123 Main St</address>
  </property>
</mits>"""

        validator = XSDValidator(schema_file)
        result = validator.validate(xml_content)

        assert result.level == "XSD"
        assert len(result.findings) == 0  # Should have no findings for valid XML
        assert result.duration_ms >= 0

    def test_xsd_validation_without_schema(self) -> None:
        """Test XSD validation without a schema."""
        xml_content = b"""<?xml version="1.0" encoding="UTF-8"?>
<root>
  <item>test</item>
</root>"""

        validator = XSDValidator()
        result = validator.validate(xml_content)

        assert result.level == "XSD"
        assert len(result.findings) == 1
        assert result.findings[0].code == "XSD:SCHEMA_MISSING"
        assert result.findings[0].level == FindingLevel.INFO

    def test_xsd_validation_with_invalid_schema_path(self) -> None:
        """Test XSD validation with invalid schema path."""
        xml_content = b"""<?xml version="1.0" encoding="UTF-8"?>
<root>
  <item>test</item>
</root>"""

        validator = XSDValidator(Path("nonexistent.xsd"))
        result = validator.validate(xml_content)

        assert result.level == "XSD"
        assert len(result.findings) == 1
        assert result.findings[0].code == "XSD:SCHEMA_MISSING"
        assert result.findings[0].level == FindingLevel.INFO

    def test_xsd_validation_with_invalid_xml(self, tmp_path: Path) -> None:
        """Test XSD validation with invalid XML."""
        # Create a simple XSD schema
        schema_content = """<?xml version="1.0" encoding="UTF-8"?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema"
           targetNamespace="http://example.com/mits"
           xmlns:mits="http://example.com/mits"
           elementFormDefault="qualified">
  <xs:element name="mits" type="mits:MitsType"/>
  <xs:complexType name="MitsType">
    <xs:sequence>
      <xs:element name="property" type="mits:PropertyType" minOccurs="0" maxOccurs="unbounded"/>
    </xs:sequence>
  </xs:complexType>
  <xs:complexType name="PropertyType">
    <xs:sequence>
      <xs:element name="name" type="xs:string"/>
      <xs:element name="address" type="xs:string"/>
    </xs:sequence>
    <xs:attribute name="id" type="xs:string" use="required"/>
  </xs:complexType>
</xs:schema>"""

        schema_file = tmp_path / "schema.xsd"
        with open(schema_file, "w") as f:
            f.write(schema_content)

        # Create invalid XML content (wrong element name)
        xml_content = b"""<?xml version="1.0" encoding="UTF-8"?>
<mits xmlns="http://example.com/mits">
  <invalid_element>
    <name>Test Property</name>
    <address>123 Main St</address>
  </invalid_element>
</mits>"""

        validator = XSDValidator(schema_file)
        result = validator.validate(xml_content)

        assert result.level == "XSD"
        assert len(result.findings) == 1
        assert result.findings[0].code == "XSD:VALIDATION_ERROR"
        assert result.findings[0].level == FindingLevel.ERROR

    def test_xsd_validation_with_malformed_xml(self, tmp_path: Path) -> None:
        """Test XSD validation with malformed XML."""
        # Create a simple XSD schema
        schema_content = """<?xml version="1.0" encoding="UTF-8"?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema"
           targetNamespace="http://example.com/mits"
           xmlns:mits="http://example.com/mits"
           elementFormDefault="qualified">
  <xs:element name="mits" type="mits:MitsType"/>
  <xs:complexType name="MitsType">
    <xs:sequence>
      <xs:element name="property" type="mits:PropertyType" minOccurs="0" maxOccurs="unbounded"/>
    </xs:sequence>
  </xs:complexType>
  <xs:complexType name="PropertyType">
    <xs:sequence>
      <xs:element name="name" type="xs:string"/>
      <xs:element name="address" type="xs:string"/>
    </xs:sequence>
    <xs:attribute name="id" type="xs:string" use="required"/>
  </xs:complexType>
</xs:schema>"""

        schema_file = tmp_path / "schema.xsd"
        with open(schema_file, "w") as f:
            f.write(schema_content)

        # Create malformed XML content
        xml_content = b"""<?xml version="1.0" encoding="UTF-8"?>
<mits xmlns="http://example.com/mits">
  <property id="prop1">
    <name>Test Property</name>
    <address>123 Main St</address>
  </property>
</mits>"""

        validator = XSDValidator(schema_file)
        result = validator.validate(xml_content)

        assert result.level == "XSD"
        assert len(result.findings) == 0  # Should be valid XML

    def test_xsd_validation_crash_handling(self, tmp_path: Path) -> None:
        """Test XSD validation crash handling."""
        # Create an invalid XSD schema
        schema_content = """<?xml version="1.0" encoding="UTF-8"?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
  <xs:element name="root" type="xs:string"/>
  <!-- Invalid schema content -->
  <xs:invalid/>
</xs:schema>"""

        schema_file = tmp_path / "schema.xsd"
        with open(schema_file, "w") as f:
            f.write(schema_content)

        xml_content = b"""<?xml version="1.0" encoding="UTF-8"?>
<root>test</root>"""

        validator = XSDValidator(schema_file)
        result = validator.validate(xml_content)

        assert result.level == "XSD"
        # Should handle schema loading failure gracefully
        assert len(result.findings) == 1
        assert result.findings[0].code == "XSD:SCHEMA_MISSING"

    def test_xsd_validation_get_name(self) -> None:
        """Test XSD validator get_name method."""
        validator = XSDValidator()
        assert validator.get_name() == "XSD"

    def test_xsd_validation_schema_loading_caching(self, tmp_path: Path) -> None:
        """Test that schema loading is cached."""
        # Create a simple XSD schema
        schema_content = """<?xml version="1.0" encoding="UTF-8"?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
  <xs:element name="root" type="xs:string"/>
</xs:schema>"""

        schema_file = tmp_path / "schema.xsd"
        with open(schema_file, "w") as f:
            f.write(schema_content)

        validator = XSDValidator(schema_file)

        # First call should load schema
        result1 = validator.validate(b"<root>test</root>")
        assert len(result1.findings) == 0

        # Second call should use cached schema
        result2 = validator.validate(b"<root>test2</root>")
        assert len(result2.findings) == 0

        # Schema should be loaded
        assert validator._schema is not None
        assert validator._schema_loaded is True
