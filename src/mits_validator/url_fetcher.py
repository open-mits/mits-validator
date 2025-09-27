"""URL fetching functionality with streaming and error handling."""

from __future__ import annotations

import httpx

from mits_validator.models import Finding, FindingLevel


class URLFetcher:
    """Fetches content from URLs with streaming and error handling."""

    def __init__(
        self,
        timeout: float = 30.0,
        max_size: int = 10 * 1024 * 1024,  # 10MB default
        allowed_content_types: list[str] | None = None,
    ) -> None:
        self.timeout = timeout
        self.max_size = max_size
        self.allowed_content_types = allowed_content_types or [
            "application/xml",
            "text/xml",
            "application/octet-stream",
        ]

    def fetch(self, url: str) -> tuple[bytes, list[Finding]]:
        """Fetch content from URL with streaming and error handling."""
        findings: list[Finding] = []
        content = b""

        try:
            with httpx.stream(
                "GET",
                url,
                timeout=self.timeout,
                follow_redirects=False,  # Conservative approach
                headers={
                    "User-Agent": "MITS-Validator/1.0",
                    "Accept": "application/xml, text/xml, application/octet-stream",
                },
            ) as response:
                # Check HTTP status
                if response.status_code != 200:
                    findings.append(
                        Finding(
                            level=FindingLevel.ERROR,
                            code="NETWORK:HTTP_STATUS",
                            message=f"HTTP {response.status_code}: {response.reason_phrase}",
                            rule_ref="internal://URL",
                        )
                    )
                    return content, findings

                # Check content type
                content_type = response.headers.get("content-type", "").split(";")[0].strip()
                if content_type not in self.allowed_content_types:
                    if content_type.startswith("image/") or content_type.startswith("video/"):
                        findings.append(
                            Finding(
                                level=FindingLevel.ERROR,
                                code="INTAKE:UNSUPPORTED_MEDIA_TYPE",
                                message=f"Unsupported content type: {content_type}",
                                rule_ref="internal://URL",
                            )
                        )
                        return content, findings
                elif content_type == "application/octet-stream":
                    findings.append(
                        Finding(
                            level=FindingLevel.WARNING,
                            code="WELLFORMED:SUSPICIOUS_CONTENT_TYPE",
                            message=f"Suspicious content type: {content_type}",
                            rule_ref="internal://URL",
                        )
                    )

                # Stream content with size limit
                for chunk in response.iter_bytes():
                    content += chunk
                    if len(content) > self.max_size:
                        findings.append(
                            Finding(
                                level=FindingLevel.ERROR,
                                code="NETWORK:TOO_LARGE_DURING_STREAM",
                                message=f"Content exceeds size limit of {self.max_size} bytes",
                                rule_ref="internal://URL",
                            )
                        )
                        return content, findings

        except httpx.TimeoutException:
            findings.append(
                Finding(
                    level=FindingLevel.ERROR,
                    code="NETWORK:TIMEOUT",
                    message=f"Request timed out after {self.timeout} seconds",
                    rule_ref="internal://URL",
                )
            )
        except httpx.ConnectError as e:
            error_str = str(e).lower()
            if (
                "name or service not known" in error_str
                or "dns" in error_str
                or "name resolution" in error_str
            ):
                findings.append(
                    Finding(
                        level=FindingLevel.ERROR,
                        code="NETWORK:DNS_ERROR",
                        message="Failed to resolve domain name",
                        rule_ref="internal://URL",
                    )
                )
            else:
                findings.append(
                    Finding(
                        level=FindingLevel.ERROR,
                        code="NETWORK:CONNECTION_ERROR",
                        message="Failed to connect to the server",
                        rule_ref="internal://URL",
                    )
                )
        except httpx.RequestError as e:
            findings.append(
                Finding(
                    level=FindingLevel.ERROR,
                    code="NETWORK:REQUEST_ERROR",
                    message=f"Request failed: {e}",
                    rule_ref="internal://URL",
                )
            )
        except Exception as e:
            findings.append(
                Finding(
                    level=FindingLevel.ERROR,
                    code="NETWORK:FETCH_ERROR",
                    message=f"Unexpected error: {e}",
                    rule_ref="internal://URL",
                )
            )

        return content, findings


# Global fetcher instance
_url_fetcher: URLFetcher | None = None


def get_url_fetcher(
    timeout: float = 30.0,
    max_size: int = 10 * 1024 * 1024,
    allowed_content_types: list[str] | None = None,
) -> URLFetcher:
    """Get a singleton instance of the URLFetcher."""
    global _url_fetcher
    if _url_fetcher is None:
        _url_fetcher = URLFetcher(timeout, max_size, allowed_content_types)
    return _url_fetcher
