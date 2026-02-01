from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.models import get_db, User
from app.schemas import UserCreate, UserLogin, AuthResponse, UserResponse
from app.services.user_service import UserService
from app.auth import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def signup(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user.
    
    Creates a user with free plan and returns JWT token.
    """
    print(f"[SIGNUP DEBUG] Received signup request")
    print(f"[SIGNUP DEBUG] Email: {user_data.email}")
    print(f"[SIGNUP DEBUG] Password length: {len(user_data.password)} characters")
    print(f"[SIGNUP DEBUG] Password: {user_data.password[:20]}..." if len(user_data.password) > 20 else f"[SIGNUP DEBUG] Password: {user_data.password}")
    
    try:
        user = UserService.create_user(db, user_data)
        token = UserService.create_token_for_user(user)
        
        return {
            "token": token,
            "user": UserResponse(
                id=user.id,
                email=user.email,
                name=user.name,
                role=user.role,
                plan=user.plan,
                credits=user.credits_remaining
            )
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login", response_model=AuthResponse)
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Authenticate user and return JWT token.
    """
    user = UserService.authenticate_user(db, credentials.email, credentials.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Check and reset quota if needed
    user = UserService.check_and_reset_quota(db, user)
    
    token = UserService.create_token_for_user(user)
    
    return {
        "token": token,
        "user": UserResponse(
            id=user.id,
            email=user.email,
            name=user.name,
            role=user.role,
            plan=user.plan,
            credits=user.credits_remaining
        )
    }


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Get current authenticated user's information.
    """
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        name=current_user.name,
        role=current_user.role,
        plan=current_user.plan,
        credits=current_user.credits_remaining
    )
