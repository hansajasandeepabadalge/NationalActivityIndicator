from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import jwt, JWTError
import bcrypt
from pydantic import BaseModel

from app.core.config import settings



class TokenPayload(BaseModel):
    sub: str  # Subject (user_id)
    exp: datetime  # Expiration time
    iat: datetime  # Issued at
    type: str  # Token type: access or refresh
    role: str  # User role


class TokenData(BaseModel):
    user_id: str
    role: str
    token_type: str


def create_access_token(
        subject: str,
        role: str,
        expires_delta: Optional[timedelta] = None
) -> str:
    now = datetime.now(timezone.utc)

    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)

    payload = {
        "sub": str(subject),
        "exp": expire,
        "iat": now,
        "type": "access",
        "role": role
    }

    return jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )


def create_refresh_token(
        subject: str,
        role: str,
        expires_delta: Optional[timedelta] = None
) -> str:
    now = datetime.now(timezone.utc)

    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)

    payload = {
        "sub": str(subject),
        "exp": expire,
        "iat": now,
        "type": "refresh",
        "role": role
    }

    return jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )


def verify_token(token: str) -> Optional[TokenData]:
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )

        user_id: str = payload.get("sub")
        role: str = payload.get("role")
        token_type: str = payload.get("type")

        if user_id is None:
            return None

        return TokenData(
            user_id=user_id,
            role=role,
            token_type=token_type
        )

    except JWTError:
        return None


def verify_password(plain_password: str, hashed_password: str) -> bool:
    # Truncate password to 72 bytes (bcrypt limitation)
    password_bytes = plain_password.encode('utf-8')[:72]
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)


def get_password_hash(password: str) -> str:
    # Truncate password to 72 bytes (bcrypt limitation)
    password_bytes = password.encode('utf-8')[:72]
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')
