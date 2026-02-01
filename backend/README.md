# AI TTS SaaS Backend

Production-ready backend for AI Text-to-Speech SaaS with XTTS v2 integration.

## Features

- ✅ **Async Processing**: Redis + Celery for non-blocking TTS generation
- ✅ **Swappable Adapters**: TTS, Storage, and Billing adapters
- ✅ **Quota Management**: Per-plan character limits with auto-reset
- ✅ **JWT Authentication**: Secure user authentication
- ✅ **Role-Based Access**: User and Admin roles
- ✅ **Feature Flags**: Runtime configuration for voice cloning, API access
- ✅ **Production-Ready**: Docker support, proper error handling

## Quick Start

### 1. Setup Environment

```bash
cd backend
cp .env.example .env
# Edit .env with your configuration
```

### 2. Run with Docker

```bash
docker-compose up -d
```

This starts:
- PostgreSQL database
- Redis queue
- FastAPI API server (port 8000)
- Celery worker

### 3. Access API

- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

## Manual Setup (Without Docker)

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Setup Database

```bash
# PostgreSQL
createdb tts_saas

# Or use SQLite (default in .env.example)
```

### 3. Run Services

```bash
# Terminal 1: API Server
uvicorn app.main:app --reload

# Terminal 2: Celery Worker
celery -A app.workers.celery_app worker --loglevel=info

# Terminal 3: Redis (if not using Docker)
redis-server
```

## API Endpoints

### Authentication
- `POST /api/v1/auth/signup` - Register new user
- `POST /api/v1/auth/login` - Login
- `GET /api/v1/auth/me` - Get current user

### TTS
- `POST /api/v1/tts/generate` - Generate speech (async)
- `GET /api/v1/tts/jobs/{job_id}` - Get job status
- `GET /api/v1/tts/history` - Get generation history
- `GET /api/v1/tts/voices` - List available voices

### Usage
- `GET /api/v1/usage/stats` - Get usage statistics

### Admin
- `POST /api/v1/admin/feature-flags` - Update feature flags
- `GET /api/v1/admin/stats` - Platform statistics

## Architecture

```
┌─────────────┐
│   Frontend  │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  FastAPI    │
│  (API)      │
└──────┬──────┘
       │
       ├──▶ PostgreSQL (Data)
       ├──▶ Redis (Queue)
       │
       ▼
┌─────────────┐
│   Celery    │
│   Worker    │
└──────┬──────┘
       │
       ├──▶ XTTS v2 (TTS)
       └──▶ Storage (Audio)
```

## Scaling

### Single Server
- Use GPU for worker
- 1-2 worker processes
- Local storage

### Multi-Server
- Separate API and Worker services
- Multiple GPU workers
- S3 storage
- Managed PostgreSQL & Redis

## Configuration

Key environment variables:

```bash
# TTS
USE_GPU=false                    # Enable GPU
XTTS_MODEL_PATH=./models/xtts_v2
MAX_CHARS_PER_REQUEST=5000

# Feature Flags
ENABLE_VOICE_CLONING=true
ENABLE_API_ACCESS=true

# Pricing
FREE_DAILY_QUOTA=1000
STARTER_MONTHLY_QUOTA=100000
PRO_MONTHLY_QUOTA=500000
```

## Adding New TTS Engine

1. Create adapter in `app/adapters/tts/`
2. Inherit from `BaseTTS`
3. Implement all abstract methods
4. Update factory in `tts_service.py`

## Security

- JWT tokens for authentication
- Password hashing with bcrypt
- Rate limiting (configurable)
- Input validation
- SQL injection protection (SQLAlchemy)

## License

Proprietary
