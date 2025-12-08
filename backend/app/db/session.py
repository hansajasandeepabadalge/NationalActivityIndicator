"""Database session setup - Integrated"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from typing import AsyncGenerator
from app.core.config import settings
from app.db.base_class import Base

# Create database engine with connection pooling (sync)
engine = create_engine(
    settings.DATABASE_URL,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_timeout=settings.DB_POOL_TIMEOUT,
    pool_recycle=settings.DB_POOL_RECYCLE,
    pool_pre_ping=True
)

# Create SessionLocal class (sync)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Dependency for getting database sessions (sync)."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ============== Async Session Support ==============

def _get_async_database_url() -> str:
    """Convert sync database URL to async (asyncpg)"""
    url = settings.DATABASE_URL
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+asyncpg://", 1)
    elif url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+asyncpg://", 1)
    return url


# Create async engine
try:
    async_engine = create_async_engine(
        _get_async_database_url(),
        pool_size=settings.DB_POOL_SIZE,
        max_overflow=settings.DB_MAX_OVERFLOW,
        pool_timeout=settings.DB_POOL_TIMEOUT,
        pool_recycle=settings.DB_POOL_RECYCLE,
        pool_pre_ping=True,
        echo=False
    )

    # Create async session factory
    AsyncSessionLocal = async_sessionmaker(
        async_engine,
        class_=AsyncSession,
        autocommit=False,
        autoflush=False,
        expire_on_commit=False
    )

    async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
        """Dependency for getting async database sessions."""
        async with AsyncSessionLocal() as session:
            try:
                yield session
            finally:
                await session.close()

except Exception as e:
    # Fallback if asyncpg is not installed
    async_engine = None
    AsyncSessionLocal = None
    
    async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
        """Fallback - raises error if async not available."""
        raise NotImplementedError(
            f"Async database sessions not available. Install asyncpg: pip install asyncpg. Error: {e}"
        )
        yield  # type: ignore


# Export Base for alembic
__all__ = ['engine', 'SessionLocal', 'Base', 'get_db', 'get_async_session', 'AsyncSessionLocal']
