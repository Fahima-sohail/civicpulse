import contextvars
import json
import logging
request_id_var: contextvars.ContextVar[str] = contextvars.ContextVar("request_id", default="-")

class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {"level": record.levelname, "message": record.getMessage(), "logger": record.name, "request_id": request_id_var.get()}
        for field in ("complaint_id", "provider", "error_class"):
            if hasattr(record, field): payload[field] = getattr(record, field)
        return json.dumps(payload, default=str)

def configure_logging() -> None:
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(logging.INFO)
