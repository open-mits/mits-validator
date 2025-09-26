"""Tests for XSD validation level."""

import tempfile
from pathlib import Path

from fastapi.testclient import TestClient

from mits_validator.api import app
from mits_validator.levels.xsd import XSDValidator
from mits_validator.models import FindingLevel, ValidationLevel

client = TestClient(app)


class TestXSDValidation:
    """Test XSD validation functionality."""

    def test_xsd_validation_with_schema(self):
        """Test XSD validation with a valid schema present."""
        # Create a temporary XSD schema
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xsd', delete=False) as f:
            f.write('''<?xml version="1.0" encoding="UTF-8"?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema"
           targetNamespace="http://www.mits.org/schema"
           xmlns:mits="http://www.mits.org/schema"
           elementFormDefault="qualified">
  <xs:element name="MITS" type="mits:MITSFeedType"/>
  <xs:complexType name="MITSFeedType">
    <xs:sequence>
      <xs:element name="Header" type="mits:HeaderType"/>
    </xs:sequence>
    <xs:attribute name="version" type="xs:string" use="required"/>
  </xs:complexType>
  <xs:complexType name="HeaderType">
    <xs:sequence>
      <xs:element name="Provider" type="xs:string"/>
    </xs:sequence>
  </xs:complexType>
</xs:schema>''')
            schema_path = Path(f.name)

        try:
            validator = XSDValidator(schema_path)
            
            # Test with valid XML
            valid_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<MITS xmlns="http://www.mits.org/schema" version="1.0">
  <Header>
    <Provider>Test Provider</Provider>
  </Header>
</MITS>'''
    
            result = validator.validate(valid_xml.encode())
            assert result.level == ValidationLevel.XSD
            assert len(result.findings) == 0  # No errors for valid XML
            
            # Test with invalid XML
            invalid_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<MITS xmlns="http://www.mits.org/schema" version="1.0">
  <Header>
    <InvalidElement>This should fail</InvalidElement>
  </Header>
</MITS>'''
            
            result = validator.validate(invalid_xml.encode())
            assert result.level == ValidationLevel.XSD
            assert len(result.findings) == 1
            assert result.findings[0].code == "XSD:VALIDATION_ERROR"
            assert result.findings[0].level == FindingLevel.ERROR
            
        finally:
            schema_path.unlink()

    def test_xsd_validation_without_schema(self):
        """Test XSD validation when schema is missing."""
        validator = XSDValidator(None)
        
        xml_content = b'<?xml version="1.0"?><root>test</root>'
        result = validator.validate(xml_content)
        
        assert result.level == ValidationLevel.XSD
        assert len(result.findings) == 1
        assert result.findings[0].code == "XSD:SCHEMA_MISSING"
        assert result.findings[0].level == FindingLevel.INFO

    def test_xsd_validation_with_invalid_schema_path(self):
        """Test XSD validation with non-existent schema path."""
        validator = XSDValidator(Path("/non/existent/schema.xsd"))
        
        xml_content = b'<?xml version="1.0"?><root>test</root>'
        result = validator.validate(xml_content)
        
        assert result.level == ValidationLevel.XSD
        assert len(result.findings) == 1
        assert result.findings[0].code == "XSD:SCHEMA_MISSING"
        assert result.findings[0].level == FindingLevel.INFO

    def test_xsd_validation_crash_handling(self):
        """Test XSD validation handles crashes gracefully."""
        # Create a malformed XSD schema
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xsd', delete=False) as f:
            f.write('''<?xml version="1.0" encoding="UTF-8"?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
  <xs:element name="Test">
    <xs:complexType>
      <xs:sequence>
        <xs:element name="Invalid" type="xs:invalidType"/>
      </xs:sequence>
    </xs:complexType>
  </xs:element>
</xs:schema>''')
            schema_path = Path(f.name)

        try:
            validator = XSDValidator(schema_path)
            
            # The schema should fail to load, so we should get SCHEMA_MISSING
            xml_content = b'<?xml version="1.0"?><root>test</root>'
            result = validator.validate(xml_content)
            
            assert result.level == ValidationLevel.XSD
            assert len(result.findings) == 1
            assert result.findings[0].code == "XSD:SCHEMA_MISSING"
            assert result.findings[0].level == FindingLevel.INFO
            
        finally:
            schema_path.unlink()

    def test_xsd_validation_integration(self):
        """Test XSD validation through the API."""
        # Test with invalid XML that should fail XSD validation
        xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<MITS xmlns="http://www.mits.org/schema" version="1.0">
  <Header>
    <InvalidElement>This should fail XSD validation</InvalidElement>
  </Header>
</MITS>'''
        
        response = client.post(
            "/v1/validate",
            files={"file": ("test.xml", xml_content, "application/xml")},
            params={"profile": "pms"}
        )
        
        assert response.status_code == 200
        result = response.json()
        
        # Should have XSD validation error (schema is present but XML doesn't match)
        xsd_findings = [f for f in result["findings"] if f["code"] == "XSD:VALIDATION_ERROR"]
        assert len(xsd_findings) == 1
        assert xsd_findings[0]["level"] == "error"
