from sqlmodel import SQLModel, create_engine
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# SQLite Database URLs
DATABASE_URL = "sqlite+aiosqlite:///./copiloto.db"
SYNC_DATABASE_URL = "sqlite:///./copiloto.db"

engine = AsyncEngine(create_engine(DATABASE_URL, echo=False, future=True))
_sync_engine = create_engine(SYNC_DATABASE_URL, echo=False)

def get_sync_engine():
    """Return sync engine for LangChain tools (they run synchronously)."""
    return _sync_engine

async def init_db():
    async with engine.begin() as conn:
        # Create tables
        await conn.run_sync(SQLModel.metadata.create_all)

async def get_session() -> AsyncSession:
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session
