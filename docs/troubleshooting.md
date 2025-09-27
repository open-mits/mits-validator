# Troubleshooting Guide

This guide helps you diagnose and resolve common issues with the MITS Validator.

## 🚨 Common Issues

### Container Issues

#### Container Won't Start

**Symptoms:**
- Container exits immediately
- Health checks fail
- Port binding errors

**Solutions:**
```bash
# Check container logs
docker logs mits-validator

# Check if port is already in use
netstat -tulpn | grep :8000

# Run with different port
docker run -p 8001:8000 ghcr.io/open-mits/mits-validator:latest

# Check container status
docker ps -a
```

#### Memory Issues

**Symptoms:**
- Container killed due to OOM
- High memory usage
- Slow performance

**Solutions:**
```bash
# Check memory usage
docker stats mits-validator

# Increase memory limits
docker run -m 2g ghcr.io/open-mits/mits-validator:latest

# Adjust memory settings
docker run -e MEMORY_LIMIT_MB=200 ghcr.io/open-mits/mits-validator:latest
```

### API Issues

#### Validation Failures

**Symptoms:**
- 400 Bad Request errors
- Validation timeouts
- Invalid response format

**Solutions:**
```bash
# Check request format
curl -v -X POST -F "file=@feed.xml" http://localhost:8000/v1/validate

# Check file size limits
curl -X POST -F "file=@large-feed.xml" http://localhost:8000/v1/validate

# Check content type
curl -X POST -H "Content-Type: application/xml" \
  -d @feed.xml http://localhost:8000/v1/validate
```

#### Rate Limiting

**Symptoms:**
- 429 Too Many Requests
- Slow response times
- Request timeouts

**Solutions:**
```bash
# Check rate limit settings
curl http://localhost:8000/health/detailed

# Adjust rate limits
docker run -e RATE_LIMIT_MAX_REQUESTS=200 ghcr.io/open-mits/mits-validator:latest

# Check current usage
curl http://localhost:8000/metrics | grep rate_limit
```

### Performance Issues

#### Slow Validation

**Symptoms:**
- High response times
- Timeout errors
- Resource exhaustion

**Solutions:**
```bash
# Check metrics
curl http://localhost:8000/metrics

# Monitor resource usage
docker stats mits-validator

# Adjust concurrency limits
docker run -e THROTTLE_MAX_CONCURRENT=20 ghcr.io/open-mits/mits-validator:latest

# Use async validation for large files
curl -X POST -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/large-feed.xml"}' \
  http://localhost:8000/v1/validate/async
```

#### High Memory Usage

**Symptoms:**
- Container memory usage > 1GB
- OOM kills
- Slow performance

**Solutions:**
```bash
# Check memory usage
docker stats mits-validator

# Adjust memory limits
docker run -m 2g -e MEMORY_LIMIT_MB=200 ghcr.io/open-mits/mits-validator:latest

# Use streaming validation
curl -X POST -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/large-feed.xml", "profile": "performance"}' \
  http://localhost:8000/v1/validate
```

### Redis Issues

#### Connection Failures

**Symptoms:**
- Cache errors in logs
- Slow performance
- Memory usage warnings

**Solutions:**
```bash
# Check Redis connection
docker run --network host redis:7-alpine redis-cli ping

# Test Redis URL
docker run -e REDIS_URL=redis://localhost:6379 ghcr.io/open-mits/mits-validator:latest

# Check Redis logs
docker logs redis-container
```

#### Cache Issues

**Symptoms:**
- Cache misses
- Slow schema loading
- Memory warnings

**Solutions:**
```bash
# Check cache stats
curl http://localhost:8000/health/detailed

# Clear cache
docker exec redis-container redis-cli FLUSHDB

# Adjust cache settings
docker run -e REDIS_URL=redis://localhost:6379 \
  -e CACHE_TTL=7200 ghcr.io/open-mits/mits-validator:latest
```

## 🔍 Debugging

### Enable Debug Logging

```bash
# Run with debug logging
docker run -e LOG_LEVEL=DEBUG ghcr.io/open-mits/mits-validator:latest

# Check logs
docker logs -f mits-validator
```

### Health Checks

```bash
# Basic health check
curl http://localhost:8000/health

# Detailed health check
curl http://localhost:8000/health/detailed

# Check specific components
curl http://localhost:8000/health/detailed | jq '.components'
```

### Metrics Analysis

```bash
# Get all metrics
curl http://localhost:8000/metrics

# Check specific metrics
curl http://localhost:8000/metrics | grep validation_duration
curl http://localhost:8000/metrics | grep memory_usage
curl http://localhost:8000/metrics | grep cache_hits
```

### Log Analysis

```bash
# Follow logs in real-time
docker logs -f mits-validator

# Filter for specific errors
docker logs mits-validator 2>&1 | grep ERROR

# Check structured logs
docker logs mits-validator 2>&1 | jq '.'
```

## 🛠️ Performance Tuning

### For High Throughput

```bash
# Increase concurrent requests
docker run -e THROTTLE_MAX_CONCURRENT=50 ghcr.io/open-mits/mits-validator:latest

# Increase rate limits
docker run -e RATE_LIMIT_MAX_REQUESTS=500 ghcr.io/open-mits/mits-validator:latest

# Use Redis caching
docker run -e REDIS_URL=redis://localhost:6379 ghcr.io/open-mits/mits-validator:latest
```

### For Large Files

```bash
# Increase memory limits
docker run -m 2g -e MEMORY_LIMIT_MB=500 ghcr.io/open-mits/mits-validator:latest

# Use streaming validation
curl -X POST -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/large-feed.xml", "profile": "performance"}' \
  http://localhost:8000/v1/validate

# Use async validation
curl -X POST -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/large-feed.xml"}' \
  http://localhost:8000/v1/validate/async
```

### For Production

```bash
# Production configuration
docker run -d \
  --name mits-validator \
  -p 8000:8000 \
  -e LOG_LEVEL=WARNING \
  -e REDIS_URL=redis://redis:6379 \
  -e RATE_LIMIT_MAX_REQUESTS=1000 \
  -e THROTTLE_MAX_CONCURRENT=100 \
  -e MEMORY_LIMIT_MB=1000 \
  --restart unless-stopped \
  ghcr.io/open-mits/mits-validator:latest
```

## 📊 Monitoring

### Key Metrics to Monitor

- **Response Time**: `validation_duration_seconds`
- **Error Rate**: `validation_errors_total`
- **Memory Usage**: `memory_usage_bytes`
- **Cache Performance**: `cache_hits_total`, `cache_misses_total`
- **Request Rate**: `requests_total`

### Alerting Thresholds

```yaml
# Example Prometheus alerting rules
groups:
- name: mits-validator
  rules:
  - alert: HighErrorRate
    expr: rate(validation_errors_total[5m]) > 0.1
    for: 2m
    labels:
      severity: warning
    annotations:
      summary: "High error rate detected"

  - alert: HighResponseTime
    expr: histogram_quantile(0.95, validation_duration_seconds) > 5
    for: 2m
    labels:
      severity: warning
    annotations:
      summary: "High response time detected"

  - alert: HighMemoryUsage
    expr: memory_usage_bytes > 1000000000  # 1GB
    for: 2m
    labels:
      severity: critical
    annotations:
      summary: "High memory usage detected"
```

### Log Monitoring

```bash
# Monitor for errors
docker logs mits-validator 2>&1 | grep -i error

# Monitor for warnings
docker logs mits-validator 2>&1 | grep -i warning

# Monitor for specific patterns
docker logs mits-validator 2>&1 | grep "validation failed"
```

## 🔧 Configuration Issues

### Environment Variables

```bash
# Check current configuration
curl http://localhost:8000/health/detailed | jq '.config'

# Validate environment variables
docker run --rm -e LOG_LEVEL=DEBUG ghcr.io/open-mits/mits-validator:latest \
  python -c "import os; print('Environment:', dict(os.environ))"
```

### Validation Profiles

```bash
# Check available profiles
curl http://localhost:8000/health/detailed | jq '.profiles'

# Test specific profile
curl -X POST -F "file=@feed.xml" -F "profile=enhanced-validation" \
  http://localhost:8000/v1/validate
```

### Schema Issues

```bash
# Check schema loading
curl http://localhost:8000/health/detailed | jq '.schemas'

# Test schema validation
curl -X POST -F "file=@feed.xml" -F "profile=xsd-only" \
  http://localhost:8000/v1/validate
```

## 🚨 Emergency Procedures

### Service Recovery

```bash
# Restart service
docker restart mits-validator

# Check service status
docker ps | grep mits-validator

# Check logs for errors
docker logs mits-validator --tail 100
```

### Data Recovery

```bash
# Backup Redis data
docker exec redis-container redis-cli BGSAVE

# Restore from backup
docker exec redis-container redis-cli --rdb /data/dump.rdb
```

### Performance Recovery

```bash
# Clear caches
docker exec redis-container redis-cli FLUSHDB

# Restart with clean state
docker stop mits-validator
docker rm mits-validator
docker run -d --name mits-validator ghcr.io/open-mits/mits-validator:latest
```

## 📞 Getting Help

### Log Collection

```bash
# Collect logs for support
docker logs mits-validator > validator.log
docker exec mits-validator ps aux > processes.log
curl http://localhost:8000/health/detailed > health.json
curl http://localhost:8000/metrics > metrics.txt
```

### Issue Reporting

When reporting issues, include:
- Container logs
- Health check results
- Metrics data
- Configuration details
- Steps to reproduce

### Community Support

- GitHub Issues: [open-mits/mits-validator](https://github.com/open-mits/mits-validator/issues)
- Documentation: [docs.open-mits.org](https://docs.open-mits.org)
- Discussions: [GitHub Discussions](https://github.com/open-mits/mits-validator/discussions)
