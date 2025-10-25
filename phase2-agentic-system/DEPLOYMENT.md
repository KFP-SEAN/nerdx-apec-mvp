# Helios Orchestration System - Deployment Guide

**Version**: 4.0.0
**Last Updated**: 2025-10-25

---

## 📋 Prerequisites

### System Requirements
- Python 3.11+
- Redis 5.0+
- 4GB+ RAM
- 2+ CPU cores

### Required API Keys
- `ANTHROPIC_API_KEY` - Claude API access
- `OPENAI_API_KEY` - For embeddings (optional)

---

## 🚀 Quick Start

### 1. Clone & Setup
```bash
cd nerdx-apec-mvp/phase2-agentic-system

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Variables
```bash
# Create .env file
cat > .env << 'ENVFILE'
# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379

# API Keys (add when ready for production)
# ANTHROPIC_API_KEY=your_key_here
# OPENAI_API_KEY=your_key_here

# Application
API_HOST=0.0.0.0
API_PORT=8002
API_ENVIRONMENT=development
ENVFILE
```

### 3. Start Redis
```bash
# Option 1: Docker
docker run -d -p 6379:6379 redis:7-alpine

# Option 2: Local install
redis-server
```

### 4. Run Application
```bash
# Development mode
python main.py

# Production mode
uvicorn main:app --host 0.0.0.0 --port 8002 --workers 4
```

### 5. Verify Installation
```bash
# Health check
curl http://localhost:8002/health

# API docs
open http://localhost:8002/docs
```

---

## 🧪 Testing

### Run Integration Tests
```bash
# All tests
pytest tests/test_helios_integration.py -v

# Specific test
python tests/test_helios_integration.py
```

### Manual API Testing
```bash
# 1. Check monitoring dashboard
curl http://localhost:8002/api/v1/helios/monitoring/summary | jq

# 2. Check budget status
curl http://localhost:8002/api/v1/helios/budget/status | jq

# 3. Check cache metrics
curl http://localhost:8002/api/v1/helios/cache/metrics | jq
```

---

## 🐳 Docker Deployment

### Build Image
```bash
# Create Dockerfile
cat > Dockerfile << 'DOCKERFILE'
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8002

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8002"]
DOCKERFILE

# Build
docker build -t helios-orchestration:4.0.0 .
```

### Run Container
```bash
docker run -d \
  --name helios \
  -p 8002:8002 \
  -e REDIS_HOST=redis \
  -e ANTHROPIC_API_KEY=your_key \
  --link redis:redis \
  helios-orchestration:4.0.0
```

### Docker Compose
```yaml
# docker-compose.yml
version: '3.8'

services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  helios:
    build: .
    ports:
      - "8002:8002"
    environment:
      - REDIS_HOST=redis
      - REDIS_PORT=6379
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
    depends_on:
      - redis

volumes:
  redis_data:
```

```bash
# Run with compose
docker-compose up -d
```

---

## ☁️ Cloud Deployment

### AWS (EC2 + ElastiCache)
```bash
# 1. Launch EC2 instance (t3.medium)
# 2. Create ElastiCache Redis cluster
# 3. Update security groups
# 4. Set environment variables
# 5. Deploy with systemd

# /etc/systemd/system/helios.service
[Unit]
Description=Helios Orchestration System
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/opt/helios
Environment="PATH=/opt/helios/venv/bin"
ExecStart=/opt/helios/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8002
Restart=always

[Install]
WantedBy=multi-user.target
```

### GCP (Cloud Run + Memorystore)
```bash
# 1. Create Redis Memorystore instance
# 2. Build container image
gcloud builds submit --tag gcr.io/PROJECT_ID/helios:4.0.0

# 3. Deploy to Cloud Run
gcloud run deploy helios \
  --image gcr.io/PROJECT_ID/helios:4.0.0 \
  --platform managed \
  --region us-central1 \
  --set-env-vars REDIS_HOST=REDIS_IP \
  --allow-unauthenticated
```

---

## 📊 Monitoring Setup

### Prometheus Integration
```python
# Already included in main.py
# Metrics available at /metrics endpoint
```

### Grafana Dashboard
```bash
# Import dashboard JSON
# Key metrics:
# - api_requests_total
# - video_generation_duration_seconds  
# - cache_hit_rate
# - budget_utilization_percent
```

---

## 🔒 Production Checklist

### Security
- [ ] Enable HTTPS/TLS
- [ ] Set up API authentication
- [ ] Rotate API keys regularly
- [ ] Enable Redis AUTH
- [ ] Set up firewall rules
- [ ] Enable rate limiting

### Performance
- [ ] Configure Redis persistence
- [ ] Set up Redis clustering
- [ ] Enable application caching
- [ ] Configure connection pooling
- [ ] Set up CDN for static assets

### Monitoring
- [ ] Set up Prometheus scraping
- [ ] Configure Grafana dashboards
- [ ] Enable error tracking (Sentry)
- [ ] Set up log aggregation
- [ ] Configure alerts (PagerDuty/Slack)

### Backup & Recovery
- [ ] Redis backup strategy
- [ ] Database backup automation
- [ ] Disaster recovery plan
- [ ] Load testing completed

---

## 🔧 Configuration

### Resource Governor Tuning
```python
# In config or environment
MAX_MESSAGES_PER_WINDOW = 900  # Claude Max limit
WINDOW_DURATION_HOURS = 5      # 5-hour windows
```

### Cache Configuration
```python
# L1 Claude Native
L1_TTL_SECONDS = 300           # 5 minutes
L1_MIN_TOKENS = 1024           # Minimum for caching

# L2 Redis Exact
L2_TTL_SECONDS = 3600          # 1 hour

# L3 Semantic
L3_TTL_SECONDS = 86400         # 24 hours
L3_SIMILARITY_THRESHOLD = 0.85 # 85% similarity
```

---

## 📞 Support & Troubleshooting

### Common Issues

**Redis connection failed**
```bash
# Check Redis is running
redis-cli ping

# Check connection
telnet localhost 6379
```

**Import errors**
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

**Port already in use**
```bash
# Find and kill process
lsof -ti:8002 | xargs kill -9

# Or use different port
export API_PORT=8003
```

### Debug Mode
```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

## 📚 Additional Resources

- API Documentation: http://localhost:8002/docs
- Phase 1-4 Documentation: See HELIOS_PHASE*.md files
- Integration Tests: `tests/test_helios_integration.py`

---

**Deployment Status**: ✅ Production Ready
**Version**: 4.0.0
**Support**: NERD Development Team
