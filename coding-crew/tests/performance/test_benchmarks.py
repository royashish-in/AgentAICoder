"""Performance benchmarks for coding crew application."""

import pytest
import time
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.crew_workflow import CrewWorkflowOrchestrator
from agents.crew_agents import create_analysis_agent


class TestPerformanceBenchmarks:
    """Performance benchmark tests."""
    
    def test_workflow_creation_performance(self, benchmark):
        """Benchmark workflow creation speed."""
        orchestrator = CrewWorkflowOrchestrator()
        
        def create_workflow():
            return orchestrator.create_workflow("Build a web application")
        
        result = benchmark(create_workflow)
        assert result is not None
    
    def test_agent_creation_performance(self, benchmark):
        """Benchmark agent creation speed."""
        def create_agent():
            return create_analysis_agent()
        
        agent = benchmark(create_agent)
        assert agent is not None
        assert agent.role == "Requirements Analyst & System Architect"
    
    def test_multiple_workflow_creation(self):
        """Test creating multiple workflows performance."""
        orchestrator = CrewWorkflowOrchestrator()
        
        start_time = time.time()
        
        # Create 10 workflows
        workflow_ids = []
        for i in range(10):
            workflow_id = orchestrator.create_workflow(f"Build application {i}")
            workflow_ids.append(workflow_id)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should create 10 workflows in under 1 second
        assert duration < 1.0
        assert len(workflow_ids) == 10
        assert len(orchestrator.workflows) == 10
    
    def test_workflow_status_retrieval_performance(self):
        """Test workflow status retrieval performance."""
        orchestrator = CrewWorkflowOrchestrator()
        
        # Create workflows
        workflow_ids = []
        for i in range(100):
            workflow_id = orchestrator.create_workflow(f"App {i}")
            workflow_ids.append(workflow_id)
        
        # Measure status retrieval time
        start_time = time.time()
        
        for workflow_id in workflow_ids:
            status = orchestrator.get_workflow_status(workflow_id)
            assert status["workflow_id"] == workflow_id
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should retrieve 100 statuses in under 0.1 seconds
        assert duration < 0.1
    
    @pytest.mark.slow
    def test_memory_usage_multiple_workflows(self):
        """Test memory usage with multiple workflows."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        orchestrator = CrewWorkflowOrchestrator()
        
        # Create many workflows
        for i in range(1000):
            orchestrator.create_workflow(f"Large application {i} with detailed requirements")
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (< 100MB for 1000 workflows)
        assert memory_increase < 100
        
        print(f"Memory usage: {initial_memory:.1f}MB -> {final_memory:.1f}MB (+{memory_increase:.1f}MB)")
    
    def test_concurrent_workflow_operations(self):
        """Test concurrent workflow operations performance."""
        import threading
        import queue
        
        orchestrator = CrewWorkflowOrchestrator()
        results = queue.Queue()
        
        def create_and_check_workflow(thread_id):
            try:
                # Create workflow
                workflow_id = orchestrator.create_workflow(f"Thread {thread_id} application")
                
                # Check status
                status = orchestrator.get_workflow_status(workflow_id)
                
                results.put({"thread_id": thread_id, "success": True, "workflow_id": workflow_id})
            except Exception as e:
                results.put({"thread_id": thread_id, "success": False, "error": str(e)})
        
        # Create 5 concurrent threads
        threads = []
        start_time = time.time()
        
        for i in range(5):
            thread = threading.Thread(target=create_and_check_workflow, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Collect results
        thread_results = []
        while not results.empty():
            thread_results.append(results.get())
        
        # All threads should succeed
        assert len(thread_results) == 5
        for result in thread_results:
            assert result["success"] is True
        
        # Should complete in reasonable time
        assert duration < 2.0
        
        print(f"Concurrent operations completed in {duration:.2f}s")