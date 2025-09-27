# API Examples & Interactive Guide

This document provides comprehensive examples for using the MITS Validator API with different programming languages and tools.

## Table of Contents

- [Quick Start Examples](#quick-start-examples)
- [Python Examples](#python-examples)
- [JavaScript/Node.js Examples](#javascriptnodejs-examples)
- [cURL Examples](#curl-examples)
- [Postman Collection](#postman-collection)
- [Error Handling Examples](#error-handling-examples)
- [Advanced Usage](#advanced-usage)

## Quick Start Examples

### 1. Validate a Local File

```bash
# Using cURL
curl -X POST \
  -F "file=@sample-feed.xml" \
  http://localhost:8000/v1/validate

# Using Python
import requests

with open('sample-feed.xml', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/v1/validate',
        files={'file': f}
    )
    print(response.json())
```

### 2. Validate a Remote URL

```bash
# Using cURL
curl -X POST \
  -d "url=https://example.com/feed.xml" \
  http://localhost:8000/v1/validate

# Using Python
import requests

response = requests.post(
    'http://localhost:8000/v1/validate',
    data={'url': 'https://example.com/feed.xml'}
)
print(response.json())
```

### 3. Health Check

```bash
# Using cURL
curl http://localhost:8000/health

# Using Python
import requests

response = requests.get('http://localhost:8000/health')
print(response.json())
```

## Python Examples

### Basic Client Class

```python
import httpx
import json
from typing import Dict, Any, Optional
from pathlib import Path

class MITSValidatorClient:
    """Client for MITS Validator API."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.Client(timeout=30.0)

    def validate_file(
        self,
        file_path: str,
        profile: str = "default",
        levels: Optional[str] = None
    ) -> Dict[str, Any]:
        """Validate a local file."""
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        with open(file_path, 'rb') as f:
            files = {'file': f}
            data = {'profile': profile}
            if levels:
                data['levels'] = levels

            response = self.client.post(
                f"{self.base_url}/v1/validate",
                files=files,
                data=data
            )
            response.raise_for_status()
            return response.json()

    def validate_url(
        self,
        url: str,
        profile: str = "default",
        levels: Optional[str] = None
    ) -> Dict[str, Any]:
        """Validate a remote URL."""
        data = {'url': url, 'profile': profile}
        if levels:
            data['levels'] = levels

        response = self.client.post(
            f"{self.base_url}/v1/validate",
            data=data
        )
        response.raise_for_status()
        return response.json()

    def health_check(self) -> Dict[str, Any]:
        """Check service health."""
        response = self.client.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()

    def close(self):
        """Close the client."""
        self.client.close()

# Usage examples
def main():
    client = MITSValidatorClient()

    try:
        # Health check
        health = client.health_check()
        print(f"Service status: {health['status']}")

        # Validate a file
        result = client.validate_file("sample-feed.xml", profile="pms-publisher")
        print(f"Validation result: {result['summary']['valid']}")

        # Validate a URL
        result = client.validate_url("https://example.com/feed.xml")
        print(f"URL validation: {result['summary']['valid']}")

    finally:
        client.close()

if __name__ == "__main__":
    main()
```

### Async Client

```python
import asyncio
import aiohttp
import aiofiles
from typing import Dict, Any, Optional

class AsyncMITSValidatorClient:
    """Async client for MITS Validator API."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def validate_file(
        self,
        file_path: str,
        profile: str = "default",
        levels: Optional[str] = None
    ) -> Dict[str, Any]:
        """Validate a local file asynchronously."""
        data = aiohttp.FormData()
        data.add_field('profile', profile)
        if levels:
            data.add_field('levels', levels)

        async with aiofiles.open(file_path, 'rb') as f:
            content = await f.read()
            data.add_field('file', content, filename=file_path)

            async with self.session.post(
                f"{self.base_url}/v1/validate",
                data=data
            ) as response:
                response.raise_for_status()
                return await response.json()

    async def validate_url(
        self,
        url: str,
        profile: str = "default",
        levels: Optional[str] = None
    ) -> Dict[str, Any]:
        """Validate a remote URL asynchronously."""
        data = {
            'url': url,
            'profile': profile
        }
        if levels:
            data['levels'] = levels

        async with self.session.post(
            f"{self.base_url}/v1/validate",
            data=data
        ) as response:
            response.raise_for_status()
            return await response.json()

    async def health_check(self) -> Dict[str, Any]:
        """Check service health."""
        async with self.session.get(f"{self.base_url}/health") as response:
            response.raise_for_status()
            return await response.json()

# Usage
async def main():
    async with AsyncMITSValidatorClient() as client:
        # Health check
        health = await client.health_check()
        print(f"Service status: {health['status']}")

        # Validate multiple files concurrently
        tasks = [
            client.validate_file("feed1.xml"),
            client.validate_file("feed2.xml"),
            client.validate_url("https://example.com/feed.xml")
        ]

        results = await asyncio.gather(*tasks)
        for i, result in enumerate(results):
            print(f"Result {i+1}: {result['summary']['valid']}")

if __name__ == "__main__":
    asyncio.run(main())
```

### Batch Processing

```python
import asyncio
from pathlib import Path
from typing import List, Dict, Any

async def validate_multiple_files(
    file_paths: List[str],
    profile: str = "default"
) -> List[Dict[str, Any]]:
    """Validate multiple files concurrently."""
    async with AsyncMITSValidatorClient() as client:
        tasks = [
            client.validate_file(file_path, profile)
            for file_path in file_paths
        ]
        return await asyncio.gather(*tasks)

def process_validation_results(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Process and summarize validation results."""
    total_files = len(results)
    valid_files = sum(1 for r in results if r['summary']['valid'])
    total_findings = sum(r['summary']['total_findings'] for r in results)

    return {
        'total_files': total_files,
        'valid_files': valid_files,
        'invalid_files': total_files - valid_files,
        'total_findings': total_findings,
        'success_rate': valid_files / total_files if total_files > 0 else 0
    }

# Usage
async def main():
    file_paths = [
        "feed1.xml",
        "feed2.xml",
        "feed3.xml"
    ]

    results = await validate_multiple_files(file_paths, profile="pms-publisher")
    summary = process_validation_results(results)

    print(f"Processed {summary['total_files']} files")
    print(f"Valid: {summary['valid_files']}")
    print(f"Invalid: {summary['invalid_files']}")
    print(f"Success rate: {summary['success_rate']:.2%}")

if __name__ == "__main__":
    asyncio.run(main())
```

## JavaScript/Node.js Examples

### Basic Client

```javascript
const FormData = require('form-data');
const fetch = require('node-fetch');
const fs = require('fs');

class MITSValidatorClient {
    constructor(baseUrl = 'http://localhost:8000') {
        this.baseUrl = baseUrl;
    }

    async validateFile(filePath, profile = 'default', levels = null) {
        const form = new FormData();
        form.append('file', fs.createReadStream(filePath));
        form.append('profile', profile);
        if (levels) {
            form.append('levels', levels);
        }

        const response = await fetch(`${this.baseUrl}/v1/validate`, {
            method: 'POST',
            body: form
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();
    }

    async validateUrl(url, profile = 'default', levels = null) {
        const form = new FormData();
        form.append('url', url);
        form.append('profile', profile);
        if (levels) {
            form.append('levels', levels);
        }

        const response = await fetch(`${this.baseUrl}/v1/validate`, {
            method: 'POST',
            body: form
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();
    }

    async healthCheck() {
        const response = await fetch(`${this.baseUrl}/health`);

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();
    }
}

// Usage
async function main() {
    const client = new MITSValidatorClient();

    try {
        // Health check
        const health = await client.healthCheck();
        console.log(`Service status: ${health.status}`);

        // Validate a file
        const result = await client.validateFile('sample-feed.xml', 'pms-publisher');
        console.log(`Validation result: ${result.summary.valid}`);

        // Validate a URL
        const urlResult = await client.validateUrl('https://example.com/feed.xml');
        console.log(`URL validation: ${urlResult.summary.valid}`);

    } catch (error) {
        console.error('Error:', error.message);
    }
}

main();
```

### Express.js Integration

```javascript
const express = require('express');
const multer = require('multer');
const { MITSValidatorClient } = require('./mits-validator-client');

const app = express();
const upload = multer({ dest: 'uploads/' });
const validator = new MITSValidatorClient();

// Middleware for file upload
app.post('/validate-upload', upload.single('file'), async (req, res) => {
    try {
        const result = await validator.validateFile(req.file.path);
        res.json(result);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Middleware for URL validation
app.post('/validate-url', express.urlencoded({ extended: true }), async (req, res) => {
    try {
        const { url, profile } = req.body;
        const result = await validator.validateUrl(url, profile);
        res.json(result);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

app.listen(3000, () => {
    console.log('Server running on port 3000');
});
```

## cURL Examples

### Basic Validation

```bash
# Validate a file
curl -X POST \
  -F "file=@sample-feed.xml" \
  http://localhost:8000/v1/validate

# Validate a URL
curl -X POST \
  -d "url=https://example.com/feed.xml" \
  http://localhost:8000/v1/validate

# Health check
curl http://localhost:8000/health
```

### Advanced Usage

```bash
# Validate with specific profile
curl -X POST \
  -F "file=@sample-feed.xml" \
  -F "profile=pms-publisher" \
  http://localhost:8000/v1/validate

# Validate with specific levels
curl -X POST \
  -F "file=@sample-feed.xml" \
  "http://localhost:8000/v1/validate?levels=WellFormed,XSD"

# Validate with custom headers
curl -X POST \
  -F "file=@sample-feed.xml" \
  -H "X-Profile: ils-receiver" \
  -H "X-Request-Id: custom-123" \
  http://localhost:8000/v1/validate

# Get detailed output
curl -X POST \
  -F "file=@sample-feed.xml" \
  -H "Accept: application/json" \
  http://localhost:8000/v1/validate | jq '.'

# Save response to file
curl -X POST \
  -F "file=@sample-feed.xml" \
  http://localhost:8000/v1/validate \
  -o validation-result.json
```

### Performance Testing

```bash
# Test with large file
curl -X POST \
  -F "file=@large-feed.xml" \
  -w "Time: %{time_total}s\n" \
  http://localhost:8000/v1/validate

# Test with timeout
curl -X POST \
  -F "file=@sample-feed.xml" \
  --max-time 30 \
  http://localhost:8000/v1/validate

# Test with verbose output
curl -X POST \
  -F "file=@sample-feed.xml" \
  -v \
  http://localhost:8000/v1/validate
```

## Postman Collection

### Collection JSON

```json
{
  "info": {
    "name": "MITS Validator API",
    "description": "Collection for MITS Validator API testing",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Health Check",
      "request": {
        "method": "GET",
        "header": [],
        "url": {
          "raw": "{{base_url}}/health",
          "host": ["{{base_url}}"],
          "path": ["health"]
        }
      }
    },
    {
      "name": "Validate File",
      "request": {
        "method": "POST",
        "header": [],
        "body": {
          "mode": "formdata",
          "formdata": [
            {
              "key": "file",
              "type": "file",
              "src": "sample-feed.xml"
            },
            {
              "key": "profile",
              "value": "default",
              "type": "text"
            }
          ]
        },
        "url": {
          "raw": "{{base_url}}/v1/validate",
          "host": ["{{base_url}}"],
          "path": ["v1", "validate"]
        }
      }
    },
    {
      "name": "Validate URL",
      "request": {
        "method": "POST",
        "header": [],
        "body": {
          "mode": "urlencoded",
          "urlencoded": [
            {
              "key": "url",
              "value": "https://example.com/feed.xml",
              "type": "text"
            },
            {
              "key": "profile",
              "value": "default",
              "type": "text"
            }
          ]
        },
        "url": {
          "raw": "{{base_url}}/v1/validate",
          "host": ["{{base_url}}"],
          "path": ["v1", "validate"]
        }
      }
    }
  ],
  "variable": [
    {
      "key": "base_url",
      "value": "http://localhost:8000"
    }
  ]
}
```

## Error Handling Examples

### Python Error Handling

```python
import httpx
import json

def validate_with_error_handling(file_path):
    try:
        with open(file_path, 'rb') as f:
            response = httpx.post(
                "http://localhost:8000/v1/validate",
                files={"file": f},
                timeout=30.0
            )
            response.raise_for_status()
            result = response.json()

            if result["summary"]["valid"]:
                print("✅ Validation successful!")
                return True
            else:
                print(f"❌ Validation failed with {result['summary']['total_findings']} findings")
                for finding in result["findings"]:
                    print(f"  {finding['level'].upper()}: {finding['message']}")
                    if 'location' in finding:
                        print(f"    Location: {finding['location']}")
                return False

    except httpx.HTTPStatusError as e:
        print(f"HTTP error: {e.response.status_code}")
        if e.response.status_code == 413:
            print("File too large. Try a smaller file.")
        elif e.response.status_code == 415:
            print("Unsupported content type. Ensure file is XML.")
        return False

    except httpx.TimeoutException:
        print("Request timed out. Try again or use a smaller file.")
        return False

    except httpx.RequestError as e:
        print(f"Request error: {e}")
        return False

    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return False

    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

# Usage
success = validate_with_error_handling("sample-feed.xml")
if success:
    print("File is valid!")
else:
    print("File has validation errors.")
```

### JavaScript Error Handling

```javascript
async function validateWithErrorHandling(filePath) {
    try {
        const form = new FormData();
        form.append('file', fs.createReadStream(filePath));

        const response = await fetch('http://localhost:8000/v1/validate', {
            method: 'POST',
            body: form
        });

        if (!response.ok) {
            if (response.status === 413) {
                throw new Error('File too large. Try a smaller file.');
            } else if (response.status === 415) {
                throw new Error('Unsupported content type. Ensure file is XML.');
            } else {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
        }

        const result = await response.json();

        if (result.summary.valid) {
            console.log('✅ Validation successful!');
            return true;
        } else {
            console.log(`❌ Validation failed with ${result.summary.total_findings} findings`);
            result.findings.forEach(finding => {
                console.log(`  ${finding.level.toUpperCase()}: ${finding.message}`);
                if (finding.location) {
                    console.log(`    Location: ${JSON.stringify(finding.location)}`);
                }
            });
            return false;
        }

    } catch (error) {
        console.error('Error:', error.message);
        return false;
    }
}

// Usage
validateWithErrorHandling('sample-feed.xml')
    .then(success => {
        if (success) {
            console.log('File is valid!');
        } else {
            console.log('File has validation errors.');
        }
    });
```

## Advanced Usage

### Custom Validation Profiles

```python
# Create a custom profile
custom_profile = {
    "name": "custom-validation",
    "description": "Custom validation profile",
    "enabled_levels": ["WellFormed", "XSD", "Semantic"],
    "severity_overrides": {
        "XSD:SCHEMA_MISSING": "warning"
    },
    "intake_limits": {
        "max_bytes": 52428800,  # 50MB
        "timeout_seconds": 60
    }
}

# Save profile to file
import yaml
with open('custom-profile.yaml', 'w') as f:
    yaml.dump(custom_profile, f)
```

### Integration with CI/CD

```yaml
# GitHub Actions example
name: Validate MITS Feeds

on:
  push:
    paths:
      - 'feeds/**/*.xml'

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'

      - name: Install MITS Validator
        run: pip install mits-validator

      - name: Validate feeds
        run: |
          for file in feeds/*.xml; do
            echo "Validating $file"
            mits-validate validate --file "$file" --profile pms-publisher
            if [ $? -ne 0 ]; then
              echo "Validation failed for $file"
              exit 1
            fi
          done
```

### Docker Integration

```dockerfile
# Dockerfile for MITS Validator
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "mits_validator.api:app", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  mits-validator:
    build: .
    ports:
      - "8000:8000"
    environment:
      - MAX_UPLOAD_BYTES=52428800
      - REQUEST_TIMEOUT=60
    volumes:
      - ./feeds:/app/feeds
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

This comprehensive guide provides developers with everything they need to integrate with the MITS Validator API effectively!
