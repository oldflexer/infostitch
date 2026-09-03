"""Prometheus Metrics for Observability.

Provides counters, histograms, and gauges for monitoring pipeline performance.
"""
from __future__ import annotations

from typing import Dict, Optional

from typing import Any, Dict, Optional
from prometheus_client import Counter, Gauge, Histogram, Info

from infrastructure.config import get_settings


# Pipeline metrics
pipeline_runs_total = Counter(
    "infostitch_pipeline_runs_total",
    "Total number of pipeline runs",
    ["status"],  # success, failure
)

pipeline_duration_seconds = Histogram(
    "infostitch_pipeline_duration_seconds",
    "Pipeline execution duration in seconds",
    ["dummy"],  # dummy label to allow .labels() calls
    buckets=[1, 5, 10, 30, 60, 120, 300, 600],
)

pipeline_step_duration_seconds = Histogram(
    "infostitch_pipeline_step_duration_seconds",
    "Pipeline step execution duration in seconds",
    ["step"],
    buckets=[0.1, 0.5, 1, 2, 5, 10, 30, 60, 120],
)

# Article processing metrics
articles_fetched_total = Counter(
    "infostitch_articles_fetched_total",
    "Total number of articles fetched from RSS feeds",
    ["source"],
)

articles_deduplicated_total = Counter(
    "infostitch_articles_deduplicated_total",
    "Total number of articles removed by deduplication",
    ["stage"],  # url, jaccard, embedding
)

articles_selected_total = Counter(
    "infostitch_articles_selected_total",
    "Total number of articles selected for publishing",
)

articles_published_total = Counter(
    "infostitch_articles_published_total",
    "Total number of articles published",
    ["channel", "status"],  # success, failure
)

# API call metrics
api_calls_total = Counter(
    "infostitch_api_calls_total",
    "Total number of external API calls",
    ["service", "endpoint", "status"],  # success, failure, timeout
)

api_call_duration_seconds = Histogram(
    "infostitch_api_call_duration_seconds",
    "External API call duration in seconds",
    ["service", "endpoint"],
    buckets=[0.1, 0.5, 1, 2, 5, 10, 30, 60],
)

# Database metrics
db_operations_total = Counter(
    "infostitch_db_operations_total",
    "Total number of database operations",
    ["operation", "status"],  # select, insert, update, delete / success, failure
)

db_operation_duration_seconds = Histogram(
    "infostitch_db_operation_duration_seconds",
    "Database operation duration in seconds",
    ["operation"],
    buckets=[0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1, 5],
)

# Cache metrics
cache_operations_total = Counter(
    "infostitch_cache_operations_total",
    "Total number of cache operations",
    ["operation", "status"],  # get, set, delete / hit, miss
)

# System metrics
active_pipeline_runs = Gauge(
    "infostitch_active_pipeline_runs",
    "Number of currently running pipeline instances",
)

queue_size = Gauge(
    "infostitch_queue_size",
    "Number of items in processing queue",
)

# Application info
app_info = Info(
    "infostitch_app_info",
    "Application information",
)

# Initialize app info


def init_metrics() -> None:
    """Initialize metrics with application info."""
    settings = get_settings()
    app_info.info({
        "version": "0.1.0",
        "environment": settings.app_env,
    })


class MetricsContext:
    """Context manager for timing operations."""

    def __init__(self, histogram: Histogram,
                 labels: Optional[Dict[str, str]] = None):
        self.histogram = histogram
        self.labels = labels or {}
        self.timer = None

    def __enter__(self) -> "MetricsContext":
        self.timer = self.histogram.labels(**self.labels).time()
        self.timer.__enter__()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        if self.timer:
            self.timer.__exit__(exc_type, exc_val, exc_tb)


def increment_counter(counter: Counter,
                      labels: Optional[Dict[str,
                                            str]] = None,
                      value: float = 1.0) -> None:
    """Increment a counter with labels."""
    if labels:
        counter.labels(**labels).inc(value)
    else:
        counter.inc(value)


def observe_histogram(histogram: Histogram, value: float,
                      labels: Optional[Dict[str, str]] = None) -> None:
    """Observe a value in a histogram with labels."""
    if labels:
        histogram.labels(**labels).observe(value)
    else:
        histogram.observe(value)


def set_gauge(gauge: Gauge, value: float,
              labels: Optional[Dict[str, str]] = None) -> None:
    """Set a gauge value with labels."""
    if labels:
        gauge.labels(**labels).set(value)
    else:
        gauge.set(value)
