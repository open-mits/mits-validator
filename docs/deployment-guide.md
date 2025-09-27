# Deployment Guide

This guide covers deploying the MITS Validator in various environments, from development to production.

## Table of Contents

- [Quick Start](#quick-start)
- [Development Deployment](#development-deployment)
- [Production Deployment](#production-deployment)
- [Docker Deployment](#docker-deployment)
- [Kubernetes Deployment](#kubernetes-deployment)
- [Cloud Deployment](#cloud-deployment)
- [Monitoring & Observability](#monitoring--observability)
- [Security Considerations](#security-considerations)
- [Troubleshooting](#troubleshooting)

## Quick Start

### Local Development

```bash
# Clone the repository
git clone https://github.com/open-mits/mits-validator.git
cd mits-validator

# Install dependencies
uv sync

# Start the development server
uv run uvicorn mits_validator.api:app --reload --host 0.0.0.0 --port 8000

# Test the API
curl http://localhost:8000/health
```

### Docker Quick Start

```bash
# Build the image
docker build -t mits-validator .

# Run the container
docker run -p 8000:8000 mits-validator

# Test the API
curl http://localhost:8000/health
```

## Development Deployment

### Prerequisites

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) or pip
- Git

### Setup

```bash
# Clone the repository
git clone https://github.com/open-mits/mits-validator.git
cd mits-validator

# Create virtual environment
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
uv sync

# Install pre-commit hooks
uv run pre-commit install

# Run tests
uv run pytest
```

### Configuration

```bash
# Environment variables
export MAX_UPLOAD_BYTES=52428800  # 50MB
export REQUEST_TIMEOUT=60
export LOG_LEVEL=INFO
export DEBUG=false

# Start development server
uv run uvicorn mits_validator.api:app --reload --host 0.0.0.0 --port 8000
```

### Development Tools

```bash
# Run with hot reload
uv run uvicorn mits_validator.api:app --reload

# Run with debug logging
LOG_LEVEL=DEBUG uv run uvicorn mits_validator.api:app --reload

# Run tests with coverage
uv run pytest --cov=src --cov-report=html

# Run linting
uv run ruff check .

# Run formatting
uv run ruff format .
```

## Production Deployment

### Prerequisites

- Python 3.12+
- Nginx (recommended)
- Systemd (for service management)
- SSL certificates (for HTTPS)

### System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **CPU** | 2 cores | 4+ cores |
| **RAM** | 2GB | 8GB+ |
| **Storage** | 10GB | 50GB+ |
| **Network** | 100Mbps | 1Gbps+ |

### Installation

```bash
# Create system user
sudo useradd -m -s /bin/bash mits-validator

# Create application directory
sudo mkdir -p /opt/mits-validator
sudo chown mits-validator:mits-validator /opt/mits-validator

# Clone repository
sudo -u mits-validator git clone https://github.com/open-mits/mits-validator.git /opt/mits-validator

# Install dependencies
cd /opt/mits-validator
sudo -u mits-validator uv sync --production
```

### Configuration

```bash
# Create configuration file
sudo tee /opt/mits-validator/config.env << EOF
# Server configuration
HOST=0.0.0.0
PORT=8000
WORKERS=4

# Validation limits
MAX_UPLOAD_BYTES=52428800
REQUEST_TIMEOUT=60

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# Security
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1,your-domain.com

# Performance
WORKER_CONNECTIONS=1000
KEEP_ALIVE_TIMEOUT=5
EOF

# Set permissions
sudo chown mits-validator:mits-validator /opt/mits-validator/config.env
sudo chmod 600 /opt/mits-validator/config.env
```

### Systemd Service

```bash
# Create systemd service file
sudo tee /etc/systemd/system/mits-validator.service << EOF
[Unit]
Description=MITS Validator API
After=network.target

[Service]
Type=exec
User=mits-validator
Group=mits-validator
WorkingDirectory=/opt/mits-validator
EnvironmentFile=/opt/mits-validator/config.env
ExecStart=/opt/mits-validator/.venv/bin/uvicorn mits_validator.api:app --host 0.0.0.0 --port 8000 --workers 4
ExecReload=/bin/kill -HUP \$MAINPID
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable mits-validator
sudo systemctl start mits-validator

# Check status
sudo systemctl status mits-validator
```

### Nginx Configuration

```nginx
# /etc/nginx/sites-available/mits-validator
upstream mits_validator {
    server 127.0.0.1:8000;
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
    server 127.0.0.1:8003;
}

server {
    listen 80;
    server_name your-domain.com;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    # SSL configuration
    ssl_certificate /etc/ssl/certs/your-domain.crt;
    ssl_certificate_key /etc/ssl/private/your-domain.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;

    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req zone=api burst=20 nodelay;

    # File upload limits
    client_max_body_size 50M;
    client_body_timeout 60s;

    location / {
        proxy_pass http://mits_validator;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;

        # Buffering
        proxy_buffering on;
        proxy_buffer_size 4k;
        proxy_buffers 8 4k;
    }

    # Health check endpoint
    location /health {
        proxy_pass http://mits_validator;
        access_log off;
    }

    # Static files (if any)
    location /static/ {
        alias /opt/mits-validator/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

### Enable Nginx Configuration

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/mits-validator /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Reload nginx
sudo systemctl reload nginx
```

## Docker Deployment

### Dockerfile

```dockerfile
# Dockerfile
FROM python:3.12-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create application user
RUN useradd -m -s /bin/bash mits-validator

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY pyproject.toml uv.lock ./

# Install Python dependencies
RUN pip install uv && uv sync --frozen

# Copy application code
COPY . .

# Change ownership
RUN chown -R mits-validator:mits-validator /app

# Switch to non-root user
USER mits-validator

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start application
CMD ["uvicorn", "mits_validator.api:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose

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
      - LOG_LEVEL=INFO
    volumes:
      - ./logs:/app/logs
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/ssl:ro
    depends_on:
      - mits-validator
    restart: unless-stopped

  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

volumes:
  redis_data:
```

### Build and Run

```bash
# Build image
docker build -t mits-validator .

# Run with docker-compose
docker-compose up -d

# Check logs
docker-compose logs -f mits-validator

# Scale service
docker-compose up -d --scale mits-validator=4
```

## Kubernetes Deployment

### Namespace

```yaml
# namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: mits-validator
```

### ConfigMap

```yaml
# configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: mits-validator-config
  namespace: mits-validator
data:
  MAX_UPLOAD_BYTES: "52428800"
  REQUEST_TIMEOUT: "60"
  LOG_LEVEL: "INFO"
  WORKERS: "4"
```

### Deployment

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mits-validator
  namespace: mits-validator
spec:
  replicas: 3
  selector:
    matchLabels:
      app: mits-validator
  template:
    metadata:
      labels:
        app: mits-validator
    spec:
      containers:
      - name: mits-validator
        image: mits-validator:latest
        ports:
        - containerPort: 8000
        env:
        - name: MAX_UPLOAD_BYTES
          valueFrom:
            configMapKeyRef:
              name: mits-validator-config
              key: MAX_UPLOAD_BYTES
        - name: REQUEST_TIMEOUT
          valueFrom:
            configMapKeyRef:
              name: mits-validator-config
              key: REQUEST_TIMEOUT
        - name: LOG_LEVEL
          valueFrom:
            configMapKeyRef:
              name: mits-validator-config
              key: LOG_LEVEL
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
```

### Service

```yaml
# service.yaml
apiVersion: v1
kind: Service
metadata:
  name: mits-validator-service
  namespace: mits-validator
spec:
  selector:
    app: mits-validator
  ports:
  - port: 80
    targetPort: 8000
  type: ClusterIP
```

### Ingress

```yaml
# ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: mits-validator-ingress
  namespace: mits-validator
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/rate-limit: "100"
    nginx.ingress.kubernetes.io/rate-limit-window: "1m"
spec:
  tls:
  - hosts:
    - your-domain.com
    secretName: mits-validator-tls
  rules:
  - host: your-domain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: mits-validator-service
            port:
              number: 80
```

### Horizontal Pod Autoscaler

```yaml
# hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: mits-validator-hpa
  namespace: mits-validator
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: mits-validator
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

### Deploy to Kubernetes

```bash
# Apply configurations
kubectl apply -f namespace.yaml
kubectl apply -f configmap.yaml
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
kubectl apply -f ingress.yaml
kubectl apply -f hpa.yaml

# Check status
kubectl get pods -n mits-validator
kubectl get services -n mits-validator
kubectl get ingress -n mits-validator

# Check logs
kubectl logs -f deployment/mits-validator -n mits-validator
```

## Cloud Deployment

### AWS ECS

```yaml
# ecs-task-definition.json
{
  "family": "mits-validator",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "executionRoleArn": "arn:aws:iam::account:role/ecsTaskExecutionRole",
  "taskRoleArn": "arn:aws:iam::account:role/ecsTaskRole",
  "containerDefinitions": [
    {
      "name": "mits-validator",
      "image": "your-account.dkr.ecr.region.amazonaws.com/mits-validator:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "MAX_UPLOAD_BYTES",
          "value": "52428800"
        },
        {
          "name": "REQUEST_TIMEOUT",
          "value": "60"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/mits-validator",
          "awslogs-region": "us-west-2",
          "awslogs-stream-prefix": "ecs"
        }
      },
      "healthCheck": {
        "command": ["CMD-SHELL", "curl -f http://localhost:8000/health || exit 1"],
        "interval": 30,
        "timeout": 5,
        "retries": 3,
        "startPeriod": 60
      }
    }
  ]
}
```

### Google Cloud Run

```yaml
# cloud-run.yaml
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: mits-validator
  annotations:
    run.googleapis.com/ingress: all
    run.googleapis.com/execution-environment: gen2
spec:
  template:
    metadata:
      annotations:
        autoscaling.knative.dev/maxScale: "10"
        autoscaling.knative.dev/minScale: "1"
        run.googleapis.com/cpu-throttling: "false"
    spec:
      containerConcurrency: 100
      timeoutSeconds: 300
      containers:
      - image: gcr.io/your-project/mits-validator:latest
        ports:
        - containerPort: 8000
        env:
        - name: MAX_UPLOAD_BYTES
          value: "52428800"
        - name: REQUEST_TIMEOUT
          value: "60"
        resources:
          limits:
            cpu: "2"
            memory: "2Gi"
          requests:
            cpu: "1"
            memory: "1Gi"
```

### Azure Container Instances

```yaml
# azure-container-instance.yaml
apiVersion: 2019-12-01
location: eastus
name: mits-validator
properties:
  containers:
  - name: mits-validator
    properties:
      image: your-registry.azurecr.io/mits-validator:latest
      resources:
        requests:
          cpu: 1
          memoryInGb: 1
      ports:
      - port: 8000
        protocol: TCP
      environmentVariables:
      - name: MAX_UPLOAD_BYTES
        value: "52428800"
      - name: REQUEST_TIMEOUT
        value: "60"
  osType: Linux
  ipAddress:
    type: Public
    ports:
    - protocol: TCP
      port: 8000
  restartPolicy: Always
```

## Monitoring & Observability

### Prometheus Metrics

```python
# metrics.py
from prometheus_client import Counter, Histogram, Gauge, start_http_server

# Metrics
validation_requests = Counter('validation_requests_total', 'Total validation requests', ['method', 'endpoint'])
validation_duration = Histogram('validation_duration_seconds', 'Validation duration', ['level'])
active_connections = Gauge('active_connections', 'Active connections')
memory_usage = Gauge('memory_usage_bytes', 'Memory usage in bytes')
cpu_usage = Gauge('cpu_usage_percent', 'CPU usage percentage')

def track_validation_metrics(func):
    """Decorator to track validation metrics."""
    def wrapper(*args, **kwargs):
        start_time = time.time()

        try:
            result = func(*args, **kwargs)
            validation_requests.labels(method='POST', endpoint='/v1/validate').inc()
            return result
        finally:
            duration = time.time() - start_time
            validation_duration.labels(level='all').observe(duration)

    return wrapper
```

### Grafana Dashboard

```json
{
  "dashboard": {
    "title": "MITS Validator Dashboard",
    "panels": [
      {
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(validation_requests_total[5m])",
            "legendFormat": "Requests/sec"
          }
        ]
      },
      {
        "title": "Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(validation_duration_seconds_bucket[5m]))",
            "legendFormat": "95th percentile"
          }
        ]
      },
      {
        "title": "Error Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(validation_requests_total{status=~\"5..\"}[5m])",
            "legendFormat": "Error rate"
          }
        ]
      }
    ]
  }
}
```

### Logging Configuration

```python
# logging_config.py
import logging
import sys
from pythonjsonlogger import jsonlogger

def setup_logging():
    """Setup structured logging."""
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Remove default handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Add JSON formatter
    handler = logging.StreamHandler(sys.stdout)
    formatter = jsonlogger.JsonFormatter(
        fmt='%(asctime)s %(name)s %(levelname)s %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger
```

## Security Considerations

### Input Validation

```python
# security.py
import re
from pathlib import Path

def validate_file_upload(file: UploadFile) -> bool:
    """Validate file upload for security."""
    # Check file size
    if file.size > MAX_UPLOAD_BYTES:
        raise HTTPException(413, "File too large")

    # Check content type
    allowed_types = ["application/xml", "text/xml"]
    if file.content_type not in allowed_types:
        raise HTTPException(415, "Unsupported media type")

    # Check file extension
    if not file.filename.endswith('.xml'):
        raise HTTPException(400, "Invalid file extension")

    return True

def sanitize_filename(filename: str) -> str:
    """Sanitize filename for security."""
    # Remove path traversal attempts
    filename = Path(filename).name

    # Remove dangerous characters
    filename = re.sub(r'[^\w\-_\.]', '', filename)

    return filename
```

### Rate Limiting

```python
# rate_limiting.py
from fastapi import Request, HTTPException
import time
from collections import defaultdict

class RateLimiter:
    def __init__(self, max_requests: int = 100, window: int = 60):
        self.max_requests = max_requests
        self.window = window
        self.requests = defaultdict(list)

    def is_allowed(self, client_ip: str) -> bool:
        """Check if request is allowed."""
        now = time.time()
        client_requests = self.requests[client_ip]

        # Remove old requests
        client_requests[:] = [req_time for req_time in client_requests if now - req_time < self.window]

        # Check if under limit
        if len(client_requests) >= self.max_requests:
            return False

        # Add current request
        client_requests.append(now)
        return True

# Usage
rate_limiter = RateLimiter(max_requests=100, window=60)

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host

    if not rate_limiter.is_allowed(client_ip):
        raise HTTPException(429, "Too many requests")

    response = await call_next(request)
    return response
```

### HTTPS Configuration

```nginx
# nginx-ssl.conf
server {
    listen 443 ssl http2;
    server_name your-domain.com;

    # SSL configuration
    ssl_certificate /etc/ssl/certs/your-domain.crt;
    ssl_certificate_key /etc/ssl/private/your-domain.key;

    # Modern SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Referrer-Policy "strict-origin-when-cross-origin";

    # Rest of configuration...
}
```

## Troubleshooting

### Common Issues

1. **Service won't start**
   ```bash
   # Check logs
   sudo journalctl -u mits-validator -f

   # Check configuration
   sudo systemctl status mits-validator

   # Test configuration
   sudo -u mits-validator /opt/mits-validator/.venv/bin/uvicorn mits_validator.api:app --check-config
   ```

2. **High memory usage**
   ```bash
   # Monitor memory usage
   htop

   # Check for memory leaks
   sudo systemctl restart mits-validator

   # Adjust worker count
   # Edit /opt/mits-validator/config.env
   WORKERS=2
   ```

3. **Slow response times**
   ```bash
   # Check CPU usage
   top

   # Check disk I/O
   iostat -x 1

   # Check network
   netstat -tulpn
   ```

4. **Validation errors**
   ```bash
   # Check validation logs
   tail -f /opt/mits-validator/logs/validation.log

   # Test with sample file
   curl -X POST -F "file=@sample.xml" http://localhost:8000/v1/validate
   ```

### Performance Tuning

```bash
# Optimize worker count
# Formula: (2 * CPU cores) + 1
WORKERS=9  # For 4-core system

# Optimize memory
# Set appropriate limits
MAX_UPLOAD_BYTES=52428800  # 50MB
REQUEST_TIMEOUT=60

# Enable gzip compression
# Add to nginx configuration
gzip on;
gzip_types application/json application/xml text/xml;
```

### Health Checks

```bash
# Basic health check
curl http://localhost:8000/health

# Detailed health check
curl -v http://localhost:8000/health

# Load testing
ab -n 1000 -c 10 http://localhost:8000/health
```

This comprehensive deployment guide covers all aspects of deploying the MITS Validator in various environments!
