from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class DashboardMetrics(BaseModel):
    total_active_tasks: int
    tasks_completed_this_week: int
    upcoming_collections: int
    deliveries_scheduled: int
    overdue_tasks: int
    events_today: int


class TaskSummary(BaseModel):
    id: int
    title: str
    priority: str
    status: str
    due_date: Optional[datetime] = None
    assignee_name: Optional[str] = None


class EventSummary(BaseModel):
    id: int
    title: str
    category: str
    start_datetime: datetime
    end_datetime: datetime
    location: Optional[str] = None


class DashboardResponse(BaseModel):
    metrics: DashboardMetrics
    today_tasks: List[TaskSummary]
    upcoming_events: List[EventSummary]
    overdue_tasks: List[TaskSummary]
