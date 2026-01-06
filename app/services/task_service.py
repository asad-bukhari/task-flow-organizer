from typing import List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task import Task, TaskCreate, TaskUpdate
from app.repositories.task_repository import task_repository


class TaskService:
    """Service layer for task business logic."""

    def __init__(self) -> None:
        self.repository = task_repository

    async def get_task(self, db: AsyncSession, task_id: int) -> Optional[Task]:
        """Get a single task by ID."""
        return await self.repository.get(db, task_id)

    async def get_tasks(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
        priority: Optional[str] = None,
    ) -> Tuple[List[Task], int]:
        """
        Get multiple tasks with pagination and filtering.
        Returns (tasks, total_count).
        """
        return await self.repository.get_multi(
            db, skip=skip, limit=limit, status=status, priority=priority
        )

    async def create_task(self, db: AsyncSession, task_in: TaskCreate) -> Task:
        """Create a new task."""
        return await self.repository.create(db, task_in)

    async def update_task(
        self,
        db: AsyncSession,
        task_id: int,
        task_in: TaskUpdate
    ) -> Optional[Task]:
        """Update an existing task."""
        task = await self.repository.get(db, task_id)
        if not task:
            return None
        return await self.repository.update(db, task, task_in)

    async def delete_task(self, db: AsyncSession, task_id: int) -> bool:
        """Delete a task."""
        return await self.repository.delete(db, task_id)


# Create singleton instance
task_service = TaskService()
