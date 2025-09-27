# API Examples & Integration Guide

This guide provides comprehensive examples for integrating with the MITS Validator API.

## 🚀 Quick Start

### Basic Validation

```bash
# Validate a file
curl -X POST -F "file=@feed.xml" http://localhost:8000/v1/validate

# Validate from URL
curl -X POST -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/feed.xml"}' \
  http://localhost:8000/v1/validate
```

## 📋 API Reference

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/v1/validate` | Validate XML file or URL |
| `POST` | `/v1/validate/async` | Async validation for large files |
| `GET` | `/health` | Basic health check |
| `GET` | `/health/detailed` | Detailed health check |
| `GET` | `/metrics` | Prometheus metrics |
| `GET` | `/docs` | API documentation |

## 🔧 Integration Examples

### Python Client

#### Synchronous Client

```python
import requests
import json

class MITSValidatorClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url

    def validate_file(self, file_path, profile="default"):
        """Validate a local XML file."""
        with open(file_path, 'rb') as f:
            files = {'file': f}
            data = {'profile': profile}
            response = requests.post(
                f"{self.base_url}/v1/validate",
                files=files,
                data=data
            )
        return response.json()

    def validate_url(self, url, profile="default"):
        """Validate XML from URL."""
        payload = {
            "url": url,
            "profile": profile
        }
        response = requests.post(
            f"{self.base_url}/v1/validate",
            json=payload
        )
        return response.json()

    def validate_async(self, url, profile="default"):
        """Start async validation."""
        payload = {
            "url": url,
            "profile": profile
        }
        response = requests.post(
            f"{self.base_url}/v1/validate/async",
            json=payload
        )
        return response.json()

    def get_health(self):
        """Get service health."""
        response = requests.get(f"{self.base_url}/health")
        return response.json()

    def get_metrics(self):
        """Get Prometheus metrics."""
        response = requests.get(f"{self.base_url}/metrics")
        return response.text

# Usage
client = MITSValidatorClient()

# Validate local file
result = client.validate_file("feed.xml")
print(f"Valid: {result['summary']['valid']}")
print(f"Errors: {result['summary']['errors']}")

# Validate from URL
result = client.validate_url("https://example.com/feed.xml")
print(f"Valid: {result['summary']['valid']}")

# Check health
health = client.get_health()
print(f"Status: {health['status']}")
```

#### Asynchronous Client

```python
import asyncio
import aiohttp
import json

class AsyncMITSValidatorClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url

    async def validate_file(self, file_path, profile="default"):
        """Validate a local XML file asynchronously."""
        async with aiohttp.ClientSession() as session:
            with open(file_path, 'rb') as f:
                data = aiohttp.FormData()
                data.add_field('file', f, filename='feed.xml')
                data.add_field('profile', profile)

                async with session.post(
                    f"{self.base_url}/v1/validate",
                    data=data
                ) as response:
                    return await response.json()

    async def validate_url(self, url, profile="default"):
        """Validate XML from URL asynchronously."""
        async with aiohttp.ClientSession() as session:
            payload = {
                "url": url,
                "profile": profile
            }
            async with session.post(
                f"{self.base_url}/v1/validate",
                json=payload
            ) as response:
                return await response.json()

    async def validate_async(self, url, profile="default"):
        """Start async validation."""
        async with aiohttp.ClientSession() as session:
            payload = {
                "url": url,
                "profile": profile
            }
            async with session.post(
                f"{self.base_url}/v1/validate/async",
                json=payload
            ) as response:
                return await response.json()

# Usage
async def main():
    client = AsyncMITSValidatorClient()

    # Validate multiple files concurrently
    tasks = [
        client.validate_file("feed1.xml"),
        client.validate_file("feed2.xml"),
        client.validate_url("https://example.com/feed.xml")
    ]

    results = await asyncio.gather(*tasks)

    for i, result in enumerate(results):
        print(f"File {i+1}: Valid={result['summary']['valid']}, Errors={result['summary']['errors']}")

# Run async client
asyncio.run(main())
```

### JavaScript/Node.js Client

```javascript
const axios = require('axios');
const FormData = require('form-data');
const fs = require('fs');

class MITSValidatorClient {
    constructor(baseUrl = 'http://localhost:8000') {
        this.baseUrl = baseUrl;
    }

    async validateFile(filePath, profile = 'default') {
        const form = new FormData();
        form.append('file', fs.createReadStream(filePath));
        form.append('profile', profile);

        const response = await axios.post(`${this.baseUrl}/v1/validate`, form, {
            headers: form.getHeaders()
        });

        return response.data;
    }

    async validateUrl(url, profile = 'default') {
        const response = await axios.post(`${this.baseUrl}/v1/validate`, {
            url: url,
            profile: profile
        });

        return response.data;
    }

    async validateAsync(url, profile = 'default') {
        const response = await axios.post(`${this.base_url}/v1/validate/async`, {
            url: url,
            profile: profile
        });

        return response.data;
    }

    async getHealth() {
        const response = await axios.get(`${this.baseUrl}/health`);
        return response.data;
    }

    async getMetrics() {
        const response = await axios.get(`${this.baseUrl}/metrics`);
        return response.data;
    }
}

// Usage
const client = new MITSValidatorClient();

// Validate file
client.validateFile('feed.xml')
    .then(result => {
        console.log(`Valid: ${result.summary.valid}`);
        console.log(`Errors: ${result.summary.errors}`);
    })
    .catch(error => {
        console.error('Validation failed:', error.message);
    });

// Validate URL
client.validateUrl('https://example.com/feed.xml')
    .then(result => {
        console.log(`Valid: ${result.summary.valid}`);
    })
    .catch(error => {
        console.error('Validation failed:', error.message);
    });
```

### cURL Examples

```bash
# Basic file validation
curl -X POST -F "file=@feed.xml" http://localhost:8000/v1/validate

# URL validation
curl -X POST -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/feed.xml"}' \
  http://localhost:8000/v1/validate

# Validation with profile
curl -X POST -F "file=@feed.xml" -F "profile=enhanced-validation" \
  http://localhost:8000/v1/validate

# Async validation
curl -X POST -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/large-feed.xml", "profile": "performance"}' \
  http://localhost:8000/v1/validate/async

# Health check
curl http://localhost:8000/health

# Detailed health check
curl http://localhost:8000/health/detailed

# Metrics
curl http://localhost:8000/metrics
```

## 📊 Response Examples

### Successful Validation

```json
{
  "api_version": "1.0",
  "validator": {
    "name": "mits-validator",
    "spec_version": "unversioned",
    "profile": "default",
    "levels_available": ["WellFormed", "XSD", "Schematron", "Semantic"],
    "levels_executed": ["WellFormed", "XSD", "Schematron", "Semantic"]
  },
  "input": {
    "source": "file",
    "url": null,
    "filename": "feed.xml",
    "size_bytes": 2310,
    "content_type": "application/xml"
  },
  "summary": {
    "valid": true,
    "errors": 0,
    "warnings": 0,
    "duration_ms": 15
  },
  "findings": [],
  "derived": {},
  "metadata": {
    "request_id": "fb77ee28-2e95-48df-8dbc-2a66d548d2bc",
    "timestamp": "2025-09-27T02:57:28.969956+00:00",
    "engine": {
      "fastapi": "0.117.1",
      "lxml": "6.0.2"
    }
  }
}
```

### Validation with Errors

```json
{
  "api_version": "1.0",
  "validator": {
    "name": "mits-validator",
    "spec_version": "unversioned",
    "profile": "default",
    "levels_available": ["WellFormed", "XSD", "Schematron", "Semantic"],
    "levels_executed": ["WellFormed", "XSD", "Schematron", "Semantic"]
  },
  "input": {
    "source": "file",
    "url": null,
    "filename": "feed.xml",
    "size_bytes": 2310,
    "content_type": "application/xml"
  },
  "summary": {
    "valid": false,
    "errors": 2,
    "warnings": 1,
    "duration_ms": 25
  },
  "findings": [
    {
      "level": "error",
      "code": "XSD:VALIDATION_ERROR",
      "message": "XML does not conform to XSD schema",
      "rule_ref": "internal://XSD"
    },
    {
      "level": "error",
      "code": "SEMANTIC:INVALID_CHARGE_CLASS",
      "message": "Charge classification 'InvalidClass' is not valid according to catalog",
      "rule_ref": "semantic://charge-classification",
      "location": {
        "line": 15,
        "column": 8,
        "xpath": "/PropertyMarketing/Property/ChargeOffer/ChargeOfferItem/ChargeClassification"
      }
    },
    {
      "level": "warning",
      "code": "SCHEMATRON:NO_RULES_LOADED",
      "message": "No Schematron rules available for validation",
      "rule_ref": "internal://Schematron"
    }
  ],
  "derived": {},
  "metadata": {
    "request_id": "fb77ee28-2e95-48df-8dbc-2a66d548d2bc",
    "timestamp": "2025-09-27T02:57:28.969956+00:00",
    "engine": {
      "fastapi": "0.117.1",
      "lxml": "6.0.2"
    }
  }
}
```

## 🔧 Advanced Usage

### Batch Processing

```python
import asyncio
import aiohttp
from pathlib import Path

async def validate_batch(file_paths, client):
    """Validate multiple files concurrently."""
    tasks = []
    for file_path in file_paths:
        task = client.validate_file(file_path)
        tasks.append(task)

    results = await asyncio.gather(*tasks, return_exceptions=True)

    for i, result in enumerate(results):
        if isinstance(result, Exception):
            print(f"File {file_paths[i]}: Error - {result}")
        else:
            print(f"File {file_paths[i]}: Valid={result['summary']['valid']}, Errors={result['summary']['errors']}")

# Usage
client = AsyncMITSValidatorClient()
file_paths = ["feed1.xml", "feed2.xml", "feed3.xml"]
asyncio.run(validate_batch(file_paths, client))
```

### Error Handling

```python
import requests
from requests.exceptions import RequestException

def validate_with_retry(file_path, max_retries=3):
    """Validate with retry logic."""
    for attempt in range(max_retries):
        try:
            with open(file_path, 'rb') as f:
                files = {'file': f}
                response = requests.post(
                    "http://localhost:8000/v1/validate",
                    files=files,
                    timeout=30
                )
                response.raise_for_status()
                return response.json()

        except RequestException as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt == max_retries - 1:
                raise
            time.sleep(2 ** attempt)  # Exponential backoff
```

### Monitoring Integration

```python
import time
import requests
from prometheus_client import Counter, Histogram, start_http_server

# Prometheus metrics
validation_requests = Counter('mits_validations_total', 'Total validation requests', ['status'])
validation_duration = Histogram('mits_validation_duration_seconds', 'Validation duration')

def validate_with_metrics(file_path):
    """Validate with Prometheus metrics."""
    start_time = time.time()

    try:
        with open(file_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(
                "http://localhost:8000/v1/validate",
                files=files
            )
            response.raise_for_status()
            result = response.json()

            # Record metrics
            status = 'success' if result['summary']['valid'] else 'error'
            validation_requests.labels(status=status).inc()
            validation_duration.observe(time.time() - start_time)

            return result

    except Exception as e:
        validation_requests.labels(status='error').inc()
        validation_duration.observe(time.time() - start_time)
        raise

# Start Prometheus metrics server
start_http_server(8001)
```

## 🚀 Performance Tips

### For High Throughput
- Use async clients for concurrent requests
- Implement connection pooling
- Use Redis caching for repeated validations
- Monitor rate limits and adjust accordingly

### For Large Files
- Use streaming validation for very large files
- Implement progress tracking for long-running validations
- Consider async validation for files > 10MB
- Monitor memory usage

### For Production
- Implement proper error handling and retries
- Use structured logging with correlation IDs
- Monitor performance metrics
- Set up alerting for failures

## 📋 Postman Collection

```json
{
  "info": {
    "name": "MITS Validator API",
    "description": "Collection for MITS Validator API endpoints"
  },
  "item": [
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
              "src": "feed.xml"
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
        "header": [
          {
            "key": "Content-Type",
            "value": "application/json"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"url\": \"https://example.com/feed.xml\",\n  \"profile\": \"default\"\n}"
        },
        "url": {
          "raw": "{{base_url}}/v1/validate",
          "host": ["{{base_url}}"],
          "path": ["v1", "validate"]
        }
      }
    },
    {
      "name": "Health Check",
      "request": {
        "method": "GET",
        "url": {
          "raw": "{{base_url}}/health",
          "host": ["{{base_url}}"],
          "path": ["health"]
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
