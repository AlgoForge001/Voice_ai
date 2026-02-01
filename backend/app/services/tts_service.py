from sqlalchemy.orm import Session
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from app.models import TTSJob, User, UsageLog
from app.schemas import TTSRequest
from app.config import get_settings, PRICING_TIERS

settings = get_settings()


class TTSService:
    """
    TTS service for job management and validation.
    
    Responsibilities:
    - Create and validate TTS jobs
    - Track job status
    - Enforce quota and limits
    """
    
    @staticmethod
    def validate_request(user: User, request: TTSRequest) -> tuple[bool, Optional[str]]:
        """
        Validate TTS request against user's plan and limits.
        
        Returns:
            (is_valid, error_message)
        """
        # Development Bypass: Always allow in development
        if settings.ENVIRONMENT == "development":
            print(f"[QUOTA] Development bypass enabled for user {user.email}")
            return True, None

        # Check character limit
        char_count = len(request.text)
        if char_count > settings.MAX_CHARS_PER_REQUEST:
            return False, f"Text exceeds maximum length of {settings.MAX_CHARS_PER_REQUEST} characters"
        
        # Calculate weighted cost
        from app.adapters.tts.factory import INDIAN_LANGUAGES, normalize_language
        lang = normalize_language(request.language)
        cost = char_count
        if lang in INDIAN_LANGUAGES:
            cost = int(char_count * settings.INDIC_LANGUAGE_MULTIPLIER)

        # Check quota
        if not user.has_quota(cost):
            return False, "Insufficient quota. Please upgrade your plan or wait for quota reset."
        
        # Check voice cloning permission
        if request.speaker_wav_url and not settings.ENABLE_VOICE_CLONING:
            return False, "Voice cloning is currently disabled"
        
        tier = PRICING_TIERS.get(user.plan, PRICING_TIERS["free"])
        if request.speaker_wav_url and not tier["voice_cloning"]:
            return False, f"Voice cloning not available on {user.plan} plan"
        
        return True, None
    
    @staticmethod
    def create_job(db: Session, user: User, request: TTSRequest) -> TTSJob:
        """
        Create a new TTS job.
        
        This does NOT generate audio - it creates a job record
        and pushes it to the queue for async processing.
        """
        # Validate request
        is_valid, error = TTSService.validate_request(user, request)
        if not is_valid:
            # Standardized error message for frontend
            if "Insufficient quota" in error:
                raise ValueError("INSUFFICIENT_QUOTA")
            raise ValueError(error)
        
        # Get priority based on plan
        tier = PRICING_TIERS.get(user.plan, PRICING_TIERS["free"])
        priority = tier["priority"]
        
        # Calculate cost (weighted by language)
        char_count = len(request.text)
        from app.adapters.tts.factory import INDIAN_LANGUAGES, normalize_language
        lang = normalize_language(request.language)
        cost = char_count
        if lang in INDIAN_LANGUAGES:
            cost = int(char_count * settings.INDIC_LANGUAGE_MULTIPLIER)

        # Create job
        job = TTSJob(
            user_id=user.id,
            text=request.text,
            voice_id=request.voice_id,
            language=request.language,
            voice_age=request.voice_age,
            prosody_preset=request.prosody_preset,
            speaker_wav_url=request.speaker_wav_url,
            character_count=cost, # Store the weighted cost for deduction
            settings=request.settings,
            status="queued",
            priority=priority
        )
        
        db.add(job)
        db.commit()
        db.refresh(job)
        
        # Log usage
        usage_log = UsageLog(
            user_id=user.id,
            job_id=job.id,
            characters_used=cost
        )
        db.add(usage_log)
        db.commit()
        
        return job
    
    @staticmethod
    def get_job(db: Session, job_id: UUID, user_id: UUID) -> Optional[TTSJob]:
        """
        Get job by ID (user can only access their own jobs).
        """
        return db.query(TTSJob).filter(
            TTSJob.id == job_id,
            TTSJob.user_id == user_id
        ).first()
    
    @staticmethod
    def get_user_jobs(
        db: Session,
        user_id: UUID,
        limit: int = 20,
        offset: int = 0
    ) -> List[TTSJob]:
        """
        Get user's job history.
        """
        return db.query(TTSJob).filter(
            TTSJob.user_id == user_id
        ).order_by(TTSJob.created_at.desc()).limit(limit).offset(offset).all()
    
    @staticmethod
    def update_job_status(
        db: Session,
        job_id: UUID,
        status: str,
        audio_url: Optional[str] = None,
        error_message: Optional[str] = None
    ):
        """
        Update job status (called by worker).
        """
        job = db.query(TTSJob).filter(TTSJob.id == job_id).first()
        if not job:
            raise ValueError(f"Job {job_id} not found")
        
        job.status = status
        
        if status == "processing":
            job.started_at = datetime.utcnow()
        elif status in ["completed", "failed"]:
            job.completed_at = datetime.utcnow()
        
        if audio_url:
            job.audio_url = audio_url
        
        if error_message:
            job.error_message = error_message
        
        db.commit()
        db.refresh(job)
        
        return job
