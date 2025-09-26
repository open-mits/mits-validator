from __future__ import annotations

import os
import time
from typing import Any

from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import JSONResponse

from mits_validator import __version__
from mits_validator.validation import (
    ValidationEngine,
    ValidationLevel,
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
) -> JSONResponse:
    """
    Validate MITS XML feed.

    Accepts either a file upload or URL (mutually exclusive).
    Performs minimal validation (XML well-formedness only).
    """
    start_time = time.time()

    # Validate input parameters
    if file and url:
        raise HTTPException(status_code=400, detail="Cannot provide both file and URL")

    if not file and not url:
        raise HTTPException(status_code=400, detail="Must provide either file or URL")

    # Process file upload
    if file:
        return await _validate_file_upload(file, max_size_mb, start_time)

    # Process URL
    if url:
        return await _validate_url(url, max_size_mb, start_time)

    # This should never be reached
    raise HTTPException(status_code=500, detail="Internal error")


async def _validate_file_upload(
    file: UploadFile, max_size_mb: int, start_time: float
) -> JSONResponse:
    """Validate file upload."""
    # Check content type
    content_type = file.content_type or "application/octet-stream"
    if not _is_acceptable_content_type(content_type):
        raise HTTPException(status_code=422, detail=f"Unacceptable content type: {content_type}")

    # Read and check file size
    content = await file.read()
    size_bytes = len(content)
    max_size_bytes = max_size_mb * 1024 * 1024

    if size_bytes > max_size_bytes:
        raise HTTPException(status_code=413, detail=f"File too large. Max size: {max_size_mb}MB")

    # Create validation request
    validation_request = ValidationRequest(
        source="file",
        url=None,
        filename=file.filename,
        size_bytes=size_bytes,
        content_type=content_type,
    )

    # Perform validation
    results = validation_engine.validate(content, content_type, [ValidationLevel.WELLFORMED])

    # Build response
    response = ValidationResponse(
        input=validation_request, findings=_build_findings_from_results(results)
    )

    # Add request ID header
    return JSONResponse(
        content=response.model_dump(),
        headers={"X-Request-Id": response.metadata["request_id"], "Cache-Control": "no-store"},
    )


async def _validate_url(url: str, max_size_mb: int, start_time: float) -> JSONResponse:
    """Validate URL (intake only, no actual fetching yet)."""
    # Validate URL format
    if not url.startswith(("http://", "https://")):
        raise HTTPException(
            status_code=422, detail="Invalid URL format. Must start with http:// or https://"
        )

    # For now, just acknowledge URL intake without fetching
    # TODO: Implement actual URL fetching in future milestone
    validation_request = ValidationRequest(
        source="url",
        url=url,
        filename=None,
        size_bytes=0,  # Unknown until fetched
        content_type="application/xml",  # Assume XML for URLs
    )

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

    return JSONResponse(
        content=response.model_dump(),
        headers={"X-Request-Id": response.metadata["request_id"], "Cache-Control": "no-store"},
    )


def _is_acceptable_content_type(content_type: str) -> bool:
    """Check if content type is acceptable for XML validation."""
    acceptable_types = [
        "application/xml",
        "text/xml",
        "application/octet-stream",  # Allow with warning
        "text/plain",  # Allow with warning
    ]
    return any(ct in content_type.lower() for ct in acceptable_types)


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
