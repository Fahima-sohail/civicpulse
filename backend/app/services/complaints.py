from uuid import UUID, uuid4
from app.models import Complaint
from app.providers.redis_client import RedisClient
from app.repositories.complaints import ComplaintRepository
from app.schemas import Category, ComplaintCreate, ComplaintPage, ComplaintOut, Priority, StatsOut, Status
from app.services.triage import TriageService

TRANSITIONS: dict[Status, set[Status]] = {
    Status.open: {Status.in_progress, Status.rejected},
    Status.in_progress: {Status.resolved, Status.rejected},
    Status.resolved: set(),
    Status.rejected: set(),
}

class NotFoundError(LookupError): pass
class InvalidTransitionError(ValueError): pass

class ComplaintService:
    def __init__(self, repository: ComplaintRepository, triage: TriageService, redis_client: RedisClient):
        self.repository, self.triage, self.redis = repository, triage, redis_client

    def create(self, data: ComplaintCreate) -> ComplaintOut:
        complaint_id = uuid4()
        result, triaged_by, latency = self.triage.triage(complaint_id, data.text, data.location)
        row = Complaint(id=complaint_id, text=data.text, location=data.location, reporter_contact=data.reporter_contact,
                        category=result.category, priority=result.priority, ai_summary=result.summary,
                        triaged_by=triaged_by, triage_latency_ms=latency)
        saved = self.repository.create(row)
        try: self.redis.delete("stats:v1")
        except Exception: pass
        return ComplaintOut.model_validate(saved)

    def get(self, complaint_id: UUID) -> ComplaintOut:
        row = self.repository.get(complaint_id)
        if not row: raise NotFoundError("Complaint not found")
        return ComplaintOut.model_validate(row)

    def list(self, category: Category | None, priority: Priority | None, status: Status | None, page: int, page_size: int) -> ComplaintPage:
        rows, total = self.repository.list(category, priority, status, page, page_size)
        return ComplaintPage(items=[ComplaintOut.model_validate(row) for row in rows], total=total, page=page, page_size=page_size)

    def set_status(self, complaint_id: UUID, requested: Status) -> ComplaintOut:
        current = self.repository.get(complaint_id)
        if not current: raise NotFoundError("Complaint not found")
        if requested not in TRANSITIONS[current.status]:
            raise InvalidTransitionError(f"Invalid transition: {current.status.value} -> {requested.value}")
        row = self.repository.update_status(complaint_id, requested)
        try: self.redis.delete("stats:v1")
        except Exception: pass
        return ComplaintOut.model_validate(row)

    def stats(self) -> tuple[StatsOut, str]:
        try:
            cached = self.redis.get_json("stats:v1")
            if cached: return StatsOut.model_validate(cached), "HIT"
        except Exception: pass
        categories, priorities = self.repository.stats()
        payload = StatsOut(by_category=categories, by_priority=priorities)
        try: self.redis.set_json("stats:v1", payload.model_dump(), 30)
        except Exception: pass
        return payload, "MISS"
