from sqlalchemy.orm import Session
from uuid import UUID
import os
from pathlib import Path
# from pydub import AudioSegment
from app.models import get_db, TTSJob, User

# Celery Availability Check
CELERY_AVAILABLE = False
try:
    from app.workers.celery_app import celery_app
    # Check if we can actually reach Redis (optional, but good for early warning)
    # celery_app.connection().connect()  # Too slow for startup?
    CELERY_AVAILABLE = True
except Exception as e:
    print(f"[CELERY] Background worker queue (Redis) not available: {e}")
    celery_app = None

from app.adapters.tts.factory import INDIAN_LANGUAGES, normalize_language


# Use a dummy Task if celery not available
try:
    from celery import Task
except ImportError:
    Task = object

class DatabaseTask(Task):
    """Base task with database session management."""
    _db = None
    
    @property
    def db(self) -> Session:
        if self._db is None:
            self._db = next(get_db())
        return self._db
    
    def after_return(self, *args, **kwargs):
        if self._db is not None:
            self._db.close()


# Only register Celery task if Celery is available
if CELERY_AVAILABLE:
    @celery_app.task(base=DatabaseTask, bind=True, name="app.workers.tts_worker.process_tts_job")
    def process_tts_job(self, job_id: str):
        """
        Process TTS job asynchronously.
        
        This is the worker that actually generates audio.
        
        Flow:
        1. Get job from database
        2. Update status to 'processing'
        3. Generate audio using XTTS adapter
        4. Convert WAV to MP3
        5. Upload to storage
        6. Update job with audio URL
        7. Deduct user quota
        """
        db = self.db
        
        try:
            # Lazy imports to prevent circularity and startup hangs
            from app.services.tts_service import TTSService
            from app.services.user_service import UserService
            from app.adapters.tts.factory import get_tts_adapter
            from app.adapters.storage.local import get_storage_adapter
            
            # Get job
            job = db.query(TTSJob).filter(TTSJob.id == UUID(job_id)).first()
            if not job:
                print(f"[ASYNC WORKER] Job {job_id} not found in database")
                raise ValueError(f"Job {job_id} not found")
            
            print(f"[ASYNC WORKER] Starting job {job_id} for language: {job.language}")
            TTSService.update_job_status(db, UUID(job_id), "processing")
            
            # Get TTS adapter with language to use preloaded instance
            tts_adapter = get_tts_adapter(language=job.language)
            
            # Generate audio
            import asyncio
            wav_path = asyncio.run(tts_adapter.generate(
                text=job.text,
                voice_id=job.voice_id,
                language=job.language,
                voice_age=job.voice_age,
                prosody_preset=job.prosody_preset,
                speaker_wav_path=job.speaker_wav_url,
                settings=job.settings
            ))
            print(f"[ASYNC WORKER] Audio generation complete: {wav_path}")
            
            # Optional: Convert WAV to MP3 for smaller file size
            # Requires FFmpeg
            final_path = wav_path
            final_ext = "wav"
            
            try:
                print(f"[ASYNC WORKER] Attempting MP3 conversion for {wav_path}...")
                from pydub import AudioSegment
                mp3_path = wav_path.replace(".wav", ".mp3")
                audio = AudioSegment.from_wav(wav_path)
                audio.export(mp3_path, format="mp3", bitrate="128k")
                final_path = mp3_path
                final_ext = "mp3"
                print(f"[ASYNC WORKER] Conversion successful: {mp3_path}")
                # Cleanup WAV after conversion
                if os.path.exists(wav_path):
                    os.remove(wav_path)
            except Exception as conv_err:
                print(f"[ASYNC WORKER] MP3 conversion failed (likely missing FFmpeg): {conv_err}")
                print(f"[ASYNC WORKER] Falling back to WAV.")
                final_path = wav_path
                final_ext = "wav"
            
            # Upload to storage
            storage = get_storage_adapter()
            audio_url = asyncio.run(storage.upload_file(
                final_path,
                f"audio/{job.user_id}/{job.id}.{final_ext}"
            ))
            
            # Update job
            TTSService.update_job_status(
                db,
                UUID(job_id),
                "completed",
                audio_url=audio_url
            )
            
            # Deduct user quota
            user = db.query(User).filter(User.id == job.user_id).first()
            if user:
                UserService.deduct_quota(db, user, job.character_count)
            
            # Cleanup final file if stored locally
            if os.path.exists(final_path) and audio_url.startswith("http"):
                os.remove(final_path)
            
            print(f"[ASYNC WORKER] Job {job_id} completed successfully! URL: {audio_url}")
            return {"status": "completed", "audio_url": audio_url}
        
        except Exception as e:
            # Update job with error
            TTSService.update_job_status(
                db,
                UUID(job_id),
                "failed",
                error_message=str(e)
            )
            raise
else:
    # Dummy function when Celery is not available
    def process_tts_job(job_id: str):
        print(f"Celery not available, cannot queue job {job_id}")


# Synchronous version for bypassing Redis/Celery
def _process_tts_job_sync(job_id_str: str):
    """
    Process TTS job synchronously without Celery.
    Runs in a separate thread via FastAPI BackgroundTasks to avoid blocking the event loop.
    """
    import asyncio
    db = next(get_db())
    try:
        job_id = UUID(job_id_str)
        job = db.query(TTSJob).filter(TTSJob.id == job_id).first()
        
        if not job:
            print(f"[SYNC WORKER] Job {job_id_str} not found")
            return
        
        # --- DEVELOPMENT BYPASS: ALLOW INDIC TTS IN SYNC PATH ---
        from app.config import get_settings
        settings = get_settings()
        lang = normalize_language(job.language)
        if lang in INDIAN_LANGUAGES and settings.ENVIRONMENT != "development":
            error_msg = f"CRITICAL: Indic TTS ({lang}) is NOT allowed in synchronous path in production. Must use Celery."
            print(f"[SYNC WORKER] Access Denied: {error_msg}")
            job.status = "failed"
            job.error_message = error_msg
            db.commit()
            return
        # ----------------------------------------------------
        
        user = db.query(User).filter(User.id == job.user_id).first()
        if not user:
            job.status = "failed"
            job.error_message = "User not found"
            db.commit()
            return
        
        job.status = "processing"
        db.commit()
        
        try:
            # Lazy imports for sync path too
            from app.adapters.tts.factory import get_tts_adapter
            from app.adapters.storage.local import get_storage_adapter
            from app.services.user_service import UserService
            
            # Generate audio using TTS adapter
            tts_adapter = get_tts_adapter(language=job.language or "en")
            
            # Handle voice cloning URL if present
            speaker_wav_path = job.speaker_wav_url
            
            print(f"[SYNC WORKER] Starting generation for {job_id_str}...")
            # Use asyncio.run because generate() is async but we are in a thread
            wav_path = asyncio.run(tts_adapter.generate(
                text=job.text,
                voice_id=job.voice_id,
                language=job.language or "en",
                voice_age=job.voice_age,
                prosody_preset=job.prosody_preset,
                speaker_wav_path=speaker_wav_path,
                settings=job.settings or {}
            ))
            print(f"[SYNC WORKER] WAV generated: {wav_path}")
            
            # Upload to storage
            print(f"[SYNC WORKER] Uploading to storage: {wav_path}")
            storage = get_storage_adapter()
            audio_url = asyncio.run(storage.upload_file(
                wav_path,
                f"audio/{job.user_id}/{job_id}.wav"
            ))
            print(f"[SYNC WORKER] Audio uploaded: {audio_url}")
            
            # Update job
            job.status = "completed"
            job.audio_url = audio_url
            db.commit()
            
        except Exception as e:
            print(f"[SYNC WORKER] ERROR: {e}")
            import traceback
            traceback.print_exc()
            job.status = "failed"
            job.error_message = str(e)
            db.commit()
        finally:
            if job.character_count:
                try:
                    UserService.deduct_quota(db, user, job.character_count)
                except Exception as q_err:
                    print(f"[SYNC WORKER] Error deducting quota: {q_err}")
    finally:
        db.close()
