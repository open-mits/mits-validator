from __future__ import annotations

import os
import time
import uuid
from datetime import UTC, datetime
from typing import Any

import fastapi
import httpx
import lxml
from fastapi import FastAPI, File, Form, HTTPException, Query, Request, UploadFile
from fastapi.responses import JSONResponse

from mits_validator import __version__
from mits_validator.alerting import get_alert_manager
from mits_validator.async_validation import get_async_validation_engine
from mits_validator.findings import create_finding
from mits_validator.health_checks import check_system_health
from mits_validator.metrics import get_metrics_collector
from mits_validator.models import FindingLevel, ValidationRequest, ValidationResponse
from mits_validator.profiles import get_profile
from mits_validator.streaming_parser import MemoryOptimizedValidator
from mits_validator.validation_engine import ValidationEngine, build_v1_envelope

# Create default values to avoid B008 error
DEFAULT_FILE = File(None)
DEFAULT_FORM = Form(None)
DEFAULT_SIZE = Form(10)

# Configuration
MAX_UPLOAD_BYTES = int(os.getenv("MAX_UPLOAD_BYTES", "10485760"))  # 10MB default
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "30"))  # 30 seconds default

app = FastAPI(
    title="MITS Validator API",
    version=__version__,
    docs_url="/docs",
    redoc_url="/redoc",
    description="Professional validator for MITS (Property Marketing / ILS) XML feeds",
    tags_metadata=[
        {
            "name": "health",
            "description": "Health check and service status",
        },
        {
            "name": "validation",
            "description": "XML feed validation endpoints",
        },
    ],
)

# Initialize validation engine
validation_engine = ValidationEngine()


def _create_error_response(
    finding: dict[str, Any], status_code: int, source: str = "unknown"
) -> JSONResponse:
    """Create a standardized error response with result envelope."""
    response_data: dict[str, Any] = {
        "api_version": "1.0",
        "validator": {
            "name": "mits-validator",
            "spec_version": "unversioned",
            "profile": "default",
            "levels_executed": [],
            "levels_available": validation_engine.get_available_levels(),
        },
        "input": {
            "source": source,
            "url": None,
            "filename": None,
            "size_bytes": 0,
            "content_type": "unknown",
        },
        "summary": {
            "valid": False,
            "errors": 1 if finding["level"] == "error" else 0,
            "warnings": 1 if finding["level"] == "warning" else 0,
            "duration_ms": 0,
        },
        "findings": [finding],
        "derived": {},
        "metadata": {
            "request_id": str(uuid.uuid4()),
            "timestamp": datetime.now(UTC).isoformat(),
            "engine": {"fastapi": fastapi.__version__, "lxml": lxml.__version__},
        },
    }

    request_id = str(response_data["metadata"]["request_id"])
    headers: dict[str, str] = {
        "X-Request-Id": request_id,
        "Cache-Control": "no-store",
    }
    return JSONResponse(
        content=response_data,
        status_code=status_code,
        headers=headers,
    )


@app.get(
    "/health",
    tags=["health"],
    summary="Health Check",
    description="Check service health and version information",
    response_description="Service status and version",
)
def health() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok", "version": __version__}


@app.get(
    "/metrics",
    tags=["monitoring"],
    summary="Prometheus Metrics",
    description="Prometheus metrics endpoint for monitoring",
    response_description="Prometheus metrics in text format",
)
def metrics() -> str:
    """Prometheus metrics endpoint."""
    metrics_collector = get_metrics_collector()
    return metrics_collector.get_metrics()


@app.get(
    "/health/detailed",
    tags=["health"],
    summary="Detailed Health Check",
    description="Comprehensive health check including dependencies",
    response_description="Detailed health status",
)
async def detailed_health(
    checks: str = Query(None, description="Comma-separated list of checks to run"),
):
    """Detailed health check endpoint."""
    check_list = checks.split(",") if checks else None
    return await check_system_health(check_list)


@app.post(
    "/v1/validate/async",
    response_model=ValidationResponse,
    tags=["validation"],
    summary="Async XML Validation",
    description="Validate MITS XML feed asynchronously for large files",
    response_description="Async validation results",
)
async def validate_async(
    request: Request,
    file: UploadFile = DEFAULT_FILE,
    url: str = Query(None, description="URL to fetch XML from"),
    profile: str = Query("default", description="Validation profile to use"),
    max_memory_mb: int = Query(100, description="Maximum memory usage in MB"),
):
    """Async validation endpoint for large files."""
    # Validate input
    if file is None and url is None:
        raise HTTPException(
            status_code=400, detail={"error": "Either file or url must be provided"}
        )

    if file is not None and url is not None:
        raise HTTPException(status_code=400, detail={"error": "Cannot provide both file and url"})

    # Get content
    if file is not None:
        content = await file.read()
        content_type = file.content_type or "application/xml"
    else:
        # Fetch from URL
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            content = response.content
            content_type = response.headers.get("content-type", "application/xml")

    # Create validation request
    validation_request = ValidationRequest(
        content=content.decode("utf-8") if isinstance(content, bytes) else content,
        content_type=content_type,
    )

    # Generate validation ID
    validation_id = f"async_{int(time.time())}_{hash(content) % 10000}"

    # Use memory-optimized validator for large files
    if len(content) > 10 * 1024 * 1024:  # 10MB threshold
        validator = MemoryOptimizedValidator(max_memory_mb=max_memory_mb)
        result = await validator.validate_large_file(content)

        # Convert to ValidationResponse format
        return ValidationResponse(
            summary={
                "valid": result["valid"],
                "total_findings": len(result["findings"]),
                "errors": result.get("error_count", 0),
                "warnings": result.get("warning_count", 0),
            },
            findings=result["findings"],
            metadata={
                "validation_id": validation_id,
                "profile": profile,
                "memory_usage": result.get("memory_usage", {}),
                "validation_levels": result.get("validation_levels", []),
            },
        )
    else:
        # Use async validation engine for smaller files
        async_engine = get_async_validation_engine()
        result = await async_engine.validate_async(validation_request, validation_id, profile)

        # Convert to ValidationResponse format
        return ValidationResponse(
            summary={
                "valid": result.valid,
                "total_findings": len(result.findings),
                "errors": len([f for f in result.findings if f.level == FindingLevel.ERROR]),
                "warnings": len([f for f in result.findings if f.level == FindingLevel.WARNING]),
            },
            findings=[
                {
                    "level": f.level.value,
                    "code": f.code,
                    "message": f.message,
                    "location": f.location.__dict__ if f.location else None,
                }
                for f in result.findings
            ],
            metadata=result.metadata,
        )


@app.get(
    "/alerts",
    tags=["monitoring"],
    summary="Get Active Alerts",
    description="Get list of active alerts",
    response_description="List of active alerts",
)
async def get_alerts():
    """Get active alerts."""
    alert_manager = get_alert_manager()
    return {
        "active_alerts": alert_manager.get_active_alerts(),
        "alert_stats": alert_manager.get_alert_stats(),
    }


@app.post(
    "/alerts/resolve/{alert_type}",
    tags=["monitoring"],
    summary="Resolve Alert",
    description="Resolve a specific alert",
    response_description="Alert resolution status",
)
async def resolve_alert(alert_type: str):
    """Resolve an alert."""
    alert_manager = get_alert_manager()
    resolved = await alert_manager.resolve_alert(alert_type)

    if resolved:
        return {"message": f"Alert {alert_type} resolved", "resolved": True}
    else:
        raise HTTPException(status_code=404, detail={"error": f"Alert {alert_type} not found"})


@app.post(
    "/v1/validate",
    response_model=ValidationResponse,
    tags=["validation"],
    summary="Validate XML Feed",
    description="Validate MITS XML feed for well-formedness and basic structure",
    response_description="Structured validation results with findings",
)
async def validate(
    request: Request,
    file: UploadFile | None = DEFAULT_FILE,
    url: str | None = DEFAULT_FORM,
    max_size_mb: int = DEFAULT_SIZE,
    profile: str | None = None,
    mode: str = Query("xsd", description="Validation mode: xsd, schematron, or both"),
) -> JSONResponse:
    """
    Validate MITS XML feed.

    Accepts either a file upload or URL (mutually exclusive).
    Performs minimal validation (XML well-formedness only).
    """
    start_time = time.time()

    # Get validation profile (for future use)
    _ = get_profile(profile)

    # Validate input parameters with defensive error handling
    if file and url:
        error_finding = create_finding("INTAKE:BOTH_INPUTS")
        return _create_error_response(error_finding, 400, "file")

    if not file and not url:
        error_finding = create_finding("INTAKE:NO_INPUTS")
        return _create_error_response(error_finding, 400, "unknown")

    # Process file upload
    if file:
        return await _validate_file_upload(file, max_size_mb, start_time, profile)

    # Process URL
    if url:
        return await _validate_url(url, max_size_mb, start_time, profile)

    # This should never be reached
    raise HTTPException(status_code=500, detail="Internal error")


async def _validate_file_upload(
    file: UploadFile,
    max_size_mb: int,
    start_time: float,
    profile: str | None = None,
    mode: str = "xsd",
) -> JSONResponse:
    """Validate file upload."""
    # Get validation profile
    validation_profile = get_profile(profile)

    # Check content type with profile-aware validation
    content_type = file.content_type or "application/octet-stream"
    if not _is_acceptable_content_type(content_type, validation_profile.allowed_content_types):
        error_finding = create_finding(
            "INTAKE:UNSUPPORTED_MEDIA_TYPE",
            f"Content type '{content_type}' not allowed for profile '{validation_profile.name}'",
        )
        return _create_error_response(error_finding, 415, "file")

    # Generate warning for suspicious content types
    suspicious_types = ["application/octet-stream", "text/plain"]
    if content_type.lower() in suspicious_types:
        # This warning will be added to the validation results
        pass  # Warning will be generated during validation

    # Read and check file size with profile limits
    content = await file.read()
    size_bytes = len(content)
    max_size_bytes = min(max_size_mb, validation_profile.max_size_mb) * 1024 * 1024

    if size_bytes > max_size_bytes:
        error_finding = create_finding(
            "INTAKE:TOO_LARGE", f"File size {size_bytes} bytes exceeds limit {max_size_bytes} bytes"
        )
        return _create_error_response(error_finding, 413, "file")

    # Create validation request
    validation_request = ValidationRequest(
        content=content,
        content_type=content_type,
        source="file",
        url=None,
        filename=file.filename,
        size_bytes=size_bytes,
    )

    # Initialize validation engine with profile
    engine = ValidationEngine(profile=profile)

    # Perform validation with all levels in profile
    results = engine.validate(content, content_type=content_type)

    # Build v1 envelope
    duration_ms = int((time.time() - start_time) * 1000)
    response_data = build_v1_envelope(
        validation_request, results, profile or "default", duration_ms
    )

    # Add request ID header
    return JSONResponse(
        content=response_data,
        headers={
            "X-Request-Id": response_data["metadata"]["request_id"],
            "Cache-Control": "no-store",
        },
    )


async def _validate_url(
    url: str, max_size_mb: int, start_time: float, profile: str | None = None, mode: str = "xsd"
) -> JSONResponse:
    """Validate URL (intake only, no actual fetching yet)."""
    # Validate URL format with defensive error handling
    if not url.startswith(("http://", "https://")):
        error_finding = create_finding(
            "INTAKE:INVALID_URL", f"URL '{url}' must start with http:// or https://"
        )
        return _create_error_response(error_finding, 422, "url")

    # Get validation profile (for future use)
    _ = get_profile(profile)

    # Fetch URL content with network error handling
    try:
        content, content_type, size_bytes = await _fetch_url_content(url, max_size_mb)

        # Create validation request with fetched content
        validation_request = ValidationRequest(
            content=content,
            content_type=content_type,
            source="url",
            url=url,
            filename=None,
            size_bytes=size_bytes,
        )

        # Initialize validation engine with profile
        engine = ValidationEngine(profile=profile)

        # Perform validation with all levels in profile
        results = engine.validate(content, content_type=content_type)

        # Build v1 envelope
        duration_ms = int((time.time() - start_time) * 1000)
        response_data = build_v1_envelope(
            validation_request, results, profile or "default", duration_ms
        )

    except Exception as e:
        # Network or other error occurred
        error_finding = create_finding("NETWORK:FETCH_ERROR", f"Failed to fetch URL: {str(e)}")
        return _create_error_response(error_finding, 502, "url")

    return JSONResponse(
        content=response_data,
        headers={
            "X-Request-Id": response_data["metadata"]["request_id"],
            "Cache-Control": "no-store",
        },
    )


async def _fetch_url_content(url: str, max_size_mb: int) -> tuple[bytes, str, int]:
    """Fetch URL content with size limits and timeout handling."""
    max_size_bytes = max_size_mb * 1024 * 1024
    timeout = httpx.Timeout(connect=10.0, read=30.0, write=10.0, pool=5.0)

    async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
        try:
            async with client.stream("GET", url) as response:
                # Check HTTP status
                if response.status_code >= 400:
                    raise httpx.HTTPStatusError(
                        f"HTTP {response.status_code}", request=response.request, response=response
                    )

                # Get content type
                content_type = response.headers.get("content-type", "application/octet-stream")

                # Stream content with size limit
                content = b""
                async for chunk in response.aiter_bytes():
                    content += chunk
                    if len(content) > max_size_bytes:
                        raise httpx.RequestError(
                            f"Content size exceeds limit of {max_size_bytes} bytes"
                        )

                return content, content_type, len(content)

        except httpx.TimeoutException as e:
            raise Exception(f"NETWORK:TIMEOUT - Request timed out: {str(e)}") from e
        except httpx.ConnectError as e:
            raise Exception(f"NETWORK:CONNECTION_ERROR - Connection failed: {str(e)}") from e
        except httpx.HTTPStatusError as e:
            raise Exception(f"NETWORK:HTTP_STATUS - HTTP {e.response.status_code}: {str(e)}") from e
        except httpx.RequestError as e:
            raise Exception(f"NETWORK:REQUEST_ERROR - {str(e)}") from e


def _is_acceptable_content_type(content_type: str, allowed_types: list[str] | None = None) -> bool:
    """Check if content type is acceptable for XML validation."""
    if allowed_types is None:
        allowed_types = [
            "application/xml",
            "text/xml",
            "application/octet-stream",  # Allow with warning
            "text/plain",  # Allow with warning
        ]
    return any(ct in content_type.lower() for ct in allowed_types)
