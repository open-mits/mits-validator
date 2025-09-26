from __future__ import annotations

from fastapi.testclient import TestClient

from mits_validator.api import app

client = TestClient(app)


def test_defensive_input_validation_both_inputs() -> None:
    """Test that providing both file and URL returns 400 with error finding."""
    test_content = b"<xml>test</xml>"
    files = {"file": ("test.xml", test_content, "application/xml")}
    data = {"url": "https://example.com", "max_size_mb": 10}

    response = client.post("/v1/validate", files=files, data=data)
    assert response.status_code == 400

    result = response.json()
    assert result["summary"]["valid"] is False
    assert result["summary"]["errors"] == 1
    assert len(result["findings"]) == 1

    finding = result["findings"][0]
    assert finding["level"] == "error"
    assert finding["code"] == "INTAKE:BOTH_INPUTS"
    assert "Cannot provide both file upload and URL" in finding["message"]


def test_defensive_input_validation_no_inputs() -> None:
    """Test that providing neither file nor URL returns 400 with error finding."""
    data = {"max_size_mb": 10}

    response = client.post("/v1/validate", data=data)
    assert response.status_code == 400

    result = response.json()
    assert result["summary"]["valid"] is False
    assert result["summary"]["errors"] == 1
    assert len(result["findings"]) == 1

    finding = result["findings"][0]
    assert finding["level"] == "error"
    assert finding["code"] == "INTAKE:NO_INPUTS"
    assert "Must provide either a file upload or URL" in finding["message"]


def test_defensive_content_type_validation() -> None:
    """Test that unacceptable content types return 415 with error finding."""
    test_content = b"<xml>test</xml>"
    files = {"file": ("test.xml", test_content, "image/jpeg")}
    data = {"max_size_mb": 10}

    response = client.post("/v1/validate", files=files, data=data)
    assert response.status_code == 415

    result = response.json()
    assert result["summary"]["valid"] is False
    assert result["summary"]["errors"] == 1
    assert len(result["findings"]) == 1

    finding = result["findings"][0]
    assert finding["level"] == "error"
    assert finding["code"] == "INTAKE:UNACCEPTABLE_CONTENT_TYPE"
    assert "not allowed for profile" in finding["message"]


def test_defensive_size_validation() -> None:
    """Test that oversized files return 413 with error finding."""
    # Create a large file (simulate)
    large_content = b"x" * (11 * 1024 * 1024)  # 11MB
    files = {"file": ("large.xml", large_content, "application/xml")}
    data = {"max_size_mb": 10}

    response = client.post("/v1/validate", files=files, data=data)
    assert response.status_code == 413

    result = response.json()
    assert result["summary"]["valid"] is False
    assert result["summary"]["errors"] == 1
    assert len(result["findings"]) == 1

    finding = result["findings"][0]
    assert finding["level"] == "error"
    assert finding["code"] == "INTAKE:TOO_LARGE"
    assert "exceeds limit" in finding["message"]


def test_defensive_url_validation() -> None:
    """Test that invalid URL format returns 422 with error finding."""
    data = {"url": "not-a-url", "max_size_mb": 10}

    response = client.post("/v1/validate", data=data)
    assert response.status_code == 422

    result = response.json()
    assert result["summary"]["valid"] is False
    assert result["summary"]["errors"] == 1
    assert len(result["findings"]) == 1

    finding = result["findings"][0]
    assert finding["level"] == "error"
    assert finding["code"] == "INTAKE:INVALID_URL"
    assert "must start with http:// or https://" in finding["message"]


def test_profile_aware_validation() -> None:
    """Test that profile parameter affects validation behavior."""
    test_content = b"<root>test</root>"
    files = {"file": ("test.xml", test_content, "application/xml")}
    data = {"max_size_mb": 10}

    response = client.post("/v1/validate?profile=pms", files=files, data=data)
    assert response.status_code == 200

    result = response.json()
    assert result["validator"]["profile"] == "pms"
    assert "WellFormed" in result["validator"]["levels_executed"]
    assert "XSD" in result["validator"]["levels_executed"]


def test_validation_levels_registry() -> None:
    """Test that validation levels are executed in order."""
    test_content = b"<root>test</root>"
    files = {"file": ("test.xml", test_content, "application/xml")}
    data = {"max_size_mb": 10}

    response = client.post("/v1/validate", files=files, data=data)
    assert response.status_code == 200

    result = response.json()
    levels_executed = result["validator"]["levels_executed"]
    levels_available = result["validator"]["levels_available"]

    # Should have WellFormed, XSD, and Schematron in default profile
    assert "WellFormed" in levels_executed
    assert "XSD" in levels_executed
    assert "Schematron" in levels_executed

    # Should report available levels
    assert "WellFormed" in levels_available
    assert "XSD" in levels_available
    assert "Schematron" in levels_available


def test_error_response_headers() -> None:
    """Test that error responses include proper headers."""
    data = {"max_size_mb": 10}  # No file or URL

    response = client.post("/v1/validate", data=data)
    assert response.status_code == 400

    # Check for required headers
    assert "X-Request-Id" in response.headers
    assert "Cache-Control" in response.headers
    assert response.headers["Cache-Control"] == "no-store"

    # Check that request ID is in response body
    result = response.json()
    assert "request_id" in result["metadata"]
    assert result["metadata"]["request_id"] == response.headers["X-Request-Id"]


def test_result_envelope_consistency() -> None:
    """Test that all responses maintain consistent envelope structure."""
    # Test error response
    data = {"max_size_mb": 10}
    response = client.post("/v1/validate", data=data)
    assert response.status_code == 400

    error_result = response.json()

    # Test success response
    test_content = b"<root>test</root>"
    files = {"file": ("test.xml", test_content, "application/xml")}
    data = {"max_size_mb": 10}

    response = client.post("/v1/validate", files=files, data=data)
    assert response.status_code == 200

    success_result = response.json()

    # Both should have same top-level structure
    for result in [error_result, success_result]:
        assert "api_version" in result
        assert "validator" in result
        assert "input" in result
        assert "summary" in result
        assert "findings" in result
        assert "derived" in result
        assert "metadata" in result

        # Validator should have required fields
        validator = result["validator"]
        assert "name" in validator
        assert "spec_version" in validator
        assert "profile" in validator
        assert "levels_executed" in validator
        assert "levels_available" in validator

        # Summary should have required fields
        summary = result["summary"]
        assert "valid" in summary
        assert "errors" in summary
        assert "warnings" in summary
        assert "duration_ms" in summary

        # Metadata should have required fields
        metadata = result["metadata"]
        assert "request_id" in metadata
        assert "timestamp" in metadata
        assert "engine" in metadata


def test_validation_level_isolation() -> None:
    """Test that validation level failures are isolated and reported."""
    # This test would require mocking a level to crash
    # For now, we'll test that the system handles missing levels gracefully
    test_content = b"<root>test</root>"
    files = {"file": ("test.xml", test_content, "application/xml")}
    data = {"max_size_mb": 10}

    response = client.post("/v1/validate", files=files, data=data)
    assert response.status_code == 200

    result = response.json()

    # Should have findings from all levels, including warnings for missing resources
    findings = result["findings"]
    level_codes = [f["code"] for f in findings]

    # Should have XSD warnings (schema missing)
    # Should have Schematron warnings (rules missing)
    # WellFormed level doesn't produce findings for valid XML
    assert any("XSD:SCHEMA_MISSING" in code for code in level_codes)
    assert any("SCHEMATRON:RULES_MISSING" in code for code in level_codes)

    # Should have executed all levels
    levels_executed = result["validator"]["levels_executed"]
    assert "WellFormed" in levels_executed
    assert "XSD" in levels_executed
    assert "Schematron" in levels_executed
