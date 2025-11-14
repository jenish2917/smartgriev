# SmartGriev Observability & Monitoring

Complete observability stack with OpenTelemetry, Prometheus metrics, structured logging, and Grafana dashboards.

## Features

### 1. **Prometheus Metrics** ✅
- HTTP request metrics (count, duration, size)
- Application metrics (complaints, users, performance)
- Custom business metrics
- Health check endpoint

### 2. **OpenTelemetry Tracing** ✅
- Distributed tracing across services
- Auto-instrumentation for Django, PostgreSQL, Redis
- OTLP export to Jaeger/Zipkin
- Custom span creation

### 3. **Structured Logging** ✅
- JSON-formatted logs in production
- Contextual information (user_id, request_id, etc.)
- Request/response logging
- Slow request detection

### 4. **Grafana Dashboards** ✅
- Pre-built dashboard for SmartGriev metrics
- Visualizations for complaints, performance, errors
- Real-time monitoring

## Quick Start

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements/observability.txt
```

### 2. Configure Environment Variables

Add to `.env`:

```env
# Observability Configuration
ENABLE_OPENTELEMETRY=True
OTLP_ENDPOINT=http://localhost:4317
USE_JSON_LOGGING=True
LOG_LEVEL=INFO
SLOW_REQUEST_THRESHOLD=1.0
APP_VERSION=1.0.0
ENVIRONMENT=production
```

### 3. Run the Application

```bash
python manage.py runserver
```

### 4. Access Endpoints

- **Metrics**: http://localhost:8000/metrics
- **Health Check**: http://localhost:8000/health
- **API Root**: http://localhost:8000/

## Prometheus Setup

### Local Prometheus Installation

```bash
# Download Prometheus
wget https://github.com/prometheus/prometheus/releases/download/v2.45.0/prometheus-2.45.0.linux-amd64.tar.gz
tar xvfz prometheus-2.45.0.linux-amd64.tar.gz
cd prometheus-2.45.0

# Copy configuration
cp /path/to/smartgriev/backend/prometheus/prometheus.yml ./

# Run Prometheus
./prometheus --config.file=./prometheus.yml
```

Access Prometheus at: http://localhost:9090

### Docker Prometheus

```yaml
# docker-compose.yml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus:latest
    volumes:
      - ./backend/prometheus/prometheus.yml:/etc/prometheus/prometheus.yml
      - ./backend/prometheus/alerts:/etc/prometheus/alerts
    ports:
      - "9090:9090"
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
```

Run with:
```bash
docker-compose up -d prometheus
```

## Grafana Setup

### Installation

```bash
# Download Grafana
wget https://dl.grafana.com/oss/release/grafana-10.0.0.linux-amd64.tar.gz
tar -zxvf grafana-10.0.0.linux-amd64.tar.gz

# Run Grafana
./grafana-10.0.0/bin/grafana-server
```

Access Grafana at: http://localhost:3000 (default login: admin/admin)

### Configure Data Source

1. Go to Configuration > Data Sources
2. Add Prometheus data source
3. URL: `http://localhost:9090`
4. Click "Save & Test"

### Import Dashboard

1. Go to Dashboards > Import
2. Upload `backend/grafana/dashboards/smartgriev_metrics.json`
3. Select Prometheus data source
4. Click "Import"

### Docker Grafana

```yaml
# docker-compose.yml
services:
  grafana:
    image: grafana/grafana:latest
    volumes:
      - ./backend/grafana/dashboards:/etc/grafana/provisioning/dashboards
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    depends_on:
      - prometheus
```

## Jaeger/OpenTelemetry Setup

### Run Jaeger All-in-One

```bash
docker run -d --name jaeger \
  -e COLLECTOR_OTLP_ENABLED=true \
  -p 16686:16686 \
  -p 4317:4317 \
  -p 4318:4318 \
  jaegertracing/all-in-one:latest
```

Access Jaeger UI at: http://localhost:16686

### Enable OpenTelemetry

Set in `.env`:
```env
ENABLE_OPENTELEMETRY=True
OTLP_ENDPOINT=http://localhost:4317
```

## Available Metrics

### HTTP Metrics
- `smartgriev_http_requests_total` - Total HTTP requests by method, endpoint, status
- `smartgriev_http_request_duration_seconds` - Request duration histogram
- `smartgriev_http_active_requests` - Currently active requests
- `smartgriev_http_request_size_bytes` - Request size histogram
- `smartgriev_http_response_size_bytes` - Response size histogram

### Application Metrics
- `smartgriev_complaints_total` - Total complaints by status and category
- `smartgriev_complaints_by_status` - Current complaints by status
- `smartgriev_complaint_resolution_time_hours` - Resolution time histogram
- `smartgriev_active_users` - Active users in last 24 hours

### System Metrics
- `smartgriev_app_info` - Application version and environment

## Prometheus Queries

### Request Rate
```promql
rate(smartgriev_http_requests_total[5m])
```

### Error Rate
```promql
rate(smartgriev_http_requests_total{status=~"5.."}[5m])
/ rate(smartgriev_http_requests_total[5m])
```

### P95 Latency
```promql
histogram_quantile(0.95,
  rate(smartgriev_http_request_duration_seconds_bucket[5m])
)
```

### Active Requests
```promql
smartgriev_http_active_requests
```

### Complaints by Status
```promql
smartgriev_complaints_by_status
```

## Alerting

Alert rules are defined in `backend/prometheus/alerts/smartgriev_alerts.yml`.

### Available Alerts

1. **HighErrorRate**: Error rate > 5% for 5 minutes
2. **SlowRequests**: P95 latency > 2s for 10 minutes
3. **HighPendingComplaints**: > 100 pending complaints for 15 minutes
4. **LowUserActivity**: < 10 active users for 1 hour
5. **ApplicationDown**: App unreachable for 2 minutes
6. **HighMemoryUsage**: Memory > 2GB for 5 minutes
7. **TooManyActiveRequests**: > 50 concurrent requests for 5 minutes

### Configure Alertmanager

```yaml
# alertmanager.yml
route:
  receiver: 'team-notifications'

receivers:
  - name: 'team-notifications'
    email_configs:
      - to: 'team@smartgriev.gov.in'
        from: 'alerts@smartgriev.gov.in'
        smarthost: 'smtp.gmail.com:587'
```

## Custom Tracing

### Create Custom Spans

```python
from smartgriev.telemetry import get_tracer

tracer = get_tracer(__name__)

def process_complaint(complaint_id):
    with tracer.start_as_current_span("process_complaint") as span:
        span.set_attribute("complaint.id", complaint_id)
        
        # Your processing logic here
        result = do_processing()
        
        span.set_attribute("complaint.status", result.status)
        return result
```

### Custom Logging

```python
from smartgriev.logging_config import get_logger

logger = get_logger(__name__)

logger.info(
    "complaint_created",
    complaint_id=123,
    user_id=456,
    category="infrastructure",
    location="Mumbai"
)
```

## Production Deployment

### Environment Variables

```env
# Production Settings
ENABLE_OPENTELEMETRY=True
OTLP_ENDPOINT=https://jaeger.smartgriev.gov.in:4317
USE_JSON_LOGGING=True
LOG_LEVEL=INFO
SLOW_REQUEST_THRESHOLD=1.0
ENVIRONMENT=production
APP_VERSION=1.0.0
```

### Nginx Configuration

```nginx
location /metrics {
    # Restrict access to metrics endpoint
    allow 10.0.0.0/8;  # Internal network
    deny all;
    
    proxy_pass http://127.0.0.1:8000/metrics;
}

location /health {
    proxy_pass http://127.0.0.1:8000/health;
    access_log off;  # Don't log health checks
}
```

### Docker Compose Full Stack

```yaml
version: '3.8'

services:
  smartgriev:
    build: .
    environment:
      - ENABLE_OPENTELEMETRY=True
      - OTLP_ENDPOINT=http://jaeger:4317
      - USE_JSON_LOGGING=True
    depends_on:
      - postgres
      - redis
      - jaeger
  
  prometheus:
    image: prom/prometheus:latest
    volumes:
      - ./backend/prometheus/prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"
  
  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    depends_on:
      - prometheus
  
  jaeger:
    image: jaegertracing/all-in-one:latest
    environment:
      - COLLECTOR_OTLP_ENABLED=true
    ports:
      - "16686:16686"
      - "4317:4317"
```

## Monitoring Best Practices

1. **Set up alerts** for critical metrics (error rate, latency, downtime)
2. **Monitor dashboards** regularly to understand system behavior
3. **Use distributed tracing** to debug slow requests
4. **Review logs** for errors and warnings
5. **Track business metrics** (complaints, resolution time, user activity)
6. **Set SLOs** (Service Level Objectives) and track SLIs
7. **Regular health checks** in load balancers

## Troubleshooting

### Metrics Not Showing

1. Check middleware is enabled in `settings.py`
2. Visit `/metrics` endpoint directly
3. Check Prometheus scrape configuration
4. Verify network connectivity

### OpenTelemetry Not Working

1. Check `ENABLE_OPENTELEMETRY=True` in `.env`
2. Verify Jaeger is running on correct port
3. Check application logs for telemetry errors
4. Ensure OTLP endpoint is accessible

### Logs Not Structured

1. Set `USE_JSON_LOGGING=True` in production
2. Restart the application
3. Check log output format

## Resources

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [OpenTelemetry Python](https://opentelemetry.io/docs/instrumentation/python/)
- [Jaeger Documentation](https://www.jaegertracing.io/docs/)
- [django-prometheus](https://github.com/korfuri/django-prometheus)
- [structlog](https://www.structlog.org/)

## Support

For issues or questions:
- Create an issue on GitHub
- Contact: support@smartgriev.gov.in
