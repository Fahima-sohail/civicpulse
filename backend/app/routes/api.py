from fastapi import APIRouter, HTTPException, Query, Request, Response, status
from uuid import UUID
from app.schemas import Category, ComplaintCreate, ComplaintOut, ComplaintPage, Priority, ProvidersOut, StatsOut, Status, StatusUpdate
from app.services.complaints import ComplaintService, InvalidTransitionError, NotFoundError

router = APIRouter()

def service(request: Request) -> ComplaintService:
    return request.app.state.complaints

@router.post("/api/complaints", response_model=ComplaintOut, status_code=status.HTTP_201_CREATED)
def create_complaint(payload: ComplaintCreate, request: Request):
    allowed, retry_after = request.app.state.redis.check_rate_limit(request.client.host if request.client else "unknown", request.app.state.settings.rate_limit_count, request.app.state.settings.rate_limit_window_seconds)
    if not allowed:
        raise HTTPException(status_code=429, detail="Rate limit exceeded", headers={"Retry-After": str(retry_after)})
    return service(request).create(payload)

@router.get("/api/complaints/{complaint_id}", response_model=ComplaintOut)
def get_complaint(complaint_id: UUID, request: Request):
    try: return service(request).get(complaint_id)
    except NotFoundError as exc: raise HTTPException(404, str(exc)) from exc

@router.get("/api/complaints", response_model=ComplaintPage)
def list_complaints(request: Request, category: Category | None = None, priority: Priority | None = None, status: Status | None = None, page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100)):
    return service(request).list(category, priority, status, page, page_size)

@router.patch("/api/complaints/{complaint_id}/status", response_model=ComplaintOut)
def update_status(complaint_id: UUID, payload: StatusUpdate, request: Request):
    try: return service(request).set_status(complaint_id, payload.status)
    except NotFoundError as exc: raise HTTPException(404, str(exc)) from exc
    except InvalidTransitionError as exc: raise HTTPException(409, str(exc)) from exc

@router.get("/api/stats", response_model=StatsOut)
def stats(request: Request, response: Response):
    result, cache_state = service(request).stats()
    response.headers["X-Cache"] = cache_state
    return result

@router.get("/api/meta/providers", response_model=ProvidersOut)
def providers(request: Request):
    triage = request.app.state.triage
    return ProvidersOut(active_provider=triage.provider.name, outcomes=triage.outcomes)

@router.get("/health")
def health():
    return {"status": "ok"}

@router.get("/ready")
def ready(request: Request):
    failures = []
    if not request.app.state.repository.healthcheck(): failures.append("postgres")
    if not request.app.state.redis.ping(): failures.append("redis")
    if failures: raise HTTPException(503, detail="Unavailable: " + ", ".join(failures))
    return {"status": "ready"}

@router.get("/metrics")
def metrics(request: Request):
    return Response(content=request.app.state.metrics.render(), media_type="text/plain; version=0.0.4; charset=utf-8")
