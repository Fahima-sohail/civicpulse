from datetime import datetime, timezone
from uuid import UUID, uuid4
from sqlalchemy import CheckConstraint, DateTime, Enum, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.db import Base
from app.schemas import Category, Priority, Status

def utcnow() -> datetime:
    return datetime.now(timezone.utc)

class Complaint(Base):
    __tablename__ = "complaints"
    __table_args__ = (
        CheckConstraint("length(text) BETWEEN 10 AND 2000", name="ck_complaints_text_length"),
        CheckConstraint("length(location) BETWEEN 3 AND 200", name="ck_complaints_location_length"),
    )
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    text: Mapped[str] = mapped_column(Text)
    location: Mapped[str] = mapped_column(String(200))
    reporter_contact: Mapped[str | None] = mapped_column(String(255), nullable=True)
    category: Mapped[Category] = mapped_column(Enum(Category, name="category", native_enum=False))
    priority: Mapped[Priority] = mapped_column(Enum(Priority, name="priority", native_enum=False))
    status: Mapped[Status] = mapped_column(Enum(Status, name="status", native_enum=False), default=Status.open)
    ai_summary: Mapped[str | None] = mapped_column(String(140), nullable=True)
    triaged_by: Mapped[str] = mapped_column(String(32))
    triage_latency_ms: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)
