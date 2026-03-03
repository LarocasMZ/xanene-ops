from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from ..models.event import EventCategory, RecurrenceType


class EventBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    location: Optional[str] = None
    start_datetime: datetime
    end_datetime: datetime
    category: EventCategory
    is_recurring: bool = False
    recurrence_type: Optional[RecurrenceType] = RecurrenceType.NONE
    assigned_staff_ids: Optional[List[int]] = []


class EventCreate(EventBase):
    pass


class EventUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    location: Optional[str] = None
    start_datetime: Optional[datetime] = None
    end_datetime: Optional[datetime] = None
    category: Optional[EventCategory] = None
    is_recurring: Optional[bool] = None
    recurrence_type: Optional[RecurrenceType] = None
    assigned_staff_ids: Optional[List[int]] = None


class EventResponse(EventBase):
    id: int
    created_by_id: int
    created_at: datetime
    updated_at: datetime
    staff: List[dict] = []

    class Config:
        from_attributes = True
