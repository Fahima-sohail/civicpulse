from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from app.config import get_settings

class Base(DeclarativeBase):
    pass

def make_engine(url: str | None = None):
    return create_engine(url or get_settings().database_url, pool_pre_ping=True)

def make_session_factory(url: str | None = None):
    return sessionmaker(bind=make_engine(url), expire_on_commit=False)
