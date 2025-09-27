"""Tests for URL fetcher functionality."""

from unittest.mock import patch

import httpx

from mits_validator.models import FindingLevel
from mits_validator.url_fetcher import URLFetcher, get_url_fetcher


class TestURLFetcher:
    """Test URL fetcher functionality."""

    def test_fetch_success(self) -> None:
        """Test successful URL fetching."""
        fetcher = URLFetcher(timeout=5.0, max_size=1024)

        with patch("httpx.stream") as mock_stream:
            # Mock successful response
            mock_response = httpx.Response(
                200,
                headers={"content-type": "application/xml"},
                content=b"<?xml version='1.0'?><root>test</root>",
            )
            mock_stream.return_value.__enter__.return_value = mock_response
            mock_stream.return_value.__exit__.return_value = None

            content, findings = fetcher.fetch("http://example.com/test.xml")

            assert content == b"<?xml version='1.0'?><root>test</root>"
            assert len(findings) == 0

    def test_fetch_http_error(self) -> None:
        """Test URL fetching with HTTP error."""
        fetcher = URLFetcher(timeout=5.0, max_size=1024)

        with patch("httpx.stream") as mock_stream:
            # Mock HTTP error response
            mock_response = httpx.Response(
                404,
                headers={"content-type": "application/xml"},
                content=b"Not Found",
            )
            mock_stream.return_value.__enter__.return_value = mock_response
            mock_stream.return_value.__exit__.return_value = None

            content, findings = fetcher.fetch("http://example.com/notfound.xml")

            assert content == b""
            assert len(findings) == 1
            assert findings[0].code == "NETWORK:HTTP_STATUS"
            assert findings[0].level == FindingLevel.ERROR

    def test_fetch_timeout(self) -> None:
        """Test URL fetching with timeout."""
        fetcher = URLFetcher(timeout=1.0, max_size=1024)

        with patch("httpx.stream") as mock_stream:
            mock_stream.side_effect = httpx.TimeoutException("Request timed out")

            content, findings = fetcher.fetch("http://example.com/slow.xml")

            assert content == b""
            assert len(findings) == 1
            assert findings[0].code == "NETWORK:TIMEOUT"
            assert findings[0].level == FindingLevel.ERROR

    def test_fetch_connection_error(self) -> None:
        """Test URL fetching with connection error."""
        fetcher = URLFetcher(timeout=5.0, max_size=1024)

        with patch("httpx.stream") as mock_stream:
            mock_stream.side_effect = httpx.ConnectError("Connection failed")

            content, findings = fetcher.fetch("http://unreachable.com/test.xml")

            assert content == b""
            assert len(findings) == 1
            assert findings[0].code == "NETWORK:CONNECTION_ERROR"
            assert findings[0].level == FindingLevel.ERROR

    def test_fetch_dns_error(self) -> None:
        """Test URL fetching with DNS error."""
        fetcher = URLFetcher(timeout=5.0, max_size=1024)

        with patch("httpx.stream") as mock_stream:
            mock_stream.side_effect = httpx.ConnectError("Name or service not known")

            content, findings = fetcher.fetch("http://nonexistent.invalid/test.xml")

            assert content == b""
            assert len(findings) == 1
            assert findings[0].code == "NETWORK:DNS_ERROR"
            assert findings[0].level == FindingLevel.ERROR

    def test_fetch_request_error(self) -> None:
        """Test URL fetching with request error."""
        fetcher = URLFetcher(timeout=5.0, max_size=1024)

        with patch("httpx.stream") as mock_stream:
            # Mock the context manager to raise RequestError
            mock_context = mock_stream.return_value.__enter__
            mock_context.side_effect = httpx.RequestError("Request failed")

            content, findings = fetcher.fetch("http://example.com/test.xml")

            assert content == b""
            assert len(findings) == 1
            assert findings[0].code == "NETWORK:REQUEST_ERROR"
            assert findings[0].level == FindingLevel.ERROR

    def test_fetch_unsupported_content_type(self) -> None:
        """Test URL fetching with unsupported content type."""
        fetcher = URLFetcher(timeout=5.0, max_size=1024)

        with patch("httpx.stream") as mock_stream:
            # Mock response with image content type
            mock_response = httpx.Response(
                200,
                headers={"content-type": "image/jpeg"},
                content=b"fake image data",
            )
            mock_stream.return_value.__enter__.return_value = mock_response
            mock_stream.return_value.__exit__.return_value = None

            content, findings = fetcher.fetch("http://example.com/image.jpg")

            assert content == b""
            assert len(findings) == 1
            assert findings[0].code == "INTAKE:UNSUPPORTED_MEDIA_TYPE"
            assert findings[0].level == FindingLevel.ERROR

    def test_fetch_suspicious_content_type(self) -> None:
        """Test URL fetching with suspicious content type."""
        fetcher = URLFetcher(timeout=5.0, max_size=1024)

        with patch("httpx.stream") as mock_stream:
            # Mock response with octet-stream content type
            mock_response = httpx.Response(
                200,
                headers={"content-type": "application/octet-stream"},
                content=b"<?xml version='1.0'?><root>test</root>",
            )
            mock_stream.return_value.__enter__.return_value = mock_response
            mock_stream.return_value.__exit__.return_value = None

            content, findings = fetcher.fetch("http://example.com/test.xml")

            assert content == b"<?xml version='1.0'?><root>test</root>"
            assert len(findings) == 1
            assert findings[0].code == "WELLFORMED:SUSPICIOUS_CONTENT_TYPE"
            assert findings[0].level == FindingLevel.WARNING

    def test_fetch_size_limit_exceeded(self) -> None:
        """Test URL fetching with size limit exceeded."""
        fetcher = URLFetcher(timeout=5.0, max_size=10)  # Very small limit

        with patch("httpx.stream") as mock_stream:
            # Mock response with large content
            mock_response = httpx.Response(
                200,
                headers={"content-type": "application/xml"},
                content=b"x" * 20,  # Exceeds 10 byte limit
            )
            mock_stream.return_value.__enter__.return_value = mock_response
            mock_stream.return_value.__exit__.return_value = None

            content, findings = fetcher.fetch("http://example.com/large.xml")

            assert content == b"x" * 20  # Content is still returned
            assert len(findings) == 1
            assert findings[0].code == "NETWORK:TOO_LARGE_DURING_STREAM"
            assert findings[0].level == FindingLevel.ERROR

    def test_fetch_unexpected_error(self) -> None:
        """Test URL fetching with unexpected error."""
        fetcher = URLFetcher(timeout=5.0, max_size=1024)

        with patch("httpx.stream") as mock_stream:
            # Mock the context manager to raise Exception
            mock_context = mock_stream.return_value.__enter__
            mock_context.side_effect = Exception("Unexpected error")

            content, findings = fetcher.fetch("http://example.com/test.xml")

            assert content == b""
            assert len(findings) == 1
            assert findings[0].code == "NETWORK:FETCH_ERROR"
            assert findings[0].level == FindingLevel.ERROR

    def test_get_url_fetcher_singleton(self) -> None:
        """Test that get_url_fetcher returns a singleton."""
        fetcher1 = get_url_fetcher()
        fetcher2 = get_url_fetcher()

        assert fetcher1 is fetcher2

    def test_fetcher_configuration(self) -> None:
        """Test fetcher configuration."""
        fetcher = URLFetcher(
            timeout=10.0, max_size=2048, allowed_content_types=["application/xml", "text/xml"]
        )

        assert fetcher.timeout == 10.0
        assert fetcher.max_size == 2048
        assert fetcher.allowed_content_types == ["application/xml", "text/xml"]
