# Scaling TTS for 10,000 Users & Multi-Language Support

## Current System Summary

### Kokoro-82M Specifications
- **Model Size**: 82M parameters (~300MB)
- **Inference Speed**: Near real-time on CPU
- **Startup Time**: 3-5 seconds
- **Memory Usage**: ~500MB RAM per instance
- **Current Limit**: 500 characters per request
- **Languages**: English (en-us), Japanese (ja), Korean (ko), Chinese (zh)
- **Voices**: 4 predefined (Sky, Adam, Bella, Michael)

---

## 🌍 Adding Multi-Language Support

### Step 1: Update Language Mapping

Kokoro supports these languages:
- **English**: `en-us`, `en-gb`
- **Japanese**: `ja`
- **Korean**: `ko`
- **Chinese**: `zh`

**Update `kokoro.py` line 119:**

```python
# Current:
lang="en-us" if language == "en" else language

# Update to support more languages:
lang_map = {
    "en": "en-us",
    "ja": "ja",
    "ko": "ko",
    "zh": "zh",
    "en-gb": "en-gb"
}
lang = lang_map.get(language, "en-us")
```

### Step 2: Add Language-Specific Voices

Different languages have different voice options. Update the voice mapping:

```python
# In kokoro.py, update get_available_voices() to include language info
def get_available_voices(self) -> list[Dict[str, Any]]:
    return [
        # English voices
        {"voice_id": "1", "name": "Sky", "language": "en", "gender": "female"},
        {"voice_id": "2", "name": "Adam", "language": "en", "gender": "male"},
        
        # Japanese voices
        {"voice_id": "5", "name": "Misaki", "language": "ja", "gender": "female"},
        
        # Add more as needed
    ]
```

### Step 3: Update Configuration

Add to `settings.py`:
```python
SUPPORTED_LANGUAGES: List[str] = ["en", "ja", "ko", "zh"]
DEFAULT_LANGUAGE: str = "en"
```

---

## 🚀 Scaling for 10,000 Concurrent Users

### Current Bottlenecks
1. **Single Server**: Can handle ~10-20 concurrent requests
2. **Synchronous Processing**: Blocks during generation
3. **No Caching**: Regenerates same text repeatedly
4. **No Load Balancing**: Single point of failure

### Scaling Strategy (3 Phases)

---

## Phase 1: Optimize Current Setup (0-100 users)

### 1.1 Enable Redis Queue (Already in code!)
```bash
# Install Redis
# Windows: Download from https://github.com/microsoftarchive/redis/releases
# Or use Docker:
docker run -d -p 6379:6379 redis:alpine

# Update .env
REDIS_URL=redis://localhost:6379/0
```

This enables async job processing - server responds immediately, workers process in background.

### 1.2 Add Response Caching
```python
# In tts_worker.py, add caching
import hashlib

def get_cache_key(text: str, voice_id: str, language: str) -> str:
    content = f"{text}:{voice_id}:{language}"
    return hashlib.md5(content.encode()).hexdigest()

# Before generating, check cache
cache_key = get_cache_key(text, voice_id, language)
cached_url = redis_client.get(f"tts:cache:{cache_key}")
if cached_url:
    return cached_url  # Skip generation!
```

**Impact**: 10x faster for repeated requests, saves compute

### 1.3 Increase Character Limit with Chunking
```python
# In kokoro.py, split long text into chunks
def _chunk_text(self, text: str, max_chars: int = 500) -> list[str]:
    """Split text into chunks at sentence boundaries."""
    sentences = text.split('. ')
    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        if len(current_chunk) + len(sentence) < max_chars:
            current_chunk += sentence + ". "
        else:
            chunks.append(current_chunk.strip())
            current_chunk = sentence + ". "
    
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks

# In generate(), process chunks and concatenate audio
```

**Impact**: Support 5000+ character requests

---

## Phase 2: Horizontal Scaling (100-1,000 users)

### 2.1 Multiple Worker Processes
```bash
# Start multiple Celery workers
celery -A app.workers.celery_app worker --concurrency=4 -n worker1@%h
celery -A app.workers.celery_app worker --concurrency=4 -n worker2@%h
celery -A app.workers.celery_app worker --concurrency=4 -n worker3@%h
```

**Impact**: 4x throughput per machine

### 2.2 Load Balancer (Nginx)
```nginx
# nginx.conf
upstream backend {
    server 127.0.0.1:8000;
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
}

server {
    listen 80;
    location / {
        proxy_pass http://backend;
    }
}
```

Run multiple backend instances:
```bash
uvicorn app.main:app --port 8000 &
uvicorn app.main:app --port 8001 &
uvicorn app.main:app --port 8002 &
```

**Impact**: 3x capacity, high availability

### 2.3 Database Optimization
```python
# Use PostgreSQL instead of SQLite
DATABASE_URL=postgresql://user:pass@localhost/tts_db

# Add database connection pooling
# In settings.py
SQLALCHEMY_POOL_SIZE: int = 20
SQLALCHEMY_MAX_OVERFLOW: int = 40
```

**Impact**: Handle 1000+ concurrent DB operations

---

## Phase 3: Cloud Infrastructure (1,000-10,000 users)

### 3.1 Cloud Architecture

```
                    ┌─────────────┐
                    │ CloudFlare  │ (CDN + DDoS protection)
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │   AWS ALB   │ (Load Balancer)
                    └──────┬──────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
   ┌────▼────┐        ┌────▼────┐       ┌────▼────┐
   │ API     │        │ API     │       │ API     │
   │ Server  │        │ Server  │       │ Server  │
   │ (EC2)   │        │ (EC2)   │       │ (EC2)   │
   └────┬────┘        └────┬────┘       └────┬────┘
        │                  │                  │
        └──────────────────┼──────────────────┘
                           │
                    ┌──────▼──────┐
                    │   Redis     │ (ElastiCache)
                    │   Cluster   │
                    └──────┬──────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
   ┌────▼────┐        ┌────▼────┐       ┌────▼────┐
   │ Worker  │        │ Worker  │       │ Worker  │
   │ (EC2)   │        │ (EC2)   │       │ (EC2)   │
   └────┬────┘        └────┬────┘       └────┬────┘
        │                  │                  │
        └──────────────────┼──────────────────┘
                           │
                    ┌──────▼──────┐
                    │     S3      │ (Audio Storage)
                    └─────────────┘
```

### 3.2 Infrastructure Specs

**API Servers** (Auto-scaling 3-10 instances)
- Instance: AWS t3.medium (2 vCPU, 4GB RAM)
- Cost: ~$30/month each
- Handles: ~100 requests/sec each

**Worker Servers** (Auto-scaling 5-20 instances)
- Instance: AWS c6i.xlarge (4 vCPU, 8GB RAM)
- Cost: ~$120/month each
- Handles: ~50 TTS generations/min each

**Database**
- AWS RDS PostgreSQL (db.t3.large)
- Cost: ~$150/month
- Handles: 10,000+ connections

**Redis**
- AWS ElastiCache (cache.t3.medium)
- Cost: ~$50/month
- Handles: 100,000+ ops/sec

**Storage**
- AWS S3 for audio files
- Cost: ~$0.023/GB/month
- CDN: CloudFront for fast delivery

### 3.3 Cost Estimation (10,000 users)

Assuming average usage: 10 requests/user/day

**Monthly Costs:**
- API Servers (5x t3.medium): $150
- Workers (10x c6i.xlarge): $1,200
- Database (RDS): $150
- Redis (ElastiCache): $50
- S3 Storage (1TB): $23
- CloudFront CDN: $85
- **Total: ~$1,660/month**

**Per User Cost**: $0.17/month

---

## 🔥 Performance Optimizations

### 1. Model Optimization
```python
# Use quantized model (80MB instead of 300MB)
# Faster loading, less memory
# Download from: kokoro-v1.0-q8.onnx
```

### 2. Audio Compression
```python
# In worker, compress audio before storage
from pydub import AudioSegment

audio = AudioSegment.from_wav(wav_path)
audio.export(mp3_path, format="mp3", bitrate="64k")  # Smaller files
```

### 3. Streaming Response
```python
# Stream audio chunks as they're generated
# User hears audio faster
async def stream_audio(text: str):
    chunks = chunk_text(text)
    for chunk in chunks:
        audio = await generate(chunk)
        yield audio  # Stream to user
```

### 4. Rate Limiting
```python
# In API, add rate limiting
from slowapi import Limiter

limiter = Limiter(key_func=get_remote_address)

@app.post("/tts/generate")
@limiter.limit("10/minute")  # 10 requests per minute per user
async def generate_speech(...):
    ...
```

---

## 📊 Monitoring & Metrics

### Essential Metrics to Track
1. **Request Rate**: Requests/second
2. **Generation Time**: Average time per TTS job
3. **Queue Length**: Pending jobs in Redis
4. **Error Rate**: Failed generations
5. **Cache Hit Rate**: % of cached responses
6. **Server CPU/Memory**: Resource usage

### Tools
- **Prometheus**: Metrics collection
- **Grafana**: Dashboards
- **Sentry**: Error tracking
- **DataDog**: Full observability

---

## 🎯 Quick Wins (Implement Today)

1. **Enable Redis Queue** → 10x concurrent capacity
2. **Add Response Caching** → 5x faster for repeats
3. **Implement Rate Limiting** → Prevent abuse
4. **Add Monitoring** → Know when to scale

---

## 📝 Next Steps

**Week 1**: Optimize current setup
- [ ] Enable Redis queue
- [ ] Add response caching
- [ ] Implement rate limiting

**Week 2**: Horizontal scaling
- [ ] Multiple workers
- [ ] Load balancer
- [ ] PostgreSQL migration

**Week 3**: Cloud deployment
- [ ] Deploy to AWS/GCP
- [ ] Auto-scaling setup
- [ ] CDN for audio delivery

**Week 4**: Monitoring & optimization
- [ ] Set up monitoring
- [ ] Performance testing
- [ ] Cost optimization

---

## 🌐 Alternative: Use Cloud TTS Services

If scaling becomes too complex, consider:

**Google Cloud TTS**
- 1M characters/month free
- $4 per 1M characters after
- 380+ voices, 50+ languages
- No infrastructure management

**AWS Polly**
- Similar pricing
- Neural voices available
- Easy integration

**Pros**: No scaling headaches, better quality
**Cons**: Ongoing costs, vendor lock-in

---

## Summary

**For 10,000 users:**
- Start with Redis + caching (handles 100 users)
- Add workers + load balancer (handles 1,000 users)
- Move to cloud with auto-scaling (handles 10,000+ users)
- Expected cost: ~$1,660/month (~$0.17/user)

**Multi-language:**
- Kokoro supports en, ja, ko, zh out of the box
- Just update language mapping in code
- Add language-specific voices as needed

Need help implementing any of these? Let me know!
