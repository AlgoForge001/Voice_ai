from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.models import get_db, User
from app.schemas import UsageStats
from app.services.usage_service import UsageService
from app.auth import get_current_user

router = APIRouter(prefix="/usage", tags=["Usage & Billing"])


@router.get("/stats", response_model=UsageStats)
async def get_usage_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's usage statistics.
    """
    stats = UsageService.get_usage_stats(db, current_user.id)
    
    return UsageStats(**stats)
