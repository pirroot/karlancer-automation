from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from karlancer_automation.config import get_settings
from karlancer_automation.models import Base


def create_database_engine():
    settings = get_settings()

    if not settings.database_url:
        raise RuntimeError("DATABASE_URL is missing from .env")

    return create_async_engine(
        settings.database_url,
        pool_pre_ping=True,
    )


def create_session_factory(engine):
    return async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )


async def create_tables(engine) -> None:
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
