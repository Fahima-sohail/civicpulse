import json
import time
from typing import Any
import redis

class RedisClient:
    def __init__(self, url: str):
        self.client = redis.Redis.from_url(url, decode_responses=True)

    def get_json(self, key: str) -> dict[str, Any] | None:
        value = self.client.get(key)
        return json.loads(value) if value else None

    def set_json(self, key: str, value: dict[str, Any], ttl: int) -> None:
        self.client.set(key, json.dumps(value), ex=ttl)

    def delete(self, key: str) -> None:
        self.client.delete(key)

    def ping(self) -> bool:
        try: return bool(self.client.ping())
        except Exception: return False

    def check_rate_limit(self, ip: str, limit: int, window_seconds: int) -> tuple[bool, int]:
        key = f"rate-limit:{ip}:{int(time.time() // window_seconds)}"
        with self.client.pipeline() as pipe:
            pipe.incr(key)
            pipe.ttl(key)
            count, ttl = pipe.execute()
        if ttl < 0: self.client.expire(key, window_seconds); ttl = window_seconds
        return int(count) <= limit, max(1, int(ttl))
