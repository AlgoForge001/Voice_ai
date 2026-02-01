from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timedelta
from app.models import User
from app.schemas import UserCreate
from app.auth import verify_password, get_password_hash, create_access_token
from app.config import PRICING_TIERS


class UserService:
    """
    User service for authentication and user management.
    
    Responsibilities:
    - User registration and login
    - Quota management
    - Role and plan management
    """
    
    @staticmethod
    def create_user(db: Session, user_data: UserCreate) -> User:
        """
        Create a new user with default free plan.
        """
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise ValueError("Email already registered")
        
        # Create user
        user = User(
            email=user_data.email,
            name=user_data.name,
            password_hash=get_password_hash(user_data.password),
            plan="free",
            role="user",
            credits_remaining=PRICING_TIERS["free"]["quota"],
            credits_total=PRICING_TIERS["free"]["quota"],
            quota_reset_date=datetime.utcnow() + timedelta(days=1)
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        return user
    
    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
        """
        Authenticate user with email and password.
        
        Returns:
            User object if authentication successful, None otherwise
        """
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            return None
        
        if not verify_password(password, user.password_hash):
            return None
        
        return user
    
    @staticmethod
    def create_token_for_user(user: User) -> str:
        """
        Create JWT token for user.
        """
        return create_access_token(data={"user_id": str(user.id)})
    
    @staticmethod
    def check_and_reset_quota(db: Session, user: User) -> User:
        """
        Check if quota needs to be reset and reset if necessary.
        """
        if datetime.utcnow() >= user.quota_reset_date:
            user.reset_quota()
            db.commit()
            db.refresh(user)
        
        return user
    
    @staticmethod
    def has_sufficient_quota(user: User, characters: int) -> bool:
        """
        Check if user has sufficient quota for the request.
        """
        return user.has_quota(characters)
    
    @staticmethod
    def deduct_quota(db: Session, user: User, characters: int):
        """
        Deduct characters from user's quota.
        """
        from app.config import get_settings
        settings = get_settings()
        
        if settings.ENVIRONMENT == "development":
            print(f"[QUOTA] Skipping quota deduction for user {user.email} in development")
            return

        user.deduct_quota(characters)
        db.commit()
        db.refresh(user)
    
    @staticmethod
    def upgrade_plan(db: Session, user: User, new_plan: str):
        """
        Upgrade user to a new plan.
        """
        if new_plan not in PRICING_TIERS:
            raise ValueError(f"Invalid plan: {new_plan}")
        
        user.plan = new_plan
        user.reset_quota()
        db.commit()
        db.refresh(user)
        
        return user
