from collections.abc import Callable
from uuid import UUID
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.models import Complaint
from app.schemas import Category, Priority, Status

class ComplaintRepository:
    """The only layer that issues SQLAlchemy/SQL queries."""
    def __init__(self, session_factory: Callable[[], Session]):
        self.session_factory = session_factory

    def create(self, complaint: Complaint) -> Complaint:
        with self.session_factory() as session:
            session.add(complaint)
            session.commit()
            session.refresh(complaint)
            return complaint

    def get(self, complaint_id: UUID) -> Complaint | None:
        with self.session_factory() as session:
            return session.get(Complaint, complaint_id)

    def list(self, category: Category | None, priority: Priority | None, status: Status | None, page: int, page_size: int) -> tuple[list[Complaint], int]:
        with self.session_factory() as session:
            stmt = select(Complaint)
            if category: stmt = stmt.where(Complaint.category == category)
            if priority: stmt = stmt.where(Complaint.priority == priority)
            if status: stmt = stmt.where(Complaint.status == status)
            total = session.scalar(select(func.count()).select_from(stmt.subquery())) or 0
            rows = session.scalars(stmt.order_by(Complaint.created_at.desc()).offset((page - 1) * page_size).limit(page_size)).all()
            return rows, total

    def update_status(self, complaint_id: UUID, status: Status) -> Complaint | None:
        with self.session_factory() as session:
            row = session.get(Complaint, complaint_id)
            if row is None: return None
            row.status = status
            session.commit()
            session.refresh(row)
            return row

    def stats(self) -> tuple[dict[str, int], dict[str, int]]:
        with self.session_factory() as session:
            categories = {str(k): v for k, v in session.execute(select(Complaint.category, func.count()).group_by(Complaint.category)).all()}
            priorities = {str(k): v for k, v in session.execute(select(Complaint.priority, func.count()).group_by(Complaint.priority)).all()}
            return categories, priorities

    def healthcheck(self) -> bool:
        try:
            with self.session_factory() as session: session.execute(select(1))
            return True
        except Exception:
            return False

    def exists_by_text_and_location(self, text: str, location: str) -> bool:
        with self.session_factory() as session:
            return session.scalar(select(Complaint.id).where(Complaint.text == text, Complaint.location == location).limit(1)) is not None
