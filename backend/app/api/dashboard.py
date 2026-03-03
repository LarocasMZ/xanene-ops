from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import datetime, timedelta
from typing import List
from ..core.database import get_db
from ..models.user import User
from ..models.task import Task, TaskStatus, TaskCategory
from ..models.event import Event, EventCategory
from ..schemas.dashboard import (
    DashboardMetrics,
    TaskSummary,
    EventSummary,
    DashboardResponse,
)
from .deps import get_current_user

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("", response_model=DashboardResponse)
async def get_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    now = datetime.utcnow()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = today_start - timedelta(days=today_start.weekday())
    week_end = week_start + timedelta(days=7)

    # Calculate metrics
    total_active_tasks = db.query(Task).filter(
        Task.is_active == True,
        Task.status != "completed",
    ).count()

    tasks_completed_this_week = db.query(Task).filter(
        Task.is_active == True,
        Task.status == "completed",
        Task.completed_at >= week_start,
        Task.completed_at < week_end,
    ).count()

    upcoming_collections = db.query(Event).filter(
        Event.is_active == True,
        Event.category == EventCategory.COLLECTION,
        Event.start_datetime >= now,
    ).count()

    deliveries_scheduled = db.query(Event).filter(
        Event.is_active == True,
        Event.category == EventCategory.DELIVERY,
        Event.start_datetime >= now,
    ).count()

    overdue_tasks = db.query(Task).filter(
        Task.is_active == True,
        Task.due_date < now,
        Task.status != "completed",
    ).count()

    events_today = db.query(Event).filter(
        Event.is_active == True,
        Event.start_datetime >= today_start,
        Event.start_datetime < today_start + timedelta(days=1),
    ).count()

    metrics = DashboardMetrics(
        total_active_tasks=total_active_tasks,
        tasks_completed_this_week=tasks_completed_this_week,
        upcoming_collections=upcoming_collections,
        deliveries_scheduled=deliveries_scheduled,
        overdue_tasks=overdue_tasks,
        events_today=events_today,
    )

    # Get today's tasks
    today_tasks_query = db.query(Task).filter(
        Task.is_active == True,
        Task.status != "completed",
        Task.due_date >= today_start,
        Task.due_date < today_start + timedelta(days=1),
    ).limit(5)

    today_tasks = []
    for task in today_tasks_query:
        today_tasks.append(TaskSummary(
            id=task.id,
            title=task.title,
            priority=task.priority.value,
            status=task.status.value,
            due_date=task.due_date,
            assignee_name=task.assignee.full_name if task.assignee else None,
        ))

    # Get upcoming events
    upcoming_events_query = db.query(Event).filter(
        Event.is_active == True,
        Event.start_datetime >= now,
    ).order_by(Event.start_datetime).limit(5)

    upcoming_events = []
    for event in upcoming_events_query:
        upcoming_events.append(EventSummary(
            id=event.id,
            title=event.title,
            category=event.category.value,
            start_datetime=event.start_datetime,
            end_datetime=event.end_datetime,
            location=event.location,
        ))

    # Get overdue tasks
    overdue_tasks_query = db.query(Task).filter(
        Task.is_active == True,
        Task.due_date < now,
        Task.status != "completed",
    ).order_by(Task.due_date).limit(5)

    overdue_list = []
    for task in overdue_tasks_query:
        overdue_list.append(TaskSummary(
            id=task.id,
            title=task.title,
            priority=task.priority.value,
            status=task.status.value,
            due_date=task.due_date,
            assignee_name=task.assignee.full_name if task.assignee else None,
        ))

    return DashboardResponse(
        metrics=metrics,
        today_tasks=today_tasks,
        upcoming_events=upcoming_events,
        overdue_tasks=overdue_list,
    )
