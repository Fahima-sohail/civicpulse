from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    database_url: str = "postgresql+psycopg://civicpulse:civicpulse@postgres:5432/civicpulse"
    redis_url: str = "redis://redis:6379/0"
    triage_provider: str = "rules"
    simulated_failure_mode: str = "none"
    groq_api_key: str | None = None
    groq_model: str = "llama-3.1-8b-instant"
    ollama_base_url: str = "http://ollama:11434"
    ollama_model: str = "llama3.2:1b"
    rate_limit_count: int = 20
    rate_limit_window_seconds: int = 60

@lru_cache
def get_settings() -> Settings:
    return Settings()
