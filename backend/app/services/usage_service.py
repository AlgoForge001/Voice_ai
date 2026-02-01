from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from typing import Dict
from uuid import UUID
from app.models import UsageLog, User


class UsageService:
    """
    Usage service for tracking and analytics.
    
    Responsibilities:
    - Track character usage
    - Generate usage statistics
    - Enforce rate limits
    """
    
    @staticmethod
    def get_usage_stats(db: Session, user_id: UUID) -> Dict:
        """
        Get usage statistics for a user.
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("User not found")
        
        # Get today's usage
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        chars_today = db.query(func.sum(UsageLog.characters_used)).filter(
            UsageLog.user_id == user_id,
            UsageLog.timestamp >= today_start
        ).scalar() or 0
        
        # Get this month's usage
        month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        chars_month = db.query(func.sum(UsageLog.characters_used)).filter(
            UsageLog.user_id == user_id,
            UsageLog.timestamp >= month_start
        ).scalar() or 0
        
        return {
            "characters_used_today": chars_today,
            "characters_used_month": chars_month,
            "credits_remaining": user.credits_remaining,
            "credits_total": user.credits_total,
            "quota_reset_date": user.quota_reset_date
        }
    
    @staticmethod
    def check_rate_limit(db: Session, user_id: UUID, window_minutes: int = 60, max_requests: int = 100) -> bool:
        """
        Check if user has exceeded rate limit.
        
        Args:
            user_id: User ID
            window_minutes: Time window in minutes
            max_requests: Maximum requests in window
        
        Returns:
            True if within limit, False if exceeded
        """
        window_start = datetime.utcnow() - timedelta(minutes=window_minutes)
        
        request_count = db.query(UsageLog).filter(
            UsageLog.user_id == user_id,
            UsageLog.timestamp >= window_start
        ).count()
        
        return request_count < max_requests
