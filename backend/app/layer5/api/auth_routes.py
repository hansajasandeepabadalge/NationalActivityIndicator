"""
Layer 5: Authentication API Routes

Handles user registration, login, and token management.
Uses synchronous SQLAlchemy sessions (same pattern as L1-L4).
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.layer5.services.auth_service import AuthService
from app.layer5.models.user import UserRole
from app.layer5.schemas.auth import (
    UserCreate, UserLogin, UserResponse, 
    TokenResponse, PasswordChange
)

router = APIRouter(prefix="/auth", tags=["auth", "layer5"])
security = HTTPBearer()


# ============== Dependency: Get Current User ==============

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
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
    
    user = auth_service.get_user_by_id(token_data.user_id)
    
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


def require_admin(
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
def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Register a new user.
    New users are created with USER role by default.
    """
    auth_service = AuthService(db)
    
    try:
        user = auth_service.create_user(user_data, role=UserRole.USER)
        return UserResponse.model_validate(user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/register/admin", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_admin(
    user_data: UserCreate,
    current_user: UserResponse = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Register a new admin user.
    Requires existing admin authentication.
    """
    auth_service = AuthService(db)
    
    try:
        user = auth_service.create_user(user_data, role=UserRole.ADMIN)
        return UserResponse.model_validate(user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# ============== Login ==============

@router.post("/login", response_model=TokenResponse)
def login(
    login_data: UserLogin,
    db: Session = Depends(get_db)
):
    """
    Login with email and password.
    Returns access and refresh tokens.
    """
    auth_service = AuthService(db)
    
    tokens = auth_service.login(login_data)
    
    if not tokens:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return tokens


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(
    refresh_token: str,
    db: Session = Depends(get_db)
):
    """
    Refresh access token using refresh token.
    """
    auth_service = AuthService(db)
    
    tokens = auth_service.refresh_tokens(refresh_token)
    
    if not tokens:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return tokens


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Logout user by invalidating refresh token.
    """
    auth_service = AuthService(db)
    auth_service.logout(current_user.id)


# ============== User Profile ==============

@router.get("/me", response_model=UserResponse)
def get_me(
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Get current user profile.
    """
    return current_user


@router.post("/change-password", status_code=status.HTTP_204_NO_CONTENT)
def change_password(
    password_data: PasswordChange,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Change current user's password.
    """
    auth_service = AuthService(db)
    
    success = auth_service.change_password(
        current_user.id,
        password_data.current_password,
        password_data.new_password
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
