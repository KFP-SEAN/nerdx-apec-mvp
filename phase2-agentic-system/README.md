# Phase 2: Agentic System (Sora + CAMEO)

## Overview

Phase 2 implements a personalized video generation system using OpenAI's Sora 2 API with CAMEO-style template integration. This service allows users to create professional videos featuring their own face combined with templates (e.g., Sam Altman at APEC).

## Architecture

```
┌─────────────────┐
│   FastAPI App   │
│   (main.py)     │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
┌───▼───┐ ┌──▼────────┐
│ CAMEO │ │   Queue   │
│Service│ │  (Redis)  │
└───┬───┘ └───────────┘
    │
┌───┴────┐
│  Sora  │
│Service │
└───┬────┘
    │
┌───▼────────┐
│  Storage   │
│ (S3/CDN)   │
└────────────┘
```

## Features

### Core Functionality
- **CAMEO Video Generation**: Personalized videos with user face + templates
- **Sora 2 Integration**: High-quality video generation using OpenAI's Sora 2 API
- **Template System**: Pre-built templates (Sam Altman APEC, fireside chat, etc.)
- **Queue Management**: Redis-based job queue for scalable processing
- **Rate Limiting**: Per-user daily limits to prevent abuse
- **CDN Delivery**: Automatic upload to S3/CloudFront for fast delivery

### Video Processing Pipeline
1. **Face Image Processing**: Upload and validate user face images
2. **Prompt Enhancement**: Template-based prompt engineering
3. **Sora Generation**: Video generation via Sora 2 API
4. **Post-Processing**: Thumbnail generation and optimization
5. **Storage Upload**: Automatic CDN upload with metadata
6. **Status Tracking**: Real-time job status and progress updates

## API Endpoints

### Video Generation

#### Generate CAMEO Video
```http
POST /api/v1/cameo/generate
Content-Type: application/json

{
  "user_id": "user_123",
  "user_face_image": "https://example.com/face.jpg",
  "template": "sam_altman_apec",
  "prompt": "Create a professional video of me discussing AI innovations at APEC",
  "duration": 30,
  "quality": "high",
  "resolution": "1920x1080",
  "audio_enabled": true
}
```

**Response**: `202 Accepted`
```json
{
  "job_id": "job_abc123",
  "user_id": "user_123",
  "status": "queued",
  "message": "Video generation queued successfully",
  "created_at": "2025-10-10T12:00:00Z",
  "estimated_completion_time": 120,
  "queue_position": 3
}
```

#### Get Video Status
```http
GET /api/v1/cameo/status/{job_id}
```

**Response**: `200 OK`
```json
{
  "job_id": "job_abc123",
  "user_id": "user_123",
  "status": "completed",
  "progress": 100,
  "message": "Video generated successfully",
  "created_at": "2025-10-10T12:00:00Z",
  "updated_at": "2025-10-10T12:02:30Z",
  "completed_at": "2025-10-10T12:02:30Z",
  "video_url": "https://cdn.nerdx.com/videos/job_abc123.mp4",
  "thumbnail_url": "https://cdn.nerdx.com/thumbnails/job_abc123.jpg",
  "duration": 30,
  "file_size": 15728640,
  "metadata": {
    "template": "sam_altman_apec",
    "quality": "high",
    "resolution": "1920x1080"
  }
}
```

#### List User Videos
```http
GET /api/v1/cameo/videos/{user_id}?page=1&page_size=10
```

#### Cancel Video Generation
```http
POST /api/v1/cameo/cancel/{job_id}?user_id={user_id}
```

### Queue Management

#### Get Queue Status
```http
GET /api/v1/cameo/queue/status
```

**Response**:
```json
{
  "total_jobs": 15,
  "pending_jobs": 5,
  "processing_jobs": 3,
  "completed_jobs": 6,
  "failed_jobs": 1,
  "average_processing_time": 145.5
}
```

### Rate Limiting

#### Get Rate Limit Info
```http
GET /api/v1/cameo/rate-limit/{user_id}
```

**Response**:
```json
{
  "user_id": "user_123",
  "videos_generated_today": 3,
  "max_videos_per_day": 5,
  "remaining_quota": 2,
  "reset_at": "2025-10-11T00:00:00Z"
}
```

## Installation

### Prerequisites
- Python 3.11+
- Redis 6.0+
- AWS S3 account (or local storage for development)
- OpenAI API key with Sora 2 access

### Local Development

1. **Clone the repository**
```bash
cd /c/Users/seans/nerdx-apec-mvp/phase2-agentic-system
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your credentials
```

4. **Start Redis**
```bash
redis-server --port 6379
```

5. **Run the application**
```bash
python main.py
```

The API will be available at `http://localhost:8002`

### Docker Deployment

1. **Build the image**
```bash
docker build -t nerdx-phase2-agentic:latest .
```

2. **Run the container**
```bash
docker run -d \
  --name phase2-agentic \
  -p 8002:8002 \
  --env-file .env \
  nerdx-phase2-agentic:latest
```

3. **Check logs**
```bash
docker logs -f phase2-agentic
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key | Required |
| `SORA_MODEL` | Sora model version | `sora-2` |
| `AWS_ACCESS_KEY_ID` | AWS access key | Required for S3 |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key | Required for S3 |
| `AWS_S3_BUCKET` | S3 bucket name | `nerdx-videos` |
| `REDIS_HOST` | Redis hostname | `localhost` |
| `REDIS_PORT` | Redis port | `6379` |
| `MAX_CAMEO_PER_USER_PER_DAY` | Rate limit | `5` |
| `CAMEO_MAX_QUEUE_SIZE` | Max queue size | `100` |

### Video Quality Settings

| Quality | Resolution | Bitrate | Est. Size (30s) |
|---------|-----------|---------|-----------------|
| `low` | 1280x720 | 2 Mbps | ~8 MB |
| `medium` | 1920x1080 | 4 Mbps | ~15 MB |
| `high` | 1920x1080 | 8 Mbps | ~30 MB |
| `maximum` | 3840x2160 | 16 Mbps | ~60 MB |

## CAMEO Templates

### Available Templates

#### 1. Sam Altman - APEC Summit
**Template ID**: `sam_altman_apec`

Professional presentation style with:
- Corporate staging and professional lighting
- Business casual attire
- Executive audience context
- High-quality production values

**Best for**: Professional presentations, product announcements, corporate communications

#### 2. Sam Altman - Fireside Chat
**Template ID**: `sam_altman_fireside`

Conversational style with:
- Warm, intimate lighting
- Comfortable modern setting
- Natural, engaging conversation
- Casual yet professional atmosphere

**Best for**: Interviews, Q&A sessions, thought leadership content

## Rate Limiting

### Per-User Limits
- **Default**: 5 videos per user per day
- **Resets**: Daily at midnight UTC
- **Configurable**: Via `MAX_CAMEO_PER_USER_PER_DAY`

### Queue Limits
- **Max Queue Size**: 100 concurrent jobs
- **Processing Timeout**: 600 seconds (10 minutes)
- **Response**: `503 Service Unavailable` when full

## Error Handling

### Common Error Codes

| Code | Error | Description |
|------|-------|-------------|
| `429` | RateLimitExceeded | Daily video limit reached |
| `503` | QueueFull | Processing queue at capacity |
| `400` | InvalidRequest | Invalid parameters or image |
| `404` | JobNotFound | Job ID doesn't exist |
| `500` | ServiceError | Internal service error |

### Error Response Format
```json
{
  "error": "RateLimitExceeded",
  "message": "You have exceeded the maximum number of videos per day",
  "details": {
    "max_videos_per_day": 5,
    "videos_generated_today": 5
  },
  "timestamp": "2025-10-10T12:00:00Z"
}
```

## Monitoring

### Health Checks

**Basic Health**
```bash
curl http://localhost:8002/health
```

**Detailed Health**
```bash
curl http://localhost:8002/health/detailed
```

### Prometheus Metrics

Available at `/metrics`:

- `video_generation_total` - Total generation requests
- `video_generation_duration_seconds` - Generation duration histogram
- `api_requests_total` - API request counter

### Logging

Structured JSON logging with levels:
- `INFO`: Normal operations
- `ERROR`: Service errors
- `DEBUG`: Detailed debugging (set `LOG_LEVEL=DEBUG`)

## Storage Architecture

### S3 Structure
```
nerdx-videos/
├── videos/
│   └── {user_id}/
│       └── {year}/{month}/{day}/
│           └── {job_id}.mp4
├── thumbnails/
│   └── {user_id}/
│       └── {year}/{month}/{day}/
│           └── {job_id}.jpg
└── faces/
    └── {user_id}/
        └── {job_id}.jpg
```

### CDN Integration
- CloudFront distribution for global delivery
- Automatic cache invalidation
- Signed URLs for private content (optional)
- Multi-region replication (optional)

## Performance Optimization

### Queue Processing
- Concurrent job processing (configurable)
- Priority queues for premium users (future)
- Automatic retry on transient failures

### Storage Optimization
- Video compression without quality loss
- Lazy thumbnail generation
- Automatic cleanup of old videos (configurable)

### Caching
- Redis caching for job status
- CDN edge caching for videos
- Face image caching

## Testing

### Run Tests
```bash
pytest tests/ -v
```

### Test Coverage
```bash
pytest --cov=services --cov=models tests/
```

### Integration Tests
```bash
pytest tests/integration/ -v
```

## Security

### Best Practices
- API key rotation
- S3 bucket encryption (AES256)
- Private S3 buckets with CDN access only
- Rate limiting per user/IP
- Input validation and sanitization
- Face image validation and scanning

### Compliance
- GDPR: User data deletion support
- Privacy: Face images encrypted at rest
- Content moderation: Integration ready

## Troubleshooting

### Common Issues

**1. Redis Connection Failed**
```bash
# Check Redis is running
redis-cli ping
# Should return PONG
```

**2. Sora API Errors**
- Verify API key is valid
- Check API quota and billing
- Review rate limits

**3. S3 Upload Failures**
- Verify AWS credentials
- Check bucket permissions
- Confirm bucket exists

**4. Video Generation Timeout**
- Increase `CAMEO_PROCESSING_TIMEOUT`
- Check Sora API response times
- Monitor network connectivity

## Roadmap

### Phase 2.1 - Enhancements
- [ ] Multiple face detection and swapping
- [ ] Custom template builder
- [ ] Voice cloning integration
- [ ] Batch video generation
- [ ] Webhook notifications

### Phase 2.2 - Advanced Features
- [ ] Real-time preview generation
- [ ] Video editing capabilities
- [ ] Multi-language support
- [ ] Advanced analytics
- [ ] A/B testing framework

## Support

### Documentation
- API Docs: http://localhost:8002/docs
- Project Wiki: [Link to wiki]
- Architecture Diagrams: `/docs/architecture/`

### Contact
- Technical Issues: [GitHub Issues]
- General Questions: [Slack/Discord]
- Security: security@nerdx.com

## License

Proprietary - NERDX APEC MVP Project

---

**Built with**: FastAPI, Sora 2, Redis, AWS S3, Docker
**Last Updated**: October 10, 2025
**Version**: 1.0.0
