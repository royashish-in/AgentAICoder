"""Async processing for non-blocking operations."""

import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, Any, Dict, Optional
from datetime import datetime
import uuid
from loguru import logger
from dataclasses import dataclass
from enum import Enum


class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class AsyncTask:
    id: str
    name: str
    status: TaskStatus
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Any = None
    error: Optional[str] = None
    progress: int = 0


class AsyncProcessor:
    """Local async processor for background tasks."""
    
    def __init__(self, max_workers: int = 4):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.tasks: Dict[str, AsyncTask] = {}
        self.task_queue = asyncio.Queue()
        self.running = False
        
    async def start(self):
        """Start the async processor."""
        if not self.running:
            self.running = True
            asyncio.create_task(self._process_queue())
            logger.info(f"AsyncProcessor started with {self.executor._max_workers} workers")
    
    async def stop(self):
        """Stop the async processor."""
        self.running = False
        self.executor.shutdown(wait=True)
        logger.info("AsyncProcessor stopped")
    
    async def submit_task(self, name: str, func: Callable, *args, **kwargs) -> str:
        """Submit a task for async processing."""
        task_id = str(uuid.uuid4())
        task = AsyncTask(
            id=task_id,
            name=name,
            status=TaskStatus.PENDING,
            created_at=datetime.now()
        )
        
        self.tasks[task_id] = task
        await self.task_queue.put((task_id, func, args, kwargs))
        
        logger.info(f"Task submitted: {name} ({task_id})")
        return task_id
    
    async def get_task_status(self, task_id: str) -> Optional[AsyncTask]:
        """Get task status and result."""
        return self.tasks.get(task_id)
    
    async def get_all_tasks(self) -> Dict[str, AsyncTask]:
        """Get all tasks."""
        return self.tasks.copy()
    
    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a pending task."""
        if task_id in self.tasks:
            task = self.tasks[task_id]
            if task.status == TaskStatus.PENDING:
                task.status = TaskStatus.FAILED
                task.error = "Cancelled by user"
                task.completed_at = datetime.now()
                return True
        return False
    
    async def _process_queue(self):
        """Process the task queue."""
        while self.running:
            try:
                # Wait for task with timeout to allow checking running status
                task_item = await asyncio.wait_for(self.task_queue.get(), timeout=1.0)
                task_id, func, args, kwargs = task_item
                
                if task_id in self.tasks:
                    asyncio.create_task(self._execute_task(task_id, func, args, kwargs))
                    
            except asyncio.TimeoutError:
                continue  # Check if still running
            except Exception as e:
                logger.error(f"Queue processing error: {e}")
    
    async def _execute_task(self, task_id: str, func: Callable, args: tuple, kwargs: dict):
        """Execute a single task."""
        task = self.tasks[task_id]
        
        try:
            task.status = TaskStatus.RUNNING
            task.started_at = datetime.now()
            
            # Run in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(self.executor, func, *args, **kwargs)
            
            task.status = TaskStatus.COMPLETED
            task.result = result
            task.progress = 100
            task.completed_at = datetime.now()
            
            logger.info(f"Task completed: {task.name} ({task_id})")
            
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error = str(e)
            task.completed_at = datetime.now()
            
            logger.error(f"Task failed: {task.name} ({task_id}) - {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get processor statistics."""
        total_tasks = len(self.tasks)
        completed_tasks = sum(1 for t in self.tasks.values() if t.status == TaskStatus.COMPLETED)
        failed_tasks = sum(1 for t in self.tasks.values() if t.status == TaskStatus.FAILED)
        running_tasks = sum(1 for t in self.tasks.values() if t.status == TaskStatus.RUNNING)
        
        return {
            "running": self.running,
            "max_workers": self.executor._max_workers,
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "failed_tasks": failed_tasks,
            "running_tasks": running_tasks,
            "success_rate": completed_tasks / total_tasks if total_tasks > 0 else 0
        }


# Global async processor
async_processor = AsyncProcessor()


# Decorator for async task execution
def async_task(name: str = None):
    """Decorator to make functions run as async tasks."""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            task_name = name or f"{func.__name__}"
            task_id = await async_processor.submit_task(task_name, func, *args, **kwargs)
            return task_id
        return wrapper
    return decorator


# Common async operations
@async_task("AI Requirements Analysis")
def async_analyze_requirements(project_data: Dict[str, Any]) -> str:
    """Async wrapper for requirements analysis."""
    try:
        from agents.analysis_crew import AnalysisCrew
        crew = AnalysisCrew()
        return crew.analyze_requirements(project_data)
    except Exception as e:
        logger.error(f"Async analysis failed: {e}")
        return f"Analysis failed: {str(e)}"


@async_task("AI Code Generation")
def async_generate_code(project_data: Dict[str, Any], analysis: str) -> Dict[str, Any]:
    """Async wrapper for code generation."""
    try:
        from agents.enhanced_development_crew import EnhancedDevelopmentCrew
        crew = EnhancedDevelopmentCrew()
        return crew.generate_code(project_data, analysis)
    except Exception as e:
        logger.error(f"Async code generation failed: {e}")
        return {"code": f"Code generation failed: {str(e)}", "files_generated": []}


@async_task("Test Generation")
def async_generate_tests(project_data: Dict[str, Any], code: str) -> Dict[str, Any]:
    """Async wrapper for test generation."""
    try:
        from agents.test_cycle_crew import TestCycleCrew
        crew = TestCycleCrew()
        return crew.run_test_cycle(project_data, code)
    except Exception as e:
        logger.error(f"Async test generation failed: {e}")
        return {"final_tests": f"Test generation failed: {str(e)}", "iterations_completed": 0}