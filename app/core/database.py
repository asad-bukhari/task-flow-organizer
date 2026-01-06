from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
from app.core.config import get_settings

settings = get_settings()

# Convert postgresql:// to postgresql+asyncpg:// and clean URL
database_url = settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

# Remove sslmode and other incompatible query params for asyncpg
# Neon works with asyncpg without needing explicit sslmode in the URL
if "sslmode" in database_url:
    database_url = database_url.split("?")[0]

# Create async engine
engine = create_async_engine(
    database_url,
    echo=True,
    future=True,
)

# Create async session factory
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def init_db():
    """Initialize database tables."""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_db() -> AsyncSession:
    """Dependency for database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
