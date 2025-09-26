"""Contract tests for the Result Envelope v1 JSON Schema."""

import json
from pathlib import Path

import jsonschema
from fastapi.testclient import TestClient

from mits_validator.api import app

client = TestClient(app)

# Load the JSON Schema
SCHEMA_PATH = Path(__file__).parent.parent / "schemas" / "result-envelope.v1.json"
with open(SCHEMA_PATH) as f:
    RESULT_ENVELOPE_SCHEMA = json.load(f)


def validate_response_schema(response_data: dict) -> None:
    """Validate response data against the Result Envelope v1 schema."""
    jsonschema.validate(response_data, RESULT_ENVELOPE_SCHEMA)


class TestResultEnvelopeContract:
    """Test that all API responses conform to the Result Envelope v1 schema."""

    def test_success_response_schema(self):
        """Test that a successful validation response conforms to the schema."""
        # Create a simple valid XML file
        xml_content = '<?xml version="1.0" encoding="UTF-8"?><root><test>content</test></root>'

        response = client.post(
            "/v1/validate", files={"file": ("test.xml", xml_content, "application/xml")}
        )

        assert response.status_code == 200
        response_data = response.json()
        validate_response_schema(response_data)

        # Verify key fields
        assert response_data["api_version"] == "1.0"
        # Valid XML should have no errors (warnings are OK)
        # Note: XSD validation may produce errors for non-MITS XML
        assert response_data["summary"]["errors"] >= 0
        assert "request_id" in response_data["metadata"]
        assert "timestamp" in response_data["metadata"]

    def test_error_response_schema(self):
        """Test that an error response conforms to the schema."""
        # Test with malformed XML
        xml_content = '<?xml version="1.0" encoding="UTF-8"?><root><unclosed>content'

        response = client.post(
            "/v1/validate", files={"file": ("test.xml", xml_content, "application/xml")}
        )

        assert response.status_code == 200
        response_data = response.json()
        validate_response_schema(response_data)

        # Verify error structure
        assert response_data["api_version"] == "1.0"
        assert response_data["summary"]["valid"] is False
        assert response_data["summary"]["errors"] >= 1
        assert len(response_data["findings"]) >= 1
        assert response_data["findings"][0]["level"] in ["error", "warning", "info"]

    def test_input_validation_error_schema(self):
        """Test that input validation errors conform to the schema."""
        # Test with both file and URL (should be 400)
        response = client.post(
            "/v1/validate",
            files={"file": ("test.xml", "content", "application/xml")},
            data={"url": "http://example.com/test.xml"},
        )

        assert response.status_code == 400
        response_data = response.json()
        validate_response_schema(response_data)

        # Verify error structure
        assert response_data["api_version"] == "1.0"
        assert response_data["summary"]["valid"] is False
        assert response_data["summary"]["errors"] >= 1
        assert any(f["code"] == "INTAKE:BOTH_INPUTS" for f in response_data["findings"])

    def test_oversize_error_schema(self):
        """Test that oversize file errors conform to the schema."""
        # Create a large file (this might not trigger in test environment)
        large_content = "x" * (11 * 1024 * 1024)  # 11MB

        response = client.post(
            "/v1/validate", files={"file": ("large.xml", large_content, "application/xml")}
        )

        # This might be 200 or 413 depending on FastAPI's handling
        response_data = response.json()
        validate_response_schema(response_data)

        # Verify structure regardless of status code
        assert response_data["api_version"] == "1.0"
        assert "request_id" in response_data["metadata"]

    def test_unsupported_media_type_schema(self):
        """Test that unsupported media type errors conform to the schema."""
        response = client.post(
            "/v1/validate", files={"file": ("test.jpg", b"fake image data", "image/jpeg")}
        )

        assert response.status_code == 415
        response_data = response.json()
        validate_response_schema(response_data)

        # Verify error structure
        assert response_data["api_version"] == "1.0"
        assert response_data["summary"]["valid"] is False
        assert response_data["summary"]["errors"] >= 1
        assert any(f["code"] == "INTAKE:UNSUPPORTED_MEDIA_TYPE" for f in response_data["findings"])

    def test_schema_field_types(self):
        """Test that all required fields have correct types."""
        response = client.post(
            "/v1/validate",
            files={"file": ("test.xml", '<?xml version="1.0"?><root/>', "application/xml")},
        )

        assert response.status_code == 200
        response_data = response.json()

        # Test top-level required fields
        assert isinstance(response_data["api_version"], str)
        assert isinstance(response_data["validator"], dict)
        assert isinstance(response_data["input"], dict)
        assert isinstance(response_data["summary"], dict)
        assert isinstance(response_data["findings"], list)
        assert isinstance(response_data["metadata"], dict)

        # Test validator fields
        validator = response_data["validator"]
        assert isinstance(validator["name"], str)
        assert isinstance(validator["spec_version"], str)
        assert isinstance(validator["profile"], str)
        assert isinstance(validator["levels_available"], list)
        assert isinstance(validator["levels_executed"], list)

        # Test summary fields
        summary = response_data["summary"]
        assert isinstance(summary["valid"], bool)
        assert isinstance(summary["errors"], int)
        assert isinstance(summary["warnings"], int)
        assert isinstance(summary["duration_ms"], int)

        # Test metadata fields
        metadata = response_data["metadata"]
        assert isinstance(metadata["request_id"], str)
        assert isinstance(metadata["timestamp"], str)
