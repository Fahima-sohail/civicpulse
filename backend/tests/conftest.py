import fakeredis
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.config import Settings
from app.db import Base
from app.main import create_app
from app.providers.redis_client import RedisClient
from app.providers.triage.simulated import SimulatedTriage

def fake_redis():
    wrapper = RedisClient.__new__(RedisClient)
    wrapper.client = fakeredis.FakeRedis(decode_responses=True)
    return wrapper

@pytest.fixture
def app():
    engine = create_engine("sqlite+pysqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    application = create_app(
        settings=Settings(database_url="sqlite+pysqlite://", redis_url="redis://unused", triage_provider="simulated", rate_limit_count=20),
        redis_client=fake_redis(),
        session_factory=sessionmaker(engine, expire_on_commit=False),
        provider=SimulatedTriage(),
    )
    yield application
    engine.dispose()

@pytest.fixture
def client(app):
    with TestClient(app) as test_client: yield test_client

@pytest.fixture
def complaint_payload():
    return {"text": "Water pipe burst near school and road is flooding badly.", "location": "Street 12, Gulshan"}
