from datetime import datetime, timezone
from typing import Optional, Tuple
from loguru import logger

from app.models.user import User
from app.schemas.auth import UserRegister, UserLogin, TokenResponse, UserResponse
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_token
)
from app.core.config import settings


class AuthService:
    """Service for authentication operations."""

    @staticmethod
    async def register_user(user_data: UserRegister) -> User:
        # Check if user already exists
        existing_user = await User.find_one(User.email == user_data.email)
        if existing_user:
            raise ValueError("Email already registered")

        # Create new user
        user = User(
            email=user_data.email,
            password_hash=get_password_hash(user_data.password),
            role=user_data.role,
            full_name=user_data.full_name
        )

        await user.insert()
        logger.info(f"New user registered: {user.email}")

        return user

    @staticmethod
    async def authenticate_user(login_data: UserLogin) -> Optional[User]:
        user = await User.find_one(User.email == login_data.email)

        if not user:
            logger.warning(f"Login attempt for non-existent user: {login_data.email}")
            return None

        if not verify_password(login_data.password, user.password_hash):
            logger.warning(f"Failed login attempt for user: {login_data.email}")
            return None

        if not user.is_active:
            logger.warning(f"Login attempt for inactive user: {login_data.email}")
            return None

        # Update last login
        user.record_login()
        await user.save()

        logger.info(f"User logged in: {user.email}")
        return user

    @staticmethod
    def create_tokens(user: User) -> TokenResponse:
        access_token = create_access_token(
            subject=str(user.id),
            role=user.role
        )
        refresh_token = create_refresh_token(
            subject=str(user.id),
            role=user.role
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )

    @staticmethod
    async def refresh_tokens(refresh_token: str) -> Optional[Tuple[User, TokenResponse]]:
        token_data = verify_token(refresh_token)

        if not token_data or token_data.token_type != "refresh":
            return None

        user = await User.get(token_data.user_id)

        if not user or not user.is_active:
            return None

        tokens = AuthService.create_tokens(user)
        return user, tokens

    @staticmethod
    async def get_user_by_id(user_id: str) -> Optional[User]:
        try:
            return await User.get(user_id)
        except Exception:
            return None

    @staticmethod
    async def change_password(
            user: User,
            current_password: str,
            new_password: str
    ) -> bool:
        if not verify_password(current_password, user.password_hash):
            return False

        user.password_hash = get_password_hash(new_password)
        user.update_timestamp()
        await user.save()

        logger.info(f"Password changed for user: {user.email}")
        return True

    @staticmethod
    def user_to_response(user: User) -> UserResponse:
        return UserResponse(
            id=str(user.id),
            email=user.email,
            role=user.role,
            full_name=user.full_name,
            is_active=user.is_active,
            is_verified=user.is_verified,
            company_id=user.company_id,
            created_at=user.created_at.isoformat()
        )