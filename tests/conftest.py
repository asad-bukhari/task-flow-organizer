import pytest
import asyncio
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.core.database import get_db
from app.models.task import Task, Priority, Status
from app.core.config import get_settings
from app.core.rate_limiter import limiter
from sqlmodel import SQLModel

settings = get_settings()

# Test database URL (use in-memory SQLite for fast tests)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_engine():
    """Create test database engine."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        future=True
    )

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    yield engine

    # Cleanup
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)

    await engine.dispose()


@pytest.fixture
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create database session for tests with automatic rollback."""
    async_session_maker = sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    async with async_session_maker() as session:
        # Begin transaction for test isolation
        await session.begin_nested()

        yield session

        # Rollback all changes after test
        await session.rollback()


@pytest.fixture(autouse=True)
async def reset_rate_limiter():
    """Reset rate limiter state before each test."""
    # Clear rate limiter state
    if hasattr(limiter, "storage"):
        # Access and clear the storage
        storage = limiter.storage
        if hasattr(storage, "storage"):
            storage.storage.clear()

    yield

    # Cleanup after test
    if hasattr(limiter, "storage"):
        storage = limiter.storage
        if hasattr(storage, "storage"):
            storage.storage.clear()


@pytest.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create test client with database override."""
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
async def sample_task(db_session: AsyncSession) -> Task:
    """Create a sample task in database."""
    task = Task(
        title="Sample Task",
        description="This is a sample task for testing",
        priority=Priority.MEDIUM,
        status=Status.TODO
    )
    db_session.add(task)
    await db_session.commit()
    await db_session.refresh(task)
    return task


@pytest.fixture
async def sample_tasks(db_session: AsyncSession) -> list[Task]:
    """Create multiple sample tasks in database."""
    tasks = [
        Task(
            title=f"Task {i}",
            description=f"Description for task {i}",
            priority=Priority(list(Priority)[i % len(Priority)]),
            status=Status(list(Status)[i % len(Status)])
        )
        for i in range(1, 11)
    ]
    db_session.add_all(tasks)
    await db_session.commit()
    for task in tasks:
        await db_session.refresh(task)
    return tasks


@pytest.fixture
def task_data():
    """Provide sample task creation data."""
    return {
        "title": "Test Task",
        "description": "This is a test task description",
        "priority": "high",
        "status": "todo",
        "due_date": "2026-12-31T23:59:59"
    }


@pytest.fixture
def task_update_data():
    """Provide sample task update data."""
    return {
        "title": "Updated Task Title",
        "description": "Updated description",
        "status": "in_progress",
        "priority": "high"
    }
