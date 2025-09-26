from __future__ import annotations

from fastapi.testclient import TestClient

from mits_validator.api import app

client = TestClient(app)


def test_health_endpoint() -> None:
    """Test health endpoint returns 200 with status=ok and version."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data
    assert isinstance(data["version"], str)
    assert len(data["version"]) > 0


def test_validate_both_file_and_url() -> None:
    """Test that providing both file and URL returns 400."""
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


def test_validate_neither_file_nor_url() -> None:
    """Test that providing neither file nor URL returns 400."""
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


def test_validate_valid_xml_file() -> None:
    """Test valid XML file returns 200 with valid=true."""
    test_content = b"<root><item>test</item></root>"
    files = {"file": ("test.xml", test_content, "application/xml")}
    data = {"max_size_mb": 10}

    response = client.post("/v1/validate", files=files, data=data)
    assert response.status_code == 200

    result = response.json()
    assert result["api_version"] == "1.0"
    assert result["input"]["source"] == "file"
    assert result["input"]["filename"] == "test.xml"
    assert result["input"]["size_bytes"] == len(test_content)
    assert result["input"]["content_type"] == "application/xml"
    assert result["summary"]["valid"] is True
    assert result["summary"]["errors"] == 0
    assert "WellFormed" in result["validator"]["levels_executed"]
    assert "request_id" in result["metadata"]
    assert "timestamp" in result["metadata"]
    assert "engine" in result["metadata"]


def test_validate_malformed_xml_file() -> None:
    """Test malformed XML returns 200 with valid=false and error finding."""
    test_content = b"<root><item>test</item></root"  # Missing closing tag
    files = {"file": ("test.xml", test_content, "application/xml")}
    data = {"max_size_mb": 10}

    response = client.post("/v1/validate", files=files, data=data)
    assert response.status_code == 200

    result = response.json()
    assert result["summary"]["valid"] is False
    assert result["summary"]["errors"] == 1
    # Should have multiple findings (WellFormed error + XSD/Schematron warnings)
    assert len(result["findings"]) >= 1

    # Find the WellFormed error
    wellformed_finding = next(
        f for f in result["findings"] if f["code"] == "WELLFORMED:PARSE_ERROR"
    )
    assert wellformed_finding["level"] == "error"
    assert "XML parsing failed" in wellformed_finding["message"]
    assert wellformed_finding["rule_ref"] == "internal://WellFormed"


def test_validate_url_intake() -> None:
    """Test URL intake returns 200 with appropriate response."""
    data = {"url": "https://example.com/feed.xml", "max_size_mb": 10}

    response = client.post("/v1/validate", data=data)
    assert response.status_code == 200

    result = response.json()
    assert result["input"]["source"] == "url"
    assert result["input"]["url"] == "https://example.com/feed.xml"
    assert result["input"]["content_type"] == "application/xml"
    assert len(result["findings"]) == 1
    assert result["findings"][0]["code"] == "URL:INTAKE_ACKNOWLEDGED"


def test_validate_invalid_url_format() -> None:
    """Test invalid URL format returns 422."""
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


def test_validate_file_size_limit() -> None:
    """Test file size limit enforcement."""
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


def test_validate_unacceptable_content_type() -> None:
    """Test unacceptable content type returns 415."""
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


def test_validate_content_type_warning() -> None:
    """Test suspicious content type generates warning."""
    test_content = b"<root>test</root>"
    files = {"file": ("test.xml", test_content, "application/octet-stream")}
    data = {"max_size_mb": 10}

    response = client.post("/v1/validate", files=files, data=data)
    assert response.status_code == 200

    result = response.json()
    assert result["summary"]["valid"] is True
    # Should have multiple warnings (content type + XSD/Schematron missing)
    assert result["summary"]["warnings"] >= 1

    # Find the content type warning
    content_type_warning = next(
        f for f in result["findings"] if f["code"] == "WELLFORMED:SUSPICIOUS_CONTENT_TYPE"
    )
    assert content_type_warning["level"] == "warning"
    assert "may not be XML" in content_type_warning["message"]


def test_response_headers() -> None:
    """Test response includes proper headers."""
    test_content = b"<root>test</root>"
    files = {"file": ("test.xml", test_content, "application/xml")}
    data = {"max_size_mb": 10}

    response = client.post("/v1/validate", files=files, data=data)
    assert response.status_code == 200

    # Check for request ID header
    assert "X-Request-Id" in response.headers
    assert "Cache-Control" in response.headers
    assert response.headers["Cache-Control"] == "no-store"


def test_result_envelope_structure() -> None:
    """Test result envelope has all required fields."""
    test_content = b"<root>test</root>"
    files = {"file": ("test.xml", test_content, "application/xml")}
    data = {"max_size_mb": 10}

    response = client.post("/v1/validate", files=files, data=data)
    assert response.status_code == 200

    result = response.json()

    # Check top-level fields
    assert "api_version" in result
    assert "validator" in result
    assert "input" in result
    assert "summary" in result
    assert "findings" in result
    assert "derived" in result
    assert "metadata" in result

    # Check validator fields
    validator = result["validator"]
    assert validator["name"] == "mits-validator"
    assert validator["spec_version"] == "unversioned"
    assert validator["profile"] == "default"
    assert "WellFormed" in validator["levels_executed"]

    # Check summary fields
    summary = result["summary"]
    assert "valid" in summary
    assert "errors" in summary
    assert "warnings" in summary
    assert "duration_ms" in summary

    # Check metadata fields
    metadata = result["metadata"]
    assert "request_id" in metadata
    assert "timestamp" in metadata
    assert "engine" in metadata
    assert "fastapi" in metadata["engine"]
    assert "lxml" in metadata["engine"]
