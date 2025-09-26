from __future__ import annotations

import httpx
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from pydantic import BaseModel, Field

from mits_validator import __version__

# Create default values to avoid B008 error
DEFAULT_FILE = File(None)
DEFAULT_FORM = Form(None)
DEFAULT_SIZE = Form(10)

app = FastAPI(
    title="MITS Validator API",
    version=__version__,
    docs_url="/docs",
    redoc_url="/redoc",
)


class ValidationRequest(BaseModel):
    """Request model for validation endpoint."""

    url: str | None = Field(None, description="URL to validate")
    max_size_mb: int = Field(10, description="Maximum file size in MB")


class ValidationResponse(BaseModel):
    """Response model for validation endpoint."""

    input_type: str
    size_bytes: int | None = None
    status: str = "stub"
    message: str = "Validation not yet implemented"


@app.get("/health")
def health() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok", "version": __version__}


@app.post("/v1/validate", response_model=ValidationResponse)
async def validate(
    file: UploadFile | None = DEFAULT_FILE,
    url: str | None = DEFAULT_FORM,
    max_size_mb: int = DEFAULT_SIZE,
) -> ValidationResponse:
    """
    Validate MITS XML feed.

    Accepts either a file upload or URL (mutually exclusive).
    Currently returns a stub response.
    """
    if file and url:
        raise HTTPException(status_code=400, detail="Cannot provide both file and URL")

    if not file and not url:
        raise HTTPException(status_code=400, detail="Must provide either file or URL")

    if file:
        # Check file size
        content = await file.read()
        size_bytes = len(content)
        max_size_bytes = max_size_mb * 1024 * 1024

        if size_bytes > max_size_bytes:
            raise HTTPException(
                status_code=413, detail=f"File too large. Max size: {max_size_mb}MB"
            )

        return ValidationResponse(
            input_type="file",
            size_bytes=size_bytes,
            message=f"File validation stub - {file.filename}",
        )

    if url:
        # Basic URL validation
        if not url.startswith(("http://", "https://")):
            raise HTTPException(status_code=400, detail="Invalid URL format")

        try:
            async with httpx.AsyncClient() as client:
                response = await client.head(url, timeout=30.0)
                if response.status_code >= 400:
                    raise HTTPException(status_code=400, detail="URL not accessible")
        except httpx.RequestError as e:
            raise HTTPException(status_code=400, detail=f"URL request failed: {str(e)}") from e

        return ValidationResponse(input_type="url", message=f"URL validation stub - {url}")

    # This should never be reached due to validation above
    raise HTTPException(status_code=500, detail="Internal error")
