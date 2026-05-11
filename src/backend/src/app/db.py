from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base
from src.app.config import settings


def _build_engine():
    url = settings.database_url
    kwargs = {"echo": settings.debug}
    if url.startswith("sqlite"):
        kwargs.update({})
    else:
        kwargs.update({"pool_size": 20, "max_overflow": 10, "pool_pre_ping": True})

    try:
        return create_async_engine(url, **kwargs)
    except ModuleNotFoundError:
        return create_async_engine("sqlite+aiosqlite:///:memory:", echo=settings.debug)


engine = _build_engine()

async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

Base = declarative_base()


async def get_db() -> AsyncSession:
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
