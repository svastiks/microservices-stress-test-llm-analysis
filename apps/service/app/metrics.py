from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST

REQUEST_DURATION = Histogram(
    "http_request_duration_seconds", "Request duration", ["method", "path"], buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0)
)
REQUESTS_IN_FLIGHT = Gauge("http_requests_in_flight", "In-flight requests", ["path"])
ERROR_COUNT = Counter("http_errors_total", "Total errors", ["method", "path", "status"])

def metrics_response():
    return generate_latest(), CONTENT_TYPE_LATEST
