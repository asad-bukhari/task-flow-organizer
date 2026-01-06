from typing import List, Optional, Type
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlmodel import SQLModel

from app.models.task import Task, TaskCreate, TaskUpdate


class TaskRepository:
    """Repository for task CRUD operations."""

    def __init__(self) -> None:
        self.model = Task

    async def get(self, db: AsyncSession, task_id: int) -> Optional[Task]:
        """Get a task by ID."""
        result = await db.execute(
            select(self.model).where(self.model.id == task_id)
        )
        return result.scalars().first()

    async def get_multi(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
        priority: Optional[str] = None,
    ) -> tuple[List[Task], int]:
        """
        Get multiple tasks with optional filtering.
        Returns (tasks, total_count).
        """
        query = select(self.model)

        # Apply filters
        if status:
            query = query.where(self.model.status == status)
        if priority:
            query = query.where(self.model.priority == priority)

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        count_result = await db.execute(count_query)
        total = count_result.scalar() or 0

        # Apply pagination
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        tasks = result.scalars().all()

        return list(tasks), total

    async def create(self, db: AsyncSession, obj_in: TaskCreate) -> Task:
        """Create a new task."""
        db_obj = self.model(**obj_in.model_dump())
        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self,
        db: AsyncSession,
        db_obj: Task,
        obj_in: TaskUpdate
    ) -> Task:
        """Update an existing task."""
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj

    async def delete(self, db: AsyncSession, task_id: int) -> bool:
        """Delete a task."""
        obj = await self.get(db, task_id)
        if obj:
            await db.delete(obj)
            return True
        return False


# Create singleton instance
task_repository = TaskRepository()
