"""Khởi tạo async engine và session factory cho PostgreSQL."""

from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession

from app.config.settings import Config

database_url = make_url(Config.DATABASE_URL)

sync_engine = create_engine(
    url=database_url, 
    echo=True
)
engine = AsyncEngine(sync_engine)
session_factory = async_sessionmaker(engine, class_=AsyncSession)
