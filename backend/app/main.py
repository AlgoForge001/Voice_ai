import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from app.config import get_settings
from app.models import create_tables
from app.api.v1 import auth, tts, usage, admin

settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title="AI TTS SaaS API",
    description="Production-ready Text-to-Speech API with XTTS v2",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(tts.router, prefix="/api/v1")
app.include_router(usage.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")

# Serve static files (audio)
storage_path = Path("./storage")
storage_path.mkdir(exist_ok=True)
app.mount("/storage", StaticFiles(directory=str(storage_path)), name="storage")


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    print("--- STARTUP: Initializing database ---")
    create_tables()
    print("--- STARTUP: Database tables created ---")
    print(f"--- STARTUP: Environment: {settings.ENVIRONMENT} ---")
    print(f"--- STARTUP: GPU enabled: {settings.USE_GPU} ---")
    
    # Preload IndicParler model for faster first request
    print("--- STARTUP: Preloading IndicParler model ---")
    try:
        from app.adapters.tts.indicparler import get_indicparler_adapter
        adapter = get_indicparler_adapter()
        adapter._load_model()
        print("--- STARTUP: IndicParler model ready ---")
    except Exception as e:
        print(f"--- STARTUP: Failed to preload IndicParler model: {e} ---")
        print("--- STARTUP: Model will lazy-load on first request ---")
    
    print("--- STARTUP: Application ready ---")


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "online",
        "service": "AI TTS SaaS API",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Detailed health check."""
    return {
        "status": "healthy",
        "database": "connected",
        "tts_engine": "xtts_v2",
        "gpu_available": settings.USE_GPU
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
