from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from ..models.task import TaskPriority, TaskStatus, TaskCategory


class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    priority: TaskPriority = TaskPriority.MEDIUM
    category: TaskCategory
    due_date: Optional[datetime] = None
    assigned_to_id: Optional[int] = None


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    priority: Optional[TaskPriority] = None
    status: Optional[TaskStatus] = None
    category: Optional[TaskCategory] = None
    due_date: Optional[datetime] = None
    assigned_to_id: Optional[int] = None


class TaskResponse(TaskBase):
    id: int
    status: TaskStatus
    completed_at: Optional[datetime] = None
    created_by_id: int
    created_at: datetime
    updated_at: datetime
    assigned_to_id: Optional[int] = None

    class Config:
        from_attributes = True
