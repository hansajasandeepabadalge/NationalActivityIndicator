"""
Layer 5: Authentication Service

Handles user authentication with JWT tokens.
"""
from datetime import datetime, timedelta
from typing import Optional, Tuple
import bcrypt
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.layer5.config import layer5_settings
from app.layer5.models.user import User, UserRole
from app.layer5.schemas.auth import UserCreate, UserLogin, TokenResponse, TokenData


class AuthService:
    """Service for user authentication and JWT management"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    # ============== Password Hashing ==============
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt"""
        salt = bcrypt.gensalt(rounds=layer5_settings.PASSWORD_HASH_ROUNDS)
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """Verify a password against its hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    # ============== JWT Token Management ==============
    
    @staticmethod
    def create_access_token(user: User) -> str:
        """Create JWT access token"""
        expire = datetime.utcnow() + timedelta(minutes=layer5_settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        payload = {
            "sub": str(user.id),
            "email": user.email,
            "role": user.role.value if isinstance(user.role, UserRole) else user.role,
            "company_id": user.company_id,
            "exp": expire,
            "type": "access"
        }
        return jwt.encode(payload, layer5_settings.JWT_SECRET_KEY, algorithm=layer5_settings.JWT_ALGORITHM)
    
    @staticmethod
    def create_refresh_token(user: User) -> str:
        """Create JWT refresh token"""
        expire = datetime.utcnow() + timedelta(days=layer5_settings.REFRESH_TOKEN_EXPIRE_DAYS)
        payload = {
            "sub": str(user.id),
            "exp": expire,
            "type": "refresh"
        }
        return jwt.encode(payload, layer5_settings.JWT_SECRET_KEY, algorithm=layer5_settings.JWT_ALGORITHM)
    
    @staticmethod
    def decode_token(token: str) -> Optional[TokenData]:
        """Decode and validate JWT token"""
        try:
            payload = jwt.decode(
                token, 
                layer5_settings.JWT_SECRET_KEY, 
                algorithms=[layer5_settings.JWT_ALGORITHM]
            )
            
            return TokenData(
                user_id=int(payload.get("sub")),
                email=payload.get("email", ""),
                role=UserRole(payload.get("role", "user")),
                company_id=payload.get("company_id"),
                exp=datetime.fromtimestamp(payload.get("exp", 0))
            )
        except JWTError:
            return None
    
    # ============== User Management ==============
    
    async def create_user(self, user_data: UserCreate, role: UserRole = UserRole.USER) -> User:
        """Create a new user"""
        # Check if email already exists
        existing = await self.get_user_by_email(user_data.email)
        if existing:
            raise ValueError("Email already registered")
        
        # Create user
        user = User(
            email=user_data.email,
            password_hash=self.hash_password(user_data.password),
            full_name=user_data.full_name,
            role=role,
            company_id=user_data.company_id,
            is_active=True,
            is_verified=False
        )
        
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        
        return user
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()
    
    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def authenticate(self, login_data: UserLogin) -> Optional[User]:
        """Authenticate user with email and password"""
        user = await self.get_user_by_email(login_data.email)
        
        if not user:
            return None
        
        if not user.is_active:
            return None
        
        if not self.verify_password(login_data.password, user.password_hash):
            return None
        
        # Update last login
        await self.db.execute(
            update(User).where(User.id == user.id).values(last_login_at=datetime.utcnow())
        )
        await self.db.commit()
        
        return user
    
    async def login(self, login_data: UserLogin) -> Optional[TokenResponse]:
        """Login and return tokens"""
        user = await self.authenticate(login_data)
        
        if not user:
            return None
        
        access_token = self.create_access_token(user)
        refresh_token = self.create_refresh_token(user)
        
        # Store refresh token
        await self.db.execute(
            update(User).where(User.id == user.id).values(refresh_token=refresh_token)
        )
        await self.db.commit()
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=layer5_settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
    
    async def refresh_tokens(self, refresh_token: str) -> Optional[TokenResponse]:
        """Refresh access token using refresh token"""
        token_data = self.decode_token(refresh_token)
        
        if not token_data:
            return None
        
        user = await self.get_user_by_id(token_data.user_id)
        
        if not user or user.refresh_token != refresh_token:
            return None
        
        if not user.is_active:
            return None
        
        # Create new tokens
        new_access_token = self.create_access_token(user)
        new_refresh_token = self.create_refresh_token(user)
        
        # Update stored refresh token
        await self.db.execute(
            update(User).where(User.id == user.id).values(refresh_token=new_refresh_token)
        )
        await self.db.commit()
        
        return TokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            expires_in=layer5_settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
    
    async def logout(self, user_id: int) -> bool:
        """Logout user by invalidating refresh token"""
        await self.db.execute(
            update(User).where(User.id == user_id).values(refresh_token=None)
        )
        await self.db.commit()
        return True
    
    async def change_password(self, user_id: int, current_password: str, new_password: str) -> bool:
        """Change user password"""
        user = await self.get_user_by_id(user_id)
        
        if not user:
            return False
        
        if not self.verify_password(current_password, user.password_hash):
            return False
        
        new_hash = self.hash_password(new_password)
        
        await self.db.execute(
            update(User).where(User.id == user_id).values(
                password_hash=new_hash,
                refresh_token=None  # Invalidate all sessions
            )
        )
        await self.db.commit()
        
        return True
