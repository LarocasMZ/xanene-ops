from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
import enum
from ..core.database import Base


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    OPERATIONS_MANAGER = "operations_manager"
    FIELD_STAFF = "field_staff"
    SALES = "sales"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.FIELD_STAFF, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    assigned_tasks = relationship("Task", foreign_keys="Task.assigned_to_id", back_populates="assignee")
    created_tasks = relationship("Task", foreign_keys="Task.created_by_id", back_populates="creator")
    assigned_events = relationship("Event", secondary="event_staff", back_populates="staff")
    created_events = relationship("Event", back_populates="creator")

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"
