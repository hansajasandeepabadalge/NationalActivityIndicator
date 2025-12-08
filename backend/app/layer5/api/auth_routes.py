"""
Layer 5: Authentication API Routes

Handles user registration, login, and token management.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_async_session
from app.layer5.services.auth_service import AuthService
from app.layer5.models.user import UserRole
from app.layer5.schemas.auth import (
    UserCreate, UserLogin, UserResponse, 
    TokenResponse, PasswordChange
)

router = APIRouter(prefix="/auth", tags=["auth", "layer5"])
security = HTTPBearer()


# ============== Dependency: Get Current User ==============

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_async_session)
) -> UserResponse:
    """Get current authenticated user from JWT token"""
    token = credentials.credentials
    
    auth_service = AuthService(db)
    token_data = auth_service.decode_token(token)
    
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    user = await auth_service.get_user_by_id(token_data.user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled"
        )
    
    return UserResponse.model_validate(user)


async def require_admin(
    current_user: UserResponse = Depends(get_current_user)
) -> UserResponse:
    """Require admin role"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


# ============== Registration ==============

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_async_session)
):
    """
    Register a new user.
    New users are created with USER role by default.
    """
    auth_service = AuthService(db)
    
    try:
        user = await auth_service.create_user(user_data, role=UserRole.USER)
        return UserResponse.model_validate(user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/register/admin", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_admin(
    user_data: UserCreate,
    current_user: UserResponse = Depends(require_admin),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Register a new admin user.
    Requires existing admin authentication.
    """
    auth_service = AuthService(db)
    
    try:
        user = await auth_service.create_user(user_data, role=UserRole.ADMIN)
        return UserResponse.model_validate(user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# ============== Login ==============

@router.post("/login", response_model=TokenResponse)
async def login(
    login_data: UserLogin,
    db: AsyncSession = Depends(get_async_session)
):
    """
    Login with email and password.
    Returns access and refresh tokens.
    """
    auth_service = AuthService(db)
    
    tokens = await auth_service.login(login_data)
    
    if not tokens:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return tokens


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_token: str,
    db: AsyncSession = Depends(get_async_session)
):
    """
    Refresh access token using refresh token.
    """
    auth_service = AuthService(db)
    
    tokens = await auth_service.refresh_tokens(refresh_token)
    
    if not tokens:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return tokens


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Logout user by invalidating refresh token.
    """
    auth_service = AuthService(db)
    await auth_service.logout(current_user.id)


# ============== User Profile ==============

@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Get current user profile.
    """
    return current_user


@router.post("/change-password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(
    password_data: PasswordChange,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Change current user's password.
    """
    auth_service = AuthService(db)
    
    success = await auth_service.change_password(
        current_user.id,
        password_data.current_password,
        password_data.new_password
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
