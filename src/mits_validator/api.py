from __future__ import annotations

import os
import time
import uuid
from datetime import UTC, datetime
from typing import Any

import fastapi
import lxml
from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import JSONResponse

from mits_validator import __version__
from mits_validator.findings import create_finding
from mits_validator.profiles import get_profile
from mits_validator.validation import (
    ValidationEngine,
    ValidationRequest,
    ValidationResponse,
)

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


def _create_error_response(finding: dict[str, Any], status_code: int) -> JSONResponse:
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
            "source": "unknown",
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
        return _create_error_response(error_finding, 400)

    if not file and not url:
        error_finding = create_finding("INTAKE:NO_INPUTS")
        return _create_error_response(error_finding, 400)

    # Process file upload
    if file:
        return await _validate_file_upload(file, max_size_mb, start_time, profile)

    # Process URL
    if url:
        return await _validate_url(url, max_size_mb, start_time, profile)

    # This should never be reached
    raise HTTPException(status_code=500, detail="Internal error")


async def _validate_file_upload(
    file: UploadFile, max_size_mb: int, start_time: float, profile: str | None = None
) -> JSONResponse:
    """Validate file upload."""
    # Get validation profile
    validation_profile = get_profile(profile)

    # Check content type with profile-aware validation
    content_type = file.content_type or "application/octet-stream"
    if not _is_acceptable_content_type(content_type, validation_profile.allowed_content_types):
        error_finding = create_finding(
            "INTAKE:UNACCEPTABLE_CONTENT_TYPE",
            f"Content type '{content_type}' not allowed for profile '{validation_profile.name}'",
        )
        return _create_error_response(error_finding, 415)

    # Read and check file size with profile limits
    content = await file.read()
    size_bytes = len(content)
    max_size_bytes = min(max_size_mb, validation_profile.max_size_mb) * 1024 * 1024

    if size_bytes > max_size_bytes:
        error_finding = create_finding(
            "INTAKE:TOO_LARGE", f"File size {size_bytes} bytes exceeds limit {max_size_bytes} bytes"
        )
        return _create_error_response(error_finding, 413)

    # Create validation request
    validation_request = ValidationRequest(
        source="file",
        url=None,
        filename=file.filename,
        size_bytes=size_bytes,
        content_type=content_type,
    )

    # Initialize validation engine with profile
    engine = ValidationEngine(profile=profile)

    # Perform validation with all levels in profile
    results = engine.validate(content, content_type)

    # Build response
    response = ValidationResponse(
        input=validation_request,
        findings=_build_findings_from_results(results),
    )

    # Update validator info with profile data
    profile_info = engine.get_profile_info()
    response.validator.update(
        {
            "profile": profile_info["name"],
            "levels_executed": [result.level.value for result in results],
            "levels_available": engine.get_available_levels(),
        }
    )

    # Add request ID header
    return JSONResponse(
        content=response.model_dump(),
        headers={"X-Request-Id": response.metadata["request_id"], "Cache-Control": "no-store"},
    )


async def _validate_url(
    url: str, max_size_mb: int, start_time: float, profile: str | None = None
) -> JSONResponse:
    """Validate URL (intake only, no actual fetching yet)."""
    # Validate URL format with defensive error handling
    if not url.startswith(("http://", "https://")):
        error_finding = create_finding(
            "INTAKE:INVALID_URL", f"URL '{url}' must start with http:// or https://"
        )
        return _create_error_response(error_finding, 422)

    # Get validation profile (for future use)
    _ = get_profile(profile)

    # For now, just acknowledge URL intake without fetching
    # TODO: Implement actual URL fetching in future milestone
    validation_request = ValidationRequest(
        source="url",
        url=url,
        filename=None,
        size_bytes=0,  # Unknown until fetched
        content_type="application/xml",  # Assume XML for URLs
    )

    # Initialize validation engine with profile
    engine = ValidationEngine(profile=profile)

    # Create a minimal response for URL intake
    response = ValidationResponse(
        input=validation_request,
        findings=[
            {
                "level": "info",
                "code": "URL:INTAKE_ACKNOWLEDGED",
                "message": "URL intake acknowledged. Actual fetching not yet implemented.",
                "location": None,
                "rule_ref": "internal://URL",
            }
        ],
    )

    # Update validator info with profile data
    profile_info = engine.get_profile_info()
    response.validator.update(
        {
            "profile": profile_info["name"],
            "levels_executed": [],
            "levels_available": engine.get_available_levels(),
        }
    )

    return JSONResponse(
        content=response.model_dump(),
        headers={"X-Request-Id": response.metadata["request_id"], "Cache-Control": "no-store"},
    )


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


def _build_findings_from_results(results: list[Any]) -> list[dict[str, Any]]:
    """Convert validation results to findings format."""
    findings = []
    for result in results:
        for finding in result.findings:
            finding_dict = {
                "level": finding.level.value,
                "code": finding.code,
                "message": finding.message,
                "rule_ref": finding.rule_ref,
            }

            if finding.location:
                finding_dict["location"] = {
                    "line": finding.location.line,
                    "column": finding.location.column,
                    "xpath": finding.location.xpath,
                }
            else:
                finding_dict["location"] = None

            findings.append(finding_dict)

    return findings
