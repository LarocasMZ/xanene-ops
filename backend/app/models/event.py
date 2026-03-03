from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey, Boolean, Text, Table
from sqlalchemy.orm import relationship
import enum
from ..core.database import Base


class EventCategory(str, enum.Enum):
    COLLECTION = "collection"
    PRODUCTION = "production"
    DELIVERY = "delivery"
    TRAINING = "training"
    SALES = "sales"


class RecurrenceType(str, enum.Enum):
    NONE = "none"
    DAILY = "daily"
    WEEKLY = "weekly"


# Association table for many-to-many relationship between Event and User
event_staff = Table(
    "event_staff",
    Base.metadata,
    Column("event_id", Integer, ForeignKey("events.id"), primary_key=True),
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
)


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    location = Column(String, nullable=True)
    start_datetime = Column(DateTime, nullable=False)
    end_datetime = Column(DateTime, nullable=False)
    category = Column(Enum(EventCategory), nullable=False)
    is_recurring = Column(Boolean, default=False, nullable=False)
    recurrence_type = Column(Enum(RecurrenceType), default=RecurrenceType.NONE, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    creator = relationship("User", foreign_keys=[created_by_id], back_populates="created_events")
    staff = relationship("User", secondary=event_staff, back_populates="assigned_events")

    def __repr__(self):
        return f"<Event(id={self.id}, title={self.title}, start={self.start_datetime})>"
