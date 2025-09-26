# Operational Notes

This document provides operational guidance for deploying, monitoring, and maintaining the MITS Validator in production environments.

## Deployment

### Production Requirements

**Minimum Resources**:
- CPU: 2 cores
- Memory: 4GB RAM
- Storage: 10GB (for logs and temporary files)
- Network: 100Mbps

**Recommended Resources**:
- CPU: 4 cores
- Memory: 8GB RAM
- Storage: 50GB SSD
- Network: 1Gbps

### Environment Variables

```bash
# Server Configuration
export MITS_API_HOST=0.0.0.0
export MITS_API_PORT=8000
export MITS_API_WORKERS=4

# Validation Limits
export MITS_MAX_FILE_SIZE=10485760  # 10MB
export MITS_TIMEOUT_SECONDS=30
export MITS_ALLOWED_CONTENT_TYPES="application/xml,text/xml,application/octet-stream"

# URL Fetching
export URL_FETCH_TIMEOUT_SECONDS=5
export URL_FETCH_MAX_BYTES=10485760  # 10MB

# Logging
export MITS_LOG_LEVEL=INFO
export MITS_LOG_FORMAT=json
export MITS_LOG_FILE=/var/log/mits-validator.log

# Security
export MITS_DISABLE_URL_VALIDATION=false
export MITS_ALLOWED_URL_SCHEMES="http,https"
```

### Docker Deployment

```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY . .
RUN pip install -e .

EXPOSE 8000
CMD ["mits-api"]
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
      - MITS_LOG_LEVEL=INFO
      - MITS_MAX_FILE_SIZE=10485760
    volumes:
      - ./logs:/var/log
    restart: unless-stopped
```

### Kubernetes Deployment

```yaml
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
        image: mits-validator:latest
        ports:
        - containerPort: 8000
        env:
        - name: MITS_LOG_LEVEL
          value: "INFO"
        - name: MITS_MAX_FILE_SIZE
          value: "10485760"
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
```

## Monitoring

### Health Checks

**Endpoint**: `GET /health`

**Response**:
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**Monitoring Script**:
```bash
#!/bin/bash
# health-check.sh
HEALTH_URL="http://localhost:8000/health"
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" $HEALTH_URL)

if [ $RESPONSE -eq 200 ]; then
    echo "✅ Service is healthy"
    exit 0
else
    echo "❌ Service is unhealthy (HTTP $RESPONSE)"
    exit 1
fi
```

### Metrics Collection

**Key Metrics**:
- Request count and duration
- Error rates by type
- Validation level performance
- Resource usage (CPU, memory)
- File size distribution
- URL fetch success rate

**Prometheus Configuration**:
```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'mits-validator'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
    scrape_interval: 30s
```

**Grafana Dashboard**:
```json
{
  "dashboard": {
    "title": "MITS Validator",
    "panels": [
      {
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])",
            "legendFormat": "Requests/sec"
          }
        ]
      },
      {
        "title": "Error Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total{status=~\"5..\"}[5m])",
            "legendFormat": "Errors/sec"
          }
        ]
      }
    ]
  }
}
```

### Logging

**Structured Logging**:
```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "level": "INFO",
  "message": "Validation completed",
  "request_id": "req_123",
  "duration_ms": 150,
  "file_size": 1024,
  "levels_executed": ["WellFormed", "XSD"],
  "findings_count": 0,
  "valid": true
}
```

**Log Rotation**:
```bash
# logrotate.conf
/var/log/mits-validator.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 644 mits-validator mits-validator
}
```

## Scaling

### Horizontal Scaling

**Load Balancer Configuration**:
```nginx
upstream mits_validator {
    server mits-validator-1:8000;
    server mits-validator-2:8000;
    server mits-validator-3:8000;
}

server {
    listen 80;
    location / {
        proxy_pass http://mits_validator;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

**Auto-scaling Configuration**:
```yaml
# hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: mits-validator-hpa
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
```

### Vertical Scaling

**Resource Limits**:
```yaml
resources:
  requests:
    memory: "1Gi"
    cpu: "500m"
  limits:
    memory: "2Gi"
    cpu: "1000m"
```

**Performance Tuning**:
```bash
# Increase worker processes
export MITS_API_WORKERS=8

# Increase file size limit
export MITS_MAX_FILE_SIZE=52428800  # 50MB

# Increase timeout
export MITS_TIMEOUT_SECONDS=60
```

## Security

### Network Security

**Firewall Rules**:
```bash
# Allow only HTTPS
iptables -A INPUT -p tcp --dport 443 -j ACCEPT
iptables -A INPUT -p tcp --dport 80 -j DROP

# Rate limiting
iptables -A INPUT -p tcp --dport 443 -m limit --limit 100/minute -j ACCEPT
```

**TLS Configuration**:
```nginx
server {
    listen 443 ssl;
    ssl_certificate /etc/ssl/certs/mits-validator.crt;
    ssl_certificate_key /etc/ssl/private/mits-validator.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES128-GCM-SHA256;
}
```

### Application Security

**Input Validation**:
```bash
# Restrict file types
export MITS_ALLOWED_CONTENT_TYPES="application/xml,text/xml"

# Disable URL validation if not needed
export MITS_DISABLE_URL_VALIDATION=true

# Set strict size limits
export MITS_MAX_FILE_SIZE=1048576  # 1MB
```

**Access Control**:
```nginx
# Basic authentication
location / {
    auth_basic "MITS Validator";
    auth_basic_user_file /etc/nginx/.htpasswd;
    proxy_pass http://mits_validator;
}
```

## Backup and Recovery

### Configuration Backup

```bash
#!/bin/bash
# backup-config.sh
BACKUP_DIR="/backup/mits-validator"
DATE=$(date +%Y%m%d_%H%M%S)

# Backup configuration
tar -czf "$BACKUP_DIR/config_$DATE.tar.gz" \
    /etc/mits-validator/ \
    /var/log/mits-validator/

# Keep only last 30 days
find $BACKUP_DIR -name "config_*.tar.gz" -mtime +30 -delete
```

### Disaster Recovery

**Recovery Procedure**:
1. Restore configuration from backup
2. Deploy application from container image
3. Verify health check endpoint
4. Test validation functionality
5. Update DNS/load balancer configuration

## Troubleshooting

### Common Issues

**High Memory Usage**:
```bash
# Check memory usage
ps aux | grep mits-validator
free -h

# Reduce file size limit
export MITS_MAX_FILE_SIZE=5242880  # 5MB
```

**Slow Response Times**:
```bash
# Check CPU usage
top -p $(pgrep mits-validator)

# Increase timeout
export MITS_TIMEOUT_SECONDS=60
```

**Network Errors**:
```bash
# Check network connectivity
curl -v http://localhost:8000/health

# Check firewall rules
iptables -L
```

### Debug Mode

```bash
# Enable debug logging
export MITS_DEBUG=true
export MITS_LOG_LEVEL=DEBUG

# Run with verbose output
mits-api --debug
```

### Performance Profiling

```bash
# Enable profiling
export MITS_PROFILE=true
export MITS_PROFILE_DIR=/tmp/mits-profile

# Analyze profile
python -m cProfile -s cumulative mits-api
```

## Maintenance

### Regular Tasks

**Daily**:
- Check health status
- Review error logs
- Monitor resource usage

**Weekly**:
- Review performance metrics
- Check for security updates
- Backup configuration

**Monthly**:
- Update dependencies
- Review and rotate logs
- Performance analysis

### Updates

**Dependency Updates**:
```bash
# Update dependencies
uv sync --upgrade

# Run tests
uv run pytest

# Deploy update
docker build -t mits-validator:latest .
docker push mits-validator:latest
```

**Configuration Changes**:
1. Test changes in staging
2. Update configuration files
3. Restart services
4. Verify functionality
5. Monitor for issues

## Support

### Log Collection

```bash
# Collect logs for support
tar -czf mits-validator-logs.tar.gz \
    /var/log/mits-validator.log \
    /var/log/nginx/access.log \
    /var/log/nginx/error.log
```

### Health Check

```bash
# Comprehensive health check
curl -s http://localhost:8000/health | jq
curl -s -X POST -F "file=@test.xml" http://localhost:8000/v1/validate | jq
```

### Performance Test

```bash
# Load testing
ab -n 1000 -c 10 -T "application/xml" -p test.xml http://localhost:8000/v1/validate
```

This operational guide provides the foundation for running the MITS Validator in production environments with proper monitoring, scaling, and maintenance procedures.
