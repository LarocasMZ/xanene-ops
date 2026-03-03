from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Optional
from ..core.database import get_db
from ..models.user import User, UserRole
from ..models.task import Task, TaskStatus, TaskPriority, TaskCategory
from ..schemas.task import TaskCreate, TaskUpdate, TaskResponse
from .deps import get_current_user, require_admin_or_ops

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    new_task = Task(
        title=task_data.title,
        description=task_data.description,
        priority=task_data.priority,
        category=task_data.category,
        due_date=task_data.due_date,
        assigned_to_id=task_data.assigned_to_id,
        created_by_id=current_user.id,
    )

    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    return new_task


@router.get("", response_model=List[TaskResponse])
async def list_tasks(
    status_filter: Optional[TaskStatus] = Query(None, alias="status"),
    priority: Optional[TaskPriority] = Query(None),
    category: Optional[TaskCategory] = Query(None),
    assigned_to: Optional[int] = Query(None),
    include_completed: bool = Query(False),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Task).filter(Task.is_active == True)

    if status_filter:
        query = query.filter(Task.status == status_filter)
    elif not include_completed:
        query = query.filter(Task.status != TaskStatus.COMPLETED)

    if priority:
        query = query.filter(Task.priority == priority)

    if category:
        query = query.filter(Task.category == category)

    if assigned_to:
        query = query.filter(Task.assigned_to_id == assigned_to)

    tasks = query.order_by(Task.due_date.nullsfirst(), Task.created_at.desc()).all()
    return tasks


@router.get("/my-tasks", response_model=List[TaskResponse])
async def get_my_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    tasks = (
        db.query(Task)
        .filter(
            Task.is_active == True,
            Task.assigned_to_id == current_user.id,
            Task.status != TaskStatus.COMPLETED,
        )
        .order_by(Task.due_date.nullsfirst(), Task.created_at.desc())
        .all()
    )
    return tasks


@router.get("/overdue", response_model=List[TaskResponse])
async def get_overdue_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    now = datetime.utcnow()
    tasks = (
        db.query(Task)
        .filter(
            Task.is_active == True,
            Task.due_date < now,
            Task.status != TaskStatus.COMPLETED,
        )
        .order_by(Task.due_date)
        .all()
    )
    return tasks


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task or not task.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    return task


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task_data: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task or not task.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    # Field staff can only update their assigned tasks
    if current_user.role == UserRole.FIELD_STAFF:
        if task.assigned_to_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only update your assigned tasks",
            )
        # Field staff can only update status
        allowed_fields = {"status"}
        update_data = {k: v for k, v in task_data.model_dump(exclude_unset=True).items() if k in allowed_fields}
    else:
        update_data = task_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(task, field, value)

    # Set completed_at when status changes to completed
    if task.status == TaskStatus.COMPLETED and not task.completed_at:
        task.completed_at = datetime.utcnow()

    db.commit()
    db.refresh(task)
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_ops),
):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    task.is_active = False
    db.commit()
    return None


@router.get("/kanban", response_model=dict)
async def get_kanban_board(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get tasks grouped by status for Kanban view"""
    tasks = db.query(Task).filter(
        Task.is_active == True,
        Task.status != TaskStatus.COMPLETED,
    ).all()

    kanban = {
        "pending": [],
        "in_progress": [],
        "completed": [],
    }

    for task in tasks:
        task_dict = {
            "id": task.id,
            "title": task.title,
            "priority": task.priority.value,
            "category": task.category.value,
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "assignee": {"id": task.assignee.id, "full_name": task.assignee.full_name} if task.assignee else None,
        }
        kanban[task.status.value].append(task_dict)

    return kanban
