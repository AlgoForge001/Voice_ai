from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.types import JSON  # Changed from JSONB for SQLite compatibility
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.utils.database import Base


class TTSJob(Base):
    """
    TTS Job model for tracking text-to-speech generation requests.
    """
    __tablename__ = "tts_jobs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    
    # Input
    text = Column(Text, nullable=False)
    voice_id = Column(String, nullable=False)
    language = Column(String, default="en")
    voice_age = Column(String, default="adult")  # adult, child, elder
    prosody_preset = Column(String, default="neutral")  # neutral, storytelling, calm, news
    speaker_wav_url = Column(String, nullable=True)  # For voice cloning
    
    # Processing
    status = Column(String, default="queued", index=True)  # queued, processing, completed, failed
    priority = Column(Integer, default=0)  # Higher = processed first
    
    # Output
    audio_url = Column(String, nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    
    # Metadata
    character_count = Column(Integer, nullable=False)
    settings = Column(JSON, nullable=True)  # stability, similarity_boost, etc.
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<TTSJob {self.id} ({self.status})>"
    
    @property
    def text_snippet(self) -> str:
        """Return first 50 characters of text for display."""
        return self.text[:50] + "..." if len(self.text) > 50 else self.text
