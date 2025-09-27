# Deployment Guide

This guide covers various deployment options for the MITS Validator service, from local development to production environments.

## 🐳 Docker Deployment

### Quick Start

```bash
# Pull the latest image
docker pull ghcr.io/open-mits/mits-validator:latest

# Run the container
docker run -p 8000:8000 ghcr.io/open-mits/mits-validator:latest
```

### Production Configuration

```bash
# Run with production settings
docker run -d \
  --name mits-validator \
  --restart unless-stopped \
  -p 8000:8000 \
  -e MAX_UPLOAD_BYTES=52428800 \
  -e LOG_LEVEL=INFO \
  -e CORS_ORIGINS="https://yourdomain.com" \
  ghcr.io/open-mits/mits-validator:latest
```

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | `8000` | Port to bind the service |
| `MAX_UPLOAD_BYTES` | `10485760` | Maximum file size (10MB) |
| `REQUEST_TIMEOUT` | `30` | Request timeout in seconds |
| `ALLOWED_CONTENT_TYPES` | `application/xml,text/xml,application/octet-stream` | Allowed content types |
| `DEFAULT_PROFILE` | `default` | Default validation profile |
| `LOG_LEVEL` | `INFO` | Logging level |
| `CORS_ORIGINS` | `*` | CORS allowed origins |
| `CORS_METHODS` | `GET,POST,OPTIONS` | CORS allowed methods |
| `CORS_HEADERS` | `*` | CORS allowed headers |

### Docker Compose

Create a `docker-compose.yml` file:

```yaml
version: '3.8'

services:
  mits-validator:
    image: ghcr.io/open-mits/mits-validator:latest
    ports:
      - "8000:8000"
    environment:
      - MAX_UPLOAD_BYTES=52428800
      - LOG_LEVEL=INFO
      - CORS_ORIGINS=https://yourdomain.com
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

Run with:

```bash
docker-compose up -d
```

## ☁️ Cloud Deployment

### Google Cloud Run

1. **Deploy to Cloud Run**:

```bash
# Build and push to Google Container Registry
gcloud builds submit --tag gcr.io/PROJECT_ID/mits-validator

# Deploy to Cloud Run
gcloud run deploy mits-validator \
  --image gcr.io/PROJECT_ID/mits-validator \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars MAX_UPLOAD_BYTES=52428800
```

2. **Cloud Run Configuration**:

```yaml
# cloud-run.yaml
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: mits-validator
  annotations:
    run.googleapis.com/ingress: all
spec:
  template:
    metadata:
      annotations:
        autoscaling.knative.dev/maxScale: "10"
        run.googleapis.com/cpu-throttling: "false"
    spec:
      containerConcurrency: 100
      containers:
      - image: ghcr.io/open-mits/mits-validator:latest
        ports:
        - containerPort: 8000
        env:
        - name: MAX_UPLOAD_BYTES
          value: "52428800"
        - name: LOG_LEVEL
          value: "INFO"
        resources:
          limits:
            cpu: "2"
            memory: "2Gi"
```

### AWS ECS/Fargate

1. **Task Definition**:

```json
{
  "family": "mits-validator",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "executionRoleArn": "arn:aws:iam::ACCOUNT:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "mits-validator",
      "image": "ghcr.io/open-mits/mits-validator:latest",
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
          "name": "LOG_LEVEL",
          "value": "INFO"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/mits-validator",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

### Azure Container Instances

```bash
# Create resource group
az group create --name mits-validator-rg --location eastus

# Deploy container
az container create \
  --resource-group mits-validator-rg \
  --name mits-validator \
  --image ghcr.io/open-mits/mits-validator:latest \
  --ports 8000 \
  --environment-variables \
    MAX_UPLOAD_BYTES=52428800 \
    LOG_LEVEL=INFO \
  --dns-name-label mits-validator
```

## 🚀 Hugging Face Spaces (Docker)

### Deploy to Hugging Face Spaces

1. **Create a new Space**:
   - Go to [Hugging Face Spaces](https://huggingface.co/new-space)
   - Select "Docker" as the SDK
   - Set `app_port: 8000`

2. **Configure Environment**:
   ```yaml
   # README.md in your Space
   ---
   title: MITS Validator
   emoji: 🏠
   colorFrom: blue
   colorTo: green
   sdk: docker
   app_port: 8000
   pinned: false
   ---
   ```

3. **Environment Variables**:
   - `MAX_UPLOAD_BYTES`: `10485760` (10MB limit for public demo)
   - `LOG_LEVEL`: `INFO`
   - `CORS_ORIGINS`: `*` (for public access)

### Public Demo Considerations

- **Rate Limiting**: Implement rate limiting for production use
- **File Size**: Default 10MB limit (configurable)
- **Timeout**: 30-second request timeout
- **Privacy**: Never upload sensitive production data to public instances
- **Cold Starts**: Spaces may have cold start delays

## 🏗️ Kubernetes Deployment

### Helm Chart

Create a basic Helm chart in `deploy/helm/mits-validator/`:

```yaml
# deploy/helm/mits-validator/values.yaml
replicaCount: 2

image:
  repository: ghcr.io/open-mits/mits-validator
  tag: latest
  pullPolicy: IfNotPresent

service:
  type: ClusterIP
  port: 8000

ingress:
  enabled: true
  className: nginx
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
  hosts:
    - host: mits-validator.example.com
      paths:
        - path: /
          pathType: Prefix

resources:
  limits:
    cpu: 1000m
    memory: 1Gi
  requests:
    cpu: 500m
    memory: 512Mi

env:
  MAX_UPLOAD_BYTES: "52428800"
  LOG_LEVEL: "INFO"
```

### Deploy with Helm

```bash
# Add Helm repository (if using a chart repository)
helm repo add mits-validator https://charts.example.com/mits-validator

# Install the chart
helm install mits-validator ./deploy/helm/mits-validator \
  --set image.tag=v1.0.0 \
  --set env.MAX_UPLOAD_BYTES=52428800
```

## 🔧 Development Deployment

### Local Development

```bash
# Clone the repository
git clone https://github.com/open-mits/mits-validator.git
cd mits-validator

# Install dependencies
uv sync -E dev

# Run the service
uv run mits-api
```

### Docker Development

```bash
# Build the image
make build

# Run locally
make run

# Run tests
make test

# Run smoke tests
make smoke
```

## 📊 Monitoring and Observability

### Health Checks

The service provides built-in health checks:

```bash
# Basic health check
curl http://localhost:8000/health

# Detailed health information
curl http://localhost:8000/health | jq
```

### Logging

The service uses structured JSON logging:

```json
{
  "timestamp": "2024-01-01T00:00:00Z",
  "level": "INFO",
  "message": "Request processed",
  "request_id": "uuid-here",
  "method": "POST",
  "path": "/v1/validate",
  "status_code": 200,
  "duration_ms": 123
}
```

### Metrics

Consider adding metrics collection:

- **Request rate**: Requests per second
- **Response time**: P50, P95, P99 latencies
- **Error rate**: 4xx and 5xx error rates
- **File size distribution**: Upload size metrics
- **Validation results**: Success/failure rates

## 🔒 Security Considerations

### Network Security

- **TLS/SSL**: Use HTTPS in production
- **Firewall**: Restrict access to necessary ports
- **VPN**: Use VPN for internal deployments

### Data Security

- **File Uploads**: Validate and sanitize all uploads
- **Size Limits**: Enforce reasonable file size limits
- **Content Scanning**: Scan uploaded files for malware
- **Data Retention**: Implement data retention policies

### Access Control

- **Authentication**: Implement API authentication
- **Authorization**: Use role-based access control
- **Rate Limiting**: Implement rate limiting
- **CORS**: Configure CORS appropriately

## 🚨 Troubleshooting

### Common Issues

1. **Container won't start**:
   ```bash
   # Check container logs
   docker logs mits-validator

   # Check resource usage
   docker stats mits-validator
   ```

2. **Health check failing**:
   ```bash
   # Test health endpoint
   curl -v http://localhost:8000/health

   # Check port binding
   netstat -tlnp | grep 8000
   ```

3. **Validation errors**:
   ```bash
   # Check service logs
   docker logs mits-validator | grep ERROR

   # Test with sample XML
   curl -X POST -F "file=@test.xml" http://localhost:8000/v1/validate
   ```

### Performance Tuning

1. **Resource Allocation**:
   - **CPU**: 1-2 cores for production
   - **Memory**: 512MB-2GB depending on load
   - **Storage**: Minimal (stateless service)

2. **Scaling**:
   - **Horizontal**: Multiple container instances
   - **Load Balancing**: Use a load balancer
   - **Caching**: Consider Redis for caching

3. **Monitoring**:
   - **Health Checks**: Regular health check monitoring
   - **Metrics**: Collect and analyze metrics
   - **Alerting**: Set up alerts for failures

## 📚 Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Google Cloud Run Documentation](https://cloud.google.com/run/docs)
- [AWS ECS Documentation](https://docs.aws.amazon.com/ecs/)
- [Azure Container Instances Documentation](https://docs.microsoft.com/en-us/azure/container-instances/)
- [Hugging Face Spaces Documentation](https://huggingface.co/docs/hub/spaces)
