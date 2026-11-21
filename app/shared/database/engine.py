"""Khởi tạo async engine và session factory cho PostgreSQL."""

from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession

from app.shared.config.settings import Config

database_url = make_url(Config.DATABASE_URL)
if database_url.drivername in {"postgresql", "postgres"}:
    database_url = database_url.set(drivername="postgresql+asyncpg")

engine = create_async_engine(database_url, hide_parameters=True)
session_factory = async_sessionmaker(engine, class_=AsyncSession)
