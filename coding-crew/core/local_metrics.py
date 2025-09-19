"""Local performance monitoring and metrics collection."""

import psutil
import time
from typing import Dict, Any, List
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import threading
from loguru import logger


@dataclass
class MetricPoint:
    timestamp: datetime
    value: float
    tags: Dict[str, str] = None


class LocalMetrics:
    """Local metrics collector for AgentAI performance monitoring."""
    
    def __init__(self, retention_hours: int = 24):
        self.retention_hours = retention_hours
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.counters: Dict[str, int] = defaultdict(int)
        self.gauges: Dict[str, float] = defaultdict(float)
        self.timers: Dict[str, List[float]] = defaultdict(list)
        self.running = False
        self.collection_thread = None
        
    def start_collection(self, interval: int = 30):
        """Start automatic metrics collection."""
        if not self.running:
            self.running = True
            self.collection_thread = threading.Thread(
                target=self._collect_system_metrics,
                args=(interval,),
                daemon=True
            )
            self.collection_thread.start()
            logger.info(f"Metrics collection started (interval: {interval}s)")
    
    def stop_collection(self):
        """Stop metrics collection."""
        self.running = False
        if self.collection_thread:
            self.collection_thread.join()
        logger.info("Metrics collection stopped")
    
    def record_counter(self, name: str, value: int = 1, tags: Dict[str, str] = None):
        """Record a counter metric."""
        self.counters[name] += value
        self._add_metric(name, value, tags)
    
    def record_gauge(self, name: str, value: float, tags: Dict[str, str] = None):
        """Record a gauge metric."""
        self.gauges[name] = value
        self._add_metric(name, value, tags)
    
    def record_timer(self, name: str, duration_ms: float, tags: Dict[str, str] = None):
        """Record a timer metric."""
        self.timers[name].append(duration_ms)
        # Keep only last 100 measurements
        if len(self.timers[name]) > 100:
            self.timers[name] = self.timers[name][-100:]
        self._add_metric(name, duration_ms, tags)
    
    def _add_metric(self, name: str, value: float, tags: Dict[str, str] = None):
        """Add metric point to time series."""
        point = MetricPoint(
            timestamp=datetime.now(),
            value=value,
            tags=tags or {}
        )
        self.metrics[name].append(point)
        self._cleanup_old_metrics()
    
    def _cleanup_old_metrics(self):
        """Remove old metric points."""
        cutoff = datetime.now() - timedelta(hours=self.retention_hours)
        for name, points in self.metrics.items():
            while points and points[0].timestamp < cutoff:
                points.popleft()
    
    def _collect_system_metrics(self, interval: int):
        """Collect system metrics periodically."""
        while self.running:
            try:
                # CPU metrics
                cpu_percent = psutil.cpu_percent(interval=1)
                self.record_gauge("system.cpu.percent", cpu_percent)
                
                # Memory metrics
                memory = psutil.virtual_memory()
                self.record_gauge("system.memory.percent", memory.percent)
                self.record_gauge("system.memory.used_gb", memory.used / (1024**3))
                
                # Disk metrics
                disk = psutil.disk_usage('/')
                self.record_gauge("system.disk.percent", disk.percent)
                self.record_gauge("system.disk.used_gb", disk.used / (1024**3))
                
                # Process metrics
                process = psutil.Process()
                self.record_gauge("process.cpu.percent", process.cpu_percent())
                self.record_gauge("process.memory.mb", process.memory_info().rss / (1024**2))
                
                time.sleep(interval)
                
            except Exception as e:
                logger.error(f"System metrics collection error: {e}")
                time.sleep(interval)
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """Get current metric values."""
        return {
            "system": {
                "cpu_percent": self.gauges.get("system.cpu.percent", 0),
                "memory_percent": self.gauges.get("system.memory.percent", 0),
                "memory_used_gb": self.gauges.get("system.memory.used_gb", 0),
                "disk_percent": self.gauges.get("system.disk.percent", 0),
                "disk_used_gb": self.gauges.get("system.disk.used_gb", 0)
            },
            "process": {
                "cpu_percent": self.gauges.get("process.cpu.percent", 0),
                "memory_mb": self.gauges.get("process.memory.mb", 0)
            },
            "application": {
                "total_projects": self.counters.get("projects.created", 0),
                "total_analyses": self.counters.get("analyses.completed", 0),
                "total_code_generations": self.counters.get("code.generated", 0),
                "avg_analysis_time": self._get_avg_timer("analysis.duration_ms"),
                "avg_code_gen_time": self._get_avg_timer("code_generation.duration_ms")
            }
        }
    
    def get_time_series(self, metric_name: str, hours: int = 1) -> List[Dict[str, Any]]:
        """Get time series data for a metric."""
        cutoff = datetime.now() - timedelta(hours=hours)
        points = self.metrics.get(metric_name, [])
        
        return [
            {
                "timestamp": point.timestamp.isoformat(),
                "value": point.value,
                "tags": point.tags
            }
            for point in points
            if point.timestamp >= cutoff
        ]
    
    def _get_avg_timer(self, name: str) -> float:
        """Get average timer value."""
        values = self.timers.get(name, [])
        return sum(values) / len(values) if values else 0
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary for dashboard."""
        return {
            "uptime_hours": (datetime.now() - datetime.now().replace(hour=0, minute=0, second=0)).total_seconds() / 3600,
            "requests_per_minute": self.counters.get("requests.total", 0) / max(1, (datetime.now().hour * 60 + datetime.now().minute)),
            "error_rate": self.counters.get("errors.total", 0) / max(1, self.counters.get("requests.total", 1)),
            "avg_response_time_ms": self._get_avg_timer("request.duration_ms"),
            "cache_hit_rate": self.counters.get("cache.hits", 0) / max(1, self.counters.get("cache.requests", 1)),
            "active_tasks": self.gauges.get("tasks.active", 0)
        }


# Global metrics instance
local_metrics = LocalMetrics()


# Context manager for timing operations
class Timer:
    def __init__(self, metric_name: str, tags: Dict[str, str] = None):
        self.metric_name = metric_name
        self.tags = tags
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            duration_ms = (time.time() - self.start_time) * 1000
            local_metrics.record_timer(self.metric_name, duration_ms, self.tags)


# Decorator for timing functions
def timed_operation(metric_name: str = None, tags: Dict[str, str] = None):
    """Decorator to time function execution."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            name = metric_name or f"{func.__name__}.duration_ms"
            with Timer(name, tags):
                return func(*args, **kwargs)
        return wrapper
    return decorator