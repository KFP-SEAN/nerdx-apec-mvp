# Installation Verification Checklist

## Phase 2: Agentic System - Complete Setup Verification

Use this checklist to ensure all components are properly installed and configured.

## 📋 Pre-Installation Checklist

- [ ] Python 3.11+ installed
- [ ] Docker installed (optional but recommended)
- [ ] Redis installed or Docker available
- [ ] OpenAI API key with Sora access
- [ ] AWS credentials (or plan to use local storage)
- [ ] Git repository access

## 📁 File Structure Verification

### Core Files
- [x] `main.py` - FastAPI application (15KB)
- [x] `config.py` - Configuration management (1.3KB)
- [x] `requirements.txt` - Python dependencies (599B)
- [x] `Dockerfile` - Docker image definition (959B)
- [x] `docker-compose.yml` - Docker orchestration (1.6KB)
- [x] `Makefile` - Build automation (2.1KB)

### Services (services/)
- [x] `services/sora_service.py` - Sora 2 API integration
- [x] `services/cameo_service.py` - CAMEO pipeline
- [x] `services/storage_service.py` - S3/CDN storage
- [x] `services/__init__.py` - Service exports

### Models (models/)
- [x] `models/cameo_models.py` - Pydantic models
- [x] `models/__init__.py` - Model exports

### Documentation
- [x] `README.md` - Complete documentation (12KB)
- [x] `QUICKSTART.md` - Quick start guide (7KB)
- [x] `PROJECT_SUMMARY.md` - Project overview (11KB)
- [x] `INSTALLATION_CHECKLIST.md` - This file

### Configuration
- [x] `.env.example` - Environment template
- [x] `.gitignore` - Git ignore rules
- [x] `.dockerignore` - Docker ignore rules

### Testing & Examples
- [x] `test_api.py` - API test suite
- [x] `examples/request_basic.json`
- [x] `examples/request_fireside.json`
- [x] `examples/request_custom.json`
- [x] `examples/test_requests.sh`

## 🔧 Configuration Checklist

### Environment Setup
- [ ] Copied `.env.example` to `.env`
- [ ] Set `OPENAI_API_KEY`
- [ ] Set `AWS_ACCESS_KEY_ID` (or use local storage)
- [ ] Set `AWS_SECRET_ACCESS_KEY` (or use local storage)
- [ ] Set `AWS_S3_BUCKET` (or use local storage)
- [ ] Configured `STORAGE_PROVIDER` (aws/local)
- [ ] Set `REDIS_HOST` and `REDIS_PORT`
- [ ] Reviewed rate limiting settings

### Dependency Installation
- [ ] Installed Python packages: `pip install -r requirements.txt`
- [ ] Verified all packages installed successfully
- [ ] No dependency conflicts

## 🐳 Docker Setup (Recommended)

- [ ] Docker daemon is running
- [ ] Docker Compose installed
- [ ] Built Docker image: `make docker-build`
- [ ] No build errors
- [ ] Image size is reasonable (~500MB-1GB)

## 🚀 Service Startup Checklist

### Redis
- [ ] Redis is running (Docker or local)
- [ ] Can connect to Redis: `redis-cli ping` returns `PONG`
- [ ] Redis port 6379 is accessible

### Application
- [ ] Started application: `make docker-run` or `python main.py`
- [ ] No startup errors in logs
- [ ] Application listening on port 8002
- [ ] Health check passes: `curl http://localhost:8002/health`

## ✅ Verification Tests

### Basic Health Checks
```bash
# Should return: {"status": "healthy", "service": "phase2-agentic-system"}
curl http://localhost:8002/health
```
- [ ] Health check returns 200 OK
- [ ] Response JSON is valid

### Detailed Health Check
```bash
curl http://localhost:8002/health/detailed
```
- [ ] Sora API status shown
- [ ] Storage status shown
- [ ] Redis status shown
- [ ] All services report "healthy" or "degraded" (not "error")

### API Documentation
```bash
# Open in browser
http://localhost:8002/docs
```
- [ ] Swagger UI loads
- [ ] All endpoints visible
- [ ] Can expand endpoint details
- [ ] Example requests shown

### Queue Status
```bash
curl http://localhost:8002/api/v1/cameo/queue/status
```
- [ ] Returns valid JSON
- [ ] Shows queue metrics (pending, processing, etc.)

### Configuration Check
```bash
curl http://localhost:8002/api/v1/admin/config
```
- [ ] Returns configuration
- [ ] Settings are correct
- [ ] No sensitive data exposed

## 🧪 Functional Tests

### Test Suite
```bash
python test_api.py
```
- [ ] All tests pass
- [ ] No connection errors
- [ ] Health checks succeed
- [ ] Queue status works

### Example Requests
```bash
# Test basic video generation
curl -X POST http://localhost:8002/api/v1/cameo/generate \
  -H "Content-Type: application/json" \
  -d @examples/request_basic.json
```
- [ ] Request accepted (202 response)
- [ ] Job ID returned
- [ ] No errors in response

### Status Check
```bash
# Replace JOB_ID with actual job ID from above
curl http://localhost:8002/api/v1/cameo/status/JOB_ID
```
- [ ] Returns job status
- [ ] Status is valid (queued/processing/completed/failed)
- [ ] Progress percentage present

## 📊 Monitoring Checks

### Prometheus Metrics
```bash
curl http://localhost:8002/metrics
```
- [ ] Metrics endpoint accessible
- [ ] Returns Prometheus format
- [ ] Video generation metrics present
- [ ] API request metrics present

### Logging
- [ ] Logs are being written
- [ ] Log format is structured
- [ ] Log level is appropriate (INFO for production)
- [ ] Errors are logged with details

## 🔒 Security Checklist

- [ ] `.env` file is not committed to Git
- [ ] API keys are not exposed in logs
- [ ] S3 bucket has proper permissions
- [ ] CORS is configured appropriately
- [ ] Rate limiting is enabled
- [ ] Input validation is working

## 🚨 Troubleshooting Verification

### If Health Check Fails
- [ ] Check application logs: `docker-compose logs -f phase2-api`
- [ ] Verify Redis is running: `docker-compose ps`
- [ ] Check .env configuration
- [ ] Verify all required environment variables set

### If Sora API Fails
- [ ] Verify OpenAI API key is valid
- [ ] Check API quota and billing
- [ ] Review Sora API endpoint configuration
- [ ] Check network connectivity

### If Storage Fails
- [ ] Verify AWS credentials (if using S3)
- [ ] Check S3 bucket exists and is accessible
- [ ] Try local storage for testing: `STORAGE_PROVIDER=local`
- [ ] Check storage service logs

### If Redis Connection Fails
- [ ] Verify Redis is running
- [ ] Check Redis host/port in .env
- [ ] Test connection: `redis-cli -h HOST -p PORT ping`
- [ ] Check firewall rules

## 📈 Performance Verification

### Load Test (Optional)
- [ ] Can handle multiple concurrent requests
- [ ] Queue manages jobs appropriately
- [ ] Rate limiting works correctly
- [ ] No memory leaks after extended operation

### Resource Usage
- [ ] CPU usage is reasonable (<50% idle)
- [ ] Memory usage is stable
- [ ] Disk space sufficient for videos
- [ ] Network bandwidth adequate

## 🎯 Final Verification

### Complete System Test
1. [ ] Generate a test video
2. [ ] Wait for completion (or check status multiple times)
3. [ ] Verify video URL is returned
4. [ ] Check video can be accessed (if completed)
5. [ ] Verify storage location (S3 or local)
6. [ ] Check thumbnail was generated
7. [ ] Verify metadata is correct

### Production Readiness
- [ ] All tests pass
- [ ] No critical errors in logs
- [ ] Performance is acceptable
- [ ] Monitoring is working
- [ ] Documentation is accessible
- [ ] Backups configured (for production)
- [ ] Disaster recovery plan reviewed (for production)

## ✨ Success Criteria

The installation is successful when:

1. ✅ Application starts without errors
2. ✅ Health checks return "healthy"
3. ✅ Can generate a test video request
4. ✅ Queue management is working
5. ✅ Rate limiting functions correctly
6. ✅ Storage uploads work (S3 or local)
7. ✅ API documentation is accessible
8. ✅ Monitoring metrics are available
9. ✅ All tests pass
10. ✅ No security concerns

## 📞 Getting Help

If any items fail:

1. Check the logs: `docker-compose logs -f`
2. Review QUICKSTART.md for setup steps
3. Consult README.md troubleshooting section
4. Verify .env configuration
5. Check system requirements
6. Review error messages carefully

## 📝 Notes

- **Required for production**: All checkboxes should be ✅
- **For development**: Can skip AWS setup if using `STORAGE_PROVIDER=local`
- **For testing**: Can use mock services if Sora API not available
- **Documentation**: Keep this checklist for future deployments

---

**Installation Date**: _________________

**Verified By**: _________________

**Environment**: ☐ Development  ☐ Staging  ☐ Production

**Status**: ☐ Complete  ☐ Partial  ☐ Failed

**Notes**: _______________________________________________

________________________________________________________

________________________________________________________
