from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from cryptography.fernet import Fernet
import base64
import hashlib
from app.core.config import settings

from app.exceptions.logical_exception import UnauthorizedException

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify JWT token"""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise UnauthorizedException(
                message="Invalid authentication credentials",
                error_details={"headers": {"WWW-Authenticate": "Bearer"}}
            )
        return username
    except JWTError:
        raise UnauthorizedException(
            message="Invalid authentication credentials",
            error_details={"headers": {"WWW-Authenticate": "Bearer"}}
        )


def get_encryption_key() -> bytes:
    """Get encryption key for Fernet"""
    # Use SHA256 to hash the key to 32 bytes
    key = hashlib.sha256(settings.ENCRYPTION_KEY.encode()).digest()
    return base64.urlsafe_b64encode(key)


def encrypt_data(data: str) -> str:
    """Encrypt sensitive data"""
    f = Fernet(get_encryption_key())
    return f.encrypt(data.encode()).decode()


def decrypt_data(encrypted_data: str) -> str:
    """Decrypt sensitive data"""
    try:
        f = Fernet(get_encryption_key())
        return f.decrypt(encrypted_data.encode()).decode()
    except Exception as e:
        raise ValueError(f"Decryption failed: {str(e)}")


def check_ip_whitelist(client_ip: str) -> bool:
    """Check if IP is in whitelist"""
    if not settings.ENABLE_IP_WHITELIST:
        return True
    
    if not settings.ALLOWED_IPS:
        return True
    
    return client_ip in settings.ALLOWED_IPS

