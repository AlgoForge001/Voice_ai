# Full Stack AI TTS SaaS

Complete Text-to-Speech SaaS application with Next.js frontend and FastAPI backend.

## Project Structure

```
Ai/
├── frontend/          # Next.js 14 frontend
│   ├── src/
│   │   ├── app/       # App router pages
│   │   ├── components/# React components
│   │   ├── services/  # API client
│   │   └── context/   # React context
│   └── package.json
│
└── backend/           # FastAPI backend
    ├── app/
    │   ├── api/       # API routes
    │   ├── services/  # Business logic
    │   ├── adapters/  # TTS, Storage, Billing
    │   ├── workers/   # Celery workers
    │   └── models/    # Database models
    └── requirements.txt
```

## Quick Start

### 1. Start Backend

```bash
cd backend
docker-compose up -d
```

Backend will be available at `http://localhost:8000`

### 2. Start Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend will be available at `http://localhost:3000`

### 3. Access Application

1. Open `http://localhost:3000`
2. Sign up for an account
3. Start generating speech!

## Features

### Frontend
- ✅ Modern UI with Tailwind CSS
- ✅ JWT authentication
- ✅ Real-time TTS generation
- ✅ Waveform visualization
- ✅ Usage tracking

### Backend
- ✅ FastAPI + PostgreSQL
- ✅ Async TTS processing (Celery)
- ✅ XTTS v2 integration
- ✅ Quota management
- ✅ Role-based access
- ✅ Swappable adapters

## API Documentation

Once backend is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Environment Variables

### Frontend (.env.local)
```
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

### Backend (.env)
```
DATABASE_URL=postgresql://user:password@localhost:5432/tts_saas
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key
USE_GPU=false
```

## Development

### Frontend
```bash
cd frontend
npm run dev      # Development server
npm run build    # Production build
npm run lint     # Lint code
```

### Backend
```bash
cd backend
uvicorn app.main:app --reload  # API server
celery -A app.workers.celery_app worker  # Worker
```

## Production Deployment

### Frontend
Deploy to Vercel:
```bash
cd frontend
vercel
```

### Backend
Deploy with Docker:
```bash
cd backend
docker build -t tts-backend .
docker run -p 8000:8000 tts-backend
```

## Architecture

```
┌──────────┐
│ Frontend │ (Next.js)
└────┬─────┘
     │ HTTP/REST
     ▼
┌──────────┐
│ FastAPI  │ (API Server)
└────┬─────┘
     │
     ├──▶ PostgreSQL (Data)
     ├──▶ Redis (Queue)
     │
     ▼
┌──────────┐
│  Celery  │ (Worker)
└────┬─────┘
     │
     ├──▶ XTTS v2 (TTS Engine)
     └──▶ Storage (Audio Files)
```

## License

Proprietary
