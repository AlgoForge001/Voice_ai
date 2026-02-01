from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


# ============ User Schemas ============

class UserBase(BaseModel):
    email: EmailStr
    name: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=72)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(UserBase):
    id: UUID
    role: str
    plan: str
    credits: int
    
    class Config:
        from_attributes = True


class UserWithQuota(UserResponse):
    credits_remaining: int
    credits_total: int
    quota_reset_date: datetime


# ============ Auth Schemas ============

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[UUID] = None


class AuthResponse(BaseModel):
    token: str
    user: UserResponse


# ============ TTS Schemas ============

class TTSRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000)
    voice_id: str
    language: str = "en"
    voice_age: Optional[str] = "adult"  # adult, child, elder
    prosody_preset: Optional[str] = "neutral"  # neutral, storytelling, calm, news
    model_id: Optional[str] = None
    settings: Optional[dict] = None
    speaker_wav_url: Optional[str] = None  # For voice cloning


class TTSJobResponse(BaseModel):
    job_id: UUID
    status: str
    audio_url: Optional[str] = None
    created_at: datetime
    text_snippet: str
    voice_name: Optional[str] = None
    
    class Config:
        from_attributes = True


class TTSJobDetail(TTSJobResponse):
    text: str
    character_count: int
    error_message: Optional[str] = None
    completed_at: Optional[datetime] = None


# ============ Voice Schemas ============

class Voice(BaseModel):
    voice_id: str
    name: str
    accent: str
    gender: str
    language: Optional[str] = "en"
    preview_url: Optional[str] = None
    labels: Optional[dict] = None


# ============ Usage Schemas ============

class UsageStats(BaseModel):
    characters_used_today: int
    characters_used_month: int
    credits_remaining: int
    credits_total: int
    quota_reset_date: datetime


# ============ Admin Schemas ============

class FeatureFlagUpdate(BaseModel):
    flag_name: str
    enabled: bool


class QuotaUpdate(BaseModel):
    user_id: UUID
    new_quota: int
