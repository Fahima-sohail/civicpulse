from prometheus_client import CollectorRegistry, Counter, Histogram, generate_latest

class Metrics:
    def __init__(self):
        self.registry = CollectorRegistry()
        self.requests = Counter("civicpulse_http_requests_total", "HTTP requests", ["method", "path", "status"], registry=self.registry)
        self.request_latency = Histogram("civicpulse_http_request_latency_seconds", "HTTP request latency", ["method", "path"], registry=self.registry)
        self.triage_latency = Histogram("civicpulse_triage_latency_seconds", "Triage latency", registry=self.registry)
        self.fallbacks = Counter("civicpulse_triage_fallback_total", "Triage fallbacks", registry=self.registry)
    def render(self) -> bytes: return generate_latest(self.registry)
