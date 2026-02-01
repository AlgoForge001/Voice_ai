from sqlalchemy import Column, String, Integer, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, timedelta
import uuid
from app.utils.database import Base


class User(Base):
    """
    User model with authentication, roles, and quota tracking.
    """
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    name = Column(String, nullable=True)
    
    # Role & Plan
    role = Column(String, default="user")  # user, admin
    plan = Column(String, default="free")  # free, starter, pro, api
    
    # Quota Management
    credits_remaining = Column(Integer, default=1000)  # Characters remaining
    credits_total = Column(Integer, default=1000)  # Total quota for current period
    quota_reset_date = Column(DateTime, default=lambda: datetime.utcnow() + timedelta(days=1))
    
    # Subscription
    subscription_status = Column(String, default="active")  # active, cancelled, expired
    subscription_id = Column(String, nullable=True)  # External subscription ID
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Safety
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    def __repr__(self):
        return f"<User {self.email} ({self.plan})>"
    
    def has_quota(self, characters: int) -> bool:
        """Check if user has enough quota for the request."""
        return self.credits_remaining >= characters
    
    def deduct_quota(self, characters: int):
        """Deduct characters from user's quota."""
        self.credits_remaining = max(0, self.credits_remaining - characters)
    
    def reset_quota(self):
        """Reset quota based on plan."""
        from app.config import PRICING_TIERS
        tier = PRICING_TIERS.get(self.plan, PRICING_TIERS["free"])
        self.credits_total = tier["quota"]
        self.credits_remaining = tier["quota"]
        
        if tier["quota_type"] == "daily":
            self.quota_reset_date = datetime.utcnow() + timedelta(days=1)
        elif tier["quota_type"] == "monthly":
            self.quota_reset_date = datetime.utcnow() + timedelta(days=30)
