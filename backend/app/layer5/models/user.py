"""
Layer 5: User Model with Authentication

This is the Layer 5 user model with authentication support.
Links to CompanyProfile from Layer 4 for company-specific data.
"""
from sqlalchemy import (
    Column, Integer, String, Boolean, TIMESTAMP, 
    ForeignKey, Enum as SQLEnum
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base_class import Base
import enum


class UserRole(str, enum.Enum):
    """User role enumeration"""
    ADMIN = "admin"
    USER = "user"


class User(Base):
    """
    Layer 5 User model for dashboard authentication.
    
    Two roles:
    - ADMIN: Can view all national indicators, industry data, and all company insights
    - USER: Can view their company profile and company-specific insights
    """
    __tablename__ = "l5_users"
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Authentication
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    
    # Profile
    full_name = Column(String(200))
    
    # Role - admin or user
    role = Column(
        SQLEnum(UserRole, name='user_role_enum', create_type=True),
        default=UserRole.USER,
        nullable=False,
        index=True
    )
    
    # Company link (for USER role)
    # Links to company_profiles.company_id (Layer 4)
    company_id = Column(String(50), ForeignKey('company_profiles.company_id'), nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True, index=True)
    is_verified = Column(Boolean, default=False)
    
    # Tokens
    refresh_token = Column(String(500), nullable=True)
    
    # Timestamps
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
    last_login_at = Column(TIMESTAMP(timezone=True), nullable=True)
    
    # Relationships
    # company = relationship("CompanyProfile", backref="users")  # Optional
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"
