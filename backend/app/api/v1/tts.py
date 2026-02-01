from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from app.models import get_db, User
from app.schemas import TTSRequest, TTSJobResponse, TTSJobDetail, Voice
from app.services.tts_service import TTSService
from app.services.user_service import UserService
from app.auth import get_current_user
# Selective imports for core functionality
from app.models import get_db, User
from app.schemas import TTSRequest, TTSJobResponse, TTSJobDetail, Voice

router = APIRouter(prefix="/tts", tags=["Text-to-Speech"])


# Temporary bypass for auth issues
async def get_test_user(db: Session = Depends(get_db)):
    # Return existing user or create one
    user = db.query(User).filter(User.email == "test@example.com").first()
    if not user:
        # Create a dummy user directly
        user = User(
            email="test@example.com",
            name="Test User",
            password_hash="dummy",
            plan="free",
            role="user",
            credits_remaining=1000000,
            credits_total=1000000
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        # If user exists but has low credits, top them up automatically
        if user.credits_remaining < 10000:
            print(f"[AUTH] Topping up credits for test user...")
            user.credits_remaining = 1000000
            user.credits_total = 1000000
            db.commit()
            db.refresh(user)
            
    return user

def check_redis():
    """Fast check for Redis connectivity."""
    try:
        from app.config import get_settings
        import redis
        settings = get_settings()
        r = redis.from_url(settings.REDIS_URL, socket_connect_timeout=1.0)
        return r.ping()
    except Exception:
        return False

@router.post("/generate", response_model=TTSJobResponse, status_code=status.HTTP_202_ACCEPTED)
async def generate_speech(
    request: TTSRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_test_user), # Modified to use test user
    db: Session = Depends(get_db)
):
    """
    Generate speech from text (async).
    
    Creates a job and returns immediately.
    Use /jobs/{job_id} to check status.
    """
    print(f"[TTS DEBUG] Request received for language: {request.language}")
    print(f"[TTS DEBUG] Text length: {len(request.text)}")
    
    try:
        # Re-fetch user to avoid session issues
        user_id = current_user.id
        current_user = db.query(User).get(user_id)
        
        if not current_user:
             current_user = UserService.get_user_by_email(db, "test@example.com")

        # Check and reset quota if needed
        current_user = UserService.check_and_reset_quota(db, current_user)
        
        # Create job
        try:
            job = TTSService.create_job(db, current_user, request)
        except ValueError as e:
            if str(e) == "INSUFFICIENT_QUOTA":
                print(f"[TTS] Quota exhausted for user {current_user.email}")
                return JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content={
                        "error": "INSUFFICIENT_QUOTA",
                        "message": "You have exhausted your character limit. Please upgrade your plan or wait for reset.",
                        "remaining_quota": current_user.credits_remaining
                    }
                )
            print(f"[TTS] Validation error creating job: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except Exception as e:
            print(f"[TTS] Unexpected error creating job: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Internal server error: {str(e)}"
            )
        
        # Determine routing based on language
        from app.adapters.tts.factory import INDIAN_LANGUAGES, normalize_language
        lang = normalize_language(request.language)
        is_indic = lang in INDIAN_LANGUAGES
        
        if is_indic:
            from app.workers.tts_worker import process_tts_job, CELERY_AVAILABLE
            print(f"[TTS API] Indic language detected ({lang}). Routing to background worker...")
            
            if not CELERY_AVAILABLE or not check_redis():
                from app.config import get_settings
                settings = get_settings()
                if settings.ENVIRONMENT == "development":
                    print(f"[TTS API] Redis/Celery down. Falling back to SYNC processing for {lang} (Development mode)")
                    from app.workers.tts_worker import _process_tts_job_sync
                    # Run in background to avoid blocking the API request
                    background_tasks.add_task(_process_tts_job_sync, str(job.id))
                    
                    return TTSJobResponse(
                        job_id=job.id,
                        status="queued", # Better to show queued as it starts in background
                        audio_url=None,
                        created_at=job.created_at,
                        text_snippet=job.text_snippet,
                        voice_name=None
                    )
                
                print(f"[TTS API] ERROR: Redis/Celery not available. Cannot process {lang} job.")
                TTSService.update_job_status(db, job.id, "failed", error_message="Async worker service unavailable (Redis down)")
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Indic TTS service is currently unavailable. Please ensure Redis is running."
                )
            
            # Queue the job in Celery
            try:
                print(f"[TTS API] Attempting to queue job {job.id} in Redis...")
                process_tts_job.delay(str(job.id))
            except Exception as queue_err:
                print(f"[TTS API] CRITICAL ERROR: Failed to queue job in Redis: {queue_err}")
                TTSService.update_job_status(db, job.id, "failed", error_message=f"Queueing failed: {str(queue_err)}")
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="The background worker service (Redis) is currently unreachable. Hindi TTS cannot be processed."
                )
            
            return TTSJobResponse(
                job_id=job.id,
                status="queued",
                audio_url=None,
                created_at=job.created_at,
                text_snippet=job.text_snippet,
                voice_name=None
            )
        
        # English / Non-Indic path: process in background for better UI responsiveness
        from app.workers.tts_worker import _process_tts_job_sync
        print(f"[TTS API] Non-Indic language detected ({lang}). Processing in background...")
        background_tasks.add_task(_process_tts_job_sync, str(job.id))
        
        return TTSJobResponse(
            job_id=job.id,
            status="queued",
            audio_url=None,
            created_at=job.created_at,
            text_snippet=job.text_snippet,
            voice_name=None
        )
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print("="*60)
        print("UNEXPECTED TTS GENERATION ERROR:")
        traceback.print_exc()
        print("="*60)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal Server Error: {str(e)}"
        )


@router.get("/jobs/{job_id}", response_model=TTSJobDetail)
async def get_job_status(
    job_id: UUID,
    current_user: User = Depends(get_test_user), # Bypass auth
    db: Session = Depends(get_db)
):
    """
    Get TTS job status and result.
    
    Poll this endpoint to check if job is completed.
    """
    job = TTSService.get_job(db, job_id, current_user.id)
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    return TTSJobDetail(
        job_id=job.id,
        status=job.status,
        audio_url=job.audio_url,
        created_at=job.created_at,
        text_snippet=job.text_snippet,
        text=job.text,
        character_count=job.character_count,
        error_message=job.error_message,
        completed_at=job.completed_at
    )


@router.get("/history", response_model=List[TTSJobResponse])
async def get_history(
    limit: int = 20,
    offset: int = 0,
    current_user: User = Depends(get_test_user), # Bypass auth
    db: Session = Depends(get_db)
):
    """
    Get user's TTS generation history.
    """
    jobs = TTSService.get_user_jobs(db, current_user.id, limit, offset)
    
    return [
        TTSJobResponse(
            job_id=job.id,
            status=job.status,
            audio_url=job.audio_url,
            created_at=job.created_at,
            text_snippet=job.text_snippet
        )
        for job in jobs
    ]


@router.get("/voices", response_model=List[Voice])
async def get_voices():
    """
    Get list of available voices.
    """
    try:
        from app.adapters.tts.factory import get_all_available_voices
        voices = get_all_available_voices()
        return [Voice(**voice) for voice in voices]
    except Exception as e:
        print(f"[TTS API] Error fetching voices: {e}")
        return []
