from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.config import get_settings

settings = get_settings()

# Password hashing
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash. Truncates to 72 bytes for bcrypt compatibility."""
    # Bcrypt has a 72-byte limit - truncate the password first
    if len(plain_password) > 72:
        plain_password = plain_password[:72]
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password. Truncates to 72 bytes for bcrypt compatibility."""
    print(f"[PASSWORD HASH DEBUG] Original password: '{password}'")
    print(f"[PASSWORD HASH DEBUG] Password length: {len(password)} characters")
    print(f"[PASSWORD HASH DEBUG] Password bytes: {len(password.encode('utf-8'))} bytes")
    
    # Bcrypt has a 72-byte limit - truncate the password first
    if len(password) > 72:
        print(f"[PASSWORD HASH DEBUG] Truncating password from {len(password)} to 72 characters")
        password = password[:72]
    
    print(f"[PASSWORD HASH DEBUG] Final password length: {len(password)} characters")
    
    try:
        hashed = pwd_context.hash(password)
        print(f"[PASSWORD HASH DEBUG] Successfully hashed!")
        return hashed
    except Exception as e:
        print(f"[PASSWORD HASH DEBUG] ERROR: {e}")
        raise


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create JWT access token.
    
    Args:
        data: Payload data (should include user_id)
        expires_delta: Token expiration time
    
    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """
    Decode and verify JWT token.
    
    Returns:
        Decoded payload or None if invalid
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None
