"""Performance monitoring and metrics collection."""

import time
import psutil
import json
from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict
import threading
from collections import defaultdict

@dataclass
class PerformanceMetrics:
    """Performance metrics data structure."""
    timestamp: str
    operation: str
    duration_ms: float
    cpu_percent: float
    memory_mb: float
    disk_io_mb: float
    tokens_processed: Optional[int] = None
    model_name: Optional[str] = None
    agent_type: Optional[str] = None
    project_id: Optional[str] = None

class PerformanceMonitor:
    """System performance monitoring."""
    
    def __init__(self):
        self.metrics_file = Path("coding-crew/metrics/performance.jsonl")
        self.metrics_file.parent.mkdir(parents=True, exist_ok=True)
        self.active_operations = {}
        self.lock = threading.Lock()
    
    def start_operation(self, operation_id: str, operation_name: str, 
                       agent_type: str = None, project_id: str = None) -> str:
        """Start monitoring an operation."""
        with self.lock:
            self.active_operations[operation_id] = {
                "name": operation_name,
                "start_time": time.time(),
                "start_cpu": psutil.cpu_percent(),
                "start_memory": psutil.virtual_memory().used / 1024 / 1024,
                "start_disk": self._get_disk_io(),
                "agent_type": agent_type,
                "project_id": project_id
            }
        return operation_id
    
    def end_operation(self, operation_id: str, tokens_processed: int = None, 
                     model_name: str = None) -> PerformanceMetrics:
        """End monitoring and record metrics."""
        with self.lock:
            if operation_id not in self.active_operations:
                return None
            
            op = self.active_operations.pop(operation_id)
            end_time = time.time()
            
            metrics = PerformanceMetrics(
                timestamp=datetime.now().isoformat(),
                operation=op["name"],
                duration_ms=(end_time - op["start_time"]) * 1000,
                cpu_percent=psutil.cpu_percent() - op["start_cpu"],
                memory_mb=psutil.virtual_memory().used / 1024 / 1024 - op["start_memory"],
                disk_io_mb=self._get_disk_io() - op["start_disk"],
                tokens_processed=tokens_processed,
                model_name=model_name,
                agent_type=op["agent_type"],
                project_id=op["project_id"]
            )
            
            self._save_metrics(metrics)
            return metrics
    
    def _get_disk_io(self) -> float:
        """Get current disk I/O in MB."""
        try:
            disk_io = psutil.disk_io_counters()
            return (disk_io.read_bytes + disk_io.write_bytes) / 1024 / 1024
        except:
            return 0.0
    
    def _save_metrics(self, metrics: PerformanceMetrics):
        """Save metrics to file."""
        with open(self.metrics_file, "a") as f:
            f.write(json.dumps(asdict(metrics)) + "\n")
    
    def get_metrics_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get performance metrics summary."""
        if not self.metrics_file.exists():
            return {"error": "No metrics available"}
        
        cutoff_time = datetime.now().timestamp() - (hours * 3600)
        operations = defaultdict(list)
        
        with open(self.metrics_file, "r") as f:
            for line in f:
                try:
                    metric = json.loads(line.strip())
                    metric_time = datetime.fromisoformat(metric["timestamp"]).timestamp()
                    
                    if metric_time > cutoff_time:
                        operations[metric["operation"]].append(metric)
                except:
                    continue
        
        summary = {}
        for op_name, metrics in operations.items():
            if metrics:
                durations = [m["duration_ms"] for m in metrics]
                cpu_usage = [m["cpu_percent"] for m in metrics]
                memory_usage = [m["memory_mb"] for m in metrics]
                
                summary[op_name] = {
                    "count": len(metrics),
                    "avg_duration_ms": sum(durations) / len(durations),
                    "max_duration_ms": max(durations),
                    "avg_cpu_percent": sum(cpu_usage) / len(cpu_usage),
                    "avg_memory_mb": sum(memory_usage) / len(memory_usage),
                    "total_tokens": sum(m.get("tokens_processed", 0) for m in metrics)
                }
        
        return summary

class LLMMetricsCollector:
    """Collect LLM-specific performance metrics."""
    
    def __init__(self):
        self.metrics_file = Path("coding-crew/metrics/llm_metrics.jsonl")
        self.metrics_file.parent.mkdir(parents=True, exist_ok=True)
    
    def record_llm_call(self, model_name: str, operation: str, 
                       input_tokens: int, output_tokens: int, 
                       duration_ms: float, success: bool = True):
        """Record LLM API call metrics."""
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "model_name": model_name,
            "operation": operation,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": input_tokens + output_tokens,
            "duration_ms": duration_ms,
            "tokens_per_second": (input_tokens + output_tokens) / (duration_ms / 1000) if duration_ms > 0 else 0,
            "success": success
        }
        
        with open(self.metrics_file, "a") as f:
            f.write(json.dumps(metrics) + "\n")
    
    def get_llm_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get LLM performance summary."""
        if not self.metrics_file.exists():
            return {"error": "No LLM metrics available"}
        
        cutoff_time = datetime.now().timestamp() - (hours * 3600)
        model_metrics = defaultdict(list)
        
        with open(self.metrics_file, "r") as f:
            for line in f:
                try:
                    metric = json.loads(line.strip())
                    metric_time = datetime.fromisoformat(metric["timestamp"]).timestamp()
                    
                    if metric_time > cutoff_time:
                        model_metrics[metric["model_name"]].append(metric)
                except:
                    continue
        
        summary = {}
        for model, metrics in model_metrics.items():
            if metrics:
                total_tokens = sum(m["total_tokens"] for m in metrics)
                successful_calls = sum(1 for m in metrics if m["success"])
                
                summary[model] = {
                    "total_calls": len(metrics),
                    "successful_calls": successful_calls,
                    "success_rate": successful_calls / len(metrics),
                    "total_tokens": total_tokens,
                    "avg_tokens_per_second": sum(m["tokens_per_second"] for m in metrics) / len(metrics),
                    "avg_duration_ms": sum(m["duration_ms"] for m in metrics) / len(metrics)
                }
        
        return summary

class WorkflowMetricsCollector:
    """Collect end-to-end workflow metrics."""
    
    def __init__(self):
        self.metrics_file = Path("coding-crew/metrics/workflow_metrics.jsonl")
        self.metrics_file.parent.mkdir(parents=True, exist_ok=True)
        self.active_workflows = {}
    
    def start_workflow(self, project_id: str, workflow_type: str):
        """Start tracking a workflow."""
        self.active_workflows[project_id] = {
            "workflow_type": workflow_type,
            "start_time": time.time(),
            "phases": []
        }
    
    def record_phase(self, project_id: str, phase_name: str, duration_ms: float, 
                    success: bool = True, error: str = None):
        """Record a workflow phase completion."""
        if project_id in self.active_workflows:
            self.active_workflows[project_id]["phases"].append({
                "phase": phase_name,
                "duration_ms": duration_ms,
                "success": success,
                "error": error,
                "timestamp": datetime.now().isoformat()
            })
    
    def end_workflow(self, project_id: str, success: bool = True, 
                    final_status: str = "completed"):
        """End workflow tracking and save metrics."""
        if project_id not in self.active_workflows:
            return
        
        workflow = self.active_workflows.pop(project_id)
        end_time = time.time()
        
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "project_id": project_id,
            "workflow_type": workflow["workflow_type"],
            "total_duration_ms": (end_time - workflow["start_time"]) * 1000,
            "phases": workflow["phases"],
            "success": success,
            "final_status": final_status,
            "phase_count": len(workflow["phases"])
        }
        
        with open(self.metrics_file, "a") as f:
            f.write(json.dumps(metrics) + "\n")

# Global instances
performance_monitor = PerformanceMonitor()
llm_metrics = LLMMetricsCollector()
workflow_metrics = WorkflowMetricsCollector()