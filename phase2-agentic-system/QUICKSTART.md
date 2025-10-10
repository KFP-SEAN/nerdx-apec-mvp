# Quick Start Guide - Phase 2: Agentic System

## 1. Prerequisites

Before you begin, ensure you have:

- Python 3.11 or higher
- Redis 6.0+ (or Docker)
- OpenAI API key with Sora access
- AWS credentials (for S3 storage) or use local storage for testing

## 2. Installation

### Option A: Local Development

```bash
# Navigate to the project directory
cd /c/Users/seans/nerdx-apec-mvp/phase2-agentic-system

# Install dependencies
pip install -r requirements.txt

# Copy and configure environment variables
cp .env.example .env
# Edit .env with your API keys and credentials

# Start Redis (if not using Docker)
redis-server --port 6379
```

### Option B: Docker (Recommended)

```bash
# Navigate to the project directory
cd /c/Users/seans/nerdx-apec-mvp/phase2-agentic-system

# Copy and configure environment variables
cp .env.example .env
# Edit .env with your API keys

# Start all services
docker-compose up -d

# Check logs
docker-compose logs -f phase2-api
```

## 3. Configuration

Edit your `.env` file with the following required settings:

```bash
# Essential Configuration
OPENAI_API_KEY=sk-your-actual-api-key-here
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_S3_BUCKET=your-bucket-name

# For local testing without AWS
STORAGE_PROVIDER=local  # Use 'aws' for production
```

## 4. Start the Application

### Local:
```bash
python main.py
```

### Docker:
```bash
docker-compose up
```

The API will be available at: **http://localhost:8002**

## 5. Verify Installation

### Check Health Status
```bash
curl http://localhost:8002/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "phase2-agentic-system"
}
```

### Check Detailed Health
```bash
curl http://localhost:8002/health/detailed
```

## 6. Test the API

Run the included test script:
```bash
python test_api.py
```

Or test manually:

### Generate a CAMEO Video

```bash
curl -X POST http://localhost:8002/api/v1/cameo/generate \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "demo_user",
    "user_face_image": "https://example.com/face.jpg",
    "template": "sam_altman_apec",
    "prompt": "Create a professional video of me discussing AI at APEC",
    "duration": 15,
    "quality": "high"
  }'
```

Response:
```json
{
  "job_id": "job_abc123",
  "user_id": "demo_user",
  "status": "queued",
  "message": "Video generation queued successfully",
  "created_at": "2025-10-10T12:00:00Z",
  "estimated_completion_time": 120,
  "queue_position": 1
}
```

### Check Video Status

```bash
curl http://localhost:8002/api/v1/cameo/status/job_abc123
```

### List User Videos

```bash
curl http://localhost:8002/api/v1/cameo/videos/demo_user
```

## 7. Interactive API Documentation

FastAPI provides interactive API documentation at:

- **Swagger UI**: http://localhost:8002/docs
- **ReDoc**: http://localhost:8002/redoc

You can test all endpoints directly from the browser!

## 8. Common Commands

Using the included Makefile:

```bash
# Install dependencies
make install

# Run locally
make run

# Run tests
make test

# Test API
make test-api

# Build Docker image
make docker-build

# Run with Docker
make docker-run

# Stop Docker containers
make docker-stop

# View logs
make docker-logs

# Clean temporary files
make clean
```

## 9. Example Workflow

### Step 1: Generate a Video
```python
import httpx
import asyncio

async def generate_video():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8002/api/v1/cameo/generate",
            json={
                "user_id": "user_123",
                "user_face_image": "https://example.com/my-face.jpg",
                "template": "sam_altman_apec",
                "prompt": "Announce our new AI product at APEC",
                "duration": 30,
                "quality": "high"
            }
        )
        result = response.json()
        return result["job_id"]

job_id = asyncio.run(generate_video())
print(f"Job created: {job_id}")
```

### Step 2: Poll for Completion
```python
import time

async def wait_for_video(job_id):
    async with httpx.AsyncClient() as client:
        while True:
            response = await client.get(
                f"http://localhost:8002/api/v1/cameo/status/{job_id}"
            )
            status = response.json()

            print(f"Status: {status['status']} - {status['progress']}%")

            if status['status'] == 'completed':
                print(f"Video URL: {status['video_url']}")
                return status
            elif status['status'] == 'failed':
                print(f"Error: {status['error_message']}")
                return None

            time.sleep(5)

video = asyncio.run(wait_for_video(job_id))
```

## 10. Monitoring

### Prometheus Metrics
```bash
curl http://localhost:8002/metrics
```

### Queue Status
```bash
curl http://localhost:8002/api/v1/cameo/queue/status
```

### Storage Stats
```bash
curl http://localhost:8002/api/v1/admin/storage/stats
```

## 11. Troubleshooting

### API won't start
- Check Redis is running: `redis-cli ping`
- Verify .env file has correct settings
- Check logs for errors

### Video generation fails
- Verify OpenAI API key is valid
- Check Sora API quota
- Review logs: `docker-compose logs -f phase2-api`

### Redis connection error
```bash
# Using Docker
docker-compose restart redis

# Using local Redis
redis-server --port 6379
```

### Storage upload fails
- Verify AWS credentials
- Check S3 bucket permissions
- Use `STORAGE_PROVIDER=local` for testing

## 12. Development Tips

### Enable Debug Logging
Add to `.env`:
```bash
LOG_LEVEL=DEBUG
```

### Use Local Storage
For testing without AWS:
```bash
STORAGE_PROVIDER=local
```

### Test with curl
```bash
# Health check
curl http://localhost:8002/health

# Generate video
curl -X POST http://localhost:8002/api/v1/cameo/generate \
  -H "Content-Type: application/json" \
  -d @examples/request.json

# Check status
curl http://localhost:8002/api/v1/cameo/status/job_xxx
```

## 13. Next Steps

1. Read the full [README.md](README.md) for detailed documentation
2. Explore the API at http://localhost:8002/docs
3. Check out example requests in `examples/`
4. Review the architecture in `/docs/architecture/`
5. Join the development Slack/Discord channel

## 14. Support

- **Issues**: Report bugs on GitHub Issues
- **Documentation**: http://localhost:8002/docs
- **Examples**: See `examples/` directory
- **Tests**: Run `python test_api.py`

## 15. Security Notes

- Never commit `.env` file
- Rotate API keys regularly
- Use IAM roles in production
- Enable S3 encryption
- Implement rate limiting per IP (not just user)

---

**Ready to build amazing personalized videos!**

For more information, see the [complete documentation](README.md).
