from prometheus_client import Counter

issues_processed = Counter(
    "issues_processed_total",
    "Total issues processed"
)

issues_success = Counter(
    "issues_success_total",
    "Total successful fixes"
)

issues_failed = Counter(
    "issues_failed_total",
    "Total failed fixes"
)

issues_rolled_back = Counter(
    "issues_rolled_back_total",
    "Total rolled back fixes"
)

api_requests = Counter(
    "api_requests_total",
    "Total API requests"
)
