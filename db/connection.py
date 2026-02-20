"""
Database Connection and Session Management
Async SQLAlchemy with connection pooling
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from typing import AsyncGenerator
import os
from contextlib import asynccontextmanager

# Database URL from environment
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql+asyncpg://tekshila:tekshila@localhost:5432/tekshila"
)

# Create async engine with connection pooling
try:
    engine = create_async_engine(
        DATABASE_URL,
        echo=False,  # Set to True for SQL logging
        pool_size=20,
        max_overflow=30,
        pool_timeout=30,
        pool_recycle=1800,
        pool_pre_ping=True,
    )
except Exception as e:
    print(f"⚠️  Failed to create database engine: {e}")
    engine = None

# Async session factory
if engine:
    AsyncSessionLocal = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )
else:
    AsyncSessionLocal = None

@asynccontextmanager
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Get database session as async context manager"""
    # Check if engine is initialized (it might be None if connection failed)
    if engine is None:
        yield None
        return

    session = AsyncSessionLocal()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency for database sessions"""
    if engine is None:
        yield None
        return

    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

async def init_db():
    """Initialize database tables"""
    from db.models import Base
    
    if engine is None:
        print("⚠️  Database not configured or connection failed. Running in No-DB mode.")
        return

    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("✅ Database initialized")
    except Exception as e:
        print(f"⚠️  Database initialization failed: {e}. Running in No-DB mode.")

async def close_db():
    """Close database connections"""
    if engine:
        await engine.dispose()
        print("✅ Database connections closed")
