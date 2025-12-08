from fastapi import APIRouter, HTTPException, status, Depends
from loguru import logger

from app.schemas.auth import (
    UserRegister,
    UserLogin,
    TokenResponse,
    TokenRefresh,
    UserResponse,
    AuthResponse,
    PasswordChange,
    MessageResponse
)
from app.services.authService import AuthService
from app.api.deps import get_current_user
from app.models.user import User


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user"
)
async def register(user_data: UserRegister):
    try:
        user = await AuthService.register_user(user_data)
        return AuthService.user_to_response(user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


@router.post(
    "/login",
    response_model=AuthResponse,
    summary="User login"
)
async def login(login_data: UserLogin):
    user = await AuthService.authenticate_user(login_data)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    tokens = AuthService.create_tokens(user)
    user_response = AuthService.user_to_response(user)

    return AuthResponse(token=tokens, user=user_response)


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh access token"
)
async def refresh_token(token_data: TokenRefresh):
    result = await AuthService.refresh_tokens(token_data.refresh_token)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )

    _, tokens = result
    return tokens


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user"
)
async def get_me(current_user: User = Depends(get_current_user)):
    return AuthService.user_to_response(current_user)


@router.post(
    "/change-password",
    response_model=MessageResponse,
    summary="Change password"
)
async def change_password(
        password_data: PasswordChange,
        current_user: User = Depends(get_current_user)
):
    success = await AuthService.change_password(
        current_user,
        password_data.current_password,
        password_data.new_password
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )

    return MessageResponse(message="Password changed successfully")


@router.post(
    "/logout",
    response_model=MessageResponse,
    summary="Logout user"
)
async def logout(current_user: User = Depends(get_current_user)):
    # In a production app, you might want to:
    # - Add token to blacklist
    # - Clear any server-side session data
    # - Log the logout event

    logger.info(f"User logged out: {current_user.email}")
    return MessageResponse(message="Logged out successfully")