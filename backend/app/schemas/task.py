from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime

# Type definitions for string-based enums
TaskPriorityType = Literal["low", "medium", "high", "critical"]
TaskStatusType = Literal["pending", "in_progress", "completed"]
# Category can be any string now


class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    priority: TaskPriorityType = "medium"
    category: str
    due_date: Optional[datetime] = None
    assigned_to_id: Optional[int] = None


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    priority: Optional[TaskPriorityType] = None
    status: Optional[TaskStatusType] = None
    category: Optional[str] = None
    due_date: Optional[datetime] = None
    assigned_to_id: Optional[int] = None


class TaskResponse(TaskBase):
    id: int
    status: str
    completed_at: Optional[datetime] = None
    created_by_id: int
    created_at: datetime
    updated_at: datetime
    assigned_to_id: Optional[int] = None

    class Config:
        from_attributes = True
