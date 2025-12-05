"""Enhanced database connection pooling with monitoring and async support

Provides:
- Connection pool health monitoring
- Async database sessions
- Connection lifecycle hooks
- Pool statistics
"""

import asyncio
from contextlib import asynccontextmanager, contextmanager
from datetime import datetime
from typing import Optional, Dict, Any, Generator, AsyncGenerator
import logging
from dataclasses import dataclass, field
import threading
import time

from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool, NullPool
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.core.config import settings

logger = logging.getLogger(__name__)


@dataclass
class PoolStats:
    """Connection pool statistics"""
    pool_size: int = 0
    checked_out: int = 0
    overflow: int = 0
    checked_in: int = 0
    total_connections: int = 0
    invalidated: int = 0
    soft_invalidated: int = 0
    created_time: datetime = field(default_factory=datetime.now)
    last_check: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "pool_size": self.pool_size,
            "checked_out": self.checked_out,
            "overflow": self.overflow,
            "checked_in": self.checked_in,
            "total_connections": self.total_connections,
            "invalidated": self.invalidated,
            "available": self.pool_size - self.checked_out,
            "utilization_percent": (self.checked_out / self.pool_size * 100) if self.pool_size > 0 else 0,
            "last_check": self.last_check.isoformat() if self.last_check else None
        }


class ConnectionPoolManager:
    """Enhanced connection pool manager with monitoring
    
    Features:
    - Health monitoring
    - Connection lifecycle hooks
    - Statistics collection
    - Automatic reconnection
    """
    
    def __init__(self):
        self._engine = None
        self._async_engine = None
        self._session_factory = None
        self._async_session_factory = None
        self._stats = PoolStats()
        self._lock = threading.Lock()
        self._connection_count = 0
        self._query_count = 0
        self._error_count = 0
        
    @property
    def engine(self):
        """Get or create sync engine"""
        if self._engine is None:
            self._engine = self._create_sync_engine()
        return self._engine
    
    @property
    def async_engine(self):
        """Get or create async engine"""
        if self._async_engine is None:
            self._async_engine = self._create_async_engine()
        return self._async_engine
    
    def _create_sync_engine(self):
        """Create synchronous engine with optimized pooling"""
        engine = create_engine(
            settings.DATABASE_URL,
            poolclass=QueuePool,
            pool_size=settings.DB_POOL_SIZE,
            max_overflow=settings.DB_MAX_OVERFLOW,
            pool_timeout=settings.DB_POOL_TIMEOUT,
            pool_recycle=settings.DB_POOL_RECYCLE,
            pool_pre_ping=True,  # Verify connections before use
            echo=settings.DEBUG,
            connect_args={
                "connect_timeout": 10,
                "application_name": "NationalIndicator",
                "options": "-c statement_timeout=30000"  # 30s query timeout
            }
        )
        
        # Register event listeners
        self._register_pool_events(engine)
        
        return engine
    
    def _create_async_engine(self):
        """Create async engine for async operations"""
        # Convert sync URL to async
        async_url = settings.DATABASE_URL.replace(
            "postgresql://", 
            "postgresql+asyncpg://"
        )
        
        engine = create_async_engine(
            async_url,
            pool_size=settings.DB_POOL_SIZE,
            max_overflow=settings.DB_MAX_OVERFLOW,
            pool_timeout=settings.DB_POOL_TIMEOUT,
            pool_recycle=settings.DB_POOL_RECYCLE,
            pool_pre_ping=True,
            echo=settings.DEBUG
        )
        
        return engine
    
    def _register_pool_events(self, engine):
        """Register SQLAlchemy pool event listeners"""
        
        @event.listens_for(engine, "connect")
        def on_connect(dbapi_conn, connection_record):
            with self._lock:
                self._connection_count += 1
            logger.debug(f"New connection created. Total: {self._connection_count}")
        
        @event.listens_for(engine, "checkout")
        def on_checkout(dbapi_conn, connection_record, connection_proxy):
            self._stats.checked_out += 1
            logger.debug(f"Connection checked out. Active: {self._stats.checked_out}")
        
        @event.listens_for(engine, "checkin")
        def on_checkin(dbapi_conn, connection_record):
            self._stats.checked_out = max(0, self._stats.checked_out - 1)
            self._stats.checked_in += 1
            logger.debug(f"Connection checked in. Active: {self._stats.checked_out}")
        
        @event.listens_for(engine, "invalidate")
        def on_invalidate(dbapi_conn, connection_record, exception):
            self._stats.invalidated += 1
            if exception:
                logger.warning(f"Connection invalidated due to: {exception}")
    
    def get_session_factory(self) -> sessionmaker:
        """Get session factory"""
        if self._session_factory is None:
            self._session_factory = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine,
                expire_on_commit=False
            )
        return self._session_factory
    
    def get_async_session_factory(self) -> async_sessionmaker:
        """Get async session factory"""
        if self._async_session_factory is None:
            self._async_session_factory = async_sessionmaker(
                self.async_engine,
                class_=AsyncSession,
                expire_on_commit=False,
                autocommit=False,
                autoflush=False
            )
        return self._async_session_factory
    
    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """Get database session with automatic cleanup"""
        session = self.get_session_factory()()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            self._error_count += 1
            logger.error(f"Database error: {e}")
            raise
        finally:
            session.close()
    
    @asynccontextmanager
    async def get_async_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get async database session"""
        async with self.get_async_session_factory()() as session:
            try:
                yield session
                await session.commit()
            except Exception as e:
                await session.rollback()
                self._error_count += 1
                logger.error(f"Async database error: {e}")
                raise
    
    def get_pool_stats(self) -> PoolStats:
        """Get current pool statistics"""
        if self._engine is not None:
            pool = self._engine.pool
            self._stats.pool_size = pool.size()
            self._stats.total_connections = self._connection_count
            self._stats.last_check = datetime.now()
        return self._stats
    
    def health_check(self) -> Dict[str, Any]:
        """Perform health check on connection pool"""
        start = time.time()
        
        try:
            with self.get_session() as session:
                result = session.execute(text("SELECT 1"))
                result.fetchone()
            
            elapsed = time.time() - start
            stats = self.get_pool_stats()
            
            return {
                "healthy": True,
                "response_time_ms": round(elapsed * 1000, 2),
                "pool_stats": stats.to_dict(),
                "error_count": self._error_count,
                "query_count": self._query_count
            }
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "healthy": False,
                "error": str(e),
                "error_count": self._error_count
            }
    
    async def async_health_check(self) -> Dict[str, Any]:
        """Async health check"""
        start = time.time()
        
        try:
            async with self.get_async_session() as session:
                result = await session.execute(text("SELECT 1"))
                result.fetchone()
            
            elapsed = time.time() - start
            
            return {
                "healthy": True,
                "response_time_ms": round(elapsed * 1000, 2),
                "async_supported": True
            }
        except Exception as e:
            logger.error(f"Async health check failed: {e}")
            return {
                "healthy": False,
                "error": str(e),
                "async_supported": False
            }
    
    def dispose(self):
        """Dispose of all connections"""
        if self._engine is not None:
            self._engine.dispose()
            logger.info("Sync engine disposed")
        
        if self._async_engine is not None:
            # Async engine disposal should be called in async context
            asyncio.get_event_loop().run_until_complete(
                self._async_engine.dispose()
            )
            logger.info("Async engine disposed")


# Global pool manager instance
_pool_manager: Optional[ConnectionPoolManager] = None


def get_pool_manager() -> ConnectionPoolManager:
    """Get global pool manager instance"""
    global _pool_manager
    if _pool_manager is None:
        _pool_manager = ConnectionPoolManager()
    return _pool_manager


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency for sync database sessions"""
    manager = get_pool_manager()
    with manager.get_session() as session:
        yield session


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency for async database sessions"""
    manager = get_pool_manager()
    async with manager.get_async_session() as session:
        yield session


# Convenience functions
def get_pool_health() -> Dict[str, Any]:
    """Get connection pool health status"""
    return get_pool_manager().health_check()


async def get_async_pool_health() -> Dict[str, Any]:
    """Get async pool health status"""
    return await get_pool_manager().async_health_check()
