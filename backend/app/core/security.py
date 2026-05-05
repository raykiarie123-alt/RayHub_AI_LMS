from datetime import datetime, timedelta #datetime for token expiry
from typing import Optional, Union
from jose import JWTError, jwt #JWT for token encoding and decoding
from passlib.context import CryptContext #for password hashing and verification
from app.core.config import settings #import settings to access configuration values like SECRET_KEY and ALGORITHM

# Security utilities for password hashing, token creation, and token decoding. This module provides functions to hash passwords, verify passwords, create JWT access tokens, and decode JWT tokens. It uses the settings defined in the config module for configuration values.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Function to verify a plain password against a hashed password using the password context.
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# Function to create a hash of a password using the password context.
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# Function to create a JWT access token with the given data and expiration delta.
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

# Function to decode a JWT token and return the payload if the token is valid, or None if the token is invalid or expired.
def decode_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None