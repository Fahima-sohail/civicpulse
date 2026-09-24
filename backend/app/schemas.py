from datetime import datetime
from enum import StrEnum
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field

class Category(StrEnum):
    water = "water"
    electricity = "electricity"
    sanitation = "sanitation"
    roads = "roads"
    streetlights = "streetlights"
    other = "other"

class Priority(StrEnum):
    high = "high"
    normal = "normal"
    low = "low"

class Status(StrEnum):
    open = "open"
    in_progress = "in_progress"
    resolved = "resolved"
    rejected = "rejected"

class ComplaintCreate(BaseModel):
    text: str = Field(min_length=10, max_length=2000)
    location: str = Field(min_length=3, max_length=200)
    reporter_contact: str | None = Field(default=None, max_length=255)

class StatusUpdate(BaseModel):
    status: Status

class ComplaintOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    text: str
    location: str
    reporter_contact: str | None
    category: Category
    priority: Priority
    status: Status
    ai_summary: str | None
    triaged_by: str
    triage_latency_ms: int
    created_at: datetime
    updated_at: datetime

class ComplaintPage(BaseModel):
    items: list[ComplaintOut]
    total: int
    page: int
    page_size: int

class StatsOut(BaseModel):
    by_category: dict[str, int]
    by_priority: dict[str, int]

class ProviderOutcome(BaseModel):
    provider: str
    latency_ms: int
    fallback: bool

class ProvidersOut(BaseModel):
    active_provider: str
    outcomes: list[ProviderOutcome]
