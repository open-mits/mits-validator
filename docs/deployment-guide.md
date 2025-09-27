# Deployment Guide

This guide covers deploying the MITS Validator in different environments, from development to production.

## 🚀 Quick Start

### Docker Deployment (Recommended)

```bash
# Pull the latest image
docker pull ghcr.io/open-mits/mits-validator:latest

# Run with default settings
docker run -p 8000:8000 ghcr.io/open-mits/mits-validator:latest

# Run with custom configuration
docker run -p 8000:8000 \
  -e MAX_UPLOAD_BYTES=52428800 \
  -e REDIS_URL=redis://localhost:6379 \
  -e RATE_LIMIT_MAX_REQUESTS=200 \
  ghcr.io/open-mits/mits-validator:latest
```

## 🏗️ Environment Configurations

### Development

```bash
# Local development with hot reload
uv run uvicorn src.mits_validator.api:app --reload --port 8000

# With environment variables
REDIS_URL=redis://localhost:6379 \
RATE_LIMIT_MAX_REQUESTS=50 \
uv run uvicorn src.mits_validator.api:app --reload --port 8000
```

### Staging

```bash
# Docker Compose for staging
version: '3.8'
services:
  mits-validator:
    image: ghcr.io/open-mits/mits-validator:latest
    ports:
      - "8000:8000"
    environment:
      - REDIS_URL=redis://redis:6379
      - RATE_LIMIT_MAX_REQUESTS=100
      - LOG_LEVEL=INFO
    depends_on:
      - redis
      - prometheus

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
```

### Production

#### Docker Swarm

```yaml
# docker-stack.yml
version: '3.8'
services:
  mits-validator:
    image: ghcr.io/open-mits/mits-validator:latest
    ports:
      - "8000:8000"
    environment:
      - REDIS_URL=redis://redis:6379
      - RATE_LIMIT_MAX_REQUESTS=500
      - THROTTLE_MAX_CONCURRENT=50
      - LOG_LEVEL=WARNING
    deploy:
      replicas: 3
      resources:
        limits:
          memory: 1G
          cpus: '0.5'
        reservations:
          memory: 512M
          cpus: '0.25'
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3
    depends_on:
      - redis

  redis:
    image: redis:7-alpine
    deploy:
      replicas: 1
      resources:
        limits:
          memory: 512M
          cpus: '0.25'
    volumes:
      - redis_data:/data

volumes:
  redis_data:
```

#### Kubernetes

```yaml
# k8s-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mits-validator
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
        image: ghcr.io/open-mits/mits-validator:latest
        ports:
        - containerPort: 8000
        env:
        - name: REDIS_URL
          value: "redis://redis-service:6379"
        - name: RATE_LIMIT_MAX_REQUESTS
          value: "500"
        - name: THROTTLE_MAX_CONCURRENT
          value: "50"
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
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
---
apiVersion: v1
kind: Service
metadata:
  name: mits-validator-service
spec:
  selector:
    app: mits-validator
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
```

## 🔧 Configuration

### Environment Variables

#### Core Settings
- `PORT`: Service port (default: 8000)
- `MAX_UPLOAD_BYTES`: Maximum file size (default: 10MB)
- `REQUEST_TIMEOUT`: Request timeout in seconds (default: 30)
- `LOG_LEVEL`: Logging level (default: INFO)

#### Performance Settings
- `REDIS_URL`: Redis connection URL for caching
- `RATE_LIMIT_MAX_REQUESTS`: Maximum requests per time window (default: 100)
- `RATE_LIMIT_TIME_WINDOW`: Rate limit time window in seconds (default: 60)
- `THROTTLE_MAX_CONCURRENT`: Maximum concurrent requests (default: 10)
- `ASYNC_VALIDATION_MAX_CONCURRENT`: Maximum concurrent async validations (default: 5)
- `MEMORY_LIMIT_MB`: Memory limit for streaming parser (default: 100)

#### Monitoring Settings
- `ALERT_THRESHOLD_ERROR_RATE`: Error rate threshold for alerts (default: 0.1)
- `ALERT_THRESHOLD_RESPONSE_TIME`: Response time threshold for alerts (default: 5.0)

### Validation Profiles

Configure different validation profiles for different use cases:

```yaml
# rules/mits-5.0/profiles/production.yaml
name: production
description: Production validation profile
enabled_levels:
  - WellFormed
  - XSD
  - Schematron
  - Semantic
severity_overrides:
  "XSD:SCHEMA_MISSING": warning
  "SCHEMATRON:NO_RULES_LOADED": warning
intake_limits:
  max_bytes: 52428800  # 50MB
  allowed_content_types:
    - application/xml
    - text/xml
  timeout_seconds: 60
```

## 📊 Monitoring & Observability

### Health Checks

```bash
# Basic health check
curl http://localhost:8000/health

# Detailed health check
curl http://localhost:8000/health/detailed
```

### Metrics

```bash
# Prometheus metrics
curl http://localhost:8000/metrics
```

### Logging

The validator uses structured logging with correlation IDs:

```json
{
  "timestamp": "2025-09-27T02:57:28.969956+00:00",
  "level": "info",
  "service": "mits-validator",
  "version": "0.1.0",
  "correlation_id": "fb77ee28-2e95-48df-8dbc-2a66d548d2bc",
  "message": "Validation completed",
  "valid": false,
  "errors": 13,
  "warnings": 0,
  "findings_count": 14,
  "duration_seconds": 0.019
}
```

## 🔒 Security Considerations

### Network Security
- Use HTTPS in production
- Configure proper CORS settings
- Implement rate limiting
- Use reverse proxy (nginx, traefik)

### Container Security
- Run as non-root user
- Use read-only filesystem where possible
- Scan images for vulnerabilities
- Keep base images updated

### Data Security
- Validate all inputs
- Implement proper error handling
- Use secure logging practices
- Monitor for suspicious activity

## 🚀 Scaling Strategies

### Horizontal Scaling
- Use load balancer (nginx, HAProxy)
- Implement session affinity if needed
- Use Redis for shared state
- Monitor resource usage

### Vertical Scaling
- Increase memory limits for large files
- Adjust concurrent request limits
- Optimize database connections
- Monitor performance metrics

### Caching Strategy
- Use Redis for schema caching
- Implement CDN for static assets
- Cache validation results
- Monitor cache hit rates

## 🛠️ Troubleshooting

### Common Issues

#### High Memory Usage
```bash
# Check memory usage
docker stats mits-validator

# Adjust memory limits
docker run -m 1g ghcr.io/open-mits/mits-validator:latest
```

#### Slow Response Times
```bash
# Check metrics
curl http://localhost:8000/metrics | grep duration

# Adjust rate limits
docker run -e RATE_LIMIT_MAX_REQUESTS=50 ghcr.io/open-mits/mits-validator:latest
```

#### Redis Connection Issues
```bash
# Test Redis connection
docker run --network host redis:7-alpine redis-cli ping

# Check Redis logs
docker logs redis-container
```

### Performance Tuning

#### For High Throughput
- Increase `THROTTLE_MAX_CONCURRENT`
- Use Redis caching
- Optimize validation profiles
- Monitor resource usage

#### For Large Files
- Increase `MEMORY_LIMIT_MB`
- Use streaming validation
- Adjust timeout settings
- Monitor memory usage

## 📈 Production Checklist

- [ ] Configure proper environment variables
- [ ] Set up Redis caching
- [ ] Configure monitoring and alerting
- [ ] Set up log aggregation
- [ ] Configure backup strategies
- [ ] Test disaster recovery procedures
- [ ] Set up security scanning
- [ ] Configure rate limiting
- [ ] Test load balancing
- [ ] Monitor performance metrics
