import asyncio
import signal
import time
import threading
import uuid
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.config import get_settings
from app.db import make_engine, make_session_factory
from app.logging import configure_logging, request_id_var
from app.providers.redis_client import RedisClient
from app.providers.triage.factory import make_triage_provider
from app.repositories.complaints import ComplaintRepository
from app.routes.api import router
from app.services.complaints import ComplaintService
from app.services.metrics import Metrics
from app.services.triage import TriageService

def create_app(settings=None, redis_client=None, session_factory=None, provider=None) -> FastAPI:
    configure_logging()
    settings = settings or get_settings()
    engine = None if session_factory else make_engine(settings.database_url)
    session_factory = session_factory or make_session_factory(settings.database_url)
    redis_client = redis_client or RedisClient(settings.redis_url)
    provider = provider or make_triage_provider(settings)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        app.state.accepting = True
        app.state.inflight = 0
        def stopping(*_): app.state.accepting = False
        can_manage_signal = threading.current_thread() is threading.main_thread()
        previous = signal.getsignal(signal.SIGTERM) if can_manage_signal else None
        if can_manage_signal: signal.signal(signal.SIGTERM, stopping)
        try:
            yield
        finally:
            app.state.accepting = False
            deadline = time.monotonic() + 15
            while app.state.inflight and time.monotonic() < deadline:
                await asyncio.sleep(0.05)
            if engine is not None: engine.dispose()
            if can_manage_signal: signal.signal(signal.SIGTERM, previous)

    app = FastAPI(title="CivicPulse", version="0.1.0", lifespan=lifespan)
    app.state.settings = settings
    app.state.redis = redis_client
    app.state.repository = ComplaintRepository(session_factory)
    app.state.metrics = Metrics()
    app.state.triage = TriageService(provider, redis_client, app.state.metrics)
    app.state.complaints = ComplaintService(app.state.repository, app.state.triage, redis_client)

    @app.exception_handler(RequestValidationError)
    async def validation_error(_: Request, exc: RequestValidationError):
        return JSONResponse(status_code=400, content={"detail": exc.errors()})

    @app.middleware("http")
    async def observability(request: Request, call_next):
        if not request.app.state.accepting:
            return JSONResponse(status_code=503, content={"detail": "Server is shutting down"})
        request.app.state.inflight += 1
        token = request_id_var.set(request.headers.get("X-Request-ID", str(uuid.uuid4())))
        started = time.perf_counter()
        response = None
        try:
            response = await call_next(request)
            response.headers["X-Request-ID"] = request_id_var.get()
            return response
        finally:
            elapsed = time.perf_counter() - started
            response_status = response.status_code if response is not None else 500
            request.app.state.metrics.requests.labels(request.method, request.url.path, str(response_status)).inc()
            request.app.state.metrics.request_latency.labels(request.method, request.url.path).observe(elapsed)
            request.app.state.inflight -= 1
            request_id_var.reset(token)

    app.include_router(router)
    return app

app = create_app()
