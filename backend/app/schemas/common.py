"""
Common schemas used across the application.
"""
from typing import Generic, TypeVar, List, Optional, Any
from pydantic import BaseModel, Field


T = TypeVar("T")


class PaginationParams(BaseModel):
    """Schema for pagination parameters."""
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)

    @property
    def skip(self) -> int:
        """Calculate skip value for database query."""
        return (self.page - 1) * self.page_size


class PaginatedResponse(BaseModel, Generic[T]):
    """Schema for paginated response."""
    items: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_prev: bool


class ErrorResponse(BaseModel):
    """Schema for error response."""
    error: str
    detail: Optional[str] = None
    code: Optional[str] = None


class SuccessResponse(BaseModel):
    """Schema for success response."""
    success: bool = True
    message: str
    data: Optional[Any] = None


class HealthCheck(BaseModel):
    """Schema for health check response."""
    status: str
    version: str
    database: str
    cache: str
    timestamp: str


class MessageResponse(BaseModel):
    """Generic message response."""
    message: str
    success: bool = True
