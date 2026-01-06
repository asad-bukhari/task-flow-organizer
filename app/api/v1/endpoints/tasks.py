from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.rate_limiter import limiter
from app.models.task import Task, TaskCreate, TaskUpdate, TaskRead
from app.services.task_service import task_service

router = APIRouter()


@router.post("/", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
@limiter.limit("20/minute")
async def create_task(
    request: Request,
    task_in: TaskCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new task."""
    task = await task_service.create_task(db, task_in)
    return task


@router.get("/", response_model=List[TaskRead])
@limiter.limit("100/minute")
async def get_tasks(
    request: Request,
    skip: int = Query(0, ge=0, description="Number of tasks to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum number of tasks to return"),
    status: Optional[str] = Query(None, description="Filter by status"),
    priority: Optional[str] = Query(None, description="Filter by priority"),
    db: AsyncSession = Depends(get_db)
):
    """Get all tasks with optional filtering and pagination."""
    tasks, _ = await task_service.get_tasks(
        db, skip=skip, limit=limit, status=status, priority=priority
    )
    return tasks


@router.get("/stats")
@limiter.limit("50/minute")
async def get_task_stats(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Get task statistics."""
    tasks, total = await task_service.get_tasks(db, skip=0, limit=1000)

    # Calculate stats
    status_counts = {}
    priority_counts = {}

    for task in tasks:
        # Count by status
        status_key = task.status.value
        status_counts[status_key] = status_counts.get(status_key, 0) + 1

        # Count by priority
        priority_key = task.priority.value
        priority_counts[priority_key] = priority_counts.get(priority_key, 0) + 1

    return {
        "total": total,
        "by_status": status_counts,
        "by_priority": priority_counts
    }


@router.get("/{task_id}", response_model=TaskRead)
@limiter.limit("100/minute")
async def get_task(
    request: Request,
    task_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific task by ID."""
    task = await task_service.get_task(db, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found"
        )
    return task


@router.patch("/{task_id}", response_model=TaskRead)
@limiter.limit("30/minute")
async def update_task(
    request: Request,
    task_id: int,
    task_in: TaskUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a task."""
    task = await task_service.update_task(db, task_id, task_in)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found"
        )
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("20/minute")
async def delete_task(
    request: Request,
    task_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete a task."""
    deleted = await task_service.delete_task(db, task_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found"
        )
    return None
