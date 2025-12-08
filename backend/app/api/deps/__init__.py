"""
API dependencies for authentication and authorization.
"""
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from loguru import logger

from app.core.security import verify_token, TokenData
from app.models.user import User
from app.services.authService import AuthService


# HTTP Bearer scheme for token authentication
security = HTTPBearer(auto_error=False)


async def get_current_user_optional(
        credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[User]:
    """
    Get current user from token (optional).

    Args:
        credentials: HTTP Bearer credentials

    Returns:
        User if authenticated, None otherwise
    """
    if not credentials:
        return None

    token_data = verify_token(credentials.credentials)
    if not token_data:
        return None

    user = await AuthService.get_user_by_id(token_data.user_id)
    return user


async def get_current_user(
        credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> User:
    """
    Get current user from token (required).

    Args:
        credentials: HTTP Bearer credentials

    Returns:
        User object

    Raises:
        HTTPException: If not authenticated or invalid token
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )

    if not credentials:
        raise credentials_exception

    token_data = verify_token(credentials.credentials)
    if not token_data:
        raise credentials_exception

    if token_data.token_type != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type"
        )

    user = await AuthService.get_user_by_id(token_data.user_id)

    if not user:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )

    return user


async def get_current_admin(
        current_user: User = Depends(get_current_user)
) -> User:
    """
    Get current admin user.

    Args:
        current_user: Current authenticated user

    Returns:
        User object if admin

    Raises:
        HTTPException: If not an admin
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user


async def get_current_business_user(
        current_user: User = Depends(get_current_user)
) -> User:
    """
    Get current business user.

    Args:
        current_user: Current authenticated user

    Returns:
        User object if regular user

    Raises:
        HTTPException: If not a regular user
    """
    if current_user.role != "user":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Business user account required"
        )
    return current_user


def get_token_data(
        credentials: HTTPAuthorizationCredentials = Depends(security)
) -> TokenData:
    """
    Extract and validate token data.

    Args:
        credentials: HTTP Bearer credentials

    Returns:
        TokenData

    Raises:
        HTTPException: If invalid token
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )

    token_data = verify_token(credentials.credentials)

    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

    return token_data