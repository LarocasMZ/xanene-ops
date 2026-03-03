from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Optional
from ..core.database import get_db
from ..models.user import User, UserRole
from ..models.event import Event, event_staff
from ..schemas.event import EventCreate, EventUpdate, EventResponse
from .deps import get_current_user, require_admin_or_ops

router = APIRouter(prefix="/events", tags=["Events"])


@router.post("", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
async def create_event(
    event_data: EventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if event_data.start_datetime >= event_data.end_datetime:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="End datetime must be after start datetime",
        )

    new_event = Event(
        title=event_data.title,
        description=event_data.description,
        location=event_data.location,
        start_datetime=event_data.start_datetime,
        end_datetime=event_data.end_datetime,
        category=event_data.category,
        is_recurring=event_data.is_recurring,
        recurrence_type=event_data.recurrence_type,
        created_by_id=current_user.id,
    )

    db.add(new_event)
    db.commit()
    db.refresh(new_event)

    # Assign staff if provided
    if event_data.assigned_staff_ids:
        staff_users = db.query(User).filter(User.id.in_(event_data.assigned_staff_ids)).all()
        new_event.staff = staff_users
        db.commit()
        db.refresh(new_event)

    return new_event


@router.get("", response_model=List[EventResponse])
async def list_events(
    category: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    include_past: bool = Query(False),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Event).filter(Event.is_active == True)

    if category:
        query = query.filter(Event.category == category)

    if start_date:
        query = query.filter(Event.start_datetime >= start_date)

    if end_date:
        query = query.filter(Event.end_datetime <= end_date)

    if not include_past:
        query = query.filter(Event.end_datetime >= datetime.utcnow())

    events = query.order_by(Event.start_datetime).all()
    return events


@router.get("/today", response_model=List[EventResponse])
async def get_todays_events(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)

    events = (
        db.query(Event)
        .filter(
            Event.is_active == True,
            Event.start_datetime >= today_start,
            Event.start_datetime < today_end,
        )
        .order_by(Event.start_datetime)
        .all()
    )
    return events


@router.get("/upcoming", response_model=List[EventResponse])
async def get_upcoming_events(
    days: int = Query(7, ge=1, le=30),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    now = datetime.utcnow()
    future_date = now + timedelta(days=days)

    events = (
        db.query(Event)
        .filter(
            Event.is_active == True,
            Event.start_datetime >= now,
            Event.start_datetime <= future_date,
        )
        .order_by(Event.start_datetime)
        .limit(10)
        .all()
    )
    return events


@router.get("/{event_id}", response_model=EventResponse)
async def get_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event or not event.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )
    return event


@router.put("/{event_id}", response_model=EventResponse)
async def update_event(
    event_id: int,
    event_data: EventUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_ops),
):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event or not event.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )

    update_data = event_data.model_dump(exclude_unset=True)
    update_data.pop("assigned_staff_ids", None)

    for field, value in update_data.items():
        setattr(event, field, value)

    # Update staff assignments if provided
    if event_data.assigned_staff_ids is not None:
        staff_users = db.query(User).filter(User.id.in_(event_data.assigned_staff_ids)).all()
        event.staff = staff_users

    db.commit()
    db.refresh(event)
    return event


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_ops),
):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )

    event.is_active = False
    db.commit()
    return None
