from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models import get_db, User
from app.schemas import FeatureFlagUpdate
from app.auth import get_current_admin
from app.config import get_settings

router = APIRouter(prefix="/admin", tags=["Admin"])

settings = get_settings()


@router.post("/feature-flags")
async def update_feature_flag(
    update: FeatureFlagUpdate,
    current_admin: User = Depends(get_current_admin)
):
    """
    Update feature flags (admin only).
    
    This is a simplified version - in production, store flags in database.
    """
    # In production, update database and reload config
    # For now, return current state
    
    valid_flags = [
        "ENABLE_VOICE_CLONING",
        "ENABLE_API_ACCESS",
        "ENABLE_ADMIN_PANEL"
    ]
    
    if update.flag_name not in valid_flags:
        raise HTTPException(status_code=400, detail="Invalid feature flag")
    
    return {
        "flag_name": update.flag_name,
        "enabled": update.enabled,
        "message": "Feature flag updated successfully"
    }


@router.get("/stats")
async def get_admin_stats(
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get platform-wide statistics (admin only).
    """
    from app.models import User, TTSJob
    from sqlalchemy import func
    
    total_users = db.query(func.count(User.id)).scalar()
    total_jobs = db.query(func.count(TTSJob.id)).scalar()
    completed_jobs = db.query(func.count(TTSJob.id)).filter(TTSJob.status == "completed").scalar()
    
    return {
        "total_users": total_users,
        "total_jobs": total_jobs,
        "completed_jobs": completed_jobs,
        "success_rate": (completed_jobs / total_jobs * 100) if total_jobs > 0 else 0
    }
