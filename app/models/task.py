from typing import Optional
from datetime import datetime, timezone
from sqlmodel import Field, SQLModel
from enum import Enum
from pydantic import field_validator


class Priority(str, Enum):
    """Task priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Status(str, Enum):
    """Task status."""
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    CANCELLED = "cancelled"


class TaskBase(SQLModel):
    """Base task model."""
    title: str = Field(index=True, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)
    priority: Priority = Field(default=Priority.MEDIUM)
    status: Status = Field(default=Status.TODO)
    due_date: Optional[datetime] = Field(default=None)


class Task(TaskBase, table=True):
    """Task database model."""
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class TaskCreate(TaskBase):
    """Schema for creating a task."""

    @field_validator('due_date')
    @classmethod
    def remove_timezone(cls, v: Optional[datetime]) -> Optional[datetime]:
        """Remove timezone info from due_date to match database column."""
        if v is not None and v.tzinfo is not None:
            return v.replace(tzinfo=None)
        return v


class TaskUpdate(SQLModel):
    """Schema for updating a task."""
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)
    priority: Optional[Priority] = Field(default=None)
    status: Optional[Status] = Field(default=None)
    due_date: Optional[datetime] = Field(default=None)

    @field_validator('due_date')
    @classmethod
    def remove_timezone(cls, v: Optional[datetime]) -> Optional[datetime]:
        """Remove timezone info from due_date to match database column."""
        if v is not None and v.tzinfo is not None:
            return v.replace(tzinfo=None)
        return v


class TaskRead(TaskBase):
    """Schema for reading a task."""
    id: int
    created_at: datetime
    updated_at: datetime
